import os

# Create folders
os.makedirs("backend", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

# --------------------------
# backend/main.py
# --------------------------
with open("backend/main.py", "w", encoding="utf-8") as f:
    f.write('''
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.analyze import analyze_video
import base64

app = FastAPI(title="Mentor Scoring AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    b64_video = base64.b64encode(content).decode()
    result = analyze_video(b64_video)
    return result
''')

# --------------------------
# backend/analyze.py
# --------------------------
with open("backend/analyze.py", "w", encoding="utf-8") as f:
    f.write('''
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_video(b64_video):

    transcript = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Transcribe the teaching video."},
            {"role": "user", "content": f"Please transcribe this base64 encoded video: {b64_video}"}
        ]
    ).choices[0].message["content"]

    prompt = f"""
    You are an AI trained to evaluate teaching quality.

    TRANSCRIPT:
    {transcript}

    Score the following categories from 0 to 100:
    - Clarity
    - Engagement
    - Confidence
    - Technical Depth
    - Interaction Quality

    Compute:
    total = 0.20*clarity + 0.20*engagement + 0.20*confidence + 0.30*technical + 0.10*interaction

    Output JSON only:
    {{
        "clarity": <int>,
        "engagement": <int>,
        "confidence": <int>,
        "technical": <int>,
        "interaction": <int>,
        "overall": <float>,
        "suggestions": ["..."]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert teaching evaluator."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message["content"]
''')

# --------------------------
# frontend/app.py
# --------------------------
with open("frontend/app.py", "w", encoding="utf-8") as f:
    f.write('''
import streamlit as st
import requests

API_URL = "http://localhost:8000/analyze"

st.title("Mentor Scoring AI")
st.write("Upload a teaching video and get AI-based evaluation.")

video = st.file_uploader("Upload MP4 video", type=["mp4"])

if video and st.button("Analyze"):
    with st.spinner("Analyzing..."):
        files = {"file": (video.name, video.read(), "video/mp4")}
        res = requests.post(API_URL, files=files)

        if res.status_code == 200:
            st.success("Done!")
            st.json(res.json())
        else:
            st.error("Error from backend")
''')

# --------------------------
# requirements.txt
# --------------------------
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write('''
fastapi
uvicorn
streamlit
requests
python-multipart
openai
''')

# --------------------------
# README.md
# --------------------------
with open("README.md", "w", encoding="utf-8") as f:
    f.write('''
# Mentor Scoring AI (OpenAI-powered)

This project evaluates teaching videos using OpenAI models.

## Commands

### Backend:
uvicorn backend.main:app --reload --port 8000

### Frontend:
streamlit run frontend/app.py
''')

# --------------------------
# .gitignore
# --------------------------
with open(".gitignore", "w", encoding="utf-8") as f:
    f.write('''
__pycache__/
*.mp4
.env
''')

print("🎉 Project generated successfully!")
