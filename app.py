import streamlit as st

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="TrueFit - AI Resume Matching",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# CUSTOM CSS
# ======================================================
st.markdown("""
    <style>
    /* Hide default Streamlit header */
    .stAppHeader { display: none; }
    
    /* Landing page styling */
    .landing-hero {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 10px;
        margin-bottom: 40px;
    }
    
    .landing-hero h1 {
        font-size: 3.5em;
        font-weight: 900;
        background: linear-gradient(90deg, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .landing-hero p {
        font-size: 1.3em;
        color: #cbd5e1;
        margin-bottom: 30px;
    }
    
    .tagline {
        font-size: 1.1em;
        color: #94a3b8;
        font-style: italic;
        margin-top: 20px;
    }
    
    .cta-container {
        display: flex;
        gap: 20px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 40px;
    }
    
    .cta-card {
        flex: 1;
        min-width: 300px;
        padding: 40px;
        border: 2px solid #334155;
        border-radius: 12px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .cta-card:hover {
        border-color: #60a5fa;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(96, 165, 250, 0.2);
    }
    
    .cta-card h2 {
        font-size: 2em;
        margin-bottom: 15px;
        color: #e2e8f0;
    }
    
    .cta-card p {
        color: #94a3b8;
        font-size: 1.1em;
        margin-bottom: 20px;
    }
    
    .cta-icon {
        font-size: 3em;
        margin-bottom: 20px;
    }
    
    .button-primary {
        background: linear-gradient(90deg, #60a5fa, #34d399);
        color: white;
        padding: 12px 30px;
        border: none;
        border-radius: 8px;
        font-size: 1em;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .button-primary:hover {
        transform: scale(1.05);
    }
    
    .features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 30px;
        margin-top: 60px;
    }
    
    .feature-box {
        padding: 30px;
        background: #1e293b;
        border-radius: 10px;
        border-left: 4px solid #60a5fa;
    }
    
    .feature-box h3 {
        color: #60a5fa;
        margin-bottom: 10px;
    }
    
    .feature-box p {
        color: #cbd5e1;
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================
# LANDING PAGE CONTENT
# ======================================================
st.markdown("""
    <div class="landing-hero">
        <h1>✨ TrueFit</h1>
        <p>AI-Powered Resume Matching Platform</p>
        <p class="tagline">Helping candidates improve. Helping recruiters decide.</p>
    </div>
    """, unsafe_allow_html=True)

# Use columns for CTA buttons
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("""
    <div class="cta-card">
        <div class="cta-icon">📄</div>
        <h2>For Candidates</h2>
        <p>Optimize your resume against job descriptions. Get match scores and AI-powered suggestions to improve your chances.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Get Started as Candidate", key="candidate_btn", use_container_width=True):
        st.switch_page("pages/01_applicant.py")

with col2:
    st.markdown("""
    <div class="cta-card">
        <div class="cta-icon">👥</div>
        <h2>For Recruiters</h2>
        <p>Screen multiple resumes instantly. Get ranked candidates with match scores and AI-generated feedback.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Get Started as Recruiter", key="recruiter_btn", use_container_width=True):
        st.switch_page("pages/02_recruiter.py")

# Features section
st.markdown("---")
st.markdown("## Key Features")

st.markdown("""
    <div class="features">
        <div class="feature-box">
            <h3>🧠 AI-Powered Analysis</h3>
            <p>Uses advanced semantic matching to analyze resumes beyond keyword matching.</p>
        </div>
        <div class="feature-box">
            <h3>📊 Match Scoring</h3>
            <p>Get detailed match scores showing how well your resume aligns with job requirements.</p>
        </div>
        <div class="feature-box">
            <h3>💡 Smart Suggestions</h3>
            <p>Receive actionable, specific recommendations to improve your resume for each role.</p>
        </div>
        <div class="feature-box">
            <h3>⚖️ Legally Compliant</h3>
            <p>Built with compliance in mind. Feedback focuses on skills and experience only.</p>
        </div>
        <div class="feature-box">
            <h3>🔒 Privacy First</h3>
            <p>Your data is processed securely. We don't store or sell your information.</p>
        </div>
        <div class="feature-box">
            <h3>⚡ Fast & Efficient</h3>
            <p>Get results in seconds. Analyze multiple candidates or resumes quickly.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.caption("✨ TrueFit | Making hiring and job search smarter, faster, fairer")