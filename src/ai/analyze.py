import os
import time
import json
import assemblyai as aai
from groq import Groq

# Load API Keys from environment variables
ASSEMBLY_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not ASSEMBLY_KEY:
    raise RuntimeError("AssemblyAI key not found. Set ASSEMBLYAI_API_KEY.")
if not GROQ_KEY:
    raise RuntimeError("Groq key not found. Set GROQ_API_KEY.")

# Configure clients
aai.settings.api_key = ASSEMBLY_KEY
groq_client = Groq(api_key=GROQ_KEY)

def transcribe_with_assemblyai(filepath: str):
    """
    Uploads file to AssemblyAI and returns transcript text.
    """
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(filepath)

    if transcript.status == "error":
        raise RuntimeError("AssemblyAI error: " + transcript.error)
    
    return transcript.text

def score_with_groq(transcript_text: str):
    """
    Sends transcript to Groq LLaMA for scoring.
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
        model="llama-3.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message["content"]

    # Try reading JSON directly
    try:
        return json.loads(content)
    except:
        # Try extracting JSON substring
        import re
        m = re.search(r"\{.*\}", content, re.S)
        if m:
            return json.loads(m.group(0))
        return {"error": "Could not parse Groq response", "raw": content}


def analyze_video_bytes(data: bytes, filename: str):
    """
    Full pipeline:
    1. Save temp file
    2. Transcribe with AssemblyAI
    3. Score with Groq
    4. Delete temp file
    """
    temp_name = f"temp_{int(time.time())}_{filename}"

    with open(temp_name, "wb") as f:
        f.write(data)

    try:
        transcript = transcribe_with_assemblyai(temp_name)
        scores = score_with_groq(transcript)
        scores["transcript"] = transcript
        return scores
    finally:
        try:
            os.remove(temp_name)
        except:
            pass
