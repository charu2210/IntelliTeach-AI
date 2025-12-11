from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid

from moviepy import VideoFileClip  # Correct import
import whisper
import librosa
import numpy as np
import cv2

app = FastAPI()


# ---------- AUDIO EXTRACTION ---------- #
def extract_audio(video_path: str) -> str:
    """Extract audio from the video using MoviePy and save as temp wav."""
    clip = VideoFileClip(video_path)
    audio_path = f"temp_audio_{uuid.uuid4()}.wav"
    clip.audio.write_audiofile(audio_path)  # FIX: removed verbose + logger
    clip.close()
    return audio_path


# ---------- 1) CLARITY + WPM SCORE (Whisper) ---------- #
def clarity_score(audio_path: str):
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path)
    text = result.get("text", "").strip()

    # Word count
    words = text.split()
    total_words = len(words)

    # Audio duration
    y, sr = librosa.load(audio_path)
    duration_sec = librosa.get_duration(y=y, sr=sr)
    duration_min = max(0.1, duration_sec / 60)  # avoid division by zero

    # Words Per Minute
    wpm = round(total_words / duration_min, 2)

    # Filler word penalty
    fillers = ["um", "uh", "like", "basically", "you know", "actually", "so"]
    lower_text = text.lower()
    filler_count = sum(lower_text.count(w) for w in fillers)

    clarity = max(0, 100 - (filler_count / max(1, total_words) * 200))

    return round(clarity, 2), text, wpm


# ---------- 2) ENGAGEMENT SCORE (Movement per frame) ---------- #
def engagement_score(video_path: str) -> float:
    cap = cv2.VideoCapture(video_path)
    prev = None
    movement = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev is not None:
            diff = cv2.absdiff(gray, prev)
            movement.append(np.sum(diff))

        prev = gray

    cap.release()

    # SAFE FALLBACK: if no visible movement → neutral score
    if not movement or np.mean(movement) == 0:
        return 50.0  # neutral engagement

    score = min(100, (np.mean(movement) / 5000) * 100)
    return round(score, 2)



# ---------- 3) CONFIDENCE SCORE (Voice Stability) ---------- #
def confidence_score(audio_path: str) -> float:
    y, sr = librosa.load(audio_path)
    pitches, mags = librosa.piptrack(y=y, sr=sr)
    pitch_values = pitches[mags > np.median(mags)]
    if pitch_values.size == 0:
        return 0.0

    variation = float(np.std(pitch_values))
    score = max(0.0, 100.0 - variation)
    return round(score, 2)


# ---------- ROUTES ---------- #
@app.get("/")
def root():
    return {"message": "IntelliTeach AI Backend Ready! 🚀"}


@app.post("/score")
async def score_video(file: UploadFile = File(...)):
    # 1) Save uploaded file
    video_path = f"uploaded_{uuid.uuid4()}.mp4"
    with open(video_path, "wb") as buffer:
        buffer.write(await file.read())

    # 2) Extract audio
    audio_path = extract_audio(video_path)

    # 3) Compute individual metrics
    clarity, transcript, wpm = clarity_score(audio_path)
    engagement = engagement_score(video_path)
    confidence = confidence_score(audio_path)

    # ---------- GLOBAL BENCHMARK SCORE ----------
    # Ideal range: 130–180 WPM
    if wpm < 80:
        pace_score = (wpm / 80) * 50
    elif wpm > 200:
        pace_score = (200 / wpm) * 50
    else:
        pace_score = 50

    # Engagement score = energy
    energy_score = engagement

    global_benchmark = round(min(100, pace_score + energy_score), 2)

    # ---------- Overall Dummy Weighted Score (for now) ----------
    overall = (clarity * 0.2 + engagement * 0.2 + confidence * 0.1) / 0.5
    overall = round(overall, 2)

    # 4) Cleanup temporary files
    for p in [video_path, audio_path]:
        try:
            os.remove(p)
        except OSError:
            pass

    # 5) Response JSON
    return JSONResponse({
        "clarity": clarity,
        "engagement": engagement,
        "confidence": confidence,
        "overall_score": overall,
        "wpm": wpm,
        "global_benchmark": global_benchmark,
        "transcript_preview": (
            transcript[:200] + "..." if len(transcript) > 200 else transcript
        ),
    })
