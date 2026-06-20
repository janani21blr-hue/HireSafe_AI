import streamlit as st
import json
from detector import analyze_job_description

# 1. Page Configuration & Title
st.set_page_config(
    page_title="HireSafe AI | Fraud Detection Layer",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ HireSafe AI")
st.subheader("AI-Powered Recruitment Fraud & Job Scam Detector")
st.markdown(
    "Paste any suspicious job description, message template, or email offer below "
    "to instantly calculate its fraud probability and map out underlying risk vectors."
)

st.divider()

# 2. Main Interface Layout
job_text = st.text_area(
    "Job Posting / Message Text:",
    height=250,
    placeholder="Paste the full job post, WhatsApp text message, or recruitment email here..."
)

if st.button("Analyze Posting for Risks", type="primary"):
    if not job_text.strip():
        st.warning("Please paste some text to begin validation.")
    else:
        with st.spinner("Executing rule engine, identity verification & AI reasoning layer..."):
            # Call the backend engine we built in detector.py
            results = analyze_job_description(job_text)
            
        st.success("Analysis Complete!")
        
        # 3. Metrics Layout
        score = results["final_risk_score"]
        confidence = results["confidence"]
        review_needed = results["requires_manual_review"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if score >= 70:
                st.error(f"🚨 Scam Risk Score: {score}/100")
            elif score >= 40:
                st.warning(f"⚠️ Scam Risk Score: {score}/100")
            else:
                st.success(f"✅ Scam Risk Score: {score}/100")
                
        with col2:
            st.metric(label="AI Confidence Level", value=confidence)
            
        with col3:
            if review_needed:
                st.info("🚨 Status: Requires Institutional Manual Review")
            else:
                st.metric(label="Status", value="Automated Verdict Reached")
                
        st.divider()
        
        # 4. Explainable AI (XAI) Breakdown - Hackathon Winning Feature
        st.write("### 🔍 Risk Factor Breakdown (Explainable AI)")
        
        if not results["reasons"]:
            st.write("No suspicious patterns or behavioral signals were identified.")
        else:
            for reason in results["reasons"]:
                # Style the different layers so judges see your hybrid approach
                if reason.startswith("Heuristic:"):
                    st.markdown(f"- ⚙️ **[Rule Engine]** {reason.replace('Heuristic:', '').strip()}")
                elif reason.startswith("Identity Layer:"):
                    st.markdown(f"- 🌐 **[Domain Verifier]** {reason.replace('Identity Layer:', '').strip()}")
                else:
                    st.markdown(f"- 🤖 **[AI Intuition]** {reason}")
                    
        st.divider()
        
        # 5. Developer Debug JSON Block
        with st.expander("View Raw Developer Payload (JSON)"):
            st.json(results)