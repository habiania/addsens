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

# [404 에러 끝장내기] 모델 경로를 명시적으로 'models/gemini-1.5-flash'로 지정합니다.
try:
    model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
except Exception:
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')

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
st.set_page_config(page_title="EEAT Optimized Bot", layout="wide")
st.title("🛡️ EEAT-Optimized AdSense Pilot (v2.1)")
st.info("모델명 404 에러를 수정한 최종 버전입니다. 2,500자 포스팅 5개를 예약합니다.")

keyword = st.text_input("메인 키워드 입력", placeholder="예: Future of AI in E-commerce 2026")

if st.button("EEAT 최적화 포스팅 5개 예약 시작"):
    if not keyword:
        st.error("키워드를 입력해주세요.")
    else:
        service = get_blogger_service()
        progress_bar = st.progress(0)
        
        styles = [
            "In-depth Expert Review (Experience-based)",
            "A-to-Z Ultimate Roadmap (Authoritative)",
            "What Most People Get Wrong (Insightful)",
            "Step-by-Step Practical Implementation (Helpful)",
            "Future Predictions & Expert Analysis (Trustworthy)"
        ]

        for i, style in enumerate(styles):
            with st.spinner(f"[{i+1}/5] '{style}' 스타일로 글 생성 중..."):
                try:
                    # 프롬프트 구성 (최신 애드센스 승인 조건 반영)
                    prompt = f"""
                    Write an extensive, human-like SEO blog post in American English.
                    Topic: '{keyword}' / Style: {style}
                    
                    Instructions:
                    - Word count: 2,500+ words.
                    - Tone: Professional yet conversational (EEAT focused).
                    - Content: Include a personal anecdote, statistical data, and a final expert verdict.
                    - Format: Clean HTML (H2, H3, P, B, UL, LI).
                    - Image: <img src="https://pollinations.ai/p/a_realistic_professional_illustration_of_{keyword.replace(' ', '_')}_{i}" style="width:100%; max-width:800px; border-radius:12px; margin:20px 0;">
                    
                    Respond ONLY with the HTML body content.
                    """
                    
                    response = model.generate_content(prompt)
                    content_html = response.text
                    
                    if not content_html:
                        raise ValueError("Gemini가 내용을 생성하지 못했습니다.")
                    
                    # 예약 시간 설정 (2시간 간격 + 랜덤 분)
                    random_min = random.randint(3, 15)
                    publish_time = (datetime.utcnow() + timedelta(hours=(i+1)*2, minutes=random_min)).isoformat() + "Z"
                    
                    post_body = {
                        'kind': 'blogger#post',
                        'title': f"{keyword}: {style} (2026 Edition)",
                        'content': content_html,
                        'published': publish_time,
                        'labels': ['Expert Series', 'SEO Strategy']
                    }
                    
                    service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
                    
                    st.write(f"✅ {i+1}번 예약 성공: {style}")
                    progress_bar.progress((i+1) * 20)
                    time.sleep(3) # API 제한 준수
                    
                except Exception as e:
                    st.error(f"❌ {i+1}번째 글 오류: {e}")
        
        st.success("🎉 모든 프로세스가 완료되었습니다! 블로그에서 확인하세요.")
        st.balloons()
