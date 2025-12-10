# saved as app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
import os
import uuid
import tempfile
import traceback

# MoviePy correct import
from moviepy.editor import VideoFileClip

# Whisper (openai/whisper) - ensure package installed and ffmpeg available
import whisper

import librosa
import numpy as np
import cv2

app = FastAPI()

# --- Load Whisper model once (module level) ---
# WARNING: this can take time & memory. Use a smaller model for lower memory.
try:
    WHISPER_MODEL = whisper.load_model("tiny")
except Exception as e:
    # if model fails to load at import, keep None and raise at runtime
    WHISPER_MODEL = None
    print("Warning: Whisper model failed to load at startup:", e)


# ---------- AUDIO EXTRACTION (moviepy) ---------- #
def extract_audio(video_path: str) -> str:
    """Extract audio from the video using MoviePy and save as a temp wav file path (returns path)."""
    clip = VideoFileClip(video_path)
    # use tempfile so filename is unique and automatically on tmp dir
    out_fd, audio_path = tempfile.mkstemp(suffix=".wav", prefix="audio_")
    os.close(out_fd)
    try:
        # write_audiofile is blocking
        clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
    finally:
        clip.close()
    return audio_path


# ---------- 1) CLARITY + WPM SCORE (Whisper) ---------- #
def clarity_score(audio_path: str):
    if WHISPER_MODEL is None:
        # try to lazy-load once
        try:
            model = whisper.load_model("tiny")
        except Exception as e:
            raise RuntimeError("Whisper model not available: " + str(e))
    else:
        model = WHISPER_MODEL

    # transcribe (blocking)
    result = model.transcribe(audio_path)
    text = result.get("text", "") or ""
    text = text.strip()

    # Word count
    words = text.split()
    total_words = len(words)

    # Audio duration - use sr=None to preserve original sr
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        duration_sec = librosa.get_duration(y=y, sr=sr)
    except Exception:
        # fallback: assume 0.0
        duration_sec = 0.0

    duration_min = max(0.1, duration_sec / 60.0)  # avoid division by zero

    # Words Per Minute
    wpm = round(total_words / duration_min, 2)

    # Filler word penalty (simple count)
    fillers = ["um", "uh", "like", "basically", "you know", "actually", "so"]
    lower_text = text.lower()
    filler_count = sum(lower_text.count(w) for w in fillers)

    clarity = max(0.0, 100.0 - (filler_count / max(1, total_words) * 200.0))
    clarity = round(clarity, 2)

    return clarity, text, wpm


# ---------- 2) ENGAGEMENT SCORE (Movement per frame) ---------- #
def engagement_score(video_path: str) -> float:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0.0

    prev = None
    movement = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            diff = cv2.absdiff(gray, prev)
            movement.append(float(np.sum(diff)))
        prev = gray

    cap.release()
    if not movement:
        return 0.0

    # normalize - tuned value (guard against huge numbers)
    mean_mov = float(np.mean(movement))
    score = min(100.0, (mean_mov / 5000.0) * 100.0)
    return round(score, 2)


# ---------- 3) CONFIDENCE SCORE (Voice Stability) ---------- #
def confidence_score(audio_path: str) -> float:
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
    except Exception:
        return 0.0

    # pitch track
    try:
        pitches, mags = librosa.piptrack(y=y, sr=sr)
        # mags is 2D; pick values where mag is above median
        mag_median = np.median(mags) if mags.size else 0.0
        mask = mags > mag_median
        pitch_values = pitches[mask]
    except Exception:
        pitch_values = np.array([])

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
    # Save uploaded file to a temp file
    vid_fd, video_path = tempfile.mkstemp(suffix=".mp4", prefix="upload_")
    os.close(vid_fd)
    try:
        # write bytes (async)
        contents = await file.read()
        with open(video_path, "wb") as f:
            f.write(contents)

        # run blocking heavy work in threadpool so uvicorn/event loop not blocked
        def process_all():
            audio_path = None
            try:
                audio_path = extract_audio(video_path)

                clarity, transcript, wpm = clarity_score(audio_path)
                engagement = engagement_score(video_path)
                confidence = confidence_score(audio_path)

                # GLOBAL BENCHMARK
                if wpm < 80:
                    pace_score = (wpm / 80.0) * 50.0
                elif wpm > 200:
                    pace_score = (200.0 / wpm) * 50.0
                else:
                    pace_score = 50.0

                energy_score = engagement
                global_benchmark = round(min(100.0, pace_score + energy_score), 2)

                overall = (clarity * 0.2 + engagement * 0.2 + confidence * 0.1) / 0.5
                overall = round(float(overall), 2)

                # Ensure all returned values are native Python types
                response = {
                    "clarity": float(clarity),
                    "engagement": float(engagement),
                    "confidence": float(confidence),
                    "overall_score": float(overall),
                    "wpm": float(wpm),
                    "global_benchmark": float(global_benchmark),
                    "transcript_preview": (transcript[:200] + "...") if len(transcript) > 200 else transcript,
                }
                return response
            finally:
                # cleanup audio temp file if exists
                if audio_path and os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                    except OSError:
                        pass

        result = await run_in_threadpool(process_all)
        return JSONResponse(result)
    except Exception as e:
        tb = traceback.format_exc()
        # return error with stack trace suppressed in production; here return brief message
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # cleanup uploaded video
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except OSError:
                pass

