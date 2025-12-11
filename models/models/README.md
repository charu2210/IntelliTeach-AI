# 📦 Models Used — Mentor Scoring AI (Round 2)

This project uses **free-tier AI models** so students can build and test the system without cost.

---

## 🎤 1. Transcription Model — AssemblyAI
**Purpose:** Convert mentor teaching video → text transcript  
**API:** https://www.assemblyai.com  
**Tier:** Free (5 hours/month)

### Features:
- Robust speech-to-text  
- Handles accents  
- Good for educational content  
- Stable API  

---

## 🧠 2. Scoring Model — Groq LLaMA 3.1 Mini
**Purpose:** Score clarity, engagement, confidence, technical depth, interaction  
**API:** https://console.groq.com  
**Tier:** Free

### Why LLaMA Mini?
- Extremely fast  
- Free to run  
- Ideal for structured scoring JSON  
- Zero cost for hackathon prototypes  

---

## 📊 Scoring Weights
overall = 0.20clarity
+ 0.20engagement
+ 0.20confidence
+ 0.30technical
+ 0.10interaction

---

## 📁 Model Storage
Since models are hosted via APIs, **no large model files** are stored locally. This keeps the repo lightweight and avoids licensing issues.

---

## 🔮 Future Model Improvements (Round 3)
- Add multimodal scoring (vision + speech)  
- Evaluate gestures and expression  
- Detect pace, pauses, emphasis  
- Fine-tune rubric for IIT Bombay evaluation criteria  


