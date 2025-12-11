
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
