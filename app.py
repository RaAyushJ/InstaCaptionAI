import streamlit as st
from PIL import Image
import requests
import json
import base64
from io import BytesIO

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
    page_icon="imgs/avatar.png", # Ensure this path is correct
    layout="wide"
)

# --- Pre-load and Base64 encode banner image for CSS background ---
try:
    with open("imgs/banner.png", "rb") as f:
        banner_bytes = f.read()
    BASE64_BANNER = base64.b64encode(banner_bytes).decode('utf-8')
    BANNER_MIME_TYPE = "image/png" # Assuming it's a PNG based on your mention
    CSS_BACKGROUND_IMAGE_URL = f"data:{BANNER_MIME_TYPE};base64,{BASE64_BANNER}"
except FileNotFoundError:
    st.error("Error: banner.png not found in the 'imgs' folder. Please ensure it exists.")
    st.stop()
except Exception as e:
    st.error(f"Error processing banner.png: {e}")
    st.stop()

# --- Custom CSS for Glowing Neon UI ---
st.markdown(f"""
    <style>
    /* Main Streamlit App Container - for full page background */
    .stApp {{
        background-image: url("{CSS_BACKGROUND_IMAGE_URL}"); /* Using Base64 encoded image */
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    
    body {{
        color: #ffffff; /* Default text color */
        font-family: 'Montserrat', sans-serif; /* A modern, sleek font */
    }}
    
    /* Global Container Styles for better spacing and background */
    /* These classes target the main content area containers within Streamlit */
    /* Adjusted padding and margins for a slightly more compact feel */
    .st-emotion-cache-z5fcl4, .st-emotion-cache-1cyp85d, .st-emotion-cache-1r6dmc3, .st-emotion-cache-1v0mbdj {{ /* Added another potential Streamlit class for robustness */
        background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent dark background for readability */
        padding: 25px; /* Slightly less padding */
        border-radius: 20px;
        margin-top: 15px; /* Slightly less top margin */
        margin-bottom: 15px; /* Slightly less bottom margin */
        box-shadow: 0 0 20px rgba(248, 28, 229, 0.3); /* Subtle outer glow for the content box */
    }}

    .title-text {{
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #81e6d9, #d946ef); /* Brighter, more contrasting gradient for title */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-top: 10px;
        padding-bottom: 10px;
        margin-bottom: 20px;
        text-shadow: 0 0 10px rgba(129, 230, 217, 0.8), 0 0 20px rgba(217, 70, 239, 0.7); /* Stronger glow for title */
    }}

    /* Subheadings styling (e.g., "Upload Your Image", "Image Preview", "Caption Output") */
    h2 {{
        font-size: 1.8rem;
        background: linear-gradient(90deg, #64ffda, #ff00ff); /* Brighter gradient for h2 */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 8px rgba(100, 255, 218, 0.7), 0 0 15px rgba(255, 0, 255, 0.6); /* Stronger glow for h2 */
        margin-top: 25px;
        margin-bottom: 15px;
        text-align: center; /* Center h2 text within its container */
        width: 100%; /* Ensure h2 takes full width for centering */
    }}

    .caption-box {{
        background-color: rgba(21, 21, 37, 0.7); /* Slightly transparent background for caption output */
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 0 15px #f81ce5, 0 0 25px #7928ca; /* Neon glow */
        font-size: 1.1rem;
        margin-top: 1rem;
        word-wrap: break-word; /* Ensure long captions wrap */
        min-height: 100px; /* Give it a minimum height to avoid collapsing when empty */
        display: flex; /* For vertical centering of placeholder text */
        align-items: center; /* Center vertically inside the box */
        justify-content: center; /* Center horizontally inside the box */
        text-align: center; /* Center text within the box */
        
        /* --- Centering within its parent container (now a full-width section) --- */
        width: 90%; /* Give it a specific width relative to its parent */
        max-width: 700px; /* Increased max-width for better readability in full-width */
        margin-left: auto; /* Push to center */
        margin-right: auto; /* Push to center */
    }}
    
    /* Sidebar Styling */
    .st-emotion-cache-vk338m, .st-emotion-cache-1ajx971, .st-emotion-cache-1fttfy0 {{ 
        background-color: rgba(60, 0, 90, 0.6); /* More purple, slightly transparent */
        box-shadow: 0 0 15px rgba(248, 28, 229, 0.5), 0 0 25px rgba(121, 40, 202, 0.5); /* Subtle glow for sidebar */
        border-radius: 15px; /* Rounded corners for sidebar */
        padding: 20px; /* Add some padding inside sidebar */
        margin-left: 10px; /* Space from the edge of the screen */
    }}
    
    /* Sidebar Markdown text styling */
    .stMarkdown h3 {{
        color: #64ffda; /* Bright cyan for sidebar headings */
        text-shadow: 0 0 5px rgba(100, 255, 218, 0.7);
    }}
    .stMarkdown p {{
        color: #ffffff; /* White for sidebar paragraphs */
    }}

    /* Image Styling (for uploaded image preview) */
    /* Ensure image in col2 is centered */
    .st-emotion-cache-1gf7fay img, .st-emotion-cache-1gu2n0k img, .st-emotion-cache-1kyxpyf img {{
        border-radius: 15px;
        border: 2px solid #7928ca; /* Neon border for images */
        box-shadow: 0 0 10px #f81ce5, 0 0 20px #7928ca; /* Neon glow for images */
        max-width: 100%; /* Ensure image fits column */
        height: auto; /* Maintain aspect ratio */
        display: block; /* Remove extra space below image */
        margin-left: auto; /* Center image within its parent column */
        margin-right: auto; /* Center image within its parent column */
    }}
    
    /* Button Styling */
    .stButton>button {{
        background-color: #7928ca; /* Base button color */
        color: white;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: bold;
        border: 2px solid #f81ce5; /* Neon border */
        box-shadow: 0 0 10px #f81ce5, 0 0 20px #7928ca; /* Neon glow */
        transition: all 0.3s ease; /* Smooth transition for hover effects */
        cursor: pointer; /* Indicate clickable */
    }}
    .stButton>button:hover {{
        background-color: #f81ce5; /* Hover color */
        border: 2px solid #7928ca;
        box-shadow: 0 0 15px #7928ca, 0 0 25px #f81ce5; /* Stronger glow on hover */
        transform: translateY(-2px); /* Slight lift on hover */
    }}

    /* Input field styling (for st.text_input, st.text_area) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: rgba(21, 21, 37, 0.7); /* Darker, slightly transparent input */
        color: white;
        border: 1px solid #7928ca;
        border-radius: 8px;
        padding: 0.7rem;
        box-shadow: 0 0 5px #f81ce5;
        width: 100%; /* Ensure it takes full width of column */
    }}
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
        border-color: #f81ce5;
        box-shadow: 0 0 8px #f81ce5, 0 0 15px #7928ca;
        outline: none; /* Remove default browser focus outline */
    }}

    /* File uploader styling */
    .stFileUploader>div>button {{ /* This targets the actual "Browse files" button */
        background-color: #7928ca;
        color: white;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: bold;
        border: 2px solid #f81ce5;
        box-shadow: 0 0 10px #f81ce5, 0 0 20px #7928ca;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    .stFileUploader>div>button:hover {{
        background-color: #f81ce5;
        border: 2px solid #7928ca;
        box-shadow: 0 0 15px #7928ca, 0 0 25px #f81ce5;
        transform: translateY(-2px);
    }}
    /* Style for the text near browse files (e.g., "No file uploaded") */
    .stFileUploader>div>div>p {{
        color: #ddd; /* Light gray text */
        margin-top: 10px;
        margin-left: 5px;
    }}

    /* Specific centering for col2 content (Image Preview) */
    /* Only apply flex properties to col2's internal container if needed to center its items */
    /* Removed justify-content: center to avoid pushing content too low if image is small */
    .st-emotion-cache-1gf7fay, .st-emotion-cache-1gu2n0k, .st-emotion-cache-1kyxpyf {{ 
        display: flex;
        flex-direction: column;
        align-items: center; /* Center items horizontally within this flex container */
        /* height: 100%; This might push the image too far down if col1 is tall. Better to let it flow */
        text-align: center; /* Center text within this column */
    }}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Avatar ---
with st.sidebar:
    try:
        avatar = Image.open("imgs/avatar.png")
        st.image(avatar, width=140)
    except FileNotFoundError:
        st.warning("Avatar image 'imgs/avatar.png' not found. Please ensure it exists in the 'imgs' folder.")
    st.markdown("### Welcome to InstaCaptionAI")
    st.markdown("✨ Your AI-powered caption wizard.")
    st.markdown("Just upload an image, describe the vibe, and get an engaging caption!")

# --- Title ---
st.markdown('<div class="title-text">InstaCaptionAI - Neon Caption Wizard ✨</div>', unsafe_allow_html=True)

# --- Main Content - Two Columns for Inputs & Image Preview ---
col1, col2 = st.columns([1, 1]) 

with col1:
    st.markdown("<h2>📸 Upload Your Image</h2>", unsafe_allow_html=True)
    uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"], key="image_uploader") 

    st.markdown("<h2>💬 Describe the Vibe</h2>", unsafe_allow_html=True)
    caption_prompt = st.text_area("e.g., beach, workout, birthday...", height=80, key="vibe_description")

    st.markdown("---") # Separator line

    if 'generated_caption' not in st.session_state:
        st.session_state['generated_caption'] = ""

    if st.button("✨ Generate Caption", key="generate_button"): 
        if not uploaded_image and not caption_prompt:
            st.warning("Please upload an image and describe the vibe to generate a caption.")
        elif not uploaded_image:
            st.warning("Please upload an image for image-based captioning.")
        elif not caption_prompt:
            st.warning("Please describe the vibe for better caption generation.")
        
        if uploaded_image and caption_prompt:
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
                    
                    if 'candidates' in result and len(result['candidates']) > 0 and \
                       'content' in result['candidates'][0] and \
                       'parts' in result['candidates'][0]['content'] and \
                       len(result['candidates'][0]['content']['parts']) > 0 and \
                       'text' in result['candidates'][0]['content']['parts'][0]:
                        caption = result['candidates'][0]['content']['parts'][0]['text']
                        st.session_state['generated_caption'] = caption
                    else:
                        st.error("❌ API response missing expected 'candidates' or 'content' structure.")
                        st.session_state['generated_caption'] = "Error: Could not generate caption due to unexpected API response format."
                        st.json(result)
                
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ API request failed: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        st.error(f"Response details: {e.response.text}")
                    st.session_state['generated_caption'] = "Error: API request failed. Please check your API key and try again."
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.session_state['generated_caption'] = "Error: An unexpected error occurred during caption generation."

with col2:
    st.markdown("<h2>✨ Image Preview</h2>", unsafe_allow_html=True)
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    else:
        try:
            st.image("imgs/placeholder.png", caption="Upload an image to see a preview", use_column_width=True)
        except FileNotFoundError:
            st.warning("Placeholder image 'imgs/placeholder.png' not found. Please create it.")

# --- Caption Output (Full Width, Centered) ---
# Moved outside the columns
st.markdown("<h2>✍️ Caption Output</h2>", unsafe_allow_html=True)
if st.session_state['generated_caption']:
    st.markdown(f'<div class="caption-box">{st.session_state["generated_caption"]}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="caption-box">Your caption will appear here.</div>', unsafe_allow_html=True)