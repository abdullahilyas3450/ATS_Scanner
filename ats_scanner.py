import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List
import io
import fitz  # PyMuPDF

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ATS Scanner Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --border: #1e1e2e;
    --accent: #7c3aed;
    --accent2: #06b6d4;
    --accent3: #f59e0b;
    --text: #e2e8f0;
    --muted: #64748b;
    --success: #10b981;
    --danger: #ef4444;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Mono', monospace;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 1200px; }

/* ── Hero Header ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    margin-bottom: 2rem;
}
.hero-tag {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--accent2);
    border: 1px solid var(--accent2);
    padding: 0.3rem 0.8rem;
    margin-bottom: 1.5rem;
    opacity: 0.8;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 800;
    line-height: 1.05;
    margin: 0 0 1rem;
    background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p {
    color: var(--muted);
    font-size: 0.95rem;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── Input Cards ── */
.input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.input-card:hover { border-color: var(--accent); }
.card-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent2);
    margin-bottom: 0.5rem;
}

/* ── Score Ring ── */
.score-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    margin-bottom: 1.5rem;
}
.score-ring {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
}
.score-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
}

/* ── Result Sections ── */
.result-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* ── Skill Tags ── */
.skill-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.skill-tag {
    padding: 0.35rem 0.75rem;
    border-radius: 4px;
    font-size: 0.78rem;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    letter-spacing: 0.02em;
}
.skill-matched {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #6ee7b7;
}
.skill-missing {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
}

/* ── Suggestion Box ── */
.suggestion-text {
    font-size: 0.9rem;
    line-height: 1.8;
    color: #cbd5e1;
    padding: 1rem;
    background: rgba(124, 58, 237, 0.06);
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
}

/* ── Streamlit overrides ── */
.stTextArea textarea {
    background: #0d0d16 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    resize: vertical;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
}
.stTextInput input {
    background: #0d0d16 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
}
label { color: var(--muted) !important; font-size: 0.8rem !important; }

/* ── Analyze Button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, var(--accent) 0%, #5b21b6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.85rem !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    margin-top: 1rem;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
}

/* divider */
hr { border-color: var(--border) !important; margin: 2rem 0 !important; }

/* ── File Uploader ── */
.stFileUploader {
    background: #0d0d16 !important;
    border: 1px dashed #2d2d44 !important;
    border-radius: 8px !important;
    transition: border-color 0.2s;
}
.stFileUploader:hover { border-color: var(--accent) !important; }
.stFileUploader label { color: var(--muted) !important; }
[data-testid="stFileUploaderDropzone"] {
    background: #0d0d16 !important;
    border: 1px dashed #2d2d44 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    color: var(--muted) !important;
    font-size: 0.8rem !important;
}

/* ── PDF Preview Badge ── */
.pdf-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(6, 182, 212, 0.1);
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 6px;
    padding: 0.4rem 0.8rem;
    font-size: 0.75rem;
    color: #67e8f9;
    margin-top: 0.5rem;
}

/* spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ─── Pydantic Model ────────────────────────────────────────────────────────────
class ATS(BaseModel):
    ATS_Score: int = Field(..., description="ATS score for the resume out of 100")
    Skills_missing: List[str] = Field(..., description="Skills missing in the resume according to the job description")
    skills_matched: List[str] = Field(..., description="Skills that match the job description")
    suggestion: str = Field(..., description="Suggestions to improve the resume for this job")

# ─── Prompt Template ──────────────────────────────────────────────────────────
template_string = """
You are an experienced HR recruiter and ATS (Applicant Tracking System) evaluator.

Your task is to analyze how well a candidate's resume matches a given job description.

Job Description:
{JD}

Candidate Resume:
{resume}

Instructions:
1. Carefully compare the resume with the job description.
2. Identify important skills, technologies, and qualifications required for the job.
3. Check whether the resume contains those skills or related experience.
4. Evaluate the candidate on the following criteria:
   - Technical Skills Match
   - Relevant Experience
   - Education
   - Tools & Technologies
   - Overall Job Fit
"""
prompt_template = ChatPromptTemplate.from_template(template_string)

# ─── Score Styling ─────────────────────────────────────────────────────────────
def get_score_style(score: int):
    if score >= 75:
        return "#10b981", "#052e16", "STRONG MATCH"
    elif score >= 50:
        return "#f59e0b", "#1c1203", "MODERATE MATCH"
    else:
        return "#ef4444", "#1f0707", "WEAK MATCH"

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">AI-Powered Resume Analysis</div>
    <h1>ATS Scanner Pro</h1>
    <p>Instantly evaluate how well your resume matches any job description. Get a score, gap analysis, and actionable improvements.</p>
</div>
""", unsafe_allow_html=True)

# ─── Layout ───────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="card-label">API Configuration</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        help="Your Google AI Studio API key"
    )

    st.markdown('<div class="card-label" style="margin-top:1.5rem;">Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste the full job description",
        height=220,
        placeholder="We are looking for a Senior Software Engineer with experience in Python, distributed systems...",
        label_visibility="collapsed"
    )

    st.markdown('<div class="card-label" style="margin-top:1.5rem;">Resume (PDF)</div>', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader(
        "Upload your resume as PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Upload your resume in PDF format"
    )

    resume_text = ""
    if uploaded_pdf is not None:
        try:
            pdf_bytes = uploaded_pdf.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            resume_text = "\n".join(page.get_text() for page in doc)
            doc.close()
            page_count = fitz.open(stream=pdf_bytes, filetype="pdf").page_count
            st.markdown(f"""
            <div class="pdf-badge">
                📄 {uploaded_pdf.name} &nbsp;·&nbsp; {page_count} page{"s" if page_count != 1 else ""} &nbsp;·&nbsp; {len(resume_text.split())} words extracted
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")

    analyze_btn = st.button("⚡ Analyze Resume")

# ─── Analysis Logic ────────────────────────────────────────────────────────────
with right:
    if analyze_btn:
        if not api_key:
            st.error("⚠️ Please enter your Google Gemini API key.")
        elif not job_description.strip():
            st.error("⚠️ Please paste a job description.")
        elif not resume_text.strip():
            st.error("⚠️ Please upload a valid PDF resume.")
        else:
            with st.spinner("Analyzing your resume…"):
                try:
                    model = ChatGoogleGenerativeAI(
                        model="gemini-3-flash-preview",
                        temperature=0.3,
                        max_tokens=None,
                        timeout=None,
                        max_retries=2,
                        api_key=api_key,
                    )
                    structured_model = model.with_structured_output(ATS)
                    messages = prompt_template.format_messages(
                        JD=job_description,
                        resume=resume_text
                    )
                    result: ATS = structured_model.invoke(messages)

                    score = result.ATS_Score
                    color, bg_color, verdict = get_score_style(score)

                    # Score Ring
                    st.markdown(f"""
                    <div class="score-container">
                        <div class="score-ring" style="
                            background: conic-gradient({color} {score * 3.6}deg, #1e1e2e {score * 3.6}deg);
                            box-shadow: 0 0 40px {color}33;
                        ">
                            <div style="
                                width: 120px; height: 120px;
                                border-radius: 50%;
                                background: var(--surface);
                                display: flex; flex-direction: column;
                                align-items: center; justify-content: center;
                            ">
                                <span style="color: {color}; font-size: 2.2rem; font-family: 'Syne', sans-serif; font-weight: 800; line-height: 1;">{score}</span>
                                <span style="color: var(--muted); font-size: 0.6rem; letter-spacing: 0.1em;">/100</span>
                            </div>
                        </div>
                        <div class="score-label" style="color: {color};">{verdict}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Matched Skills
                    if result.skills_matched:
                        matched_tags = "".join([
                            f'<span class="skill-tag skill-matched">✓ {s}</span>'
                            for s in result.skills_matched
                        ])
                        st.markdown(f"""
                        <div class="result-section">
                            <div class="section-header" style="color: #10b981;">✓ Matched Skills ({len(result.skills_matched)})</div>
                            <div class="skill-grid">{matched_tags}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Missing Skills
                    if result.Skills_missing:
                        missing_tags = "".join([
                            f'<span class="skill-tag skill-missing">✗ {s}</span>'
                            for s in result.Skills_missing
                        ])
                        st.markdown(f"""
                        <div class="result-section">
                            <div class="section-header" style="color: #ef4444;">✗ Missing Skills ({len(result.Skills_missing)})</div>
                            <div class="skill-grid">{missing_tags}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Suggestions
                    st.markdown(f"""
                    <div class="result-section">
                        <div class="section-header" style="color: #a78bfa;">💡 How to Improve</div>
                        <div class="suggestion-text">{result.suggestion}</div>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"**Analysis failed:** {str(e)}")
                    st.info("💡 Tip: Make sure your API key is valid and has access to Gemini models.")
    else:
        # Placeholder state
        st.markdown("""
        <div style="
            height: 100%;
            min-height: 500px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--surface);
            border: 1px dashed var(--border);
            border-radius: 16px;
            padding: 3rem;
            text-align: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1.5rem;">🎯</div>
            <div style="font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem;">
                Ready to Analyze
            </div>
            <div style="color: var(--muted); font-size: 0.82rem; line-height: 1.7; max-width: 280px;">
                Fill in your API key, job description, and upload your <strong style="color: var(--accent2);">PDF resume</strong> on the left — then hit <strong style="color: var(--accent);">Analyze Resume</strong> to get your ATS score.
            </div>
            <div style="margin-top: 2rem; display: flex; gap: 2rem;">
                <div style="text-align: center;">
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #10b981;">ATS</div>
                    <div style="font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em;">Score</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #06b6d4;">GAP</div>
                    <div style="font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em;">Analysis</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #a78bfa;">TIPS</div>
                    <div style="font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em;">To Improve</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem; color: #334155; font-size: 0.72rem; letter-spacing: 0.05em;">
    POWERED BY GOOGLE GEMINI + LANGCHAIN · ATS SCANNER PRO
</div>
""", unsafe_allow_html=True)