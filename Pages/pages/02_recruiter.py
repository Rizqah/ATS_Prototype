import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from ats_engine import (
    rank_candidates, 
    generate_compliant_feedback, 
    extract_text_from_pdf,
    clean_and_structure_resume
)

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="TrueFit - Recruiter Screening",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("👥 Candidate Screening Dashboard")
st.subheader("AI-powered resume ranking and feedback generation")

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

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF Format):", 
    type=['pdf'], 
    accept_multiple_files=True,
    help="Upload one or more resume PDFs"
)

if uploaded_files:
    st.info(f"📄 {len(uploaded_files)} resume(s) ready to process")

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
    with st.spinner("🔄 Processing resumes, cleaning with AI, and analyzing..."):
        
        candidate_list_for_ranking = []
        processing_status = st.status("Processing Progress", expanded=True)
        
        try:
            for idx, file in enumerate(uploaded_files, 1):
                with processing_status:
                    st.write(f"📖 [{idx}/{len(uploaded_files)}] Extracting: {file.name}")
                
                # Step 1: Extract raw text
                try:
                    raw_resume_text = extract_text_from_pdf(file)
                except ValueError as e:
                    st.warning(f"⚠️ Could not extract text from {file.name}: {str(e)}")
                    continue
                
                if not raw_resume_text or len(raw_resume_text.strip()) < 10:
                    st.warning(f"⚠️ {file.name} appears empty or unreadable")
                    continue
                
                with processing_status:
                    st.write(f"🧹 Cleaning: {file.name}")
                
                # Step 2: Clean and structure
                clean_resume_text = clean_and_structure_resume(raw_resume_text)
                
                if clean_resume_text.startswith("Error"):
                    st.warning(f"⚠️ Processing failed for {file.name}")
                    continue
                
                # Add to ranking list
                candidate_list_for_ranking.append({
                    "name": file.name.replace('.pdf', ''),
                    "resume": clean_resume_text
                })
                
                with processing_status:
                    st.write(f"✅ Processed: {file.name}")
            
            processing_status.update(label="✅ Extraction Complete", state="complete")
            
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
        
        df_display = pd.DataFrame([
            {
                'Rank': idx + 1,
                'Candidate': result['name'],
                'Match Score': f"{result['score'] * 100:.1f}%"
            }
            for idx, result in enumerate(ranking_results)
        ])
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
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