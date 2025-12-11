import os
import time
import assemblyai as aai
from groq import Groq

# Load API Keys
ASSEMBLY_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

aai.settings.api_key = ASSEMBLY_KEY
groq_client = Groq(api_key=GROQ_KEY)

def transcribe_video(file_path):
    """Upload and transcribe video using AssemblyAI (FREE tier)."""

    transcriber = aai.Transcriber()

    print("Uploading + transcribing video (AssemblyAI)...")
    transcript = transcriber.transcribe(file_path)

    if transcript.status == "error":
        raise Exception("Transcription failed: " + transcript.error)

    return transcript.text


def score_with_groq(transcript_text):
    """Use Groq LLaMA 3.1 to score the mentor (FREE)."""

    prompt = f"""
    You are an AI teaching evaluator.

    TRANSCRIPT:
    {transcript_text}

    Score the categories:
    - Clarity (0-100)
    - Engagement (0-100)
    - Confidence (0-100)
    - Technical Depth (0-100)
    - Interaction Quality (0-100)

    Then compute:
    total = 0.20*clarity + 0.20*engagement + 0.20*confidence + 0.30*technical + 0.10*interaction

    Return STRICT JSON ONLY:
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

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]


def analyze_video(file: bytes, filename: str):
    """Full pipeline: save file → transcribe → score."""

    temp_path = f"temp_{filename}"

    # Save the video file temporarily
    with open(temp_path, "wb") as f:
        f.write(file)

    # Step 1: FREE transcription
    transcript_text = transcribe_video(temp_path)

    # Step 2: FREE scoring via Groq
    scores = score_with_groq(transcript_text)

    # Remove temp file
    os.remove(temp_path)

    return scores

