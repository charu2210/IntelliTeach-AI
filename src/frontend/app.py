import streamlit as st
import requests

st.title("Mentor Scoring AI Prototype")

video = st.file_uploader("Upload Mentor Session Video", type=["mp4", "mov", "mkv"])

if video:
    if st.button("Analyze"):
        files = {"file": video}
        response = requests.post("http://localhost:8000/score", files=files)
        
        if response.status_code == 200:
            st.success("Analysis complete!")
            st.json(response.json())
        else:
            st.error("Backend error: " + response.text)
