import streamlit as st
import json
from detector import analyze_job_description

# 1. Page Configuration
st.set_page_config(
    page_title="HireSafe AI | Fraud Detection Layer",
    page_icon="🛡️",
    layout="wide"
)

# 2. CSS Injection — pure cosmetic, zero logic changes
st.markdown("""
<style>
/* ── Base & Background ── */
.stApp {
    background: linear-gradient(135deg, #0D1B2A 0%, #0F2D3D 100%);
    font-family: 'Segoe UI', sans-serif;
}

/* ── Header Block ── */
.hiresafe-header {
    background: linear-gradient(90deg, #0D9488 0%, #065A82 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(13,148,136,0.25);
}
.hiresafe-header h1 {
    color: #FFFFFF;
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.5px;
}
.hiresafe-header p {
    color: #CCFBF1;
    font-size: 1rem;
    margin: 0;
    opacity: 0.9;
}

/* ── Input Card ── */
.input-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(13,148,136,0.3);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.input-label {
    color: #0D9488;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Score Cards ── */
.score-card {
    border-radius: 14px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    margin-bottom: 0.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.score-card-danger  { background: linear-gradient(135deg, #7F1D1D, #991B1B); border: 1px solid #EF4444; }
.score-card-warning { background: linear-gradient(135deg, #451A03, #78350F); border: 1px solid #F59E0B; }
.score-card-safe    { background: linear-gradient(135deg, #052E16, #14532D); border: 1px solid #22C55E; }
.score-card-neutral { background: linear-gradient(135deg, #0F2D3D, #1E3A4A); border: 1px solid #0D9488; }
.score-label { color: rgba(255,255,255,0.6); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.4rem; }
.score-value { color: #FFFFFF; font-size: 1.8rem; font-weight: 800; line-height: 1; }
.score-sub   { color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-top: 0.3rem; }

/* ── XAI Section ── */
.xai-header {
    color: #FFFFFF;
    font-size: 1.15rem;
    font-weight: 700;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(13,148,136,0.4);
}

/* ── Flag Cards ── */
.flag-card {
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    font-size: 0.92rem;
    line-height: 1.5;
}
.flag-rule    { background: rgba(245,158,11,0.1); border-left: 3px solid #F59E0B; color: #FDE68A; }
.flag-ml      { background: rgba(99,102,241,0.1); border-left: 3px solid #818CF8; color: #C7D2FE; }
.flag-domain  { background: rgba(13,148,136,0.1); border-left: 3px solid #0D9488; color: #CCFBF1; }
.flag-ai      { background: rgba(236,72,153,0.1); border-left: 3px solid #EC4899; color: #FBCFE8; }
.flag-badge   { font-weight: 700; font-size: 0.78rem; white-space: nowrap; opacity: 0.9; }
.flag-text    { flex: 1; }

/* ── Status Banner ── */
.status-banner-review  { background: rgba(239,68,68,0.15); border: 1px solid #EF4444; border-radius: 10px; padding: 0.9rem 1.2rem; color: #FCA5A5; font-weight: 600; text-align: center; }
.status-banner-clear   { background: rgba(34,197,94,0.12); border: 1px solid #22C55E; border-radius: 10px; padding: 0.9rem 1.2rem; color: #86EFAC; font-weight: 600; text-align: center; }

/* ── Streamlit widget overrides ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(13,148,136,0.4) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-size: 0.95rem !important;
}
.stTextArea textarea:focus {
    border-color: #0D9488 !important;
    box-shadow: 0 0 0 2px rgba(13,148,136,0.2) !important;
}
.stButton > button {
    background: linear-gradient(90deg, #0D9488, #065A82) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 15px rgba(13,148,136,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(13,148,136,0.5) !important;
}
div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
.stSpinner > div { color: #0D9488 !important; }
label { color: #94A3B8 !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

# 3. Header
st.markdown("""
<div class="hiresafe-header">
    <h1>🛡️ HireSafe AI</h1>
    <p>AI-Powered Recruitment Fraud & Job Scam Detector &nbsp;·&nbsp; 4-Layer Detection Engine &nbsp;·&nbsp; Explainable AI</p>
</div>
""", unsafe_allow_html=True)

# 4. Input
job_text = st.text_area(
    "Paste job posting, WhatsApp message, or recruitment email:",
    height=220,
    placeholder="Paste the full job post, WhatsApp text message, or recruitment email here..."
)

if st.button("🔍  Analyze Posting for Risks", type="primary"):
    if not job_text.strip():
        st.warning("Please paste some text to begin validation.")
    else:
        with st.spinner("Running heuristic engine → ML classifier → domain verifier → Gemini AI..."):
            results = analyze_job_description(job_text)

        score = results["final_risk_score"]
        confidence = results["confidence"]
        display_confidence = confidence.replace(" (Fallback)", " ⚡")
        review_needed = results["requires_manual_review"]

        # 5. Score Cards
        col1, col2, col3 = st.columns(3)

        with col1:
            if score >= 70:
                card_class = "score-card-danger"
                score_icon = "🚨"
            elif score >= 40:
                card_class = "score-card-warning"
                score_icon = "⚠️"
            else:
                card_class = "score-card-safe"
                score_icon = "✅"
            st.markdown(f"""
            <div class="score-card {card_class}">
                <div class="score-label">Scam Risk Score</div>
                <div class="score-value">{score_icon} {score} <span style="font-size:1rem;opacity:0.6">/ 100</span></div>
                <div class="score-sub">{"HIGH RISK" if score >= 70 else "MEDIUM RISK" if score >= 40 else "LOW RISK"}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="score-card score-card-neutral">
                <div class="score-label">AI Confidence</div>
                <div class="score-value" style="font-size:1.3rem;">{display_confidence}</div>
                <div class="score-sub">Gemini 2.5 Flash</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if review_needed:
                st.markdown('<div class="status-banner-review">🚨 Requires Institutional<br>Manual Review</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-banner-clear">✅ Automated Verdict<br>Reached</div>', unsafe_allow_html=True)

        # 6. XAI Breakdown
        st.markdown('<div class="xai-header">🔍 Risk Factor Breakdown — Explainable AI</div>', unsafe_allow_html=True)

        if not results["reasons"]:
            st.markdown('<div class="flag-card flag-domain"><span class="flag-text">No suspicious patterns or behavioral signals were identified.</span></div>', unsafe_allow_html=True)
        else:
            for reason in results["reasons"]:
                if reason.startswith("Heuristic:"):
                    text = reason.replace("Heuristic:", "").strip()
                    st.markdown(f'<div class="flag-card flag-rule"><span class="flag-badge">⚙️ RULE ENGINE</span><span class="flag-text">{text}</span></div>', unsafe_allow_html=True)
                elif reason.startswith("Identity Layer:"):
                    text = reason.replace("Identity Layer:", "").strip()
                    st.markdown(f'<div class="flag-card flag-domain"><span class="flag-badge">🌐 DOMAIN VERIFIER</span><span class="flag-text">{text}</span></div>', unsafe_allow_html=True)
                elif reason.startswith("ML Classifier:"):
                    text = reason.replace("ML Classifier:", "").strip()
                    st.markdown(f'<div class="flag-card flag-ml"><span class="flag-badge">📊 ML CLASSIFIER</span><span class="flag-text">{text}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="flag-card flag-ai"><span class="flag-badge">🤖 AI INTUITION</span><span class="flag-text">{reason}</span></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 7. Debug JSON
        with st.expander("🛠️ View Raw Developer Payload (JSON)"):
            st.json(results)