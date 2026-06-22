# 🛡️ HireSafe AI
**AI-Powered Recruitment Fraud & Job Scam Detector**

*Bharat Academix CodeQuest 2026 — Grand Finale Submission*
*Submitted by: Janani Krishnamoorthy | CSE, NMIT Bangalore*

---

HireSafe AI is an automated fraud detection layer that protects students and early-career professionals from sophisticated recruitment scams. It uses a **4-layer hybrid detection engine** — combining heuristic rules, a trained ML classifier, domain identity verification, and Gemini LLM reasoning — returning not just a risk score, but a human-readable, source-labeled breakdown of every flag triggered.

---

## 🚀 Features

- **Heuristic Rule Engine** — Deterministically flags upfront fee requests, WhatsApp-based recruitment with payment language, and public email domains (Gmail/Yahoo) used in place of corporate domains. Zero API cost, zero latency.
- **ML Classifier (TF-IDF + Logistic Regression)** — A scikit-learn model trained on 500 labeled job postings that calculates a probabilistic scam likelihood score independently of the rule engine and LLM.
- **Domain Identity Verification** — Regex extraction of all emails and URLs from the posting, cross-referenced against a curated dictionary of 15 verified Indian corporate domains to catch company impersonation attacks.
- **Explainable AI (XAI) via Gemini 2.5 Flash** — Structured, human-readable breakdown of every risk signal, labeled by source layer (`[Rule Engine]`, `[ML Classifier]`, `[Domain Verifier]`, `[AI Intuition]`), so users learn to recognize scams — not just avoid them.
- **B2B FastAPI Backend** — Production-ready REST API for institutional placement cells to screen postings at scale programmatically.

---

## 🏗️ System Architecture

```
User Input (Job Posting Text)
         │
         ▼
┌──────────────────────────┐
│   Heuristic Rule Engine   │  ← Regex: WhatsApp + fee combos, Gmail domains, upfront payments
└──────────┬───────────────┘
           │ heuristic_score (0–100)
           ▼
┌──────────────────────────┐
│    ML Classifier Layer    │  ← TF-IDF (1–3 ngrams) + Logistic Regression → scam probability %
└──────────┬───────────────┘
           │ ml_probability (0–100)
           ▼
┌──────────────────────────┐
│  Domain Identity Check    │  ← Email/URL extraction → verified corporate domain lookup
└──────────┬───────────────┘
           │ score adjustments: +15 (no domain) / -30 (verified) / +20 (unrecognized)
           ▼
┌──────────────────────────┐
│  Gemini 2.5 Flash (LLM)  │  ← Contextual analysis, strict JSON schema, confidence level
└──────────┬───────────────┘
           │ ai_score (0–100)
           ▼
┌──────────────────────────┐
│    Score Aggregation      │  ← max(heuristic, ml, ai_score) + domain adjustments
└──────────┬───────────────┘
           │
           ▼
  Final Risk Score (0–100)
  XAI Breakdown (labeled by source layer)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend / API | FastAPI + Uvicorn |
| Rule Engine | Python RegEx (deterministic heuristics) |
| ML Classifier | scikit-learn — TF-IDF Vectorizer (1–3 ngrams) + Logistic Regression |
| Domain Verifier | Python RegEx + curated corporate domain dictionary |
| LLM Reasoning | Google Gemini 2.5 Flash (`google-genai`, strict JSON schema output) |
| Model Persistence | joblib (`.pkl` serialization) |

---

## 📁 Project Structure

```
HireSafe_AI/
│
├── app.py                   # Streamlit frontend — UI, XAI breakdown, debug JSON
├── api.py                   # FastAPI B2B backend (POST /api/v1/scan)
├── detector.py              # Core 4-layer analysis pipeline
├── train.py                 # ML classifier training script
├── requirements.txt         # All Python dependencies
├── .env                     # API keys (not committed to repo)
│
├── ml_model/
│   └── scam_classifier.pkl  # Trained TF-IDF + Logistic Regression model
│
└── utils/
    ├── __init__.py
    └── verifier.py          # Domain identity verification module
```

---

## 💻 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/janani21blr-hue/HireSafe_AI.git
cd HireSafe_AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```
Get a free key at: [Google AI Studio](https://aistudio.google.com)

### 4. Train the ML Model (Required on First Run)
```bash
python train.py
```
This generates `ml_model/scam_classifier.pkl`. Run once — no need to retrain unless you modify `train.py`.

### 5. Start the Streamlit UI
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

### 6. (Optional) Start the FastAPI B2B Backend
In a separate terminal:
```bash
uvicorn api:app --reload
```
API docs auto-generated at `http://localhost:8000/docs`

---

## 🧪 Test Cases

### ✅ Legitimate Posting — Expected: 0/100

```
Software Engineering Intern opening at Infosys.
Looking for proficiency in Python and basic database management.
Please submit your official application through our corporate portal at careers.infosys.com
or contact the university recruitment team directly at freshers@infosys.com.
```

**Result:** Score `0/100` | Domain Verified ✅ | Confidence: High | Status: Automated Verdict Reached

---

### 🚨 Scam Posting — Expected: 100/100

```
URGENT HIRING!! Earn 5000 daily liking YouTube videos.
Pay a fully refundable registration fee of Rs. 2000 to secure your spot.
WhatsApp +919876543210 immediately. Contact: officialhr42@gmail.com
```

**Result:** Score `100/100` | Multiple Red Flags Detected 🚨 | Confidence: High | Status: Automated Verdict Reached

---

## 🌐 B2B API — Placement Cell Integration

The FastAPI backend allows colleges and job boards to integrate HireSafe AI programmatically for bulk screening.

**Endpoint:** `POST http://localhost:8000/api/v1/scan`

**Request Body:**
```json
{
  "job_text": "Paste full job posting text here..."
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "final_risk_score": 100,
    "ml_probability_score": 96.4,
    "confidence": "High",
    "reasons": [
      "⚙️ [Rule Engine] Direct WhatsApp contact combined with payment language detected.",
      "⚙️ [Rule Engine] Job posting uses a public domain email (Gmail/Yahoo) instead of a corporate domain.",
      "⚙️ [Rule Engine] Explicit mention of upfront payment or onboarding fees.",
      "📊 [ML Classifier] 96.4% scam probability (TF-IDF + Logistic Regression)",
      "🤖 [AI Intuition] Unrealistic compensation claim with no verifiable company identity.",
      "🤖 [AI Intuition] Requests for financial payment are a confirmed scam indicator."
    ],
    "requires_manual_review": false
  }
}
```

---

## 🗺️ Roadmap

- [x] Phase 1 — Heuristic rule engine + Streamlit UI
- [x] Phase 2 — ML classifier (TF-IDF + Logistic Regression, trained on 500 synthetic samples)
- [x] Phase 3 — Domain identity verification layer (15 verified Indian corporate domains)
- [x] Phase 4 — Gemini 2.5 Flash LLM reasoning + source-labeled XAI breakdown
- [x] Phase 5 — FastAPI B2B REST API backend
- [ ] Phase 6 — Real-world dataset integration (EMSCAD from Kaggle)
- [ ] Phase 7 — Bulk upload + ranked risk queue for placement cells
- [ ] Phase 8 — Browser extension for real-time LinkedIn / Naukri scanning

---

## 👩‍💻 Author

**Janani Krishnamoorthy**
CSE Undergraduate, NMIT Bangalore
[GitHub](https://github.com/janani21blr-hue) | Built for Bharat Academix CodeQuest 2026