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

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="TrueFit - Candidate Resume Optimizer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Resume Optimizer")
st.subheader("See how your resume matches the job description and get AI-powered improvements")

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

resume_file = st.file_uploader(
    "Upload your resume (PDF):",
    type=['pdf'],
    help="Text-based PDF only (not scanned images)"
)

st.header("2️⃣ Paste the Job Description")

job_description = st.text_area(
    "Paste the full job description:",
    height=250,
    placeholder="Job title, responsibilities, required skills, qualifications, etc.",
    help="The more detailed, the better the analysis"
)

# ======================================================
# PROCESS & ANALYSIS
# ======================================================
if resume_file and job_description and st.button("🔍 Analyze Resume & Job Match", type="primary", use_container_width=True):
    
    # Validation
    if not job_description.strip() or len(job_description.strip()) < 50:
        st.error("❌ Job description too short (minimum 50 characters)")
        st.stop()
    
    with st.spinner("📖 Processing your resume..."):
        try:
            # Step 1: Extract text
            raw_resume = extract_text_from_pdf(resume_file)
            
            if not raw_resume or len(raw_resume.strip()) < 10:
                st.error("❌ Could not extract text from resume. Make sure it's a text-based PDF (not scanned).")
                st.stop()
            
            # Step 1.5: Validate it's actually a resume
            st.write("🔍 Validating resume document...")
            is_valid_resume, error_msg = validate_resume_document(raw_resume)
            
            if not is_valid_resume:
                st.error(error_msg)
                st.stop()
            
            # Step 2: Clean and structure
            st.write("🧹 Cleaning and structuring resume...")
            cleaned_resume = clean_and_structure_resume(raw_resume)
            
            if cleaned_resume.startswith("Error"):
                st.error(f"❌ {cleaned_resume}")
                st.stop()
            
            st.session_state.resume_cleaned = cleaned_resume
            
            # Step 3: Calculate match score
            st.write("📊 Calculating match score...")
            resume_vector = get_embedding(cleaned_resume)
            jd_vector = get_embedding(job_description)
            
            if resume_vector is None or jd_vector is None:
                st.error("❌ Could not analyze resume. Please try again.")
                st.stop()
            
            score = cosine_similarity([jd_vector], [resume_vector])[0][0]
            st.session_state.match_score = float(score)
            
            # Step 4: Generate improvement suggestions
            st.write("💡 Generating personalized improvement suggestions...")
            suggestions = generate_resume_improvement_suggestions(job_description, cleaned_resume)
            st.session_state.improvement_suggestions = suggestions
            
        except Exception as e:
            st.error(f"❌ Error processing resume: {str(e)}")
            st.stop()

# ======================================================
# RESULTS DISPLAY
# ======================================================
if st.session_state.match_score is not None:
    st.divider()
    st.header("📊 Analysis Results")
    
    # Match score with visualization
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        score_percent = st.session_state.match_score * 100
        
        # Color coding based on score
        if score_percent >= 80:
            color = "🟢"
            status = "Excellent Match"
        elif score_percent >= 60:
            color = "🟡"
            status = "Good Match"
        elif score_percent >= 40:
            color = "🟠"
            status = "Fair Match"
        else:
            color = "🔴"
            status = "Needs Work"
        
        # Display metric
        st.metric(
            label="Overall Match Score",
            value=f"{score_percent:.1f}%",
            delta=f"{status} {color}"
        )
    
    # Interpretation guide
    st.markdown("""
    **What does this score mean?**
    - **80-100%**: Your resume aligns very well. You're a strong candidate.
    - **60-79%**: Good alignment. Consider the suggestions below.
    - **40-59%**: Fair alignment. Improvements recommended.
    - **Below 40%**: Significant gaps. Review suggestions carefully.
    """)
    
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