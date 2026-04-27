import streamlit as st
import os
import pickle
import google.generativeai as genai
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- 1. 설정 정보 ---
BLOG_ID = '8075636289883732328'
# GitHub에 올린 파일명과 동일하게 'client_secret.json'으로 설정
JSON_FILE = 'client_secret.json' 
GEMINI_API_KEY = "AIzaSyAw7YnMqZS4ObAVaO8b3yMFCcY3No_r1ik"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
st.set_page_config(page_title="AI Blog Poster", layout="wide")
st.title("🎨 Unique AI-Generated Content Bot")

keyword = st.text_input("Enter Topic (e.g., Future of AI in Daily Life)", placeholder="키워드를 입력하세요")

if st.button("Generate & Post (AI Illustration Included)"):
    if not keyword:
        st.error("Please enter a keyword.")
    else:
        with st.spinner("Gemini 3가 독창적인 AI 이미지와 글을 생성 중입니다..."):
            try:
                # 직접 그린 듯한 '일러스트' 스타일을 강조한 프롬프트
                prompt = f"""
                Write a professional blog post in American English about '{keyword}'.
                
                Requirements:
                - Length: 1,500+ words.
                - Format: HTML tags (<h2>, <h3>, <p>, <ul>).
                - **Custom Image**: Insert this HTML tag after the first paragraph to represent a unique AI-generated illustration:
                  <img src="https://pollinations.ai/p/a_high_quality_digital_art_illustration_of_{keyword.replace(' ', '_')}_concept_art_highly_detailed_trending_on_artstation" alt="{keyword}" style="width:100%; max-width:800px; border-radius:15px; margin:25px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                - Tone: Informative and authoritative for a US audience.
                """
                
                response = model.generate_content(prompt)
                full_html = response.text
                
                service = get_blogger_service()
                post_body = {
                    'kind': 'blogger#post',
                    'title': f"Exploring the Future: {keyword}",
                    'content': full_html,
                    'labels': ['AI Generated', 'Expert Guide']
                }
                
                post = service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
                st.success("🎉 직접 그린 듯한 AI 이미지가 포함된 포스팅이 완료되었습니다!")
                st.write(f"**URL:** [확인하기]({post.get('url')})")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
