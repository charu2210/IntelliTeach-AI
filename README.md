# 🎓 IntelliTeach-AI — Round 2 Prototype (IIT Bombay Upskill India)

IntelliTeach-AI evaluates teaching videos and produces a detailed, quantitative scorecard across:
- Clarity  
- Engagement  
- Confidence  
- Technical Depth  
- Interaction Quality  

This Round-2 prototype demonstrates a **complete end-to-end workflow** using free-tier AI tools, a modular backend, and a functional frontend.

---

# 🚀 Features
✔ Upload a video (MP4)  
✔ Automatic transcription via **AssemblyAI (Free)**  
✔ Scoring via **Groq LLaMA (Free)**  
✔ JSON output with:
  - category-wise scores  
  - computed overall score  
  - improvement suggestions  
✔ Transcript preview  
✔ Frontend in Streamlit  
✔ Backend in FastAPI  
✔ Clean documentation (`/docs`)  
✔ Hackathon-approved folder structure (`/src`)  

---

# 🏗️ Architecture Overview

### 🟦 Frontend — `src/frontend/app.py`
Streamlit UI for:
- Video upload  
- Sending request to backend  
- Displaying scores + transcript  

### 🟩 Backend — `src/backend/main.py`
FastAPI server with:
- `POST /analyze`  
- Temporary file handling  
- Calls AI pipeline  
- Returns JSON  

### 🤖 AI Pipeline — `src/ai/analyze.py`
Handles:
- AssemblyAI transcription  
- Groq LLaMA scoring  
- JSON cleanup  
- Weighted scoring  

### 📂 Full Documentation in `/docs`
- Architecture document  
- Technical summary  
- Workflow  

---

# 📁 Folder Structure (Hackathon-Compliant)

IntelliTeach-AI/
│
├── src/
│ ├── backend/
│ │ └── main.py
│ ├── frontend/
│ │ └── app.py
│ ├── ai/
│ │ └── analyze.py
│ └── utils/ (reserved for Round 3)
│
├── docs/
│ ├── architecture.md
│ ├── technical_summary.md
│ └── (future diagrams)
│
├── models/
│ └── README.md
│
├── requirements.txt
├── README.md
└── .gitignore


---

# ⚙️ Setup Instructions

## 1️⃣ Install dependencies
pip install -r requirements.txt

## 2️⃣ Add FREE API Keys (PowerShell)
setx ASSEMBLYAI_API_KEY "your-assembly-key"
setx GROQ_API_KEY "your-groq-key"

Close PowerShell and reopen it.

## 3️⃣ Run the backend
python -m uvicorn src.backend.main:app --reload --port 8000

Check health:
👉 http://localhost:8000/health

Should show:
{"status": "ok", "message": "Free version running!"}

## 4️⃣ Run the frontend
streamlit run src/frontend/app.py


Upload a short MP4 and view the scorecard.

---

# 🧪 API Documentation

### **POST /analyze**  
Upload a video and receive JSON scores.

Example curl:
curl -X POST http://localhost:8000/analyze-F "file=@sample.mp4"


Response structure:
```json
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
