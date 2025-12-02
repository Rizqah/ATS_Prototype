import streamlit as st
import pandas as pd
import os
import docx
import openai
from ats_engine import (
    rank_candidates,
    generate_compliant_feedback,
    extract_text_from_pdf,
    # NOTE: You must ensure extract_text_from_docx is available in ats_engine.py
    extract_text_from_docx, 
    clean_and_structure_resume,
    compute_fit_score,
    rewrite_resume, # Restored rewrite_resume for Applicant mode
)

# --- API Key Setup ---
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") 
    if not OPENAI_API_KEY:
        st.error("OpenAI API Key not found. Please set it in st.secrets or environment variables.")
        st.stop()
        
client = openai.OpenAI(api_key=OPENAI_API_KEY)


# --- Utility Function for Applicant List Feedback (New) ---
def generate_applicant_list_feedback(job_description, cleaned_resume):
    """Generates structured, list-based feedback for the applicant."""
    
    system_prompt = (
        "You are an Expert ATS Consultant providing direct, objective, and actionable feedback "
        "to a job applicant. Based ONLY on the provided Job Description and Resume content, "
        "generate a concise, two-section Markdown list. "
        "Section 1: '### 🚀 Top 3 Strengths (Alignment)' "
        "Section 2: '### 🎯 Top 3 Areas for Improvement (Gaps)' "
        "Focus strictly on hard skills, tools, and quantifiable experience missing or weakly stated in the resume. "
        "Provide bullet points under each section."
    )
    user_prompt = f"Job Description:\n---\n{job_description}\n---\nCleaned Resume Content:\n---\n{cleaned_resume}"

    # Use a faster, capable model for chat completions
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content


# --- Main UI and Role Setup ---

st.set_page_config(page_title="Compliant ATS Matcher", layout="wide")

# --- ROLE SELECTION (Sidebar) ---
with st.sidebar:
    st.title("ATS Prototype")
    role = st.radio("I am a:", ["Recruiter", "Applicant"])

st.title("🤖 Compliant ATS Prototype")


# =========================================
# RECRUITER MODE (Kept with Tabs and Email Feedback)
# =========================================
if role == "Recruiter":
    st.subheader("Recruiter Dashboard – Rank Candidates & Generate Compliant Feedback")

    # Define the tabs to manage the workflow
    tab1, tab2, tab3 = st.tabs(["⚙️ Setup & Upload", "📊 Ranking & Scores", "📧 Feedback Generator"])

    # Initialize session state for storing results across tabs
    if 'ranked_data' not in st.session_state:
        st.session_state['ranked_data'] = None
        st.session_state['job_description'] = ""

    # --- TAB 1: Setup & Upload ---
    with tab1:
        st.header("1. Define Job & Gather Resumes")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Job Description")
            job_description = st.text_area(
                "Paste the Full Job Description Here:", 
                height=300,
                key="job_desc_input_recruiter",
                value=st.session_state.get('job_description', "We need a Chief Financial Officer (CFO). Must have CPA certification. Experience managing large corporate budgets. Strategic financial planning."),
            )
            st.session_state['job_description'] = job_description


        with col2:
            st.subheader("Candidate Resumes")
            uploaded_files = st.file_uploader(
                "Upload Resumes (PDF, DOCX, and DOC supported):", 
                type=['pdf', 'docx', 'doc'], 
                accept_multiple_files=True
            )

        st.markdown("---")
        
        # Ranking Trigger Button
        if uploaded_files and st.button("🚀 Run Ranking Engine", type="primary"):
            if not job_description:
                st.error("Please paste the Job Description before running the engine.")
                st.stop()
                
            with st.spinner("Processing files, cleaning with AI, and running Vector Embedding analysis..."):
                
                candidate_list_for_ranking = []
                
                for file in uploaded_files:
                    file_extension = file.name.split('.')[-1].lower()
                    raw_resume_text = ""

                    # Step 1: Extract RAW text (Multi-format handling)
                    if file_extension == 'pdf':
                        raw_resume_text = extract_text_from_pdf(file)
                    elif file_extension == 'docx':
                        file.seek(0)
                        raw_resume_text = extract_text_from_docx(file)
                    elif file_extension == 'doc':
                        st.error(f"⚠️ **Skipping {file.name}:** The legacy '.doc' format is unsupported on this cloud environment. Please convert this file to a modern '.docx' or '.pdf' and re-upload.")
                        continue
                    else:
                        st.warning(f"Skipping unsupported file type: {file.name}")
                        continue 
                    
                    if raw_resume_text:
                        # Step 2: Clean and Structure the text with AI
                        clean_resume_text = clean_and_structure_resume(raw_resume_text)
                        
                        candidate_list_for_ranking.append({
                            "name": file.name,
                            "resume": clean_resume_text
                        })
                
                if candidate_list_for_ranking:
                    st.info(f"Successfully processed and cleaned {len(candidate_list_for_ranking)} resumes.")
                    
                    # Step 3: Call the ranking function
                    ranking_results = rank_candidates(job_description, candidate_list_for_ranking)
                    st.session_state['ranked_data'] = ranking_results
                    st.success("Ranking Complete! See the **Ranking & Scores** tab.")
                else:
                    st.warning("No valid files were processed.")
            
    # --- TAB 2: Ranking & Scores ---
    with tab2:
        st.header("2. Candidate Ranking Results")

        if st.session_state.get('ranked_data') is not None:
            ranking_results = st.session_state['ranked_data']
            
            df = pd.DataFrame(ranking_results)
            df['Score'] = (df['score'] * 100).round(1).astype(str) + '%'
            
            df_display = df[['name', 'Score']].rename(columns={'name': 'Candidate'})
            
            st.subheader("Semantic Match Scoreboard")
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            st.info("The table is sorted by score (highest match first).")

            st.subheader("Review Cleaned Resume Text")
            candidate_names = [r['name'] for r in ranking_results]
            selected_name = st.selectbox("Select Candidate to Review:", candidate_names)
            
            selected_candidate = next((r for r in ranking_results if r['name'] == selected_name), None)
            
            if selected_candidate:
                with st.expander(f"Cleaned Resume Text for {selected_name}"):
                    st.code(selected_candidate['resume'], language='markdown')

        else:
            st.warning("Please run the ranking engine in the 'Setup & Upload' tab first.")

    # --- TAB 3: Feedback Generator ---
    with tab3:
        st.header("3. Generate Compliant Rejection Feedback")

        if st.session_state.get('ranked_data') is not None:
            ranking_results = st.session_state['ranked_data']
            job_description = st.session_state['job_description']
            
            # Target the lowest scoring candidate for rejection (last element in sorted list)
            candidate_to_reject = ranking_results[-1]
            
            st.info(f"Targeting **{candidate_to_reject['name']}** (Lowest Score: {(candidate_to_reject['score'] * 100):.1f}%) for Compliant Feedback.")
            
            if st.button(f"✍️ Draft Email for {candidate_to_reject['name']}"):
                
                with st.spinner("Generating Tangible, Legally Compliant Draft..."):
                    
                    feedback_draft = generate_compliant_feedback(
                        job_description, 
                        candidate_to_reject['resume']
                    )
                
                st.subheader("Final Draft (Recruiter Review Required)")
                st.code(feedback_draft, language='text')

                if st.checkbox("Recruiter Review: I confirm this feedback is safe and accurate."):
                    st.success("✅ Email ready to send! Liability risk minimized.")
                    st.download_button(
                        label="Download Draft",
                        data=feedback_draft,
                        file_name=f"Rejection_Email_{candidate_to_reject['name'].replace('.', '_')}.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("Please run the ranking engine in the 'Setup & Upload' tab first.")


# =========================================
# APPLICANT MODE (Restored List Feedback & Resume Rewrite)
# =========================================
elif role == "Applicant":
    st.subheader("Applicant Dashboard – Check Fit, Get List Feedback, & Optimise")

    st.markdown(
        "Upload your resume and paste the job description to get your ATS fit score, "
        "a list of actionable improvements, and a suggested AI-optimised resume version."
    )

    col1, col2 = st.columns(2)

    with col1:
        jd_applicant = st.text_area(
            "Paste the Job Description:",
            height=260,
            key="jd_applicant_input",
            placeholder="Paste the job description you are applying for...",
        )

    with col2:
        # Multi-format support added
        resume_file = st.file_uploader(
            "Upload Your Resume (PDF, DOCX, or DOC preferred):",
            type=["pdf", "docx", "doc"],
            key="applicant_uploader"
        )
        manual_resume_text = st.text_area(
            "Or paste your resume text here:",
            height=260,
            key="manual_applicant_text",
            placeholder="If you don't have a file, paste your resume content here...",
        )

    analyze_button = st.button("🔍 Analyse & Improve My Resume", type="primary")

    if analyze_button:
        if not jd_applicant:
            st.error("Please paste the Job Description first.")
            st.stop()
        
        # --- File Extraction Logic (Multi-Format) ---
        raw_resume = ""
        if resume_file is not None:
            file_extension = resume_file.name.split('.')[-1].lower()
            if file_extension == 'pdf':
                raw_resume = extract_text_from_pdf(resume_file)
            elif file_extension == 'docx':
                resume_file.seek(0)
                raw_resume = extract_text_from_docx(resume_file)
            elif file_extension == 'doc':
                st.error("⚠️ The legacy '.doc' format is unsupported on this cloud environment. Please convert this file to a modern '.docx' or '.pdf' and re-upload.")
                st.stop()
        elif manual_resume_text.strip():
            raw_resume = manual_resume_text.strip()
        
        if not raw_resume:
            st.error("Please upload a resume file or paste your resume text.")
            st.stop()

        with st.spinner("Analysing your resume and generating improvements..."):
            
            # 1. Clean and structure the text
            cleaned_resume = clean_and_structure_resume(raw_resume)

            # 2. Compute fit score
            score = compute_fit_score(jd_applicant, cleaned_resume)

            # 3. Generate list-based feedback (NEW/REPLACED)
            applicant_feedback_list = generate_applicant_list_feedback(jd_applicant, cleaned_resume)

            # 4. Rewrite resume (RESTORED)
            optimised_resume_md = rewrite_resume(jd_applicant, cleaned_resume)

        # --- OUTPUT SECTION ---
        st.success("Analysis complete! Scroll down to see your results.")

        # Show fit score
        st.header("1. ATS Fit Score")
        score_percent = max(0.0, min(1.0, score)) * 100 
        col_a, col_b = st.columns([1, 3])
        with col_a:
            st.metric("Overall Match", f"{score_percent:.1f}%")
        with col_b:
            st.progress(score_percent / 100.0)

        st.caption(
            "This score is based on how closely your resume aligns with the job description."
        )

        # Show List Feedback (NEW)
        st.header("2. Actionable Feedback List")
        st.markdown(
            "Use these objective points to quickly edit and improve your resume's alignment."
        )
        st.markdown(applicant_feedback_list)
        
        # Show optimised resume (RESTORED)
        st.header("3. Suggested Optimised Resume")
        st.markdown(
            "This is an AI-enhanced version of your content focused on the key terms in the JD. "
            "**Review and verify carefully before using.**"
        )
        st.code(optimised_resume_md, language="markdown")

        # Optional download button (simple text version)
        st.download_button(
            label="📩 Download Optimised Resume (Markdown)",
            data=optimised_resume_md,
            file_name="optimised_resume.md",
            mime="text/markdown",
        )