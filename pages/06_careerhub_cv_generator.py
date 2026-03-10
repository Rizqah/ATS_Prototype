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
    check_cv_limit,
    save_generated_cv,
    update_cv_status
)

from cv_generator import (
    generate_ats_optimized_cv,
    generate_cv_docx,
    format_cv_for_display,
    generate_optimized_cv_content,
)

from ats_engine import extract_text_from_pdf, generate_resume_improvement_suggestions
from cv_helpers import show_cv_template_selector, show_template_comparison, show_download_options
from ui_components import show_top_navigation

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="TrueFit – CV Generator",
    page_icon="📄",
    layout="wide"
)

# ======================================================
# AUTH CHECK
# ======================================================
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Please log in first")
    st.switch_page("pages/03_careerhub_auth.py")

user_email = st.session_state.user_email
show_top_navigation("Generate CV")

# ======================================================
# HEADER
# ======================================================
st.title("📄 Generate a Tailored CV")
st.caption("Upload a job description and generate an ATS-optimized CV")

# ======================================================
# LOAD PROFILE DATA
# ======================================================
profile = get_profile(user_email).get("profile", {})
work_experiences = get_work_experience(user_email).get("experiences", [])
skills = get_skills(user_email).get("skills", [])

# ======================================================
# PROFILE COMPLETENESS CHECK
# ======================================================
if not work_experiences or len(skills) < 3:
    st.warning(
        "⚠️ Your profile is incomplete.\n\n"
        "You need at least:\n"
        "- 1 work experience\n"
        "- 3 skills"
    )

    if st.button("👤 Complete Profile"):
        st.switch_page("pages/05_careerhub_profile.py")

    st.stop()

# ======================================================
# CV LIMIT CHECK
# ======================================================
limit_data = check_cv_limit(user_email)

if limit_data.get("limit_reached"):
    st.error(
        f"❌ Monthly CV limit reached ({limit_data['limit']}).\n\n"
        "Upgrade to Premium for unlimited CVs."
    )
    st.stop()

remaining = limit_data["limit"] - limit_data["cvs_generated"]
st.info(f"📊 CVs remaining this month: {remaining}")

# ======================================================
# JOB DESCRIPTION INPUT
# ======================================================
st.header("1️⃣ Job Description")

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
        placeholder="Job title, responsibilities, requirements..."
    )
else:
    jd_file = st.file_uploader("Upload job description (PDF)", type=["pdf"])
    if jd_file:
        with st.spinner("Extracting text from PDF..."):
            job_description = extract_text_from_pdf(jd_file)
            st.success("Job description extracted successfully")

# ======================================================
# CV TEMPLATE SELECTION
# ======================================================
st.header("2️⃣ Choose Your CV Template")

template_tab1, template_tab2 = st.tabs(["Select Template", "Compare All"])

with template_tab1:
    selected_template = show_cv_template_selector()

with template_tab2:
    show_template_comparison()

st.divider()

# ======================================================
# CV DETAILS
# ======================================================
st.header("3️⃣ CV Details")

col1, col2 = st.columns(2)

with col1:
    job_title = st.text_input(
        "Job title you are applying for",
        placeholder="e.g. Senior Operations Analyst"
    )

with col2:
    template_display = st.session_state.get("selected_cv_template", "professional").title() if st.session_state.get("selected_cv_template") else "Professional"
    st.metric("Selected Template", template_display)

# ======================================================
# GENERATE CV
# ======================================================
st.header("4️⃣ Generate & Download")

if st.button("🚀 Generate CV", type="primary", use_container_width=True):

    if not job_description.strip():
        st.error("❌ Job description is required")
        st.stop()

    if not job_title.strip():
        st.error("❌ Job title is required")
        st.stop()

    with st.spinner("Generating your CV..."):

        try:
            # --------------------------------------------------
            # BUILD ACHIEVEMENTS MAP
            # --------------------------------------------------
            achievements_by_exp = {}
            for exp in work_experiences:
                achievements_by_exp[exp["id"]] = (
                    get_achievements(exp["id"]).get("achievements", [])
                )

            # --------------------------------------------------
            # GENERATE CV PDF
            # --------------------------------------------------
            pdf_bytes, match_score = generate_ats_optimized_cv(
                profile=profile,
                work_experiences=work_experiences,
                achievements_by_experience=achievements_by_exp,
                skills=skills,
                job_description=job_description
            )

            # --------------------------------------------------
            # GENERATE DOCX (Word) FOR DOWNLOAD
            # --------------------------------------------------
            docx_bytes = generate_cv_docx(
                profile=profile,
                work_experiences=work_experiences,
                achievements_by_experience=achievements_by_exp,
                skills=skills,
            )

            # --------------------------------------------------
            # STORE IN SESSION STATE
            # --------------------------------------------------
            st.session_state.generated_pdf = pdf_bytes
            st.session_state.generated_docx = docx_bytes
            st.session_state.match_score = match_score
            st.session_state.job_title = job_title
            st.session_state.job_description = job_description

            # --------------------------------------------------
            # SAVE CV RECORD
            # --------------------------------------------------
            cv_text = format_cv_for_display(
                profile,
                work_experiences,
                achievements_by_exp,
                skills
            )

            st.session_state.cv_text = cv_text

            save_generated_cv(
                user_email=user_email,
                job_title=job_title,
                match_score=match_score,
                cv_content=cv_text,
                job_description=job_description
            )

            st.success(f"✅ CV generated successfully – Match score: {match_score*100:.1f}%")

        except Exception as e:
            st.error(f"❌ Error generating CV: {e}")
            st.stop()

# ======================================================
# RESULTS & DOWNLOAD (when user has generated a CV)
# ======================================================
if "generated_pdf" in st.session_state:

    st.divider()
    st.subheader("📊 Match Score")

    score = st.session_state.match_score

    if score >= 0.8:
        label = "Excellent Match"
        color = "🟢"
    elif score >= 0.6:
        label = "Good Match"
        color = "🟡"
    elif score >= 0.4:
        label = "Fair Match"
        color = "🟠"
    else:
        label = "Needs Improvement"
        color = "🔴"

    st.metric("ATS Match Score", f"{score*100:.1f}%", f"{label} {color}")

    # ===== OPTIMIZE BUTTON IF SCORE < 60% (and not yet optimised) =====
    if score < 0.6 and "optimized_pdf" not in st.session_state:
        st.divider()
        st.warning(
            "⚠️ **Your CV match score is below 60%**\n\n"
            "Click 'Optimize CV with AI' to get a downloadable CV rewritten for this job "
            "(summary, skills order, and wording tailored to the role)."
        )
        
        if st.button("✨ Optimize CV with AI", type="primary", use_container_width=True):
            with st.spinner("🤖 Creating your AI-optimised CV..."):
                try:
                    # Build achievements map
                    achievements_by_exp = {}
                    for exp in work_experiences:
                        achievements_by_exp[exp["id"]] = (
                            get_achievements(exp["id"]).get("achievements", [])
                        )
                    # Get AI-optimised content (summary, skills reordered for JD)
                    optimized_data = generate_optimized_cv_content(
                        profile=profile,
                        work_experiences=work_experiences,
                        achievements_by_experience=achievements_by_exp,
                        skills=skills,
                        job_description=st.session_state.job_description,
                    )
                    # Generate PDF and DOCX from optimised content
                    pdf_bytes, optimized_score = generate_ats_optimized_cv(
                        profile=optimized_data["profile"],
                        work_experiences=optimized_data["work_experiences"],
                        achievements_by_experience=optimized_data["achievements_by_exp"],
                        skills=optimized_data["skills"],
                        job_description=st.session_state.job_description,
                    )
                    docx_bytes = generate_cv_docx(
                        profile=optimized_data["profile"],
                        work_experiences=optimized_data["work_experiences"],
                        achievements_by_experience=optimized_data["achievements_by_exp"],
                        skills=optimized_data["skills"],
                    )
                    st.session_state.optimized_pdf = pdf_bytes
                    st.session_state.optimized_docx = docx_bytes
                    st.session_state.optimized_score = optimized_score
                    st.session_state.show_suggestions = False
                    st.success("✅ Your AI-optimised CV is ready to download below!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error creating optimised CV: {str(e)}")

    # ===== AI-OPTIMISED CV DOWNLOAD (after user clicked Optimize) =====
    if "optimized_pdf" in st.session_state:
        st.divider()
        st.subheader("📊 AI-Optimised CV")
        optimized_score = st.session_state.optimized_score
        if optimized_score >= 0.8:
            label = "Excellent Match"
            color = "🟢"
        elif optimized_score >= 0.6:
            label = "Good Match"
            color = "🟡"
        elif optimized_score >= 0.4:
            label = "Fair Match"
            color = "🟠"
        else:
            label = "Needs Improvement"
            color = "🔴"
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Original Score", f"{st.session_state.match_score*100:.1f}%")
        with col2:
            improvement = (optimized_score - st.session_state.match_score) * 100
            delta = f"+{improvement:.1f}%" if improvement >= 0 else f"{improvement:.1f}%"
            st.metric("Optimised Score", f"{optimized_score*100:.1f}%", delta)
        with col3:
            st.metric("Status", label, color)
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📄 Download AI-Optimised CV (PDF)",
                data=st.session_state.optimized_pdf,
                file_name=f"{profile.get('full_name','CV').replace(' ','_')}_{st.session_state.job_title.replace(' ','_')}_OPTIMISED.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
        with col_dl2:
            if st.session_state.get("optimized_docx"):
                st.download_button(
                    label="📝 Download AI-Optimised CV (DOCX)",
                    data=st.session_state.optimized_docx,
                    file_name=f"{profile.get('full_name','CV').replace(' ','_')}_{st.session_state.job_title.replace(' ','_')}_OPTIMISED.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
        st.caption("Summary and skills have been tailored to this job description.")

    # Download original CV (PDF + DOCX)
    st.divider()
    st.subheader("📥 Download CV")
    st.caption("**Formats:** PDF (ATS-optimised) | DOCX (Microsoft Word, easy to edit)")
    col_pdf, col_docx = st.columns(2)
    with col_pdf:
        st.download_button(
            label="📄 PDF (ATS-optimised)",
            data=st.session_state.generated_pdf,
            file_name=f"{profile.get('full_name','CV').replace(' ','_')}_{st.session_state.job_title.replace(' ','_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col_docx:
        if st.session_state.get("generated_docx"):
            st.download_button(
                label="📝 DOCX (Microsoft Word)",
                data=st.session_state.generated_docx,
                file_name=f"{profile.get('full_name','CV').replace(' ','_')}_{st.session_state.job_title.replace(' ','_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        else:
            st.caption("Generate a new CV to get DOCX.")

# ======================================================
# OPTIMIZATION SUGGESTIONS (legacy – only if set elsewhere)
# ======================================================
if st.session_state.get("show_suggestions") and "suggestions" in st.session_state:
    st.divider()
    st.subheader("💡 AI Optimization Suggestions")
    suggestions = st.session_state.suggestions
    if suggestions.startswith("Error"):
        st.error(suggestions)
    else:
        st.markdown(suggestions)
        if st.button("👤 Go to Profile to Update", use_container_width=True):
            st.switch_page("pages/05_careerhub_profile.py")

# ======================================================
# NAVIGATION
# ======================================================
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.switch_page("pages/04_careerhub_dashboard.py")

with col2:
    if st.button("📊 View All CVs", use_container_width=True):
        st.switch_page("pages/07_careerhub_tracker.py")

with col3:
    if st.button("👤 Update Profile", use_container_width=True):
        st.switch_page("pages/05_careerhub_profile.py")
