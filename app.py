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
model = genai.GenerativeModel('gemini-1.5-flash-latest')

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
st.title("✍️ Human-Like SEO Auto-Pilot")
st.info("AI 흔적을 지운 2,000자 이상의 정성 글 5개를 2시간 간격으로 예약 발행합니다.")

keyword = st.text_input("메인 키워드 입력", placeholder="예: Passive income ideas for 2026")

if st.button("AI 흔적 제거 포스팅 5개 시작"):
    if not keyword:
        st.error("키워드를 입력해주세요.")
    else:
        service = get_blogger_service()
        progress_bar = st.progress(0)
        
        # 각각 다른 스타일의 글 작성
        styles = [
            "Ultimate Beginner's Guide",
            "Personal Experience & Case Study",
            "Common Mistakes & How to Avoid Them",
            "Advanced Strategies & Pro Tips",
            "Honest Review & Comparison"
        ]

        for i, style in enumerate(styles):
            with st.spinner(f"[{i+1}/5] '{style}' 스타일로 정성껏 작성 중..."):
                try:
                    # AI 흔적을 지우기 위한 강력한 프롬프트 지시사항
                    prompt = f"""
                    Write a long-form blog post (2,500+ words) in American English about '{keyword}'.
                    Article Type: {style}

                    [CRITICAL INSTRUCTIONS TO REMOVE AI FOOTPRINTS]:
                    1. DO NOT use typical AI transition phrases like "In conclusion," "In summary," or "Additionally."
                    2. Use a conversational, human-like tone. Start with a hook that relates to a real-life situation.
                    3. Include a "My Personal Take" or "Common Myths" section to add unique perspective.
                    4. Use varied sentence lengths. Use some rhetorical questions to engage the reader.
                    5. Use HTML formatting (H2, H3, P, B, UL, LI) but keep it looking like a blog, not a manual.
                    6. Include a high-quality AI illustration:
                       <img src="https://pollinations.ai/p/a_realistic_and_artistic_illustration_of_{keyword.replace(' ', '_')}_lifestyle_vibe" alt="{keyword}" style="width:100%; max-width:800px; border-radius:12px; margin:20px 0;">

                    Structure:
                    - Catchy, click-worthy Title (No "The Future of..." type cliches)
                    - Introduction (Empathize with the reader's problem)
                    - Comprehensive Body (Deep, actionable information)
                    - FAQ section based on common search queries
                    - Human-like closing thought (encouraging comment/engagement)

                    Respond only with the HTML body.
                    """
                    
                    response = model.generate_content(prompt)
                    content_html = response.text
                    
                    # 2시간 간격 예약 발행 (약간의 분 단위 오차를 주어 더 사람처럼 보이게 함)
                    random_minute = random.randint(1, 15)
                    publish_time = (datetime.utcnow() + timedelta(hours=(i+1)*2, minutes=random_minute)).isoformat() + "Z"
                    
                    post_body = {
                        'kind': 'blogger#post',
                        'title': f"{keyword}: {style}",
                        'content': content_html,
                        'published': publish_time,
                        'labels': ['Expert Opinion', 'Guide']
                    }
                    
                    service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
                    
                    st.write(f"✅ {i+1}번째 글 예약 완료 (예정 시간: {publish_time})")
                    progress_bar.progress((i+1) * 20)
                    time.sleep(3) # 과부하 방지
                    
                except Exception as e:
                    st.error(f"❌ {i+1}번째 글 에러: {e}")
        
        st.success("🎉 사람의 손길이 느껴지는 5개의 글이 예약되었습니다!")
        st.balloons()
