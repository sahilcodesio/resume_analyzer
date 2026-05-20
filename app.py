import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd
import plotly.graph_objects as go

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

# FIX 1: Added @st.cache_data so PDF is not re-read on every button click

@st.cache_data
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

# FIX 2: Changed regex to support international numbers, not just Indian

def extract_phone(text):

    pattern = r'(\+?\d[\d\s\-().]{7,}\d)'

    matches = re.findall(pattern, text)

    if matches:
        return matches[0].strip()

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

    # FIX 3: ATS Score now based on JD overlap instead of fixed points
    # We check which skills are mentioned in JD, then see how many are in resume

    jd_skills = [
        skill for skill in TECH_SKILLS
        if word_match(job_description, skill)
    ]

    if jd_skills:
        matched_jd_skills = [
            s for s in jd_skills
            if word_match(resume_text, s)
        ]
        score = int((len(matched_jd_skills) / len(jd_skills)) * 100)

    else:
        # Fallback if no JD provided
        score = min(len(found_skills) * 8 + len(found_soft) * 5, 100)

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

        # FIX 4: Replaced meaningless st.progress(100) with colored skill badges

        st.subheader("🛠 Technical Skills Found")

        if tech:
            badges = " ".join([
                f'<span style="background:#1f77b4;color:white;padding:4px 12px;border-radius:12px;margin:3px;display:inline-block">{skill}</span>'
                for skill in tech
            ])
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.info("No technical skills found.")

        # ---------------- SOFT SKILLS ----------------

        st.subheader("🤝 Soft Skills Found")

        if soft:
            badges = " ".join([
                f'<span style="background:#2ecc71;color:white;padding:4px 12px;border-radius:12px;margin:3px;display:inline-block">{skill}</span>'
                for skill in soft
            ])
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.info("No soft skills found.")

        # ---------------- MISSING SKILLS ----------------

        st.subheader("❌ Skills Missing")

        if missing:
            badges = " ".join([
                f'<span style="background:#e74c3c;color:white;padding:4px 12px;border-radius:12px;margin:3px;display:inline-block">{skill}</span>'
                for skill in missing[:10]
            ])
            st.markdown(badges, unsafe_allow_html=True)

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

        # FIX 5: Replaced bar chart with Plotly donut chart

        st.subheader("📈 Skills Analysis Chart")

        fig = go.Figure(data=[go.Pie(
            labels=["Technical Skills", "Soft Skills", "Missing Skills"],
            values=[len(tech), len(soft), len(missing)],
            hole=0.4,
            marker=dict(colors=["#2ecc71", "#3498db", "#e74c3c"])
        )])

        fig.update_layout(height=350, margin=dict(t=20, b=20))

        st.plotly_chart(fig, use_container_width=True)

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
