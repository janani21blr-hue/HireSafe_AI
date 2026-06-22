import os
import re
import random
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

print("⚙️ Initializing Production ML Training Sequence...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'fake_job_postings.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'ml_model')
MODEL_PATH = os.path.join(MODEL_DIR, 'scam_classifier.pkl')

# --- HTML STRIPPER ---
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ── REAL DATA LOADER ──────────────────────────────────────────────────────────
def load_real_data(path):
    print("⏳ Loading CSV and stripping HTML... (This may take a few seconds)")
    df = pd.read_csv(path)

    text_cols = ['title', 'company_profile', 'description', 'requirements', 'benefits']
    for col in text_cols:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].fillna('')

    df['combined_text'] = df[text_cols].apply(lambda row: ' '.join(row.values), axis=1)
    df['combined_text'] = df['combined_text'].apply(clean_text)

    print(f"📊 Real Dataset Loaded: {len(df)} total records")
    print(f"   ✅ Legitimate postings : {(df['fraudulent'] == 0).sum()}")
    print(f"   🚨 Fraudulent postings : {(df['fraudulent'] == 1).sum()}")

    return df['combined_text'], df['fraudulent']

# ── SYNTHETIC FALLBACK ────────────────────────────────────────────────────────
def load_synthetic_data():
    print("⚠️  Real dataset not found — using synthetic fallback.")
    print(f"   Place fake_job_postings.csv from Kaggle at:\n   {DATA_PATH}\n")

    safe_templates = [
        "{role} position available at {company}. Looking for candidates with strong skills in {skill}. {perk}. {ending}",
        "Join {company} as a {role}. Must have 2+ years experience in {skill}. {ending}",
        "We are hiring a {role}. Ideal candidates possess deep knowledge of {skill} and strong teamwork. {perk}. {ending}",
        "{company} is seeking a motivated {role}. Core requirements include {skill}. {ending}",
        "Exciting opportunity for a {role} at {company}. {skill} expertise required. {perk}. {ending}",
        "Opening for {role} at {company}. We need someone proficient in {skill}. {perk}. {ending}",
        "{company} is expanding its {role} team. If you have strong {skill} skills, we want you. {ending}",
    ]
    scam_templates = [
        "{hook} {action} {contact}",
        "Immediate opening! {hook} {action}. Reach out today: {contact}",
        "{hook} You have been selected for a premium role. {action} {contact}",
        "No interview required. {action} Send details to {contact}",
        "{hook} Guaranteed income from home. {action} Apply now: {contact}",
        "Work from home opportunity. {hook} {action} Limited slots! {contact}",
        "Earn money online easily. {hook} {action} {contact}",
    ]

    roles     = ["Software Engineer", "Data Analyst", "Marketing Manager", "HR Executive",
                 "System Admin", "Product Manager", "Business Analyst", "DevOps Engineer",
                 "QA Engineer", "Frontend Developer"]
    companies = ["Infosys", "TCS", "Wipro", "Amazon", "Google", "Tech Mahindra",
                 "Microsoft", "Accenture", "Deloitte", "IBM", "Capgemini", "Cognizant"]
    skills    = ["Python", "Java", "SQL", "React", "Data Analysis", "AWS",
                 "Project Management", "Agile methodologies", "Machine Learning",
                 "Cloud Computing", "REST APIs", "Kubernetes"]
    perks     = ["Comprehensive health benefits included", "Stock options available",
                 "Relocation assistance provided", "Generous PTO policy", "Annual bonus included",
                 "Hybrid work model", "Learning & development budget provided"]
    endings   = ["Apply via our official corporate portal.",
                 "Submit your resume directly to our verified HR team.",
                 "Applications accepted only through the company website.",
                 "Send your CV to our recruitment team at careers@company.com.",
                 "Visit our careers page to apply.",
                 "Shortlisted candidates will be contacted within 5 business days."]
    hooks     = ["Urgent Hiring!!", "Work from home data entry job.",
                 "100% remote guaranteed job.", "Massive salary for freshers.",
                 "No experience needed, earn daily.", "Earn Rs. 5000 daily from home.",
                 "Part-time job, no qualification needed."]
    actions   = ["Pay a fully refundable registration fee of Rs. 2000.",
                 "Transfer the portal training fee.",
                 "Buy our starter kit and start earning immediately.",
                 "Secure your company laptop with a small security deposit.",
                 "Pay onboarding charges to activate your account.",
                 "Register by paying a nominal fee to confirm your slot."]
    contacts  = ["WhatsApp +919876543210 immediately.",
                 "Contact officialhr42@gmail.com.",
                 "DM us your bank details on Telegram.",
                 "Message our recruiter on WhatsApp now.",
                 "Call us now — limited slots available.",
                 "Reach us at hiring_team99@yahoo.com."]

    texts, labels = [], []
    for _ in range(350):
        t = random.choice(safe_templates).format(
            role=random.choice(roles), company=random.choice(companies),
            skill=random.choice(skills), perk=random.choice(perks),
            ending=random.choice(endings)
        )
        texts.append(t)
        labels.append(0)
    for _ in range(350):
        t = random.choice(scam_templates).format(
            hook=random.choice(hooks), action=random.choice(actions),
            contact=random.choice(contacts)
        )
        texts.append(t)
        labels.append(1)

    print(f"📊 Synthetic Dataset: {len(texts)} records generated (350 legit + 350 scam)")
    return pd.Series(texts), pd.Series(labels)


# ── LOAD ──────────────────────────────────────────────────────────────────────
if os.path.exists(DATA_PATH):
    print(f"✅ Real dataset found at: {DATA_PATH}")
    X, y = load_real_data(DATA_PATH)
else:
    X, y = load_synthetic_data()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── TRAIN ─────────────────────────────────────────────────────────────────────
print("\n🧠 Training TF-IDF + Logistic Regression Classifier...")
pipeline = make_pipeline(
    TfidfVectorizer(
        stop_words='english',
        lowercase=True,
        ngram_range=(1, 3),
        max_features=10000,
        sublinear_tf=True
    ),
    LogisticRegression(
        class_weight='balanced',
        max_iter=1000,
        C=1.0
    )
)

pipeline.fit(X_train, y_train)

# ── EVALUATE ──────────────────────────────────────────────────────────────────
predictions = pipeline.predict(X_test)
print("\n📈 Model Evaluation on Unseen Test Data:")
print(classification_report(y_test, predictions, target_names=['Legitimate (0)', 'Fraudulent (1)']))

# ── SAVE ──────────────────────────────────────────────────────────────────────
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)
print(f"\n✅ Model saved to: {MODEL_PATH}")
