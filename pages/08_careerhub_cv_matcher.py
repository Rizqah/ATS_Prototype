import streamlit as st
import sys
import os

# ======================================================
# PATH SETUP
# ======================================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# ======================================================
# IMPORTS
# ======================================================
from careerhub_db import (
    get_profile,
    get_work_experience,
    get_achievements,
    get_skills,
)
from ats_engine import extract_text_from_pdf, match_profile_to_jd
from ui_components import show_top_navigation

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="TrueFit - Check CV Match",
    page_icon="🎯",
    layout="wide"
)

# ======================================================
# AUTH CHECK
# ======================================================
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Please log in first")
    st.switch_page("pages/03_careerhub_auth.py")

user_email = st.session_state.user_email
show_top_navigation("CV Match")

# ======================================================
# HEADER
# ======================================================
st.title("🎯 Check Your CV Match")
st.caption("See how your profile matches a job description")

# ======================================================
# LOAD PROFILE DATA
# ======================================================
profile = get_profile(user_email).get("profile", {})
work_experiences = get_work_experience(user_email).get("experiences", [])
skills = get_skills(user_email).get("skills", [])

# ======================================================
# PROFILE COMPLETENESS CHECK
# ======================================================
if not work_experiences or len(skills) < 1:
    st.warning(
        "⚠️ Your profile is incomplete.\n\n"
        "You need at least:\n"
        "- 1 work experience\n"
        "- 1 skill"
    )

    if st.button("👤 Complete Profile"):
        st.switch_page("pages/05_careerhub_profile.py")

    st.stop()

# ======================================================
# JOB DESCRIPTION INPUT
# ======================================================
st.header("1️⃣ Provide Job Description")

jd_source = st.radio(
    "How would you like to provide the job description?",
    ["Paste Text", "Upload PDF"],
    horizontal=True
)

job_description = ""

if jd_source == "Paste Text":
    job_description = st.text_area(
        "Paste the job description",
        height=250,
        placeholder="Job title, responsibilities, requirements, qualifications..."
    )
else:
    jd_file = st.file_uploader("Upload job description (PDF)", type=["pdf"])
    if jd_file:
        with st.spinner("📖 Extracting text from PDF..."):
            try:
                job_description = extract_text_from_pdf(jd_file)
                st.success("✅ Job description extracted successfully")
            except Exception as e:
                st.error(f"❌ Error extracting PDF: {str(e)}")

# ======================================================
# ANALYZE MATCH
# ======================================================
st.header("2️⃣ Analyze Your Match")

if st.button("🔍 Check Match", type="primary", use_container_width=True):
    if not job_description.strip():
        st.error("❌ Please provide a job description")
        st.stop()

    with st.spinner("🔄 Analyzing your profile against the job..."):
        try:
            # Build complete profile data
            achievements_by_exp = {}
            for exp in work_experiences:
                achievements_by_exp[exp["id"]] = (
                    get_achievements(exp["id"]).get("achievements", [])
                )

            # Run matching engine
            match_result = match_profile_to_jd(
                profile=profile,
                work_experiences=work_experiences,
                achievements_by_experience=achievements_by_exp,
                skills=skills,
                job_description=job_description
            )

            # Store in session
            st.session_state.match_score = match_result["match_score"]
            st.session_state.match_analysis = match_result["analysis"]
            st.session_state.job_description = job_description
            st.session_state.profile_data = {
                "profile": profile,
                "work_experiences": work_experiences,
                "achievements_by_exp": achievements_by_exp,
                "skills": skills
            }

            st.success("✅ Analysis complete!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error analyzing match: {str(e)}")
            st.stop()

# ======================================================
# RESULTS & DECISION GATE
# ======================================================
if "match_score" in st.session_state:
    st.divider()
    st.subheader("📊 Your Match Score")

    score = st.session_state.match_score

    if score >= 0.7:
        label = "Strong Fit"
        color = "🟢"
        recommendation = "Your profile is a strong match! You're well-positioned for this role."
    elif score >= 0.5:
        label = "Moderate Fit"
        color = "🟡"
        recommendation = "You have relevant experience, but there are some gaps. Consider optimizing your CV."
    else:
        label = "Weak Fit"
        color = "🔴"
        recommendation = "Your profile has significant gaps. We recommend optimizing your CV to highlight relevant skills."

    st.metric("Profile Match Score", f"{score*100:.1f}%", f"{label} {color}")
    st.info(recommendation)

    # Display analysis details
    st.subheader("📝 Match Analysis")
    if "match_analysis" in st.session_state:
        st.markdown(st.session_state.match_analysis)

    st.divider()

    # ===== DECISION GATE =====
    if score > 0.6:
        # High score - offer direct download
        st.success("✅ Strong match! Your profile is well-suited for this role.")

        if st.button("📄 Generate Standard CV", type="primary", use_container_width=True):
            st.switch_page("pages/06_careerhub_cv_generator.py")

    else:
        # Low score - offer optimization
        st.warning("⚠️ Your profile has gaps. Let's optimize your CV to better match this job!")

        if st.button("✨ Optimize & Generate CV", type="primary", use_container_width=True):
            st.session_state.action = "optimize"
            st.switch_page("pages/09_careerhub_cv_optimizer.py")

    # Alternative option
    st.divider()
    st.subheader("What's Next?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👤 Update Your Profile", use_container_width=True):
            st.switch_page("pages/05_careerhub_profile.py")

    with col2:
        if st.button("🔄 Check Another Job", use_container_width=True):
            st.session_state.match_score = None
            st.session_state.match_analysis = None
            st.rerun()

# ======================================================
# NAVIGATION
# ======================================================
st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.switch_page("pages/04_careerhub_dashboard.py")

with col2:
    if st.button("📊 View All CVs", use_container_width=True):
        st.switch_page("pages/07_careerhub_tracker.py")
