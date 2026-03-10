import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import time
from ats_engine import (
    rank_candidates, 
    generate_compliant_feedback, 
    extract_text_from_pdf,
    clean_and_structure_resume
)
from styles import inject_global_css
from form_helpers import (
    show_jd_templates, display_jd_helper_tips, show_breadcrumb_wizard,
    auto_save_form_field, get_saved_field
)
from results_helpers import (
    show_batch_progress, show_processing_stats, show_filter_sidebar,
    apply_filters, show_sort_options, sort_candidates, show_candidates_table,
    show_match_score_card, download_match_report_button
)
from ui_components import show_success_toast, show_error_toast

# Inject global CSS
inject_global_css()

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="TrueFit - Recruiter Screening",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Require authentication before accessing recruiter screening
if not st.session_state.get("authenticated"):
    st.warning("🔐 Please log in or sign up to access Candidate Screening.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log In", key="recruiter_gate_login", use_container_width=True, type="primary"):
            st.session_state.auth_mode = "login"
            st.session_state.auth_source = "recruiter"
            st.switch_page("pages/03_careerhub_auth.py")
    with col2:
        if st.button("Sign Up", key="recruiter_gate_signup", use_container_width=True):
            st.session_state.auth_mode = "signup"
            st.session_state.auth_source = "recruiter"
            st.switch_page("pages/03_careerhub_auth.py")
    st.stop()

def show_recruiter_top_controls():
    """Show top controls for recruiter pages."""
    col1, col2, col3 = st.columns([1, 6, 2])

    with col1:
        if hasattr(st, "popover"):
            with st.popover("☰", use_container_width=True):
                if st.button("🏠 Home", key="recruiter_menu_home", use_container_width=True):
                    st.switch_page("app.py")
                if st.button("❓ Help & FAQ", key="recruiter_menu_help", use_container_width=True):
                    st.switch_page("pages/10_help_faq.py")
        else:
            st.button("☰", key="recruiter_menu_fallback", use_container_width=True, disabled=True)

    if st.session_state.get("authenticated"):
        with col3:
            if hasattr(st, "popover"):
                with st.popover("👤", use_container_width=True):
                    if st.session_state.get("user_email"):
                        st.caption(st.session_state.user_email)
                    if st.button("⚙️ Settings", key="recruiter_profile_settings", use_container_width=True):
                        st.switch_page("pages/11_security_settings.py")
                    if st.button("🚪 Logout", key="recruiter_profile_logout", use_container_width=True):
                        st.session_state.authenticated = False
                        st.session_state.user_email = None
                        st.session_state.user_role = None
                        st.switch_page("pages/03_careerhub_auth.py")
            else:
                if st.button("🚪 Logout", key="recruiter_profile_logout_fallback", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.user_email = None
                    st.session_state.user_role = None
                    st.switch_page("pages/03_careerhub_auth.py")
    else:
        with col3:
            login_col, signup_col = st.columns(2)
            with login_col:
                if st.button("Log In", key="recruiter_login", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.session_state.auth_source = "recruiter"
                    st.switch_page("pages/03_careerhub_auth.py")
            with signup_col:
                if st.button("Sign Up", key="recruiter_signup", use_container_width=True):
                    st.session_state.auth_mode = "signup"
                    st.session_state.auth_source = "recruiter"
                    st.switch_page("pages/03_careerhub_auth.py")

show_recruiter_top_controls()

st.title("👥 Candidate Screening Dashboard")
st.subheader("AI-powered resume ranking and feedback generation")

# Show breadcrumb wizard
show_breadcrumb_wizard(1, 3, ["Define Role", "Upload Resumes", "Review Rankings"])

# ======================================================
# INITIALIZE SESSION STATE
# ======================================================
def init_session_state():
    """Initialize all session state variables."""
    if 'ranked_data' not in st.session_state:
        st.session_state.ranked_data = None
    if 'job_description' not in st.session_state:
        st.session_state.job_description = ""
    if 'feedback_draft' not in st.session_state:
        st.session_state.feedback_draft = None

init_session_state()

# ======================================================
# 1. INPUT SECTION
# ======================================================
st.header("1️⃣ Define the Role & Upload Resumes")

col1, col2 = st.columns([3, 1])

with col1:
    job_description = st.text_area(
        "Paste the Full Job Description:", 
        height=200,
        placeholder="Job title, key responsibilities, required skills, experience level, compensation, etc.",
        value=st.session_state.get('job_description', ''),
        key='jd_input'
    )
    
    # Auto-save job description
    auto_save_form_field("recruiter_screening", "job_description", job_description)

with col2:
    st.write("**For Best Results:**")
    st.markdown("""
    ✓ Include responsibilities
    ✓ List required skills
    ✓ Specify experience level
    ✓ Add nice-to-have skills
    ✓ 200-500 words optimal
    """)

st.session_state.job_description = job_description

# Show job description templates
template_text = show_jd_templates()
if template_text:
    job_description = template_text
    st.session_state.job_description = template_text

# Show helper tips
display_jd_helper_tips()

st.divider()

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF Format):", 
    type=['pdf'], 
    accept_multiple_files=True,
    help="Upload one or more resume PDFs. Supports text-based PDFs only."
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} resume(s) ready to process")
else:
    st.info("📄 No resumes uploaded yet. Upload 1 or more PDF files to get started.")

# ======================================================
# 2. VALIDATION FUNCTION
# ======================================================
def validate_inputs(job_desc: str, files: List) -> tuple[bool, Optional[str]]:
    """Validate inputs before processing."""
    if not job_desc or not job_desc.strip():
        return False, "Job description cannot be empty"
    if len(job_desc.strip()) < 50:
        return False, "Job description too short (minimum 50 characters)"
    if not files:
        return False, "No resumes uploaded"
    if len(files) > 50:
        return False, "Maximum 50 resumes per batch"
    return True, None

# ======================================================
# 3. PROCESSING & RANKING
# ======================================================
st.header("2️⃣ Process & Rank Candidates")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    process_button = st.button(
        "🚀 Run Ranking Engine",
        type="primary",
        use_container_width=True,
        disabled=not (job_description and uploaded_files)
    )

with col2:
    st.metric("Resumes", len(uploaded_files) if uploaded_files else 0)

with col3:
    st.metric("JD Characters", len(job_description) if job_description else 0)

# --- PROCESS ON BUTTON CLICK ---
if process_button:
    # Validate
    is_valid, error_msg = validate_inputs(job_description, uploaded_files)
    
    if not is_valid:
        st.error(f"❌ Validation Error: {error_msg}")
        st.stop()
    
    # Process files
    candidate_list_for_ranking = []
    processing_status = st.status("Processing Progress", expanded=True)
    
    start_time = time.time()
    succeeded = 0
    failed = 0
    
    try:
        for idx, file in enumerate(uploaded_files, 1):
            # Show batch progress
            show_batch_progress(idx, len(uploaded_files), file.name)
            
            with processing_status:
                st.write(f"📖 [{idx}/{len(uploaded_files)}] Extracting: {file.name}")
            
            # Step 1: Extract raw text
            try:
                raw_resume_text = extract_text_from_pdf(file)
            except ValueError as e:
                st.warning(f"⚠️ Could not extract text from {file.name}: {str(e)}")
                failed += 1
                continue
            
            if not raw_resume_text or len(raw_resume_text.strip()) < 10:
                st.warning(f"⚠️ {file.name} appears empty or unreadable")
                failed += 1
                continue
            
            with processing_status:
                st.write(f"🧹 Cleaning: {file.name}")
            
            # Step 2: Clean and structure
            clean_resume_text = clean_and_structure_resume(raw_resume_text)
            
            if clean_resume_text.startswith("Error"):
                st.warning(f"⚠️ Processing failed for {file.name}")
                failed += 1
                continue
            
            # Add to ranking list
            candidate_list_for_ranking.append({
                "name": file.name.replace('.pdf', ''),
                "resume": clean_resume_text
            })
            
            with processing_status:
                st.write(f"✅ Processed: {file.name}")
            
            succeeded += 1
        
        processing_status.update(label="✅ Extraction Complete", state="complete")
        
        # Show processing stats
        elapsed_time = time.time() - start_time
        show_processing_stats(
            len(uploaded_files),
            succeeded + failed,
            succeeded,
            failed,
            elapsed_time
        )
        
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.stop()
        
        # Check results
        if not candidate_list_for_ranking:
            st.error("❌ No resumes could be processed.")
            st.stop()
        
        st.success(f"✅ Successfully processed {len(candidate_list_for_ranking)}/{len(uploaded_files)} resumes")
        
        # --- RANKING ---
        with st.spinner("🔍 Ranking candidates..."):
            ranking_results = rank_candidates(job_description, candidate_list_for_ranking)
        
        if not ranking_results:
            st.error("❌ Ranking failed. Please try again.")
            st.stop()
        
        # --- DISPLAY RESULTS ---
        st.subheader("✅ Ranking Results")
        
        # Convert to DataFrame for filtering/sorting
        df_candidates = pd.DataFrame([
            {
                'Rank': idx + 1,
                'Candidate': result['name'],
                'Match Score': result['score'],
                'Match % (for display)': f"{result['score'] * 100:.1f}%",
                'Status': 'Reviewed',
                'resume': result.get('resume', ''),
                'full_result': result
            }
            for idx, result in enumerate(ranking_results)
        ])
        
        # Store results
        st.session_state.ranked_data = ranking_results
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Candidates", len(ranking_results))
        with col2:
            top_score = ranking_results[0]['score'] * 100
            st.metric("Top Match", f"{top_score:.1f}%")
        with col3:
            bottom_score = ranking_results[-1]['score'] * 100
            st.metric("Lowest Match", f"{bottom_score:.1f}%")
        with col4:
            avg_score = sum(r['score'] for r in ranking_results) / len(ranking_results) * 100
            st.metric("Average", f"{avg_score:.1f}%")
        
        st.divider()
        
        # Filtering and Sorting Controls
        st.subheader("🔍 Filter & Sort Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_score, max_score = st.slider(
                "Match Score Range (%)",
                min_value=0,
                max_value=100,
                value=(int(min(df_candidates['Match Score']) * 100), 100),
                step=5,
                help="Filter candidates by match score percentage"
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Match Score", "Name", "Rank"],
                help="How to order the results"
            )
        
        with col3:
            sort_order = st.selectbox(
                "Order",
                ["Descending", "Ascending"],
                help="Ascending or Descending"
            )
        
        # Apply filters and sorting
        filtered_df = apply_filters(
            df_candidates,
            min_score / 100,
            max_score / 100,
            ['Reviewed'],
            'Match Score'
        )
        
        sorted_df = sort_candidates(
            filtered_df,
            "Match Score" if sort_by == "Match Score" else ("name" if sort_by == "Name" else "Rank"),
            sort_order.lower()
        )
        
        # Display candidates table
        st.subheader(f"📊 Candidates ({len(sorted_df)} of {len(df_candidates)} matches)")
        
        # Display each candidate with enhanced UI
        for idx, row in sorted_df.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**#{row['Rank']}. {row['Candidate']}**")
            
            with col2:
                show_match_score_card(
                    row['Match Score'],
                    st.session_state.job_description[:50] + "...",
                    row['Candidate']
                )
            
            with col3:
                # Download PDF report for this candidate
                if st.button(
                    "📄 Download Report",
                    key=f"download_{row['Candidate']}",
                    use_container_width=True,
                    help="Download match report as PDF"
                ):
                    download_match_report_button(
                        row['Candidate'],
                        row['Match Score'],
                        st.session_state.job_description[:100],
                        [],  # matched_skills would come from ats_engine analysis
                        [],  # missing_skills
                        []   # suggestions
                    )

# ======================================================
# 4. FEEDBACK ENGINE
# ======================================================
if st.session_state.ranked_data:
    st.divider()
    st.header("3️⃣ Generate Candidate Feedback")
    
    # Get lowest-ranked candidate
    lowest_candidate = st.session_state.ranked_data[-1]
    
    st.info(
        f"📧 Generate rejection feedback for candidates below your threshold"
    )
    
    # Candidate selection
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_candidate_name = st.selectbox(
            "Select candidate for feedback:",
            options=[c['name'] for c in st.session_state.ranked_data],
            index=len(st.session_state.ranked_data) - 1,
            help="Lowest-ranked candidate is selected by default"
        )
    
    with col2:
        # Show score of selected candidate
        selected = next(c for c in st.session_state.ranked_data if c['name'] == selected_candidate_name)
        st.metric("Match Score", f"{selected['score'] * 100:.1f}%")
    
    # Generate feedback button
    if st.button(
        f"✍️ Draft Email for {selected_candidate_name}",
        type="primary",
        use_container_width=True
    ):
        with st.spinner("⏳ Generating legally compliant feedback..."):
            try:
                feedback_draft = generate_compliant_feedback(
                    st.session_state.job_description,
                    selected['resume']
                )
                
                if feedback_draft.startswith("Error"):
                    st.error(f"❌ {feedback_draft}")
                else:
                    st.session_state.feedback_draft = feedback_draft
                    st.success("✅ Draft generated successfully")
                    
            except Exception as e:
                st.error(f"❌ Failed to generate feedback: {str(e)}")
    
    # Display feedback
    if st.session_state.feedback_draft:
        st.divider()
        st.subheader("📝 Email Draft (Review Required)")
        
        with st.expander("View full email draft", expanded=True):
            st.text(st.session_state.feedback_draft)
        
        st.divider()
        st.subheader("🛡️ Compliance Review")
        
        col1, col2 = st.columns(2)
        
        with col1:
            human_review = st.checkbox(
                "✅ I have reviewed this feedback for accuracy and compliance",
                value=False,
                help="Confirm you've read and approved this"
            )
        
        with col2:
            if human_review:
                st.success("✅ Email approved and ready!")
                
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.success("Email copied! Paste into your email client.")
        
        st.warning(
            "⚖️ **Legal Notice:** Always have HR/Legal review rejection communications "
            "before sending. This tool assists but doesn't replace human judgment."
        )
    
    st.divider()
    
    if st.button("🔄 Start New Screening", use_container_width=True):
        for key in ['ranked_data', 'job_description', 'feedback_draft']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("ℹ️ How It Works")
    
    st.markdown("""
    ### Process:
    1. **Input** → Provide job description
    2. **Upload** → Add candidate resumes
    3. **Clean** → AI removes noise & structures
    4. **Rank** → Semantic matching analysis
    5. **Feedback** → Generate rejection emails
    6. **Review** → Human-in-the-loop approval
    
    ### Best Practices:
    - Detailed JD (200+ words)
    - 2-20 resumes per batch
    - Always human review feedback
    - Test with a few first
    """)
    
    st.divider()
    
    st.markdown("""
    ### Limitations:
    - Text-based PDFs only
    - Max 50 resumes per batch
    - Requires valid job description
    """)
    
    st.divider()
    
    if st.button("🔄 Clear All", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.caption("v1.0 | TrueFit ✨")

# ======================================================
