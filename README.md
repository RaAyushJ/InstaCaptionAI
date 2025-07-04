
# InstaCaptionAI - AI-Powered Instagram Caption Generator

InstaCaptionAI is a sleek and modern web application that generates engaging Instagram captions based on uploaded images and an optional description. Powered by Google's Gemini 1.5 Flash API, this tool is designed to assist content creators, influencers, and marketers in producing high-quality, relevant captions quickly.

## Hosted App

Visit the live application here: https://ayush-instacaptionai.streamlit.app/

## Features

- Upload an image (JPG, PNG)
- Provide an optional vibe or mood description
- Get AI-generated Instagram captions with relevant hashtags and emojis
- Real-time image preview
- Custom neon-themed UI with glowing CSS effects
- Hosted on Streamlit Cloud

## How It Works

1. Users upload an image and optionally describe the vibe.
2. The app encodes the image into Base64 format.
3. The image and text are sent to the Gemini 1.5 Flash API.
4. The model generates a catchy caption.
5. The caption is displayed in a styled output box.

## Tech Stack

| Component        | Technology                          |
|------------------|--------------------------------------|
| Frontend         | Streamlit                           |
| Backend / API    | Google Gemini 1.5 Flash             |
| Programming      | Python 3.10+                        |
| Image Handling   | Pillow (PIL), Base64                |
| Styling          | Custom CSS                          |
| Hosting          | Streamlit Cloud                    |

## Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/InstaCaptionAI.git
cd InstaCaptionAI
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Add your API key in `.streamlit/secrets.toml`
```toml
GENAI_API_KEY = "your-google-gemini-api-key"
```

4. Run the app
```bash
streamlit run app.py
```

## Project Structure

```
InstaCaptionAI/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── secrets.toml
├── imgs/
│   ├── banner.png
│   ├── avatar.png
│   └── placeholder.png
```

## Example Use Case

- upload an image 
- Description: "sunset at the beach"
- Output Caption: "Golden skies and warm tides. #BeachVibes #SunsetGlow"


## Author

Developed by Ayush Raj
