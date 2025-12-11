# 📄 Technical Summary — Mentor Scoring AI (Round 2 Submission)

## 1. Problem Statement
Evaluating teaching quality from recorded mentor videos is subjective, time-consuming, and inconsistent.  
The goal is to build an AI system that automatically analyzes teaching videos and generates a scorecard based on:

- Clarity  
- Engagement  
- Confidence  
- Technical depth  
- Interaction quality  

This helps education teams provide structured feedback and scale mentorship programs.

---

## 2. Proposed Solution
We developed a **video-based AI evaluation pipeline** using completely free, student-friendly tools:

### ✔ Video → Transcript  
**AssemblyAI** (Free Tier: 5 hours/month)  
Automatically extracts clean speech transcripts from mentor videos.

### ✔ Transcript → AI Scorecard  
**Groq LLaMA** (Free Tier)  
Uses a lightweight LLaMA model to compute numerical scores and generate suggestions.

### ✔ Backend  
**FastAPI** handles:
- File uploads  
- Temp video storage  
- Calling AssemblyAI + Groq  
- Returning JSON response  

### ✔ Frontend  
**Streamlit** allows:
- Uploading video  
- Displaying scores  
- Showing transcript for transparency  

The combined workflow delivers reliable and fast scoring without requiring paid APIs.

---

## 3. System Architecture
1. User uploads an MP4 file via Streamlit.  
2. Backend receives the file through `/analyze`.  
3. File saved temporarily in backend.  
4. AssemblyAI transcribes the audio.  
5. Transcript is passed to Groq LLaMA for scoring.  
6. Backend sends full JSON evaluation back to frontend.  
7. Frontend displays results, transcript, and suggestions.

See `docs/architecture.md` for diagrams.

---

## 4. AI Components

### 🔹 **Transcription Model**
- AssemblyAI Standard Model  
- High-quality speech detection  
- Handles accents, pace variation  

### 🔹 **Scoring Model**
- Groq LLaMA 3.1 Mini  
- Fast inference  
- Free tier suitable for hackathon use  
- Produces structured JSON output  

### 🔹 **Scoring Formula**
overall = 0.20clarity
+ 0.20engagement
+ 0.20confidence
+ 0.30technical
+ 0.10interaction


---

## 5. Challenges & Mitigation

### **Latency**
Transcription can take time.  
💡 Mitigation: Use short demo videos for Round 2.

### **JSON Parsing Errors**
LLMs sometimes return extra text.  
💡 Mitigation: Regex-based strict JSON extraction added in `analyze.py`.

### **Model Limits**
Free tiers impose rate limits.  
💡 Mitigation: Light usage, short videos, retry strategy if needed.

---

## 6. Roadmap to Final Build (Round 3)

### ✔ Planned Improvements
- Radar chart visualization  
- PDF report export  
- Mentor profile dashboard  
- Custom scoring rubric  
- Database integration (PostgreSQL / MongoDB)  
- Deployment on Render + Streamlit Cloud  

### ✔ Possible Extensions
- Emotion detection  
- Gesture analysis  
- Multi-modal real-time feedback  
- Batch evaluation for institutions  

---

## 7. Conclusion
The Round-2 version successfully demonstrates an **end-to-end functional prototype**:

- Video upload  
- AI transcription  
- LLM scoring  
- Frontend visualization  
- Clean documentation  

The system is technically feasible, scalable, and aligned with the educational impact goals of the hackathon.
