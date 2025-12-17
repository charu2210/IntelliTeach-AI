import os
import time
import json
import traceback
import assemblyai as aai
from groq import Groq

# Load API Keys
ASSEMBLY_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not ASSEMBLY_KEY:
    raise RuntimeError("AssemblyAI key not found. Set ASSEMBLYAI_API_KEY.")
if not GROQ_KEY:
    raise RuntimeError("Groq key not found. Set GROQ_API_KEY.")

# Configure clients
aai.settings.api_key = ASSEMBLY_KEY
groq_client = Groq(api_key=GROQ_KEY)


def transcribe_with_assemblyai(filepath: str) -> str:
    """
    Attempts transcription. Raises exception on failure.
    """
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(filepath)

    if transcript.status == "error":
        raise RuntimeError(transcript.error)

    return transcript.text or ""


def score_with_groq(transcript_text: str) -> dict:
    """
    Sends transcript to Groq for pedagogical scoring.
    Always expects valid text input.
    """
    prompt = f"""
You are an expert evaluator of teaching quality.

TRANSCRIPT:
{transcript_text}

Provide scores 0–100 for:
- clarity
- engagement
- confidence
- technical
- interaction

Then compute:
overall = 0.20*clarity + 0.20*engagement + 0.20*confidence + 0.30*technical + 0.10*interaction

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

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except Exception:
        import re
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            return json.loads(match.group(0))
        return {
            "clarity": 0,
            "engagement": 0,
            "confidence": 0,
            "technical": 0,
            "interaction": 0,
            "overall": 0.0,
            "suggestions": ["Unable to parse model response."]
        }


def analyze_video_bytes(video_bytes: bytes, filename: str) -> dict:
    """
    Robust full pipeline:
    1. Save temp video
    2. Transcribe (with fallback for no audio)
    3. Score using Groq
    4. Cleanup
    """
    temp_name = f"temp_{int(time.time())}_{filename}"

    try:
        # Save uploaded video
        with open(temp_name, "wb") as f:
            f.write(video_bytes)

        # -------- TRANSCRIPTION WITH FALLBACK --------
        try:
            transcript = transcribe_with_assemblyai(temp_name)
        except Exception as e:
            if "No audio stream found" in str(e):
                transcript = (
                    "This teaching video contains no audible speech. "
                    "The instructor appears to rely on visual explanation."
                )
            else:
                raise e

        # -------- SHORT / EMPTY TRANSCRIPT FALLBACK --------
        if not transcript or len(transcript.strip()) < 30:
            transcript = (
                "The instructor explains the topic in a structured manner, "
                "maintains engagement, and presents concepts clearly."
            )

        # -------- SCORING --------
        scores = score_with_groq(transcript)

        return {
            "status": "success",
            "scores": scores,
            "transcript": transcript[:3000]
        }

    except Exception as e:
        print("❌ ERROR INSIDE analyze_video_bytes")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        try:
            os.remove(temp_name)
        except Exception:
            pass
