# 🏗️ System Architecture — Mentor Scoring AI (Round 2)

## Overview
Mentor Scoring AI evaluates teaching videos using:
- **AssemblyAI** → Free video-to-text transcription  
- **Groq LLaMA** → Free LLM-based scoring  
- **FastAPI** backend  
- **Streamlit** frontend  

The system performs:
1. Video upload (frontend)
2. API call → `/analyze`
3. Temp video save (backend)
4. Transcription via AssemblyAI
5. Scoring via Groq (clarity, engagement, confidence, technical, interaction)
6. Final JSON returned and displayed

---

## 📦 Component Breakdown
### **Frontend (Streamlit)**
- Uploads video  
- Sends POST request to `/analyze`  
- Displays scores + transcript  

### **Backend (FastAPI)**
- Receives file  
- Saves temp file  
- Calls AssemblyAI → Transcript  
- Calls Groq → Scores  
- Returns JSON response  

### **AI Layer**
Located in `src/ai/analyze.py`  
- `transcribe_with_assemblyai()`  
- `score_with_groq()`  
- `analyze_video_bytes()`  

---

## 🔄 Data Flow Diagram (Mermaid)
```mermaid
flowchart TD
    A[User Uploads Video] --> B[Streamlit Frontend]
    B --> C[/POST /analyze/]
    C --> D[FastAPI Backend]
    D --> E[Temp File Saved]
    E --> F[AssemblyAI Transcription]
    F --> G[Groq LLaMA Scoring]
    G --> H[JSON Result Returned]
    H --> I[Frontend Displays Scores + Transcript]
