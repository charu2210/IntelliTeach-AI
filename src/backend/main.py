from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.ai.analyze import analyze_video_bytes
import traceback

app = FastAPI(title="Mentor Scoring AI - Free Version (Round 2)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Free version running!"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()

        if not content:
            raise ValueError("Uploaded file is empty")

        result = analyze_video_bytes(content, file.filename)
        return {"ok": True, "result": result}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

