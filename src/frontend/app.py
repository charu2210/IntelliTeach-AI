import streamlit as st
import requests
import json

API_URL = "http://localhost:8000/analyze"

st.set_page_config(page_title="Mentor Scoring AI", layout="centered")

st.title("🎓 Mentor Scoring AI (Free Version)")
st.write("Upload a teaching video (MP4) to evaluate clarity, engagement, confidence, and more.")

video = st.file_uploader("Upload video", type=["mp4", "mov", "mkv", "webm"])

if video:
    if st.button("Analyze Video"):
        st.info("⏳ Processing... This may take 20–60 seconds depending on video length.")
        files = {"file": (video.name, video.read(), "video/mp4")}

        try:
            response = requests.post(API_URL, files=files, timeout=600)
            response.raise_for_status()

            data = response.json().get("result")

            # Try parsing string JSON if needed
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    pass

            st.success("✅ Analysis Completed!")

            st.subheader("📊 Scorecard")
            st.json(data)

            # Display transcript
            if isinstance(data, dict) and "transcript" in data:
                st.subheader("📝 Transcript (first 1000 characters)")
                st.text(data["transcript"][:1000])

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
