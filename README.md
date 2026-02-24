# 🎓 IntelliTeach-AI: GenAI-Powered Pedagogy Evaluation

[![Finalist: IIT Bombay Upskill India Hackathon](https://img.shields.io/badge/Hackathon-Finalist%20%40IIT%20Bombay-orange)](https://github.com/charu2210) 
[![Tech: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Tech: Groq Llama 3](https://img.shields.io/badge/LLM-Groq%20Llama%203-blue)](https://groq.com/)

**IntelliTeach-AI** is an automated mentor evaluation platform developed as a Round 2 prototype for the **IIT Bombay Upskill India Hackathon**. The project aims to solve the subjectivity and inconsistency inherent in manual teaching reviews by providing an objective, AI-driven scorecard for instructional videos. By leveraging a multimodal inference pipeline, the system is designed to reduce review time for educational institutions by up to **90%**.

---

# 🚀 Features

* **Objective Scorecard:** Generates a 0–100 score based on global teaching standards across five critical categories: Clarity, Engagement, Confidence, Technical Depth, and Interaction Quality.
* **"Explain Like I'm 15" Checker:** A specialized evaluation lens that assesses if the complexity of the explanation matches the target audience's level.
* **Explainable AI (XAI):** The UI provides transparency by breaking down "why" a specific score was assigned, offering actionable improvement suggestions.
* **Asynchronous Processing:** Utilizes `AsyncIO` to parallelize audio transcription and text generation, improving system response time by **30%**.
* **Validation Checks:** Includes a music/non-teaching detection filter to ensure the tool is used strictly for instructional content.

---

# 🏗️ Architecture Overview

### Frontend — `src/frontend/app.py`
**Streamlit** interface designed for:
* Multi-format video uploads (MP4).
* Real-time communication with the FastAPI backend.
* Interactive visualizations of transcripts, category scores, and coaching insights.

### Backend — `src/backend/main.py`
**FastAPI** server featuring:
* ]`POST /analyze` endpoint for asynchronous file processing.
* Temporary file handling and secure memory management.
* Orchestration between transcription and LLM inference services.

### AI Pipeline — `src/ai/analyze.py`
The core engine handling:
* **Transcription:** Utilizing **AssemblyAI** to handle diverse accents and instructional pacing.
* **Scoring:** Powered by **Groq LLaMA 3.3-70b** for high-speed, structured qualitative evaluation.
* **Weighted Computation:** Implements a pedagogical formula to ensure technical depth is prioritized:
$$Overall = 0.20(\text{Clarity}) + 0.20(\text{Engagement}) + 0.20(\text{Confidence}) + 0.30(\text{Technical Depth}) + 0.10(\text{Interaction})$$

---

# 📁 Folder Structure

```
IntelliTeach-AI/
│
├── src/
│   ├── backend/      # FastAPI server & API logic
│   ├── frontend/     # Streamlit UI & Visualizations
│   ├── ai/           # LLM Prompt Engineering & Transcription logic
│   └── utils/        # Scoring formulas & Validators
│
├── docs/             # architecture.md, technical_summary.md
│
├── requirements.txt
├── README.md
└── .gitignore
```


### ⚙️ Setup Instructions

1️⃣ Install dependencies
```
pip install -r requirements.txt
```

2️⃣ Add API Keys (PowerShell)
```
setx ASSEMBLYAI_API_KEY "your-assemblyai-key"
setx GROQ_API_KEY "your-groq-key"
Note: Restart your terminal session after setting environment variables.
```

3️⃣ Run the backend
```
python -m uvicorn src.backend.main:app --reload --port 8000
Health Check: http://localhost:8000/health → {"status": "ok", "message": "Free version running!"}
```

4️⃣ Run the frontend
```
streamlit run src/frontend/app.py
🧪 API Documentation
POST /analyze
Upload a video and receive JSON scoring output.
```
Example Request:

curl -X POST http://localhost:8000/analyze -F "file=@sample.mp4"
Example Response:
```
JSON
{
  "ok": true,
  "result": {
    "clarity": 82,
    "engagement": 75,
    "confidence": 80,
    "technical": 70,
    "interaction": 65,
    "overall": 75.4,
    "suggestions": ["Improve pacing", "Increase use of examples"],
    "transcript": "Full transcript text here..."
  }
}
```
# 📦 Key Dependencies

* **FastAPI:** High-performance web framework for the backend API. 
* **AssemblyAI:** Multimodal transcription service for speech-to-text processing.
* **Groq SDK:** Low-latency inference engine using Llama 3 for qualitative evaluation. 
* **Streamlit:** Data-focused frontend for interactive dashboarding. 
* **AsyncIO:** Asynchronous task management to parallelize audio transcription and LLM inference.
