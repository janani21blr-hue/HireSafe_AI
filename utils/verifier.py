import re

# Claude's dictionary is solid. We keep it.
VERIFIED_DOMAINS = {
    "infosys.com": "Infosys",
    "tcs.com": "Tata Consultancy Services",
    "wipro.com": "Wipro",
    "hcltech.com": "HCL Technologies",
    "accenture.com": "Accenture",
    "google.com": "Google",
    "microsoft.com": "Microsoft",
    "amazon.com": "Amazon",
    "flipkart.com": "Flipkart",
    "zomato.com": "Zomato",
    "swiggy.com": "Swiggy",
    "razorpay.com": "Razorpay",
    "paytm.com": "Paytm",
    "myntra.com": "Myntra",
    "meesho.com": "Meesho",
}

def extract_domains_from_text(text: str) -> list:
    """
    Scans the raw job description and extracts any email domains or website URLs.
    """
    # Find all emails (e.g., hr@infosys.com -> extracts infosys.com)
    email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    
    # Find all URLs (e.g., https://careers.tcs.com -> extracts careers.tcs.com)
    url_matches = re.findall(r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    
    # Combine and remove duplicates
    all_domains = list(set(email_matches + url_matches))
    return [d.lower() for d in all_domains]

def verify_company_identity(text: str) -> dict:
    """
    The main function we will call from our backend.
    """
    extracted_domains = extract_domains_from_text(text)
    
    if not extracted_domains:
        return {
            "status": "NO_DOMAIN",
            "message": "⚠️ No official corporate email or website link found in the posting. High risk for freshers."
        }
        
    results = []
    for domain in extracted_domains:
        # Basic check to handle subdomains (e.g., careers.infosys.com)
        matched_company = None
        for verified_domain, company_name in VERIFIED_DOMAINS.items():
            if verified_domain in domain:
                matched_company = company_name
                break
                
        if matched_company:
            results.append(f"✅ Identity Verified: Linked to official {matched_company} domain ({domain}).")
        else:
            # Ignore public email providers here since our heuristic engine already flags Gmail/Yahoo
            if "gmail" not in domain and "yahoo" not in domain and "outlook" not in domain:
                 results.append(f"⚠️ Unrecognized Domain: '{domain}' is not in our verified corporate database.")
            
    return {
        "status": "CHECKED",
        "messages": results
    }