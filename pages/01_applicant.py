import streamlit as st
import pandas as pd
from ats_engine import (
    extract_text_from_pdf,
    clean_and_structure_resume,
    validate_resume_document,
    get_embedding,
    generate_resume_improvement_suggestions
)
from sklearn.metrics.pairwise import cosine_similarity
import io
from pypdf import PdfReader
from styles import inject_global_css
from form_helpers import (
    display_jd_helper_tips, show_jd_templates, auto_save_form_field,
    get_saved_field, show_form_autosave_indicator
)
from results_helpers import (
    show_match_score_card, show_score_breakdown, show_improvement_suggestions,
    download_match_report_button
)
from ui_components import (
    show_success_toast, show_error_toast, show_error,
    show_file_upload_area, show_step_progress
)

# Inject global CSS
inject_global_css()

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="TrueFit - Candidate Resume Optimizer",
    page_icon="📄",
    layout="wide"
)

def show_applicant_top_controls():
    """Show top controls with auth actions for applicant page."""
    left_col, mid_col, right_col = st.columns([1, 6, 2])

    with left_col:
        if hasattr(st, "popover"):
            with st.popover("☰", use_container_width=True):
                if st.button("🏠 Home", key="applicant_menu_home", use_container_width=True):
                    st.switch_page("app.py")
                if st.button("❓ Help & FAQ", key="applicant_menu_help", use_container_width=True):
                    st.switch_page("pages/10_help_faq.py")
        else:
            st.button("☰", key="applicant_menu_fallback", use_container_width=True, disabled=True)

    if st.session_state.get("authenticated"):
        with right_col:
            if hasattr(st, "popover"):
                with st.popover("👤", use_container_width=True):
                    if st.session_state.get("user_email"):
                        st.caption(st.session_state.user_email)
                    if st.button("⚙️ Settings", key="applicant_settings", use_container_width=True):
                        st.switch_page("pages/11_security_settings.py")
                    if st.button("🚪 Logout", key="applicant_logout", use_container_width=True):
                        st.session_state.authenticated = False
                        st.session_state.user_email = None
                        st.session_state.user_role = None
                        st.switch_page("pages/03_careerhub_auth.py")
            else:
                if st.button("🚪 Logout", key="applicant_logout_fallback", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.user_email = None
                    st.session_state.user_role = None
                    st.switch_page("pages/03_careerhub_auth.py")
    else:
        with right_col:
            login_col, signup_col = st.columns(2)
            with login_col:
                if st.button("Log In", key="applicant_login", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.switch_page("pages/03_careerhub_auth.py")
            with signup_col:
                if st.button("Sign Up", key="applicant_signup", use_container_width=True):
                    st.session_state.auth_mode = "signup"
                    st.switch_page("pages/03_careerhub_auth.py")

show_applicant_top_controls()

st.title("📄 Resume Optimizer")
st.subheader("See how your resume matches against job descriptions with AI-powered analysis")

# Initialize session state
if 'resume_cleaned' not in st.session_state:
    st.session_state.resume_cleaned = None
if 'match_score' not in st.session_state:
    st.session_state.match_score = None
if 'comparison_view' not in st.session_state:
    st.session_state.comparison_view = False
if 'improvement_suggestions' not in st.session_state:
    st.session_state.improvement_suggestions = None

# ======================================================
# INPUT SECTION
# ======================================================
st.header("1️⃣ Upload Your Resume")

col1, col2 = st.columns([2, 1])

with col1:
    resume_file = st.file_uploader(
        "Upload your resume (PDF):",
        type=['pdf'],
        help="Text-based PDF only (not scanned images). Max 10 MB."
    )

with col2:
    st.info("📝 **Tip:** Use a well-formatted, text-based PDF for best results")

st.header("2️⃣ Paste the Job Description")

col1, col2 = st.columns([2, 1])

with col1:
    job_description = st.text_area(
        "Paste the full job description:",
        height=250,
        placeholder="Job title, responsibilities, required skills, qualifications, benefits, etc.",
        help="The more detailed, the better the analysis. Aim for 200+ words.",
        value=get_saved_field("applicant_jd", "job_description")
    )
    
    # Auto-save job description
    auto_save_form_field("applicant_jd", "job_description", job_description)

with col1:
    show_form_autosave_indicator()

# Show job description templates
template = show_jd_templates()
if template:
    job_description = template
    st.session_state.jd_template = template

# Show helper tips
display_jd_helper_tips()

# Initialize session state
if 'resume_cleaned' not in st.session_state:
    st.session_state.resume_cleaned = None
if 'match_score' not in st.session_state:
    st.session_state.match_score = None
if 'comparison_view' not in st.session_state:
    st.session_state.comparison_view = False
if 'improvement_suggestions' not in st.session_state:
    st.session_state.improvement_suggestions = None

# ======================================================
# INPUT SECTION
# ======================================================
st.header("1️⃣ Upload Your Resume")

col1, col2 = st.columns([2, 1])

with col1:
    resume_file = st.file_uploader(
        "Upload your resume (PDF):",
        type=['pdf'],
        help="Text-based PDF only (not scanned images). Max 10 MB."
    )

with col2:
    st.info("📝 **Tip:** Use a well-formatted, text-based PDF for best results")

st.header("2️⃣ Paste the Job Description")

job_description = st.text_area(
    "Paste the full job description:",
    height=250,
    placeholder="Job title, responsibilities, required skills, qualifications, benefits, etc.",
    help="The more detailed, the better the analysis. Aim for 200+ words."
)

# ======================================================
# PROCESS & ANALYSIS
# ======================================================
if resume_file and job_description and st.button("🔍 Analyze Resume & Job Match", type="primary", use_container_width=True):
    
    # Validation
    if not job_description.strip() or len(job_description.strip()) < 50:
        show_error("invalid_jd")
        st.stop()
    
    # Define processing steps
    steps = [
        "Extracting text from PDF",
        "Validating resume document",
        "Cleaning and structuring resume",
        "Calculating match score",
        "Generating improvement suggestions"
    ]
    
    # Show progress with step indicator
    show_step_progress(1, len(steps), steps)
    
    try:
        # Step 1: Extract text
        with st.spinner("⏳ Extracting text from PDF..."):
            raw_resume = extract_text_from_pdf(resume_file)
            
            if not raw_resume or len(raw_resume.strip()) < 10:
                show_error("text_extraction_failed")
                st.stop()
        
        show_step_progress(2, len(steps), steps)
        
        # Step 2: Validate it's actually a resume
        with st.spinner("⏳ Validating resume document..."):
            is_valid_resume, error_msg = validate_resume_document(raw_resume)
            
            if not is_valid_resume:
                show_error_toast(error_msg)
                st.stop()
        
        show_step_progress(3, len(steps), steps)
        
        # Step 3: Clean and structure
        with st.spinner("⏳ Cleaning and structuring resume..."):
            cleaned_resume = clean_and_structure_resume(raw_resume)
            
            if cleaned_resume.startswith("Error"):
                show_error_toast(cleaned_resume)
                st.stop()
            
            st.session_state.resume_cleaned = cleaned_resume
        
        show_step_progress(4, len(steps), steps)
        
        # Step 4: Calculate match score
        with st.spinner("⏳ Calculating match score..."):
            resume_vector = get_embedding(cleaned_resume)
            jd_vector = get_embedding(job_description)
            
            if resume_vector is None or jd_vector is None:
                show_error("api_error")
                st.stop()
            
            score = cosine_similarity([jd_vector], [resume_vector])[0][0]
            st.session_state.match_score = float(score)
        
        show_step_progress(5, len(steps), steps)
        
        # Step 5: Generate improvement suggestions
        with st.spinner("⏳ Generating personalized improvement suggestions..."):
            suggestions = generate_resume_improvement_suggestions(job_description, cleaned_resume)
            st.session_state.improvement_suggestions = suggestions
        
        show_success_toast("Analysis complete! See your results below.")
        
    except Exception as e:
        show_error_toast(f"Service error: {str(e)}")
        st.stop()

# ======================================================
# RESULTS DISPLAY
# ======================================================
if st.session_state.match_score is not None:
    st.divider()
    st.header("📊 Analysis Results")
    
    # Show enhanced match score card
    show_match_score_card(
        st.session_state.match_score,
        job_title="Job Position",
        candidate_name="Your Resume"
    )
    
    st.divider()
    
    # Interpretation guide
    with st.expander("📖 How to interpret your score", expanded=False):
        st.markdown("""
        **Understanding the Match Score:**
        
        - **80-100%**: Excellent Match
          - You have most/all required skills
          - Experience level aligns well
          - High chance of success in interview
          - **Action**: Ready to apply!
        
        - **60-79%**: Good Match
          - You have core required skills
          - Some specializations missing
          - Can learn on the job
          - **Action**: Address skill gaps in cover letter
        
        - **40-59%**: Fair Match
          - You have transferable skills
          - Significant gaps in specific areas
          - Would require training
          - **Action**: Consider if you're willing to learn
        
        - **Below 40%**: Poor Match
          - Fundamental mismatch
          - Major skill gaps
          - Career change required
          - **Action**: Focus on other opportunities
        """)
    
    st.divider()
    
    # Show improvement suggestions
    if st.session_state.improvement_suggestions:
        suggestions = st.session_state.improvement_suggestions.split('\n')
        suggestions = [s.strip() for s in suggestions if s.strip()]
        show_improvement_suggestions(suggestions)
    
    st.divider()
    
    # Download report
    st.subheader("📥 Export Report")
    download_match_report_button(
        candidate_name="My Resume",
        match_score=st.session_state.match_score,
        job_title="Target Position",
        matched_skills=["Example skill 1", "Example skill 2"],
        missing_skills=["Gap 1", "Gap 2"],
        suggestions=st.session_state.improvement_suggestions.split('\n') if st.session_state.improvement_suggestions else []
    )
    
    st.divider()
    
    # Comparison view toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📋 Detailed Comparison")
    with col2:
        show_comparison = st.checkbox("Show comparison view", value=False)
    
    st.divider()
    
    # Comparison view toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📋 Improvement Suggestions")
    with col2:
        show_comparison = st.checkbox("Show comparison view", value=False)
    
    if st.session_state.improvement_suggestions:
        st.markdown(st.session_state.improvement_suggestions)
    
    # Comparison view
    if show_comparison:
        st.divider()
        st.subheader("🔄 Resume vs Job Description Comparison")
        
        # Create two columns for comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Your Resume (Cleaned)**")
            with st.expander("View cleaned resume structure", expanded=False):
                st.text(st.session_state.resume_cleaned)
        
        with col2:
            st.write("**Job Description**")
            with st.expander("View job description", expanded=False):
                st.text(job_description)
        
        st.info("""
        💡 **How to use this comparison:**
        - Review your resume structure on the left
        - Compare it against the job requirements on the right
        - Identify missing sections or skills
        - Use the suggestions above to strengthen your application
        """)
    
    st.divider()
    
    # Action items
    st.subheader("✅ Next Steps")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **High Match (80%+)**
        - You're ready to apply!
        - Customize your cover letter
        - Apply with confidence
        """)
    
    with col2:
        st.markdown("""
        **Medium Match (60-79%)**
        - Address the suggestions above
        - Update relevant sections
        - Re-analyze when done
        """)
    
    with col3:
        st.markdown("""
        **Low Match (<60%)**
        - This role may not fit your profile
        - Or significant updates needed
        - Review skills gap carefully
        """)
    
    # Reset button
    st.divider()
    if st.button("🔄 Analyze Another Role", use_container_width=True):
        st.session_state.resume_cleaned = None
        st.session_state.match_score = None
        st.session_state.comparison_view = False
        st.session_state.improvement_suggestions = None
        st.rerun()

# Sidebar
with st.sidebar:
    st.title("💡 Tips for Best Results")
    st.markdown("""
    ### Resume Tips:
    - Use a clean, text-based PDF
    - Include relevant keywords
    - Quantify your achievements
    - List specific technologies/skills
    
    ### Job Description Tips:
    - Paste the full description
    - Include all requirements
    - Keep formatting simple
    - The more detail, the better
    
    ### General Tips:
    - Tailor resumes to each role
    - Focus on relevant experience
    - Use action verbs
    - Avoid generic descriptions
    """)
    
    st.divider()
    st.markdown("""
    **Need help?**
    - Unclear results? Try re-uploading your PDF
    - Low match? Check for keyword alignment
    - Questions? You're using TrueFit ✨
    """)
