import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import io
import streamlit as st
from pypdf import PdfReader
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# ======================================================
# 1. LOAD ENV FILE & API KEY SETUP
# ======================================================
# Load variables from .env file
load_dotenv()

def setup_openai_client():
    """Safely setup OpenAI client with proper error handling."""
    try:
        # Try .env file first (for local development)
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Fall back to Streamlit secrets (for production/cloud deployment)
        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY")
            except Exception:
                pass
        
        # If still no key, show error
        if not api_key:
            st.error(
                "❌ OpenAI API Key not found.\n\n"
                "Please ensure one of the following:\n"
                "1. Add `OPENAI_API_KEY=sk-...` to your `.env` file in the project root\n"
                "2. Or set it in Streamlit secrets for cloud deployment"
            )
            st.stop()
        
        return openai.OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
        st.stop()

client = setup_openai_client()

# ======================================================
# 2. RESUME VALIDATION FUNCTION
# ======================================================
def validate_resume_document(raw_text: str) -> tuple[bool, str]:
    """
    Validates if the uploaded document is actually a resume/CV.
    
    Args:
        raw_text: Extracted text from PDF
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    system_prompt = """
    You are a document classifier. Determine if the provided text is a resume/CV.
    
    INSTRUCTIONS:
    1. Check for typical resume sections: EXPERIENCE, SKILLS, EDUCATION, SUMMARY, OBJECTIVE, CONTACT
    2. Check for job titles, company names, dates, educational institutions
    3. Resumes should have work history or educational background
    
    Respond with ONLY "YES" if it's a resume, or "NO" if it's not.
    """
    
    try:
        # Use first 1000 chars to validate quickly
        sample_text = raw_text[:1000]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": sample_text}
            ],
            temperature=0.0,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().upper()
        
        if "YES" in result:
            return True, ""
        else:
            return False, "❌ This doesn't appear to be a resume/CV. Please upload a valid resume with work experience, education, and skills."
            
    except Exception as e:
        # If validation fails, let it through but warn user
        return True, ""

# ======================================================
# 3. DOCUMENT PARSING FUNCTION
# ======================================================
def extract_text_from_pdf(uploaded_file) -> str:
    """
    Reads a Streamlit UploadedFile object and extracts raw text.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Extracted text from PDF
        
    Raises:
        ValueError: If file is empty or not a valid PDF
    """
    try:
        if not uploaded_file:
            raise ValueError("No file provided")
            
        file_bytes = uploaded_file.read()
        if not file_bytes:
            raise ValueError("Uploaded file is empty")
            
        reader = PdfReader(io.BytesIO(file_bytes))
        if not reader.pages:
            raise ValueError("PDF has no pages")
            
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting PDF text: {str(e)}")

# ======================================================
# 4. AI CLEANING & STRUCTURING FUNCTION
# ======================================================
def clean_and_structure_resume(raw_resume_text: str) -> str:
    """
    Uses LLM to clean noise and apply section tags to text.
    
    Args:
        raw_resume_text: Raw text extracted from resume PDF
        
    Returns:
        Cleaned and structured resume text with tags
    """
    if not raw_resume_text or not raw_resume_text.strip():
        return "Error: Empty resume text provided"
    
    system_prompt = """
    You are an expert Document Processor. Your task is to clean up raw, noisy text extracted from a resume.

    INSTRUCTIONS:
    1. Remove all noise: page numbers, headers, footers, repetitive lines, and obvious contact information (phone numbers, email addresses, URLs).
    2. Structure the remaining core content using the following tags only: [SUMMARY], [SKILLS], [EXPERIENCE], [EDUCATION].
    3. Return only the cleaned and tagged text. DO NOT add any extra commentary or introductory phrases.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_resume_text}
            ],
            temperature=0.0,
            max_tokens=2000
        )
        cleaned_text = response.choices[0].message.content
        
        if not cleaned_text:
            return "Error: No content returned from cleaning"
            
        return cleaned_text
        
    except openai.APIError as e:
        return f"OpenAI API Error during cleaning: {str(e)}"
    except Exception as e:
        return f"Unexpected error during cleaning: {str(e)}"

# ======================================================
# 5. EMBEDDING & RANKING ENGINE FUNCTIONS
# ======================================================
def get_embedding(text: str) -> Optional[List[float]]:
    """
    Converts text into a numeric vector for ranking.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector or None if error occurs
    """
    if not text or not text.strip():
        return None
        
    try:
        text = text.replace("\n", " ").strip()
        # Truncate to avoid token limits (max ~8000 tokens for embeddings)
        text = text[:8000]
        
        response = client.embeddings.create(
            input=[text], 
            model="text-embedding-3-small"
        )
        
        if not response.data:
            return None
            
        return response.data[0].embedding
        
    except openai.APIError as e:
        st.warning(f"Embedding API error: {str(e)}")
        return None
    except Exception as e:
        st.warning(f"Error generating embedding: {str(e)}")
        return None

def rank_candidates(
    job_description: str, 
    candidates_data: List[Dict[str, str]]
) -> List[Dict[str, any]]:
    """
    Ranks candidates based on semantic similarity to the job description.
    
    Args:
        job_description: The job posting text
        candidates_data: List of dicts with 'name' and 'resume' keys
        
    Returns:
        Sorted list of candidates with scores
    """
    if not job_description or not job_description.strip():
        st.error("Job description is empty")
        return []
        
    if not candidates_data or not isinstance(candidates_data, list):
        st.error("Invalid candidates data")
        return []
    
    try:
        jd_vector = get_embedding(job_description)
        if jd_vector is None:
            st.error("Failed to embed job description")
            return []
        
        scored_candidates = []
        
        for candidate in candidates_data:
            # Validate candidate data structure
            if not isinstance(candidate, dict) or 'resume' not in candidate or 'name' not in candidate:
                st.warning(f"Skipping invalid candidate record: {candidate}")
                continue
            
            resume_vector = get_embedding(candidate['resume'])
            
            if resume_vector is None:
                st.warning(f"Could not embed resume for {candidate['name']}")
                continue
            
            # Calculate similarity score
            score = cosine_similarity([jd_vector], [resume_vector])[0][0]
            
            scored_candidates.append({
                "name": candidate['name'],
                "score": float(score),
                "resume": candidate['resume']
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates
        
    except Exception as e:
        st.error(f"Error during ranking: {str(e)}")
        return []

# ======================================================
# 6. GENERATE IMPROVEMENT SUGGESTIONS
# ======================================================
def generate_resume_improvement_suggestions(
    job_description: str, 
    candidate_resume: str
) -> str:
    """
    Generates specific, actionable suggestions for improving a resume for a specific job.
    FOR CANDIDATES - helps them improve their resume.
    
    Args:
        job_description: The job posting
        candidate_resume: The candidate's resume (cleaned/structured)
        
    Returns:
        Resume improvement suggestions
    """

    if not job_description or not job_description.strip():
        return "Error: Job description is empty"
        
    if not candidate_resume or not candidate_resume.strip():
        return "Error: Candidate resume is empty"
    
    system_prompt = """
    You are an Expert Resume Coach. Your goal is to help candidates IMPROVE their resumes to match a specific job.
    
    INSTRUCTIONS:
    1. **Identify Gaps**: Compare the resume to the job description. What skills/experience does the job require that the resume doesn't clearly show?
    2. **Be Specific**: Don't say "add more skills" - say "The job emphasizes Python for data automation. Your Python experience is mentioned but lacks detail. Add a specific project where you used Python to automate a process."
    3. **Give Actionable Steps**: Provide 3-5 concrete, specific suggestions for how to rewrite or expand existing sections.
    4. **Focus on Content, Not Format**: Suggest what to ADD, REMOVE, or REWRITE in the resume content itself.
    5. **Highlight Strengths**: Also mention what's already strong in the resume for this specific role.
    
    Format your response as a numbered list of improvements.
    """

    user_prompt = f"""
    JOB DESCRIPTION:
    {job_description}

    CANDIDATE'S RESUME:
    {candidate_resume}

    Provide 3-5 specific, actionable suggestions to improve this resume for this exact job.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        feedback = response.choices[0].message.content
        if not feedback:
            return "Error: No suggestions generated"
            
        return feedback
        
    except openai.APIError as e:
        return f"OpenAI API Error: {str(e)}"
    except Exception as e:
        return f"Error generating suggestions: {str(e)}"

# ======================================================
# 6. FEEDBACK ENGINE FUNCTIONS
# ======================================================
def generate_compliant_feedback(
    job_description: str, 
    candidate_resume: str
) -> str:
    """
    Generates legally compliant, constructive rejection feedback.
    
    Args:
        job_description: The job posting
        candidate_resume: The candidate's resume (cleaned/structured)
        
    Returns:
        Rejection email text
    """
    if not job_description or not job_description.strip():
        return "Error: Job description is empty"
        
    if not candidate_resume or not candidate_resume.strip():
        return "Error: Candidate resume is empty"
    
    system_prompt = """
    You are an Expert Resume Consultant and a Compliance Officer. Your primary goal is to provide **highly specific, tangible, and constructive feedback** based *only* on the content of the resume and the requirements of the job description (JD).

    INSTRUCTIONS FOR TANGIBLE FEEDBACK:
    1. **Analyze the Weak Link:** Identify the single biggest gap where the candidate mentioned a required hard skill but failed to demonstrate sufficient depth, context, or quantifiable results required by the JD.
    2. **Focus on Specificity:** Instead of saying "lacks Python," say, "lacks demonstrated experience using Python for **data pipeline automation** as the JD requires."
    3. **Provide Actionable Advice:** Offer one concrete, actionable suggestion for how they can re-write or strengthen the *existing* experience on their resume to better match the JD's focus (e.g., "Add metrics showing efficiency gains").

    THE "RED ZONE" (STRICTLY FORBIDDEN—Legal Compliance):
    - Do NOT mention: Personality, tone, enthusiasm, "culture fit," age, gender, or soft skills.
    
    THE "GREEN ZONE" (ONLY USE THESE):
    - Hard Skills, Objective Metrics, Demonstrated Specificity, and Mismatched Depth.

    Write a polite and legally safe rejection email using this structured, tangible advice.
    """

    user_prompt = f"""
    JOB DESCRIPTION:
    {job_description}

    CLEANED CANDIDATE RESUME:
    {candidate_resume}

    Write the rejection email.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        feedback = response.choices[0].message.content
        if not feedback:
            return "Error: No feedback generated"
            
        return feedback
        
    except openai.APIError as e:
        return f"OpenAI API Error: {str(e)}"
    except Exception as e:
        return f"Error generating feedback: {str(e)}"


# ======================================================
# 7. PROFILE-TO-JD MATCHING & CV OPTIMIZATION
# ======================================================
def match_profile_to_jd(profile, work_experiences, achievements_by_experience, skills, job_description):
    """
    Match entire applicant profile against job description.

    Returns:
        dict with match_score and analysis
    """
    try:
        profile_text = f"""
        {profile.get('full_name', '')}

        PROFESSIONAL SUMMARY:
        {profile.get('professional_summary', '')}

        SKILLS:
        {', '.join([s.get('skill_name', '') for s in skills])}

        WORK EXPERIENCE:
        """

        for exp in work_experiences:
            profile_text += f"""
            {exp.get('position', '')} at {exp.get('company', '')}
            {exp.get('description', '')}
            """
            exp_id = exp.get('id')
            if exp_id and exp_id in achievements_by_experience:
                for ach in achievements_by_experience[exp_id]:
                    profile_text += f"- {ach.get('achievement', '')} {ach.get('metric', '')}\n"

        profile_vector = get_embedding(profile_text)
        jd_vector = get_embedding(job_description)

        if not profile_vector or not jd_vector:
            raise Exception("Could not generate embeddings")

        score = cosine_similarity([jd_vector], [profile_vector])[0][0]
        match_score = float(score)

        system_prompt = """
        You are an expert recruiter analyzing candidate profile against job requirements.

        INSTRUCTIONS:
        1. Identify top 3 matching areas between profile and JD
        2. Identify top 3 gaps/missing skills
        3. Provide brief recommendation (1-2 sentences)

        Format as:
        **Matching Strengths:**
        - Strength 1
        - Strength 2
        - Strength 3

        **Skills Gaps:**
        - Gap 1
        - Gap 2
        - Gap 3

        **Recommendation:**
        [Brief 1-2 sentence recommendation]
        """

        user_prompt = f"""
        CANDIDATE PROFILE:
        {profile_text}

        JOB DESCRIPTION:
        {job_description}

        Analyze this match.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        analysis = response.choices[0].message.content
        return {"match_score": match_score, "analysis": analysis}

    except Exception as e:
        st.error(f"Error matching profile to JD: {str(e)}")
        return {"match_score": 0.0, "analysis": "Error generating analysis"}


def optimize_cv_for_jd(profile_text, job_description, work_experiences_text):
    """
    Use AI to rewrite CV content optimized for JD.
    Expands on relevant skills, reorders achievements, rewrites summary.

    Returns:
        str with optimized content (or error message)
    """
    try:
        system_prompt = """
        You are an expert CV optimizer and recruiter.

        TASK: Rewrite the CV content to better match the job description.

        INSTRUCTIONS:
        1. **Rewrite Professional Summary**: Create a new summary that:
           - Highlights skills/experience relevant to JD
           - Uses keywords from the job description
           - Shows alignment with role requirements

        2. **Expand Work Experience**: For each job, enhance descriptions to:
           - Add relevant keywords from JD
           - Expand on achievements showing impact
           - Reorder bullets by relevance to JD
           - Include specific metrics/results

        3. **Reorder Skills**: Prioritize skills that:
           - Match JD requirements
           - Appear in job description
           - Are most relevant to the role

        Return ONLY the rewritten content in this format:

        OPTIMIZED_SUMMARY:
        [Rewritten 2-3 sentence summary]

        OPTIMIZED_EXPERIENCE:
        [For each experience, in format:]
        Position: [title]
        Company: [company]
        Description: [expanded description]
        Achievements:
        - [reordered/expanded achievement 1]
        - [reordered/expanded achievement 2]

        OPTIMIZED_SKILLS:
        [Comma-separated list, ordered by relevance]
        """

        user_prompt = f"""
        JOB DESCRIPTION:
        {job_description}

        CURRENT CV CONTENT:
        {profile_text}

        WORK EXPERIENCE DETAILS:
        {work_experiences_text}

        Optimize this CV for the job description.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=2000
        )

        optimized_content = response.choices[0].message.content
        return optimized_content

    except Exception as e:
        return f"Error optimizing CV: {str(e)}"