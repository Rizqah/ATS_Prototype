import streamlit as st
from styles import inject_global_css

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="TrueFit - AI Resume Matching",
    page_icon="TF",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject global CSS stylesheet
inject_global_css()

# Initialize session state
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ======================================================
# CUSTOM CSS (LANDING PAGE SPECIFIC)
# ======================================================
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }

    .lp-hero {
        background:
            linear-gradient(120deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%),
            url('https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1800&q=80');
        background-size: cover;
        background-position: center;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 44px 38px;
        margin-bottom: 24px;
        box-shadow: 0 18px 36px rgba(2, 6, 23, 0.35);
    }

    .lp-badge {
        display: inline-block;
        background: rgba(96, 165, 250, 0.18);
        color: #bfdbfe;
        border: 1px solid rgba(96, 165, 250, 0.35);
        border-radius: 999px;
        padding: 6px 12px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.4px;
        margin-bottom: 12px;
    }

    .lp-title {
        color: #f8fafc;
        font-size: clamp(2rem, 4vw, 3.1rem);
        line-height: 1.08;
        margin: 0;
        font-weight: 900;
    }

    .lp-sub {
        color: #cbd5e1;
        margin-top: 14px;
        font-size: 1.04rem;
        max-width: 56ch;
        line-height: 1.6;
        font-weight: 500;
    }

    .lp-chip-row {
        margin-top: 18px;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .lp-chip {
        background: rgba(148, 163, 184, 0.18);
        color: #e2e8f0;
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 999px;
        padding: 5px 11px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .lp-panel {
        background: rgba(15, 23, 42, 0.58);
        border: 1px solid rgba(100, 116, 139, 0.4);
        border-radius: 14px;
        padding: 16px;
    }

    .lp-panel-title {
        color: #e2e8f0;
        font-size: 0.9rem;
        margin-bottom: 10px;
        font-weight: 700;
    }

    .lp-kpi-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
    }

    .lp-kpi {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(96, 165, 250, 0.28);
        border-radius: 10px;
        padding: 10px;
    }

    .lp-kpi-val {
        color: #eb3a34;
        font-size: 1.05rem;
        font-weight: 800;
        margin: 0;
    }

    .lp-kpi-lbl {
        color: #93c5fd;
        font-size: 0.72rem;
        margin: 2px 0 0 0;
        font-weight: 600;
    }

    .lp-section-title {
        color: #e2e8f0;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 6px 0 14px 0;
    }

    .lp-card {
        border: 1px solid #334155;
        border-radius: 14px;
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        padding: 28px 24px;
        min-height: 220px;
        transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    }

    .lp-card:hover {
        transform: translateY(-3px);
        border-color: #60a5fa;
        box-shadow: 0 14px 24px rgba(30, 64, 175, 0.18);
    }

    .lp-card h3 {
        color: #f8fafc;
        margin: 0 0 10px 0;
        font-size: 1.55rem;
        font-weight: 800;
    }

    .lp-card p {
        color: #cbd5e1;
        font-size: 1rem;
        line-height: 1.58;
        margin: 0;
        font-weight: 500;
    }

    .lp-features {
        margin-top: 8px;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
    }

    .lp-feature {
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        background: #1e293b;
        padding: 16px;
    }

    .lp-feature h4 {
        color: #eb3a34;
        font-size: 1rem;
        margin: 0 0 6px 0;
        font-weight: 700;
    }

    .lp-feature p {
        color: #cbd5e1;
        margin: 0;
        font-size: 0.92rem;
        line-height: 1.5;
        font-weight: 500;
    }

    .lp-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.88rem;
        margin-top: 18px;
        font-weight: 600;
    }

    @media (max-width: 900px) {
        .lp-kpi-grid,
        .lp-features {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================================================
# HERO
# ======================================================
hero_left, hero_right = st.columns([1.45, 1], gap="large")

with hero_left:
    st.markdown(
        """
        <div class="lp-hero">
            <div class="lp-badge">PROFESSIONAL HIRING PLATFORM</div>
            <h1 class="lp-title">TrueFit</h1>
            <p class="lp-sub">
                AI-powered resume matching for candidates and recruiters.
                Improve application quality, rank talent faster, and make decisions with confidence.
            </p>
            <div class="lp-chip-row">
                <span class="lp-chip">Semantic Matching</span>
                <span class="lp-chip">Clear Insights</span>
                <span class="lp-chip">Recruiter Workflow</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_right:
    st.markdown(
        """
        <div class="lp-panel">
            <div class="lp-panel-title">Platform Snapshot</div>
            <div class="lp-kpi-grid">
                <div class="lp-kpi">
                    <p class="lp-kpi-val">300+</p>
                    <p class="lp-kpi-lbl">Analyses</p>
                </div>
                <div class="lp-kpi">
                    <p class="lp-kpi-val">50+</p>
                    <p class="lp-kpi-lbl">Recruiters</p>
                </div>
                <div class="lp-kpi">
                    <p class="lp-kpi-val">1000+</p>
                    <p class="lp-kpi-lbl">Matches</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ======================================================
# CTA
# ======================================================
st.markdown('<h2 class="lp-section-title">Choose Your Workflow</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown(
        """
        <div class="lp-card">
            <h3>For Candidates</h3>
            <p>
                Benchmark your resume against job descriptions and get targeted suggestions
                to improve match strength before you apply.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Get Started as Candidate", key="candidate_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/03_careerhub_auth.py")

with col2:
    st.markdown(
        """
        <div class="lp-card">
            <h3>For Recruiters</h3>
            <p>
                Process multiple resumes, rank candidates instantly, and generate structured
                feedback to support hiring decisions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Get Started as Recruiter", key="recruiter_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/02_recruiter.py")

# ======================================================
# FEATURES
# ======================================================
st.markdown('<h2 class="lp-section-title">Core Capabilities</h2>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="lp-features">
        <div class="lp-feature">
            <h4>AI Analysis</h4>
            <p>Evaluates resumes using semantic context, not only keywords.</p>
        </div>
        <div class="lp-feature">
            <h4>Match Scoring</h4>
            <p>Clear score breakdowns for quick understanding and action.</p>
        </div>
        <div class="lp-feature">
            <h4>Actionable Guidance</h4>
            <p>Practical suggestions tailored to each role and profile.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="lp-footer">TrueFit | Making hiring and job search smarter</div>', unsafe_allow_html=True)
