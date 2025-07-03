import streamlit as st
from PIL import Image
import requests
import json
import base64
from io import BytesIO
from html import escape

# --- CONFIG ---
try:
    GENAI_API_KEY = st.secrets["GENAI_API_KEY"]
except KeyError:
    st.error("GENAI_API_KEY not found in Streamlit secrets. Please configure it.")
    st.stop()

GEMINI_MODEL = "models/gemini-1.5-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent"

# --- Page Setup ---
st.set_page_config(
    page_title="InstaCaptionAI",
    page_icon="imgs/avatar.png",
    layout="wide"
)

# --- Load banner as background ---
try:
    with open("imgs/banner.png", "rb") as f:
        banner_bytes = f.read()
    BASE64_BANNER = base64.b64encode(banner_bytes).decode('utf-8')
    CSS_BACKGROUND_IMAGE_URL = f"data:image/png;base64,{BASE64_BANNER}"
except:
    st.error("Missing or broken banner image in 'imgs/banner.png'.")
    st.stop()

# --- CSS Styling ---
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{CSS_BACKGROUND_IMAGE_URL}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        font-family: 'Montserrat', sans-serif;
        color: white;
    }}
    .title-text {{
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #81e6d9, #d946ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        text-shadow: 0 0 10px #81e6d9, 0 0 20px #d946ef;
        margin-bottom: 1rem;
    }}
    h2 {{
        font-size: 1.8rem;
        background: linear-gradient(90deg, #64ffda, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 8px #64ffda, 0 0 15px #ff00ff;
        text-align: center;
    }}
    .caption-box {{
        background-color: rgba(21, 21, 37, 0.7);
        padding: 1.5rem;
        border-radius: 18px;
        box-shadow: 0 0 20px #f81ce5, 0 0 30px #7928ca;
        font-size: 1.1rem;
        margin-top: 1rem;
        min-height: 150px;
        max-height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        width: 90%;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        color: white;
    }}
    .caption-box > div {{
        background: rgba(34, 34, 54, 0.8);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 0 10px #f81ce5;
        text-align: left;
        line-height: 1.6;
        transition: transform 0.2s ease;
    }}
    .caption-box > div:hover {{
        transform: scale(1.02);
        box-shadow: 0 0 15px #f81ce5, 0 0 30px #7928ca;
    }}
    .stButton>button {{
        background-color: #7928ca;
        color: white;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: bold;
        border: 2px solid #f81ce5;
        box-shadow: 0 0 10px #f81ce5, 0 0 20px #7928ca;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #f81ce5;
        transform: translateY(-2px);
        box-shadow: 0 0 15px #7928ca, 0 0 25px #f81ce5;
    }}
    /* Hide deprecation warning about use_column_width */
    .st-emotion-cache-1wmy9hl, .stAlert, .st-emotion-cache-ue6h4q {{
    display: none !important;
    }}

    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    try:
        st.image("imgs/avatar.png", width=140)
    except:
        st.warning("Missing avatar image.")
    st.markdown("### Welcome to InstaCaptionAI")
    st.markdown("✨ Your AI-powered caption wizard.\nJust upload an image, describe the vibe, and get an engaging caption!")

# --- Title ---
st.markdown('<div class="title-text">InstaCaptionAI - Neon Caption Wizard ✨</div>', unsafe_allow_html=True)

# --- Two-column layout ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h2>📸 Upload Your Image</h2>", unsafe_allow_html=True)
    uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"], key="image_uploader")

    st.markdown("<h2>💬 Describe the Vibe</h2>", unsafe_allow_html=True)
    caption_prompt = st.text_area("e.g., beach, workout, birthday...", height=80, key="vibe_description")

    st.markdown("---")

    if 'generated_caption' not in st.session_state:
        st.session_state['generated_caption'] = ""

    if st.button("✨ Generate Caption", key="generate_button"):
        if not uploaded_image or not caption_prompt:
            st.warning("Please upload an image and describe the vibe.")
        else:
            with st.spinner("Thinking like an influencer... ✨"):
                try:
                    uploaded_image.seek(0)
                    image_bytes = uploaded_image.read()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')

                    parts = [
                        {
                            "text": f"Generate an engaging Instagram caption for an image with the vibe: '{caption_prompt}'. Include relevant emojis and popular hashtags. Keep it concise, fun, and appealing for social media."
                        },
                        {
                            "inline_data": {
                                "mime_type": uploaded_image.type,
                                "data": base64_image
                            }
                        }
                    ]

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
                    response.raise_for_status()

                    result = response.json()

                    if 'candidates' in result and \
                       'content' in result['candidates'][0] and \
                       'parts' in result['candidates'][0]['content']:
                        caption = result['candidates'][0]['content']['parts'][0]['text']
                        st.session_state['generated_caption'] = caption
                    else:
                        st.session_state['generated_caption'] = "⚠️ Could not generate caption. API response incomplete."

                except requests.exceptions.RequestException as e:
                    st.error(f"API request failed: {e}")
                    st.session_state['generated_caption'] = "⚠️ API error. Please check your API key or try again later."
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
                    st.session_state['generated_caption'] = "⚠️ Unexpected error during caption generation."

with col2:
    st.markdown("<h2>✨ Image Preview</h2>", unsafe_allow_html=True)
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    else:
        try:
            st.image("imgs/placeholder.png", caption="Upload an image to see a preview", use_column_width=True)
        except:
            st.warning("Missing placeholder image.")

# --- Caption Output ---
st.markdown("<h2>✍️ Caption Output</h2>", unsafe_allow_html=True)

if st.session_state['generated_caption']:
    # Handle multiple options
    captions = st.session_state["generated_caption"].split("Option")
    caption_html = '<div class="caption-box">'
    for i, cap in enumerate(captions):
        if cap.strip():
            cap_cleaned = escape(cap.strip()).replace("\n", "<br>")
            caption_html += f'<div><b>Option {i}:</b><br>{cap_cleaned}</div>'
    caption_html += '</div>'
    st.markdown(caption_html, unsafe_allow_html=True)
else:
    st.markdown('<div class="caption-box">Your caption will appear here.</div>', unsafe_allow_html=True)
