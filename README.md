# 🛡️ HireSafe AI 
**Bharat Academix CodeQuest 2026 - Prototype Submission**

HireSafe AI is an automated verification layer designed to protect students and early-career professionals from sophisticated recruitment fraud. It utilizes a hybrid detection engine combining heuristic rules, domain verification, and Explainable AI (LLMs) to catch scams before financial or data loss occurs.

## 🚀 Features
* **Heuristic Rule Engine:** Instantly flags upfront fee requests, generic emails, and linguistic urgency.
* **Domain Identity Verification:** Cross-references job posting links against a curated dictionary of verified corporate domains (e.g., infosys.com) to prevent clone attacks.
* **Explainable AI (XAI):** Powered by Gemini, providing users with a human-readable, bulleted breakdown of exactly *why* a post was flagged.
* **B2B API:** Includes a FastAPI backend built for institutional placement cells to execute bulk screenings.

## 🛠️ Technology Stack
* **Frontend:** Streamlit 
* **Backend:** FastAPI, Python
* **AI Layer:** Google GenAI SDK (Gemini 2.5 Flash)

