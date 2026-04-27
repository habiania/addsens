import streamlit as st
import os
import pickle
import time
import random
from datetime import datetime, timedelta
import google.generativeai as genai
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- 1. 설정 정보 ---
BLOG_ID = '8075636289883732328'
JSON_FILE = 'client_secret.json' 
GEMINI_API_KEY = "AIzaSyAw7YnMqZS4ObAVaO8b3yMFCcY3No_r1ik"

# API 설정
genai.configure(api_key=GEMINI_API_KEY)

# [에러 해결 핵심] 모델명을 최신 표준인 'gemini-1.5-flash' 또는 'models/gemini-1.5-flash'로 시도합니다.
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('models/gemini-1.5-flash')

# --- 2. Blogger API 인증 함수 ---
def get_blogger_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(JSON_FILE, ['https://www.googleapis.com/auth/blogger'])
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('blogger', 'v3', credentials=creds)

# --- 3. UI 구성 ---
st.set_page_config(page_title="Human-Like AdSense Bot", layout="wide")
st.title("✍️ Human-Like AdSense Approval Automation")
st.info("AI 흔적을 지운 2,500자 포스팅 5개를 2시간 간격으로 예약 발행합니다.")

keyword = st.text_input("메인 키워드 입력", placeholder="예: High-yield savings accounts in 2026")

if st.button("AI 흔적 제거 포스팅 5개 예약 시작"):
    if not keyword:
        st.error("키워드를 입력해주세요.")
    else:
        service = get_blogger_service()
        progress_bar = st.progress(0)
        
        # 각각 다른 스타일로 AI 패턴 파괴
        styles = [
            "In-depth Beginner's Guide",
            "Advanced Strategies & Analysis",
            "Personal Case Study & Results",
            "Common Pitfalls to Avoid",
            "Comparison & Ultimate Verdict"
        ]

        for i, style in enumerate(styles):
            with st.spinner(f"[{i+1}/5] '{style}' 스타일 글 작성 및 예약 중..."):
                try:
                    # AI 흔적 제거용 강화 프롬프트
                    prompt = f"""
                    Write a 2,500+ word blog post in American English. 
                    Topic: '{keyword}' / Style: {style}

                    [HUMAN-LIKE INSTRUCTIONS]:
                    1. NO AI CLICHES: Avoid "In the fast-paced world," "In conclusion," "Unlocking the potential."
                    2. TONE: Conversational, slightly opinionated, and highly practical. Use "I" and "You."
                    3. CONTENT: Include a "Real-World Example" and a "My Honest Opinion" section.
                    4. FORMAT: Use HTML (H2, H3, P, B, UL, LI). Make it look like a manual post.
                    5. IMAGE: <img src="https://pollinations.ai/p/a_realistic_lifestyle_photo_of_{keyword.replace(' ', '_')}_concept" style="width:100%; max-width:800px; border-radius:10px; margin:20px 0;">

                    Provide only the HTML body content.
                    """
                    
                    response = model.generate_content(prompt)
                    content_html = response.text
                    
                    # 2시간 간격 + 랜덤 분(사람처럼 보이게)
                    random_min = random.randint(3, 18)
                    publish_time = (datetime.utcnow() + timedelta(hours=(i+1)*2, minutes=random_min)).isoformat() + "Z"
                    
                    post_body = {
                        'kind': 'blogger#post',
                        'title': f"{keyword}: {style}",
                        'content': content_html,
                        'published': publish_time,
                        'labels': ['Finance', 'Expert Review']
                    }
                    
                    service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
                    
                    st.write(f"✅ {i+1}번 완료: (예약 시간: {publish_time})")
                    progress_bar.progress((i+1) * 20)
                    time.sleep(5) # API 안정성 확보
                    
                except Exception as e:
                    st.error(f"❌ {i+1}번째 글 오류: {e}")
        
        st.success("🎉 모든 예약 발행이 완료되었습니다!")
        st.balloons()
