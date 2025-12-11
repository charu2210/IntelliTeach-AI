from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.analyze import analyze_video

app = FastAPI(title="Mentor Scoring AI (FREE Version)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Free version running!"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    result = analyze_video(content, file.filename)
    return {"result": result}
