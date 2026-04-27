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

genai.configure(api_key=GEMINI_API_KEY)
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
st.set_page_config(page_title="EEAT Optimized Bot", layout="wide")
st.title("🛡️ EEAT-Optimized AdSense Pilot")
st.info("최신 구글 알고리즘(EEAT)에 맞춰 '경험과 신뢰'가 강조된 2,500자 포스팅 5개를 예약합니다.")

keyword = st.text_input("메인 키워드 입력", placeholder="예: Best budget-friendly travel destinations 2026")

if st.button("EEAT 최적화 포스팅 5개 예약 시작"):
    if not keyword:
        st.error("키워드를 입력해주세요.")
    else:
        service = get_blogger_service()
        progress_bar = st.progress(0)
        
        # 각각 다른 스타일로 '전문성' 강조
        styles = [
            "In-depth Expert Review (Experience-based)",
            "A-to-Z Ultimate Roadmap (Authoritative)",
            "What Most People Get Wrong (Insightful)",
            "Step-by-Step Practical Implementation (Helpful)",
            "Future Predictions & Expert Analysis (Trustworthy)"
        ]

        for i, style in enumerate(styles):
            with st.spinner(f"[{i+1}/5] '{style}' 스타일로 EEAT 최적화 중..."):
                try:
                    # 최신 승인 조건 반영 프롬프트
                    prompt = f"""
                    Write a 2,500+ word blog post in American English. 
                    Topic: '{keyword}' / Style: {style}

                    [AD-SENSE EEAT COMPLIANCE]:
                    1. EXPERIENCE: Start with a first-person narrative ("I've tested...", "In my years of experience...").
                    2. EXPERTISE: Use specific terminology, data-driven facts, and provide deep technical insights.
                    3. AUTHORITATIVENESS: Include a "Key Takeaways" summary and "Pros/Cons" based on real usage.
                    4. TRUSTWORTHINESS: Add a "Frequently Asked Questions" section and cite general industry standards.
                    
                    [FORMATTING]:
                    - Use SEO-friendly HTML: H2, H3, P, B, UL, LI. 
                    - NO AI cliches. Keep sentences varied and engaging.
                    - IMAGE: <img src="https://pollinations.ai/p/a_professional_high_quality_photo_of_{keyword.replace(' ', '_')}_lifestyle" style="width:100%; max-width:800px; border-radius:12px; margin:20px 0;">

                    Respond ONLY with the HTML body content.
                    """
                    
                    response = model.generate_content(prompt)
                    content_html = response.text
                    
                    # 2시간 간격 + 랜덤 분 설정
                    random_min = random.randint(5, 25)
                    publish_time = (datetime.utcnow() + timedelta(hours=(i+1)*2, minutes=random_min)).isoformat() + "Z"
                    
                    post_body = {
                        'kind': 'blogger#post',
                        'title': f"{keyword}: {style} (Guide 2026)",
                        'content': content_html,
                        'published': publish_time,
                        'labels': ['Expert Guide', 'Lifestyle']
                    }
                    
                    service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
                    
                    st.write(f"✅ {i+1}번 예약 완료: {style}")
                    progress_bar.progress((i+1) * 20)
                    time.sleep(4)
                    
                except Exception as e:
                    st.error(f"❌ {i+1}번째 글 오류: {e}")
        
        st.success("🎉 EEAT 최적화 포스팅 5개가 모두 예약되었습니다!")
        st.balloons()
