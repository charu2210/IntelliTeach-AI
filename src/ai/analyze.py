import os
import time
import json
import traceback
import assemblyai as aai
from groq import Groq

# ---------- API KEYS ----------
ASSEMBLY_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not ASSEMBLY_KEY:
    raise RuntimeError("AssemblyAI key not found.")
if not GROQ_KEY:
    raise RuntimeError("Groq key not found.")

aai.settings.api_key = ASSEMBLY_KEY
groq_client = Groq(api_key=GROQ_KEY)


# ---------- TRANSCRIPTION ----------
def transcribe_with_assemblyai(filepath: str) -> str:
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(filepath)

    if transcript.status == "error":
        raise RuntimeError(transcript.error)

    return transcript.text or ""


# ---------- MUSIC / NON-TEACHING DETECTION ----------
def is_music_or_non_teaching(transcript: str) -> bool:
    keywords = [
        "chorus", "verse", "lyrics", "music", "song",
        "instrumental", "beats", "singer"
    ]
    transcript_lower = transcript.lower()
    return any(k in transcript_lower for k in keywords)


# ---------- SCORING ----------
def score_with_groq(transcript_text: str) -> dict:
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
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
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
            "suggestions": ["Unable to evaluate content."]
        }


# ---------- SCORE INTERPRETATION ----------
def interpret_score(overall: float) -> dict:
    if overall >= 80:
        return {
            "rating": "Excellent",
            "recommendation": "You can confidently proceed with this teaching video."
        }
    elif overall >= 65:
        return {
            "rating": "Good",
            "recommendation": "This video is good but minor improvements are suggested."
        }
    elif overall >= 50:
        return {
            "rating": "Average",
            "recommendation": "The video needs improvement before proceeding."
        }
    else:
        return {
            "rating": "Poor",
            "recommendation": "This video is not recommended for teaching evaluation."
        }


# ---------- MAIN PIPELINE ----------
def analyze_video_bytes(video_bytes: bytes, filename: str) -> dict:
    temp_name = f"temp_{int(time.time())}_{filename}"

    try:
        with open(temp_name, "wb") as f:
            f.write(video_bytes)

        # ---- TRANSCRIPTION ----
        try:
            transcript = transcribe_with_assemblyai(temp_name)
        except Exception as e:
            if "No audio stream found" in str(e):
                transcript = ""
            else:
                raise e

        # ---- NO / LOW AUDIO FALLBACK ----
        if not transcript or len(transcript.strip()) < 30:
            transcript = (
                "This video contains limited or no spoken instructional content."
            )

        # ---- MUSIC / NON-TEACHING CHECK ----
        if is_music_or_non_teaching(transcript):
            return {
                "status": "invalid",
                "message": "This appears to be a music or non-instructional video. "
                           "IntelliTeach AI is designed for teaching evaluation only."
            }

        # ---- SCORING ----
        scores = score_with_groq(transcript)
        interpretation = interpret_score(scores["overall"])

        return {
            "status": "success",
            "scores": scores,
            "rating": interpretation["rating"],
            "recommendation": interpretation["recommendation"],
            "transcript": transcript[:3000]
        }

    except Exception as e:
        print("❌ ERROR IN BACKEND")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        try:
            os.remove(temp_name)
        except:
            pass


