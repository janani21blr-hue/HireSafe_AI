import os
import re
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types

# Import your new verifier module
from utils.verifier import verify_company_identity

# 1. Load the API key from your .env file
load_dotenv()

# 2. Initialize the Gemini Client
client = genai.Client()

# 3. Heuristic Rule Engine (Instant, Cost-Zero Check)
def run_heuristic_check(text: str) -> dict:
    """
    Scans for obvious local red flags instantly using regex.
    """
    red_flags = []
    score_increment = 0
    
    # Check for direct suspicious contact methods
    if re.search(r'\+91[-\s]?\d{10}', text) or re.search(r'WhatsApp', text, re.IGNORECASE):
        if re.search(r'(advance|deposit|fee|pay|money|security)', text, re.IGNORECASE):
            red_flags.append("Heuristic: Direct WhatsApp contact combined with payment language detected.")
            score_increment += 40

    # Check for generic emails masking as corporate
    if re.search(r'@[gG]mail\.com|@[yY]ahoo\.com|@outlook\.com', text):
        red_flags.append("Heuristic: Job posting uses a public domain email (Gmail/Yahoo) instead of a corporate domain.")
        score_increment += 30
        
    # Check for upfront payment keywords
    if re.search(r'(registration fee|security deposit|laptop charges|training fee)', text, re.IGNORECASE):
        red_flags.append("Heuristic: Explicit mention of upfront payment or onboarding fees.")
        score_increment += 50

    return {
        "heuristic_score": min(score_increment, 100),
        "heuristic_reasons": red_flags
    }

# 4. Define the Strict Output Schema for Gemini
class JobAnalysisSchema(BaseModel):
    scam_score: int
    confidence_level: str  
    ai_reasons: list[str]
    is_ambiguous: bool

# 5. Main Analyzer Pipeline
def analyze_job_description(job_text: str) -> dict:
    """
    Combines the heuristic rule engine, domain verification, and Gemini LLM analysis.
    """
    # Run linguistics heuristics
    heuristics = run_heuristic_check(job_text)
    
    # Run identity verification check
    domain_results = verify_company_identity(job_text)
    
    system_instruction = (
        "You are an expert cybersecurity analyst specializing in recruitment fraud and employment scams. "
        "Analyze the provided job description for red flags such as linguistic urgency, lack of specific qualifications, "
        "unrealistic compensation bounds, anonymous or cloned branding, and phishing indicators. "
        "Provide a risk rating from 0 (completely safe) to 100 (confirmed scam) and bulletproof, human-readable explanations."
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Analyze this job posting text:\n\n{job_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=JobAnalysisSchema,
                temperature=0.1, 
            ),
        )
        ai_analysis = json.loads(response.text)
        
    except Exception as e:
        ai_analysis = {
            "scam_score": heuristics["heuristic_score"],
            "confidence_level": "Medium (Fallback)",
            "ai_reasons": ["AI Layer timeout or connection error. Displaying rule-engine flags only."],
            "is_ambiguous": True
        }

    # Combine linguistic heuristics and AI scores
    base_score = max(heuristics["heuristic_score"], ai_analysis["scam_score"])
    all_reasons = heuristics["heuristic_reasons"] + ai_analysis["ai_reasons"]
    
    # Apply Domain Identity Verification Weights
    if domain_results["status"] == "NO_DOMAIN":
        # No email or website link found increases risk slightly if it wasn't already maxed out
        base_score = min(base_score + 15, 100)
        all_reasons.append(domain_results["message"])
    else:
        for msg in domain_results["messages"]:
            all_reasons.append(f"Identity Layer: {msg}")
            # If an official corporate domain is verified, give a significant safety credit
            if "✅ Identity Verified:" in msg:
                base_score = max(base_score - 30, 0)
            # If an unverified domain is used, add minor penalty
            if "⚠️ Unrecognized Domain:" in msg:
                base_score = min(base_score + 20, 100)

    return {
        "final_risk_score": int(base_score),
        "confidence": ai_analysis["confidence_level"],
        "reasons": all_reasons,
        "requires_manual_review": ai_analysis["is_ambiguous"] or (40 < base_score < 70)
    }

# --- QUICK TEST EXECUTION ---
if __name__ == "__main__":
    # Test with a mock safe email matching our verification dictionary
    sample_safe = """
    Software Engineering Intern opening at Infosys.
    Looking for proficiency in Python and basic database management.
    Please submit your official application through our corporate portal at careers.infosys.com 
    or contact the university recruitment team directly at freshers@infosys.com.
    """
    
    print("🔄 Running verification pipeline with Identity Check...\n")
    result = analyze_job_description(sample_safe)
    print(json.dumps(result, indent=2))