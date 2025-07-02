import streamlit as st
from PIL import Image
import requests
import json
import base64

# --- Config ---
GENAI_API_KEY = st.secrets["GENAI_API_KEY"]
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# --- Page Setup ---
st.set_page_config(
    page_title="InstaCaptionAI",
    page_icon="imgs/avatar.png",
    layout="wide"
)

# --- Custom CSS for Glowing Neon UI ---
st.markdown("""
    <style>
    body {
        background-color: #0b0f1a;
        color: #ffffff;
    }
    .title-text {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #f81ce5, #7928ca);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .caption-box {
        background-color: #151525;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 0 15px #f81ce5, 0 0 25px #7928ca;
        font-size: 1.1rem;
        margin-top: 1rem;
    }
    .sidebar .sidebar-content {
        background-color: #0b0f1a;
    }
    img {
        border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Avatar ---
with st.sidebar:
    avatar = Image.open("imgs/avatar.png")
    st.image(avatar, width=140)
    st.markdown("### Welcome to InstaCaptionAI")
    st.markdown("✨ Your AI-powered caption wizard.")
    st.markdown("Just upload an image, describe the vibe, and get an engaging caption!")

# --- Hero Banner ---
banner = Image.open("imgs/banner.png")
st.image(banner, use_column_width=True)

# --- Title ---
st.markdown('<div class="title-text">InstaCaptionAI - Neon Caption Wizard ✨</div>', unsafe_allow_html=True)

# --- Inputs ---
uploaded_image = st.file_uploader("📸 Upload your Instagram image", type=["jpg", "jpeg", "png"])
caption_prompt = st.text_input("💬 Describe your vibe (e.g., 'aesthetic sunset, cozy mood')")

if st.button("🚀 Generate Caption") and (caption_prompt or uploaded_image):
    with st.spinner("Thinking like an influencer... ✨"):
        parts = [{"text": f"Generate an Instagram caption for this vibe: {caption_prompt}"}]

        payload = {
            "contents": [
                {
                    "parts": parts
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": GENAI_API_KEY
        }

        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            result = response.json()
            caption = result['candidates'][0]['content']['parts'][0]['text']
            st.markdown("### ✨ Your AI-Generated Caption")
            st.markdown(f'<div class="caption-box">{caption}</div>', unsafe_allow_html=True)
        else:
            st.error(f"❌ Caption generation failed. {response.status_code}: {response.text}")

# --- Optional Image Preview ---
if uploaded_image:
    st.markdown("### 🌅 Image Preview")
    st.image(uploaded_image, width=500)

