# install_intelliTeach.ps1
Write-Host "🚀 IntelliTeach-AI Installer — Creating project files..." -ForegroundColor Cyan

function Write-File {
    param(
        [string]$Path,
        [string]$Content
    )
    $folder = Split-Path $Path
    if ($folder -and -not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
    # Ensure UTF8 without BOM
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue), $Content, $utf8NoBom)
    Write-Host "✔ Created: $Path"
}

# Ensure running from repo root (optional)
if (-not (Test-Path ".git")) {
    Write-Host "⚠️  Warning: I don't see a .git folder in the current directory." -ForegroundColor Yellow
    Write-Host "Make sure you run this script from the root of your IntelliTeach-AI repo." -ForegroundColor Yellow
}

# Create src package files
Write-File "src/__init__.py" "# src package"
Write-File "src/backend/__init__.py" "# src.backend package"

# backend/main.py
Write-File "src/backend/main.py" @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.api import router as api_router

app = FastAPI(title="Mentor Scoring AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
"@

# backend/api.py
Write-File "src/backend/api.py" @"
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
from pathlib import Path
from typing import Dict

from src.backend.ai.pipeline import analyze_video_pipeline
from src.backend.utils.fileio import save_upload_tmp

router = APIRouter()
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post('/analyze-video')
async def analyze_video(file: UploadFile = File(...)) -> Dict:
    try:
        saved_path = await save_upload_tmp(file, UPLOAD_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        result = analyze_video_pipeline(str(saved_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    return JSONResponse(content=result)

@router.get('/download-report')
def download_report(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Report not found')
    return FileResponse(path, media_type='application/pdf', filename=os.path.basename(path))
"@
# backend/utils/fileio.py
Write-File "src/backend/utils/fileio.py" @"
from pathlib import Path
from fastapi import UploadFile
import uuid

async def save_upload_tmp(upload_file: UploadFile, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload_file.filename).suffix or ".mp4"
    token = uuid.uuid4().hex
    out_path = dest_dir / f"{token}{suffix}"
    with out_path.open("wb") as f:
        content = await upload_file.read()
        f.write(content)
    return out_path
"@

# backend/utils/validators.py
Write-File "src/backend/utils/validators.py" @"
ALLOWED_EXT = {'.mp4', '.mov', '.mkv', '.webm'}

def validate_extension(path: str):
    from pathlib import Path
    ext = Path(path).suffix.lower()
    return ext in ALLOWED_EXT
"@

# backend/ai/__init__.py
Write-File "src/backend/ai/__init__.py" "# ai package"

# backend/ai/pipeline.py
Write-File "src/backend/ai/pipeline.py" @"
import os
import tempfile
from pathlib import Path
from moviepy.editor import VideoFileClip

from src.backend.ai.clarity import clarity_score
from src.backend.ai.engagement import engagement_score
from src.backend.ai.confidence import confidence_score
from src.backend.ai.technical_depth import technical_depth_score
from src.backend.ai.interaction import interaction_score

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

WEIGHTS = {
    'engagement': 0.20,
    'communication': 0.20,
    'technical': 0.30,
    'clarity': 0.20,
    'interaction': 0.10,
}

def extract_audio(video_path: str, out_audio: str):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(out_audio, verbose=False, logger=None)

def analyze_video_pipeline(video_path: str) -> dict:
    tmpdir = Path(tempfile.mkdtemp(prefix='mentor_scoring_'))
    audio_path = str(tmpdir / 'audio.wav')

    extract_audio(video_path, audio_path)

    clarity = clarity_score(audio_path)
    engagement = engagement_score(video_path)
    confidence = confidence_score(audio_path)
    technical = technical_depth_score(audio_path)
    interaction = interaction_score(video_path, audio_path)

    total = (
        WEIGHTS['clarity'] * clarity +
        WEIGHTS['engagement'] * engagement +
        WEIGHTS['communication'] * ((clarity + confidence) / 2.0) +
        WEIGHTS['technical'] * technical +
        WEIGHTS['interaction'] * interaction
    )

    result = {
        'scores': {
            'clarity': round(clarity * 100, 2),
            'engagement': round(engagement * 100, 2),
            'confidence': round(confidence * 100, 2),
            'technical_depth': round(technical * 100, 2),
            'interaction': round(interaction * 100, 2),
            'overall': round(total * 100, 2),
        },
        'suggestions': generate_suggestions(clarity, engagement, confidence, technical, interaction),
    }

    report_path = str(tmpdir / 'mentor_report.pdf')
    generate_pdf_report(report_path, result)
    result['report_path'] = report_path

    return result

def generate_suggestions(c, e, conf, t, i):
    s = []
    s.append('Reduce filler words and improve clarity.' if c < 0.6 else 'Good clarity — keep it up.')
    s.append('Increase expressiveness and movement.' if e < 0.6 else 'Engagement is strong.')
    if conf < 0.55:
        s.append('Improve vocal confidence — vary pitch and project clearly.')
    if t < 0.6:
        s.append('Add deeper technical explanation and examples.')
    if i < 0.5:
        s.append('Use questions and pauses to encourage interaction.')
    return s

def generate_pdf_report(path: str, result: dict):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont('Helvetica-Bold', 16)
    c.drawString(50, height - 40, 'Mentor Scoring AI — Report')

    c.setFont('Helvetica', 12)
    y = height - 80

    for k, v in result['scores'].items():
        c.drawString(50, y, f"{k.capitalize()}: {v}")
        y -= 20

    y -= 10
    c.drawString(50, y, "Suggestions:")
    y -= 20

    for s in result['suggestions']:
        c.drawString(60, y, f"- {s}")
        y -= 18
        if y < 60:
            c.showPage()
            y = height - 50

    c.save()
"@

# backend/ai/clarity.py
Write-File "src/backend/ai/clarity.py" @"
import re
import whisper
import spacy

_whisper_model = None
_spacy_model = None

def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model('small')
    return _whisper_model

def _get_spacy():
    global _spacy_model
    if _spacy_model is None:
        try:
            _spacy_model = spacy.load('en_core_web_sm')
        except:
            spacy.cli.download('en_core_web_sm')
            _spacy_model = spacy.load('en_core_web_sm')
    return _spacy_model

FILLERS = ['um', 'uh', 'you know', 'like', 'so']

def clarity_score(audio_path: str) -> float:
    model = _get_whisper()
    res = model.transcribe(audio_path)
    text = res.get('text', '')

    filler_count = sum(text.lower().count(f) for f in FILLERS)
    words = len(text.split())
    filler_penalty = min(1.0, filler_count / max(1, words))

    nlp = _get_spacy()
    doc = nlp(text)
    sent_count = max(1, len(list(doc.sents)))
    avg_len = len(text.split()) / sent_count

    grammar_score = max(0.0, 1 - (avg_len - 20) / 100)
    clarity = 0.7 * (1 - filler_penalty) + 0.3 * grammar_score

    return float(max(0.0, min(1.0, clarity)))
"@

# backend/ai/engagement.py
Write-File "src/backend/ai/engagement.py" @"
import cv2
import numpy as np

def engagement_score(video_path: str) -> float:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0.0

    prev = None
    diffs = []
    faces = []
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            diffs.append(np.mean(cv2.absdiff(gray, prev)) / 255.0)
        prev = gray

        face_count = len(detector.detectMultiScale(gray, 1.1, 4))
        faces.append(face_count)

    cap.release()

    if not diffs:
        return 0.0

    motion = np.tanh(np.mean(diffs) * 3)
    face_score = min(1, np.mean(faces) / 1.5)

    return float(0.6 * motion + 0.4 * face_score)
"@

# backend/ai/confidence.py
Write-File "src/backend/ai/confidence.py" @"
import librosa
import numpy as np

def confidence_score(audio_path: str) -> float:
    y, sr = librosa.load(audio_path, sr=16000)
    rms = librosa.feature.rms(y=y)[0]
    rms_var = np.var(rms)

    S = np.abs(librosa.stft(y))
    pitches, mags = librosa.piptrack(S=S, sr=sr)
    pitch_vals = pitches[mags > np.median(mags)]
    pitch_std = np.std(pitch_vals) if pitch_vals.size else 0

    loudness_score = max(0, 1 - rms_var * 10)
    pitch_score = max(0, 1 - pitch_std / 50)

    return float(0.5 * loudness_score + 0.5 * pitch_score)
"@

# backend/ai/technical_depth.py
Write-File "src/backend/ai/technical_depth.py" @"
import whisper
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import textstat

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model('small')
    return _model

def technical_depth_score(audio_path: str) -> float:
    model = _get_model()
    res = model.transcribe(audio_path)
    text = res.get('text', '')

    if len(text.split()) < 5:
        return 0

    vect = TfidfVectorizer(stop_words='english')
    X = vect.fit_transform([text]).toarray()[0]
    tfidf_val = np.max(X)

    flesch = textstat.flesch_reading_ease(text)
    complexity = max(0, (100 - flesch) / 100)

    return float(0.6 * tfidf_val + 0.4 * complexity)
"@

# backend/ai/interaction.py
Write-File "src/backend/ai/interaction.py" @"
import librosa
import cv2
import numpy as np

def interaction_score(video_path: str, audio_path: str) -> float:
    y, sr = librosa.load(audio_path, sr=16000)
    intervals = librosa.effects.split(y, top_db=30)
    speech = sum(e - s for s, e in intervals)
    total = len(y)
    silence_ratio = 1 - (speech / total)

    cap = cv2.VideoCapture(video_path)
    diffs = []
    prev = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            diffs.append(np.mean(cv2.absdiff(gray, prev)) / 255.0)
        prev = gray

    cap.release()

    motion_var = np.var(diffs) if diffs else 0

    silence_score = max(0, 1 - abs(silence_ratio - 0.15) / 0.5)
    motion_score = max(0, 1 - abs(motion_var - 0.02) / 0.1)

    return float(0.6 * silence_score + 0.4 * motion_score)
"@
# frontend/app.py (Streamlit)
Write-File "src/frontend/app.py" @"
import streamlit as st
import requests

API = st.secrets.get('API_URL', 'http://localhost:8000/api')

st.set_page_config(page_title='Mentor Scoring AI', layout='centered')

st.markdown(\"\"\"
<style>
body {background: white}
.section {box-shadow: 0 6px 18px rgba(0,0,0,0.06); border-radius: 12px; padding: 18px;}
</style>
\"\"\", unsafe_allow_html=True)

st.title('Mentor Scoring AI')
st.write('Upload a short teaching video and get a mentor scorecard with suggestions.')

with st.container():
    uploaded = st.file_uploader('Upload video (mp4, mov, webm)', type=['mp4', 'mov', 'mkv', 'webm'])
    run = st.button('Analyze')

if run and uploaded is not None:
    with st.spinner('Uploading and analyzing... This can take a minute...'):
        files = {'file': (uploaded.name, uploaded.getvalue(), uploaded.type)}
        try:
            r = requests.post(f\"{API}/analyze-video\", files=files, timeout=600)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            st.error(f'Analysis failed: {e}')
            st.stop()

    scores = data['scores']
    st.subheader('Scorecard')
    st.metric('Overall', f\"{scores['overall']}%\")
    cols = st.columns(5)
    cols[0].metric('Clarity', f\"{scores['clarity']} %\")
    cols[1].metric('Engagement', f\"{scores['engagement']} %\")
    cols[2].metric('Confidence', f\"{scores['confidence']} %\")
    cols[3].metric('Technical', f\"{scores['technical_depth']} %\")
    cols[4].metric('Interaction', f\"{scores['interaction']} %\")

    st.markdown('---')
    st.subheader('Improvement Suggestions')
    for s in data.get('suggestions', []):
        st.write('- ' + s)

    if data.get('report_path'):
        download_url = f\"{API}/download-report?path={data['report_path']}\"
        st.markdown(f\"[Download PDF report]({download_url})\")

else:
    st.info('Upload a mentor video and click Analyze.')
"@

# tests/test_pipeline.py
Write-File "tests/test_pipeline.py" @"
# Basic smoke test for pipeline - place a short sample video at tests/sample.mp4 before running
from src.backend.ai.pipeline import analyze_video_pipeline

def test_pipeline_runs_with_mock_video():
    # This test expects you to provide a short sample video at tests/sample.mp4 for CI.
    res = analyze_video_pipeline('tests/sample.mp4')
    assert 'scores' in res
    assert 'overall' in res['scores']
"@

# requirements.txt
Write-File "requirements.txt" @"
fastapi==0.95.2
uvicorn==0.22.0
python-multipart==0.0.6
moviepy==1.0.3
whisper==20230314
torch>=1.12.0
librosa==0.10.0
numpy==1.25.0
scipy==1.11.0
opencv-python==4.8.0.76
scikit-learn==1.3.0
textstat==0.7.1
spacy==3.6.0
reportlab==4.0.0
streamlit==1.27.0
requests==2.31.0
"@

# README.md
Write-File "README.md" @"
# Mentor Scoring AI — IntelliTeach Integration

This repository now includes the Mentor Scoring AI engine:
- FastAPI backend
- Streamlit frontend
- Whisper-based STT
- Vision + Audio + NLP scoring modules
- PDF report generation

## Quickstart (Windows)

1. Open PowerShell and navigate to the project root.
2. Create a Python virtual environment:
   ```powershell
   python -m venv .venv



