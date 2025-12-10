# IntelliTeach-AI 🚀  

**Automatic AI-Powered Teacher Evaluation Prototype**  

## 🔎 What is this  

IntelliTeach-AI is a prototype system that analyzes a recorded teaching session (video + audio) and produces **objective, data-driven feedback** on teaching quality.  
It computes metrics like: clarity, speaking pace, voice confidence, engagement (visual movement), and a combined **Global Benchmark Score**.  

Use-cases: helping teachers improve delivery, providing scalable feedback, preparing coaching reports, or building a teaching analytics dashboard for institutions.  

## ✨ Features  

- 🎤 Transcribe lecture audio using Whisper → get full transcript and Words-Per-Minute (WPM)  
- 🧠 Clarity score (based on filler words, speech clarity)  
- 🎯 Confidence score (based on voice pitch stability)  
- 📹 Engagement score (based on video frame analysis / movement)  
- 📊 Global Benchmark Score: combined signal of pacing and energy  
- 🧪 Easy to test backend: upload video, get JSON with all relevant metrics  

## 🛠 Tech Stack  

- Python 3.x  
- Whisper (for audio transcription)  
- librosa (for audio signal analysis)  
- moviepy + OpenCV (for video processing / movement detection)  
- FastAPI (backend server / API)  

## 🚀 How to Run (Locally)  

1. Clone the repo  
```bash
git clone https://github.com/charu2210/IntelliTeach-AI.git
cd IntelliTeach-AI
