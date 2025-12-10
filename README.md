# Mentor Scoring AI - Round 2 Prototype

🚀 Functional Prototype: Video Upload → AI Scoring (Dummy)

This system evaluates mentor performance based on:
- **Clarity** (speech quality)
- **Engagement** (facial activity)
- **Confidence** (voice steadiness)

📌 Day-1 Deliverables Completed:
- Streamlit Frontend (supports video upload)
- FastAPI Backend (accepts video and returns JSON score)
- End-to-End working flow (upload → analyze → score display)

📂 Project Structure
.
├─ README.md
├─ requirements.txt
└─ src
   ├─ backend
   │   └─ main.py
   └─ frontend
       └─ app.py

🏗️ Next Steps (Day-2 & Day-3)
- Integrate real AI models (Whisper, OpenCV, Librosa)
- Add real scoring metrics (not dummy)
- UI improvements + visual score charts
- Deployment for Judges demo
