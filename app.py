import streamlit as st
import pandas as pd


from ats_engine import (
    rank_candidates, 
    generate_compliant_feedback, 
    extract_text_from_pdf,
    extract_text_from_docx, # <--- NEW IMPORT
    clean_and_structure_resume 
)
st.set_page_config(page_title="Compliant ATS Matcher", layout="wide")
st.title("🤖 Compliant ATS Prototype")
st.subheader("Now using AI to clean and structure resumes for higher accuracy.")

# --- 1. INPUT AREA ---
st.header("1. Define the Job & Upload Resumes")
job_description = st.text_area(
    "Paste the Full Job Description Here:", 
    height=200,
    value="We need a Chief Financial Officer (CFO). Must have CPA certification. Experience managing large corporate budgets. Strategic financial planning."
)



uploaded_files = st.file_uploader(
    "Upload Resumes (PDF and DOCX supported):", 
    type=['pdf', 'docx'], # <--- UPDATED TYPES
    accept_multiple_files=True
)

# --- 2. RANKING ENGINE TRIGGER ---

if uploaded_files and st.button("🚀 Run Ranking Engine", type="primary"):
    
    with st.spinner("Processing files, **cleaning with AI**, and running analysis..."):
        
        candidate_list_for_ranking = []
        
       # In app.py, replace the existing loop inside the ranking button:
# for file in uploaded_files: ...

for file in uploaded_files:
    file_extension = file.name.split('.')[-1].lower()
    raw_resume_text = ""

    if file_extension == 'pdf':
        raw_resume_text = extract_text_from_pdf(file)
    elif file_extension == 'docx':
        # The file stream needs to be reset for the docx library to read it
        file.seek(0)
        raw_resume_text = extract_text_from_docx(file)
    else:
        # Skip unsupported formats (like the old .doc, which are tricky)
        st.warning(f"Skipping unsupported file type: {file.name}")
        continue 
    
    if raw_resume_text:
        # Step 2: Clean and Structure the text with AI
        clean_resume_text = clean_and_structure_resume(raw_resume_text)
        
        # Add the clean text for ranking and feedback
        candidate_list_for_ranking.append({
            "name": file.name,
            "resume": clean_resume_text
        })

        st.info(f"Successfully processed and cleaned {len(candidate_list_for_ranking)} resumes.")
        
        # Call the ranking function with the clean, structured data
        ranking_results = rank_candidates(job_description, candidate_list_for_ranking)
        
        # Display results (unchanged)
        df = pd.DataFrame(ranking_results)
        df['Score'] = (df['score'] * 100).round(1).astype(str) + '%'
        df = df[['name', 'Score']].rename(columns={'name': 'Candidate'})
        
        st.success("Ranking Complete!")
        st.dataframe(df, use_container_width=True)
        
        st.session_state['ranked_data'] = ranking_results
        
# --- 3. FEEDBACK ENGINE TRIGGER (Unchanged) ---
# ... [Omitted code remains the same as previous app.py] ...
if 'ranked_data' in st.session_state:
    st.header("3. Generate Compliant Feedback")
    candidate_to_reject = st.session_state['ranked_data'][-1]
    st.info(f"Targeting **{candidate_to_reject['name']}** (Lowest Score) for Rejection Feedback.")
    if st.button(f"✍️ Draft Email for {candidate_to_reject['name']}"):
        st.warning("Generating Legally Compliant Draft...")
        feedback_draft = generate_compliant_feedback(
            job_description, 
            candidate_to_reject['resume']
        )
        st.subheader("Final Draft (Human-in-the-Loop Review)")
        st.code(feedback_draft, language='text')
        if st.checkbox("Recruiter Review: I confirm this feedback is safe and accurate."):
            st.success("✅ Email ready to send! Liability risk minimized.")