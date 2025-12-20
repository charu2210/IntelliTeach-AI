import streamlit as st
import requests
import json
import time

# ================= CONFIG =================
API_URL = "http://localhost:8000/analyze"

st.set_page_config(
    page_title="IntelliTeach AI",
    page_icon="🎓",
    layout="centered"
)

# ================= SCORE TRANSPARENCY =================
SCORE_DESCRIPTIONS = {
    "clarity": {
        "label": "Clarity",
        "what": "How clearly concepts are explained.",
        "how": "Sentence structure, pacing, pauses, filler words.",
        "tip": "Slow down during definitions and use examples."
    },
    "engagement": {
        "label": "Engagement",
        "what": "Ability to maintain learner interest.",
        "how": "Tone variation, emphasis, questioning.",
        "tip": "Vary tone and ask reflective questions."
    },
    "confidence": {
        "label": "Confidence",
        "what": "Speaker assurance and authority.",
        "how": "Voice stability and hesitation frequency.",
        "tip": "Practice key sections aloud."
    },
    "technical": {
        "label": "Technical Depth",
        "what": "Accuracy and depth of subject matter.",
        "how": "Correctness and terminology usage.",
        "tip": "Use precise terms with brief definitions."
    },
    "interaction": {
        "label": "Interaction",
        "what": "Audience involvement.",
        "how": "Prompts, questions, inclusive language.",
        "tip": "Invite learners to think or respond."
    }
}

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
}
.main {
    padding: 2rem;
}
body, p, span, label {
    color: #e5e7eb;
}
h1 {
    color: #38bdf8;
    font-weight: 800;
}
h2, h3 {
    color: #60a5fa;
}
.card {
    background: #020617;
    border: 1px solid #1e293b;
    padding: 1.2rem;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 0.6rem;
}
.card-title {
    font-size: 0.85rem;
    color: #c7d2fe;
}
.card-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #38bdf8;
}
.transparency-box {
    background: #020617;
    border: 1px solid #1e293b;
    padding: 1.2rem;
    border-radius: 16px;
    margin-top: 1rem;
}
.transparency-title {
    color: #93c5fd;
    font-weight: 700;
    margin-bottom: 0.8rem;
}
.transparency-col {
    font-size: 0.85rem;
}
.transparency-col b {
    color: #c7d2fe;
}
.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<h1>🎓 IntelliTeach AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<h4 style='color:#93c5fd;'>AI-Powered Teaching Evaluation Platform</h4>",
    unsafe_allow_html=True
)
st.caption("UpSkill India Challenge · IIT Bombay")

st.markdown("""
### 🧭 How it works
1️⃣ Upload a teaching video (MP4)  
2️⃣ AI evaluates pedagogy & delivery  
3️⃣ Get **explainable scores + coaching**
""")

# ================= FILE UPLOAD =================
video = st.file_uploader(
    "📤 Upload Teaching Video (MP4 only)",
    type=["mp4"]
)

# ================= ANALYSIS =================
if video and st.button("🚀 Analyze Teaching Video"):

    status = st.empty()
    progress = st.progress(0)

    status.info("🎧 Transcribing audio…")
    progress.progress(25)
    time.sleep(0.4)

    status.info("🧠 Evaluating teaching quality…")
    progress.progress(55)
    time.sleep(0.4)

    status.info("📊 Generating scores & feedback…")
    progress.progress(75)

    try:
        response = requests.post(
            API_URL,
            files={"file": (video.name, video.getvalue(), "video/mp4")},
            timeout=600
        )
        response.raise_for_status()

        data = response.json().get("result", response.json())
        scores = data.get("scores", {})

        progress.progress(100)
        status.success("✅ Analysis Complete")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["📌 Overview", "📊 Scores", "📝 Transcript", "🔍 Raw"]
        )

        # ---------- OVERVIEW ----------
        with tab1:
            overall = scores.get("overall", 0)
            st.metric("Overall Teaching Score", round(overall, 2))
            st.progress(overall / 100)

            if data.get("persona"):
                st.success(f"🧠 Teaching Persona: **{data['persona']}**")

            for s in scores.get("suggestions", []):
                st.write("•", s)

        # ---------- SCORES ----------
        with tab2:
            st.subheader("📊 Score Breakdown")

            cols = st.columns(5)
            keys = list(SCORE_DESCRIPTIONS.keys())

            for col, key in zip(cols, keys):
                value = scores.get(key, 0)
                meta = SCORE_DESCRIPTIONS[key]

                with col:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">{meta['label']}</div>
                        <div class="card-value">{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(value / 100)

            # ===== SINGLE HORIZONTAL TRANSPARENCY BOX =====
   
            st.markdown(
                '<div class="transparency-title">🔍 Why these scores?</div>',
                unsafe_allow_html=True
            )

            explain_cols = st.columns(5)

            for col, key in zip(explain_cols, keys):
                meta = SCORE_DESCRIPTIONS[key]
                with col:
                    st.markdown(
                        f"""
                        <div class="transparency-col">
                        <b>{meta['label']}</b><br>
                        {meta['what']}<br><br>
                        <i>How:</i> {meta['how']}<br><br>
                        💡 {meta['tip']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown('</div>', unsafe_allow_html=True)

        # ---------- TRANSCRIPT ----------
        with tab3:
            if data.get("transcript"):
                st.text(data["transcript"][:2500])
            else:
                st.warning("Low or no audio detected.")

        # ---------- RAW ----------
        with tab4:
            st.json(data)

        st.download_button(
            "📄 Download Full Report",
            json.dumps(data, indent=2),
            file_name="intelliteach_report.json",
            mime="application/json"
        )

    except Exception as e:
        status.error("❌ Backend Error")
        st.error(str(e))


