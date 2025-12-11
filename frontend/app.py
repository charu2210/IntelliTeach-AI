
import streamlit as st
import requests

API_URL = "http://localhost:8000/analyze"

st.title("Mentor Scoring AI")
st.write("Upload a teaching video and get AI-based evaluation.")

video = st.file_uploader("Upload MP4 video", type=["mp4"])

if video and st.button("Analyze"):
    with st.spinner("Analyzing..."):
        files = {"file": (video.name, video.read(), "video/mp4")}
        res = requests.post(API_URL, files=files)

        if res.status_code == 200:
            st.success("Done!")
            st.json(res.json())
        else:
            st.error("Error from backend")
