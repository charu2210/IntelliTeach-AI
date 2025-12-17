import streamlit as st
import requests
import json

API_URL = "http://localhost:8000/analyze"

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="IntelliTeach AI",
    page_icon="🎓",
    layout="centered"
)

# ---------- CUSTOM CSS (DARK BLUE THEME) ----------
st.markdown("""
<style>

/* FULL PAGE DARK BLUE BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
}

/* MAIN CONTENT CONTAINER */
.main {
    background-color: #020617;
    padding: 2rem;
}

/* GENERAL TEXT */
body, p, span, label {
    color: #e5e7eb;
}

/* HEADINGS */
h1 {
    color: #38bdf8; /* bright blue */
    font-weight: 800;
}
h2, h3 {
    color: #60a5fa;
}

/* CARDS */
.card {
    background: #020617;
    border: 1px solid #1e293b;
    padding: 1.2rem;
    border-radius: 14px;
    text-align: center;
}
.card-title {
    font-size: 0.9rem;
    color: #c7d2fe;
}
.card-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #38bdf8;
}

/* BUTTON */
.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    border: none;
}
.stButton > button:hover {
    background-color: #1d4ed8;
}

/* INFO / SUCCESS / WARNING BOXES */
.stAlert {
    background-color: #020617;
    border: 1px solid #1e293b;
    color: #e5e7eb;
}

/* FILE UPLOADER */
.css-1cpxqw2 {
    border-radius: 12px;
    border: 1px dashed #38bdf8;
    background-color: #020617;
    color: #e5e7eb;
}

/* TABS */
.stTabs [data-baseweb="tab"] {
    color: #c7d2fe;
}
.stTabs [aria-selected="true"] {
    color: #38bdf8;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown(
    "<h1>🎓 IntelliTeach AI</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h4 style='color:#93c5fd;'>AI-Powered Teaching Evaluation Platform</h4>",
    unsafe_allow_html=True
)
st.caption("UpSkill India Challenge · IIT Bombay")

st.markdown("""
<h3>🧭 How it works</h3>

1️⃣ Upload a short teaching video (30–60 seconds)  
2️⃣ AI transcribes and evaluates teaching quality  
3️⃣ Get structured scores and actionable feedback
""", unsafe_allow_html=True)

st.info(
    "📌 Demo Tip: Use a short video with clear speech. "
    "Silent videos are handled using fallback logic."
)

# ---------- FILE UPLOAD ----------
video = st.file_uploader(
    "📤 Upload Teaching Video (MP4)",
    type=["mp4", "mov", "mkv", "webm"]
)

# ---------- ANALYSIS ----------
if video:
    if st.button("🚀 Analyze Teaching Video"):
        st.info("⏳ Processing… Please wait (20–60 seconds).")

        files = {
            "file": (
                video.name,
                video.getvalue(),
                video.type
            )
        }

        try:
            response = requests.post(API_URL, files=files, timeout=600)
            response.raise_for_status()
            data = response.json()["result"]

            if data.get("status") == "error":
                st.error(data.get("message", "Analysis failed"))
                st.stop()

            scores = data["scores"]

            st.success("✅ Analysis Completed Successfully")

            # ---------- TABS ----------
            tab1, tab2, tab3, tab4 = st.tabs(
                ["📌 Overview", "📊 Scores", "📝 Transcript", "🔍 Raw Output"]
            )

            # ---------- TAB 1 ----------
            with tab1:
                st.subheader("⭐ Overall Teaching Score")
                st.metric("Overall Score", round(scores["overall"], 2))
                st.progress(min(scores["overall"] / 100, 1.0))

                st.subheader("💡 Improvement Suggestions")
                for s in scores.get("suggestions", []):
                    st.write("•", s)

            # ---------- TAB 2 ----------
            with tab2:
                st.subheader("📊 Evaluation Breakdown")

                cols = st.columns(5)
                metrics = [
                    ("clarity", "Clarity"),
                    ("engagement", "Engagement"),
                    ("confidence", "Confidence"),
                    ("technical", "Technical"),
                    ("interaction", "Interaction")
                ]

                for col, (key, label) in zip(cols, metrics):
                    with col:
                        st.markdown(f"""
                        <div class="card">
                            <div class="card-title">{label}</div>
                            <div class="card-value">{scores[key]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.progress(scores[key] / 100)

            # ---------- TAB 3 ----------
            with tab3:
                st.subheader("📝 Transcript Preview")
                if data.get("transcript"):
                    st.text(data["transcript"][:1500])
                else:
                    st.warning(
                        "No or low audio detected. "
                        "Scores generated using contextual inference."
                    )

            # ---------- TAB 4 ----------
            with tab4:
                st.json(data)

        except Exception as e:
            st.error(f"❌ Backend Error: {str(e)}")

