import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ---------------- TITLE ----------------

st.title("📄 AI Resume Analyzer")

st.markdown(
    "Upload your Resume PDF and compare it with a Job Description."
)

# ---------------- SKILLS DATABASE ----------------

TECH_SKILLS = [
    "python", "java", "c++", "html", "css",
    "javascript", "react", "sql", "git",
    "github", "machine learning", "django",
    "flask", "streamlit", "mongodb",
    "mysql", "nodejs", "pandas",
    "numpy", "deep learning", "ai"
]

SOFT_SKILLS = [
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "management",
    "adaptability",
    "critical thinking"
]

# ---------------- PDF TEXT EXTRACTION ----------------

def extract_text_from_pdf(uploaded_file):

    text = ""

    pdf_reader = PdfReader(uploaded_file)

    for page in pdf_reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text

# ---------------- WORD MATCH ----------------

def word_match(text, keyword):

    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'

    return bool(re.search(pattern, text.lower()))

# ---------------- EMAIL EXTRACTOR ----------------

def extract_email(text):

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    matches = re.findall(pattern, text)

    if matches:
        return matches[0]

    return "Not Found"

# ---------------- PHONE EXTRACTOR ----------------

def extract_phone(text):

    pattern = r'[6789]\d{9}'

    matches = re.findall(pattern, text)

    if matches:
        return matches[0]

    return "Not Found"

# ---------------- LINKEDIN EXTRACTOR ----------------

def extract_linkedin(text):

    pattern = r'linkedin\.com/in/[A-Za-z0-9_-]+'

    matches = re.findall(pattern, text)

    if matches:
        return matches[0]

    return "Not Found"

# ---------------- GITHUB EXTRACTOR ----------------

def extract_github(text):

    pattern = r'github\.com/[A-Za-z0-9_-]+'

    matches = re.findall(pattern, text)

    if matches:
        return matches[0]

    return "Not Found"

# ---------------- ROLE DETECTION ----------------

def detect_role(text):

    text = text.lower()

    if "machine learning" in text:
        return "Machine Learning Engineer"

    elif "react" in text or "javascript" in text:
        return "Frontend Developer"

    elif "django" in text or "flask" in text:
        return "Backend Developer"

    elif "sql" in text:
        return "Data Analyst"

    elif "python" in text:
        return "Python Developer"

    else:
        return "General Software Developer"

# ---------------- MAIN ANALYSIS FUNCTION ----------------

def analyze_resume(resume_text, job_description):

    found_skills = [
        skill for skill in TECH_SKILLS
        if word_match(resume_text, skill)
    ]

    found_soft = [
        skill for skill in SOFT_SKILLS
        if word_match(resume_text, skill)
    ]

    score = len(found_skills) * 8 + len(found_soft) * 5

    if score > 100:
        score = 100

    missing_skills = [
        skill for skill in TECH_SKILLS
        if skill not in found_skills
    ]

    # ---------------- JD MATCH ----------------

    matched_keywords = []

    missing_keywords = []

    jd_words = job_description.lower().split()

    for word in jd_words:

        word = word.strip(",.!?()[]{}")

        if len(word) > 3:

            if word.lower() in resume_text.lower():

                matched_keywords.append(word)

            else:

                missing_keywords.append(word)

    total_keywords = len(matched_keywords) + len(missing_keywords)

    if total_keywords > 0:

        match_percent = int(
            (len(matched_keywords) / total_keywords) * 100
        )

    else:

        match_percent = 0

    # ---------------- AI SUGGESTIONS ----------------

    suggestions = []

    if score < 50:

        suggestions.append(
            "Add more technical skills to improve ATS score."
        )

    if len(found_soft) < 2:

        suggestions.append(
            "Add more soft skills like communication and teamwork."
        )

    if "github" not in resume_text.lower():

        suggestions.append(
            "Add your GitHub profile link."
        )

    if "project" not in resume_text.lower():

        suggestions.append(
            "Mention academic or personal projects."
        )

    if len(missing_skills) > 5:

        suggestions.append(
            "Try learning and adding more in-demand technologies."
        )

    return (
        score,
        found_skills,
        found_soft,
        missing_skills,
        matched_keywords,
        missing_keywords,
        match_percent,
        suggestions
    )

# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"]
)

# ---------------- JOB DESCRIPTION ----------------

job_description = st.text_area(
    "Paste Job Description",
    height=200
)

resume = ""

# ---------------- PDF READING ----------------

if uploaded_file is not None:

    resume = extract_text_from_pdf(uploaded_file)

    st.success("Resume Uploaded Successfully!")

    with st.expander("View Extracted Resume Text"):

        st.text_area(
            "Resume Content",
            resume,
            height=250
        )

# ---------------- ANALYZE BUTTON ----------------

if st.button("Analyze Resume"):

    if resume.strip() == "":

        st.warning("Please upload a Resume PDF first.")

    else:

        (
            score,
            tech,
            soft,
            missing,
            matched,
            missing_kw,
            match_percent,
            suggestions

        ) = analyze_resume(
            resume,
            job_description
        )

        # ---------------- DASHBOARD ----------------

        st.subheader("📊 Resume Dashboard")

        col1, col2 = st.columns(2)

        with col1:

            st.write("### ATS Score")

            st.progress(score / 100)

            st.metric(
                label="ATS Score",
                value=f"{score}%"
            )

        with col2:

            st.write("### JD Match")

            st.progress(match_percent / 100)

            st.metric(
                label="JD Match",
                value=f"{match_percent}%"
            )

        # ---------------- STATUS ----------------

        if score >= 70:

            st.success("✅ Strong Resume")

        elif score >= 40:

            st.warning("⚠️ Resume Needs Improvement")

        else:

            st.error("❌ Weak Resume")

        # ---------------- CONTACT INFO ----------------

        email = extract_email(resume)

        phone = extract_phone(resume)

        linkedin = extract_linkedin(resume)

        github = extract_github(resume)

        role = detect_role(resume)

        st.subheader("👤 Candidate Information")

        st.write(f"📧 Email: {email}")

        st.write(f"📱 Phone: {phone}")

        st.write(f"💼 LinkedIn: {linkedin}")

        st.write(f"💻 GitHub: {github}")

        st.write(f"🧠 Detected Role: {role}")

        # ---------------- TECHNICAL SKILLS ----------------

        st.subheader("🛠 Technical Skills Found")

        for skill in tech:

            st.write(f"✅ {skill}")

            st.progress(100)

        # ---------------- SOFT SKILLS ----------------

        st.subheader("🤝 Soft Skills Found")

        for skill in soft:

            st.write(f"✅ {skill}")

            st.progress(80)

        # ---------------- MISSING SKILLS ----------------

        st.subheader("❌ Skills Missing")

        for skill in missing[:10]:

            st.write(f"❌ {skill}")

            st.progress(20)

        # ---------------- MATCHED KEYWORDS ----------------

        st.subheader("🎯 Matched JD Keywords")

        st.write(list(set(matched[:20])))

        # ---------------- MISSING KEYWORDS ----------------

        st.subheader("🚫 Missing JD Keywords")

        st.write(list(set(missing_kw[:20])))

        # ---------------- AI SUGGESTIONS ----------------

        st.subheader("🤖 AI Suggestions")

        for tip in suggestions:

            st.info(tip)

        # ---------------- CHART ----------------

        st.subheader("📈 Skills Analysis Chart")

        chart_data = pd.DataFrame({
            "Category": [
                "Technical Skills",
                "Soft Skills",
                "Missing Skills"
            ],
            "Count": [
                len(tech),
                len(soft),
                len(missing)
            ]
        })

        st.bar_chart(
            chart_data.set_index("Category")
        )

        # ---------------- DOWNLOAD REPORT ----------------

        report = f"""
AI RESUME ANALYSIS REPORT
====================================

ATS SCORE:
{score}/100

JD MATCH:
{match_percent}%

DETECTED ROLE:
{role}

------------------------------------

EMAIL:
{email}

PHONE:
{phone}

LINKEDIN:
{linkedin}

GITHUB:
{github}

------------------------------------

TECHNICAL SKILLS FOUND:
{tech}

SOFT SKILLS FOUND:
{soft}

MISSING SKILLS:
{missing}

MATCHED JD KEYWORDS:
{list(set(matched[:20]))}

MISSING JD KEYWORDS:
{list(set(missing_kw[:20]))}

AI SUGGESTIONS:
{suggestions}
"""

        st.download_button(
            label="📥 Download Full Report",
            data=report,
            file_name="resume_analysis_report.txt",
            mime="text/plain"
        )

# ---------------- FOOTER ----------------

st.markdown("---")

st.caption("Built with Python + Streamlit")