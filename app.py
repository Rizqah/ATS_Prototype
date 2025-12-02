import streamlit as st
import pandas as pd
from docx import Document
from ats_engine import (
    rank_candidates,
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_and_structure_resume,
    compute_fit_score,
    rewrite_resume,
    client,  # reuse OpenAI client from ats_engine
)


# ============================================================================
# LEGAL COMPLIANCE MODULE
# ============================================================================

class FeedbackComplianceChecker:
    """
    Ensures all generated feedback complies with employment law.
    Screens for prohibited terms and discriminatory language.
    """
    
    def __init__(self):
        # Prohibited terms that could indicate discrimination
        self.prohibited_terms = {
            # Age-related
            'age', 'young', 'old', 'mature', 'recent graduate', 'retirement',
            'youthful', 'elderly', 'senior', 'junior', 'experienced professional',
            
            # National origin
            'native', 'foreign', 'accent', 'immigrant', 'citizenship',
            'visa', 'work authorization', 'country of origin',
            
            # Gender
            'he', 'she', 'his', 'her', 'him', 'gender', 'man', 'woman',
            'masculine', 'feminine', 'lady', 'gentleman',
            
            # Disability
            'disability', 'handicap', 'disabled', 'able-bodied', 'medical condition',
            'health', 'accommodation',
            
            # Personal characteristics
            'culture fit', 'personality', 'enthusiasm', 'attitude', 'energy level',
            'passion', 'motivated', 'team player', 'ambitious',
            
            # Family/marital status
            'family', 'children', 'married', 'single', 'parent', 'spouse',
            'maternity', 'paternity',
            
            # Religion
            'religious', 'religion', 'faith', 'church', 'mosque', 'temple',
            
            # Race/ethnicity (contextual - may have false positives)
            'diverse', 'diversity', 'minority', 'majority',
            
            # Other protected characteristics
            'pregnant', 'pregnancy', 'veteran', 'military service',
        }
        
        # Context-aware exceptions (these are OK in specific contexts)
        self.allowed_contexts = {
            'experience': ['years of experience', 'work experience'],
            'technical': ['native code', 'native app', 'native development'],
        }
    
    def check_compliance(self, feedback_text: str) -> dict:
        """
        Check if feedback contains prohibited terms.
        
        Returns:
            dict with keys:
                - compliant (bool): Whether feedback passed
                - violations (list): List of found prohibited terms
                - severity (str): 'none', 'low', 'high'
                - recommendation (str): What to do next
        """
        feedback_lower = feedback_text.lower()
        violations = []
        
        for term in self.prohibited_terms:
            if term in feedback_lower:
                # Check if it's in an allowed context
                is_allowed = False
                for context_terms in self.allowed_contexts.values():
                    for context in context_terms:
                        if context in feedback_lower and term in context:
                            is_allowed = True
                            break
                
                if not is_allowed:
                    violations.append(term)
        
        # Determine severity
        severity = 'none'
        if violations:
            # High severity terms
            high_severity = {'age', 'gender', 'disability', 'race', 'religion', 
                           'pregnant', 'family', 'married', 'children'}
            if any(term in high_severity for term in violations):
                severity = 'high'
            else:
                severity = 'low'
        
        # Generate recommendation
        if severity == 'none':
            recommendation = "Feedback passed compliance check."
        elif severity == 'low':
            recommendation = "Review feedback for soft skills language. Consider focusing only on technical qualifications."
        else:
            recommendation = "CRITICAL: Feedback contains prohibited discriminatory language. Do not send. Regenerate with stricter constraints."
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'severity': severity,
            'recommendation': recommendation
        }
    
    def sanitize_feedback(self, feedback_text: str) -> str:
        """
        Attempt to automatically remove problematic phrases.
        Note: This is a basic implementation. Human review still required.
        """
        lines = feedback_text.split('\n')
        sanitized_lines = []
        
        for line in lines:
            line_lower = line.lower()
            has_violation = any(term in line_lower for term in self.prohibited_terms)
            
            if not has_violation:
                sanitized_lines.append(line)
            else:
                # Skip this line and add a comment
                sanitized_lines.append("<!-- Line removed for compliance -->")
        
        return '\n'.join(sanitized_lines)


# ============================================================================
# FEEDBACK GENERATION FUNCTIONS
# ============================================================================

def generate_compliant_feedback_for_recruiter(job_description: str, cleaned_resume: str, 
                                              max_retries: int = 2) -> dict:
    """
    Generate compliant rejection feedback for recruiters to review.
    Includes automatic compliance checking and retry logic.
    
    Args:
        job_description: Full JD text
        cleaned_resume: Cleaned/structured resume text
        max_retries: Number of retries if compliance violations found
        
    Returns:
        dict with keys:
            - feedback: Generated feedback text (or None if failed)
            - compliant: Whether feedback passed compliance
            - violations: List of prohibited terms found
            - severity: Compliance severity level
            - recommendation: Action recommendation
            - error: Error message if generation failed
    """
    
    checker = FeedbackComplianceChecker()
    
    system_prompt = """You are a Technical Recruitment Specialist generating objective, skills-based feedback for candidates.

YOUR TASK:
Write a professional rejection email that provides specific, actionable feedback based ONLY on technical qualifications and job requirements.

STRICT REQUIREMENTS:

1. **Focus ONLY on Technical Skills & Experience**:
   - Specific technical skills mentioned in JD but missing/weak in resume
   - Years of experience with specific technologies
   - Certifications or credentials required by JD
   - Quantifiable metrics and results
   - Depth of expertise in required domains

2. **Be Specific and Evidence-Based**:
   ✓ "The role requires 5+ years of experience with AWS cloud architecture, but your resume demonstrates 2 years"
   ✓ "The JD specifies expertise in React and TypeScript; your resume shows jQuery and vanilla JavaScript"
   ✗ "You don't seem like a good fit for our team"
   ✗ "We're looking for someone with more enthusiasm"

3. **Provide Constructive Guidance**:
   - Suggest specific skills to develop
   - Recommend certifications that would strengthen candidacy
   - Point to gaps in quantifiable achievements

4. **ABSOLUTE PROHIBITIONS** (Legal Compliance):
   NEVER mention or reference:
   - Age, generation, or career stage (young/old/experienced/recent graduate)
   - Gender, pronouns, or gender-related terms
   - Race, ethnicity, national origin, or accent
   - Disability, health, or medical conditions
   - Family status, marital status, or children
   - Religion or religious practices
   - Personal characteristics: personality, culture fit, enthusiasm, attitude, energy
   - Soft skills: team player, passionate, motivated (focus only on demonstrated technical skills)

5. **Email Structure**:
   - Professional greeting
   - Brief thank you for application
   - 2-3 specific technical gaps (with JD references)
   - Constructive closing with encouragement
   - Professional sign-off

Keep tone respectful, objective, and focused entirely on job-related technical qualifications."""

    user_prompt = f"""JOB DESCRIPTION:
{job_description}

---

CANDIDATE RESUME:
{cleaned_resume}

---

Generate a professional rejection email following all requirements above. Focus exclusively on technical qualifications and objective criteria."""

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistent, professional output
                max_tokens=1000
            )
            
            feedback = response.choices[0].message.content
            
            # Check compliance
            compliance_result = checker.check_compliance(feedback)
            
            if compliance_result['compliant']:
                return {
                    'feedback': feedback,
                    'compliant': True,
                    'violations': [],
                    'severity': 'none',
                    'recommendation': 'Feedback passed compliance check.',
                    'error': None
                }
            else:
                # If not compliant and we have retries left, try again
                if attempt < max_retries:
                    # Add more explicit instructions for next attempt
                    system_prompt += f"\n\nIMPORTANT: Previous attempt included prohibited terms: {compliance_result['violations']}. Completely avoid these concepts."
                    continue
                else:
                    # Out of retries, return non-compliant feedback with warning
                    return {
                        'feedback': feedback,
                        'compliant': False,
                        'violations': compliance_result['violations'],
                        'severity': compliance_result['severity'],
                        'recommendation': compliance_result['recommendation'],
                        'error': None
                    }
                    
        except Exception as e:
            return {
                'feedback': None,
                'compliant': False,
                'violations': [],
                'severity': 'none',
                'recommendation': '',
                'error': f"API Error: {str(e)}"
            }
    
    return {
        'feedback': None,
        'compliant': False,
        'violations': [],
        'severity': 'none',
        'recommendation': '',
        'error': "Failed to generate compliant feedback after maximum retries"
    }


def generate_applicant_feedback(job_description: str, cleaned_resume: str) -> str:
    """
    Generate actionable improvement feedback for applicants.
    This is less restrictive since it's for self-improvement, not rejection.
    
    Args:
        job_description: Full JD text
        cleaned_resume: Cleaned/structured resume text
        
    Returns:
        String containing structured feedback or error message
    """
    
    system_prompt = """You are an Expert Resume Coach helping candidates improve their resumes.

YOUR TASK:
Provide specific, actionable advice to help the candidate strengthen their resume's alignment with the job description.

INSTRUCTIONS:

1. **Identify Specific Gaps**:
   - Compare required skills in JD vs. demonstrated skills in resume
   - Look for missing technical competencies
   - Note where quantifiable results could be added
   - Check for missing relevant certifications or credentials

2. **Be Constructive and Specific**:
   ✓ "The JD emphasizes Docker/Kubernetes experience. Consider adding a project section highlighting container orchestration work, even if it was a side project."
   ✓ "You mention 'improved performance' but don't quantify it. Add metrics like '40% reduction in load time' or 'scaled to 10K concurrent users.'"
   ✗ "You need more experience"
   ✗ "Your resume doesn't show passion"

3. **Focus on Skills and Achievements**:
   - Technical skills and tools
   - Quantifiable accomplishments
   - Relevant certifications
   - Project complexity and scope
   - Leadership and ownership of technical initiatives

4. **Provide Actionable Steps**:
   Each suggestion should include:
   - What's missing or weak
   - Why it matters for this role
   - How to improve it (specific action)

5. **Output Format**:
   Return a bulleted list of 3-6 specific improvements:
   
   • **[Skill/Area]**: [What's missing/weak]. [Specific suggestion with example].
   
   Example:
   • **Cloud Infrastructure Details**: The JD requires AWS expertise with EC2, RDS, and Lambda, but your resume only mentions "cloud experience" generically. Add a technical skills section listing specific AWS services you've used, or create a project highlighting AWS architecture you've designed.

Keep feedback objective, skills-focused, and empowering. Avoid any comments on personality, soft skills, or non-technical attributes."""

    user_prompt = f"""JOB DESCRIPTION:
{job_description}

---

CANDIDATE RESUME:
{cleaned_resume}

---

Provide a bulleted list of specific, actionable improvements to help this candidate strengthen their resume for this role."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating feedback: {str(e)}"


# ============================================================================
# STREAMLIT UI
# ============================================================================

st.set_page_config(page_title="Compliant ATS Matcher", layout="wide")

# --- ROLE SELECTION (Sidebar) ---
with st.sidebar:
    st.title("ATS Prototype")
    st.markdown("---")
    role = st.radio("I am a:", ["Recruiter", "Applicant"])
    st.markdown("---")
    
    # Compliance information
    with st.expander("ℹ️ Legal Compliance Info"):
        st.markdown("""
        **This system includes:**
        - Automated screening for discriminatory language
        - Focus on technical qualifications only
        - Human review requirements for all feedback
        - Compliance checking before sending
        
        **Remember:**
        - All feedback must be reviewed by HR
        - Never send automated rejections without review
        - Document all hiring decisions
        - Ensure consistent evaluation criteria
        """)

st.title("🤖 Compliant ATS Prototype")


# =========================================
# RECRUITER MODE
# =========================================
if role == "Recruiter":
    st.subheader("Recruiter Dashboard – Rank Candidates & Generate Compliant Feedback")
    
    st.warning("⚠️ **Legal Notice**: All generated feedback must be reviewed by HR before sending to candidates. This system provides drafts only.")

    tab1, tab2, tab3 = st.tabs(["⚙️ Setup & Upload", "📊 Ranking & Scores", "📧 Feedback Generator"])

    if "ranked_data" not in st.session_state:
        st.session_state["ranked_data"] = None
        st.session_state["job_description"] = ""

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
                value=st.session_state.get(
                    "job_description",
                    (
                        "We need a Chief Financial Officer (CFO). Must have CPA certification. "
                        "Experience managing large corporate budgets. Strategic financial planning."
                    ),
                ),
            )
            st.session_state["job_description"] = job_description

        with col2:
            st.subheader("Candidate Resumes")
            uploaded_files = st.file_uploader(
                "Upload Resumes (PDF, DOCX, and DOC supported):",
                type=["pdf", "docx", "doc"],
                accept_multiple_files=True,
            )

        st.markdown("---")

        if uploaded_files and st.button("🚀 Run Ranking Engine", type="primary"):
            if not job_description:
                st.error("Please paste the Job Description before running the engine.")
                st.stop()

            with st.spinner("Processing files, cleaning with AI, and running vector embedding analysis..."):
                candidate_list_for_ranking = []

                for file in uploaded_files:
                    filename = file.name.lower()
                    raw_resume_text = ""

                    if filename.endswith(".pdf"):
                        raw_resume_text = extract_text_from_pdf(file)
                    elif filename.endswith(".docx") or filename.endswith(".doc"):
                        raw_resume_text = extract_text_from_docx(file)
                    else:
                        st.warning(f"Unsupported file type for {file.name}. Skipping.")
                        continue

                    if raw_resume_text:
                        clean_resume_text = clean_and_structure_resume(raw_resume_text)
                        candidate_list_for_ranking.append(
                            {
                                "name": file.name,
                                "resume": clean_resume_text,
                            }
                        )

                if candidate_list_for_ranking:
                    st.info(f"Successfully processed and cleaned {len(candidate_list_for_ranking)} resumes.")

                    ranking_results = rank_candidates(job_description, candidate_list_for_ranking)
                    st.session_state["ranked_data"] = ranking_results
                    st.success("Ranking Complete! See the **Ranking & Scores** tab.")
                else:
                    st.warning("No valid files were processed.")

    # --- TAB 2: Ranking & Scores ---
    with tab2:
        st.header("2. Candidate Ranking Results")

        if st.session_state.get("ranked_data") is not None:
            ranking_results = st.session_state["ranked_data"]

            df = pd.DataFrame(ranking_results)
            df["Score"] = (df["score"] * 100).round(1).astype(str) + "%"
            df_display = df[["name", "Score"]].rename(columns={"name": "Candidate"})

            st.subheader("Semantic Match Scoreboard")
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            st.info("The table is sorted by score (highest match first).")

            st.subheader("Review Cleaned Resume Text")
            candidate_names = [r["name"] for r in ranking_results]
            selected_name = st.selectbox("Select Candidate to Review:", candidate_names)

            selected_candidate = next((r for r in ranking_results if r["name"] == selected_name), None)

            if selected_candidate:
                with st.expander(f"Cleaned Resume Text for {selected_name}"):
                    st.code(selected_candidate["resume"], language="markdown")
        else:
            st.warning("Please run the ranking engine in the 'Setup & Upload' tab first.")

    # --- TAB 3: Feedback Generator (WITH COMPLIANCE) ---
    with tab3:
        st.header("3. Generate Compliant Rejection Feedback")

        if st.session_state.get("ranked_data") is not None:
            ranking_results = st.session_state["ranked_data"]
            job_description = st.session_state["job_description"]

            # Let recruiter select which candidate to generate feedback for
            st.info("Select a candidate to generate feedback for:")
            candidate_names = [r["name"] for r in ranking_results]
            selected_candidate_name = st.selectbox(
                "Choose candidate:",
                candidate_names,
                key="feedback_candidate_selector"
            )
            
            selected_candidate = next(
                (r for r in ranking_results if r["name"] == selected_candidate_name), 
                None
            )

            if selected_candidate:
                st.info(
                    f"Generating feedback for **{selected_candidate['name']}** "
                    f"(Score: {(selected_candidate['score'] * 100):.1f}%)"
                )

                if st.button(f"✍️ Generate Compliant Draft for {selected_candidate['name']}", type="primary"):
                    with st.spinner("Generating legally compliant feedback (with automatic compliance checking)..."):
                        result = generate_compliant_feedback_for_recruiter(
                            job_description,
                            selected_candidate["resume"],
                        )

                    # Display compliance status
                    st.markdown("---")
                    st.subheader("📋 Compliance Check Results")
                    
                    if result['compliant']:
                        st.success("✅ **PASSED** - Feedback cleared compliance screening")
                    elif result['severity'] == 'low':
                        st.warning(f"⚠️ **WARNING** - Potential compliance issues detected")
                        st.write(f"**Violations found**: {', '.join(result['violations'])}")
                        st.write(f"**Recommendation**: {result['recommendation']}")
                    else:
                        st.error(f"🚫 **FAILED** - Critical compliance violations detected")
                        st.write(f"**Violations found**: {', '.join(result['violations'])}")
                        st.write(f"**Recommendation**: {result['recommendation']}")
                    
                    st.markdown("---")
                    
                    # Display feedback if generated
                    if result['feedback']:
                        st.subheader("📧 Generated Feedback Draft")
                        st.info("**Required**: HR must review this draft before sending to candidate")
                        
                        # Show the feedback
                        st.code(result['feedback'], language="text")
                        
                        # Human review checklist
                        st.markdown("---")
                        st.subheader("✓ HR Review Checklist")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            check1 = st.checkbox("Feedback focuses only on job-related qualifications")
                            check2 = st.checkbox("No discriminatory language present")
                            check3 = st.checkbox("Feedback is specific and evidence-based")
                        
                        with col2:
                            check4 = st.checkbox("Tone is professional and constructive")
                            check5 = st.checkbox("Consistent with criteria used for other candidates")
                            check6 = st.checkbox("Legal review completed (if required by policy)")
                        
                        all_checked = all([check1, check2, check3, check4, check5, check6])
                        
                        if all_checked:
                            st.success("✅ All review items confirmed!")
                            
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.download_button(
                                    label="📩 Download Draft",
                                    data=result['feedback'],
                                    file_name=f"Feedback_{selected_candidate['name'].replace('.', '_')}.txt",
                                    mime="text/plain",
                                )
                            
                            with col_b:
                                if st.button("📧 Mark as Ready to Send", type="primary"):
                                    st.success(f"✅ Feedback for {selected_candidate['name']} marked as approved and ready to send!")
                                    st.balloons()
                        else:
                            st.warning("⚠️ Complete all checklist items before approving feedback")
                    
                    elif result['error']:
                        st.error(f"❌ Error: {result['error']}")
                        st.info("Please try regenerating the feedback or contact support.")
        else:
            st.warning("Please run the ranking engine in the 'Setup & Upload' tab first.")


# =========================================
# APPLICANT MODE
# =========================================
elif role == "Applicant":
    st.subheader("Applicant Dashboard – Check Fit, Get Feedback, & Optimize")

    st.markdown(
        "Upload your resume and paste the job description to get your ATS fit score, "
        "actionable improvements, and an AI-optimized resume version."
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
        resume_file = st.file_uploader(
            "Upload Your Resume (PDF, DOCX, or DOC):",
            type=["pdf", "docx", "doc"],
            key="applicant_uploader",
        )
        manual_resume_text = st.text_area(
            "Or paste your resume text here:",
            height=160,
            key="manual_applicant_text",
            placeholder="If you don't have a file, paste your resume content here...",
        )

    analyze_button = st.button("🔍 Analyze & Improve My Resume", type="primary")

    if analyze_button:
        if not jd_applicant:
            st.error("Please paste the Job Description first.")
            st.stop()

        raw_resume = ""
        if resume_file is not None:
            filename = resume_file.name.lower()
            if filename.endswith(".pdf"):
                raw_resume = extract_text_from_pdf(resume_file)
            elif filename.endswith(".docx") or filename.endswith(".doc"):
                raw_resume = extract_text_from_docx(resume_file)
            else:
                st.error("Unsupported file type. Please upload a PDF, DOCX, or DOC file.")
                st.stop()
        elif manual_resume_text.strip():
            raw_resume = manual_resume_text.strip()
        else:
            st.error("Please upload a resume (PDF/DOCX/DOC) or paste your resume text.")
            st.stop()

        with st.spinner("Analyzing your resume and generating improvements..."):
            cleaned_resume = clean_and_structure_resume(raw_resume)
            score = compute_fit_score(jd_applicant, cleaned_resume)
            applicant_feedback_list = generate_applicant_feedback(jd_applicant, cleaned_resume)
            optimized_resume_md = rewrite_resume(jd_applicant, cleaned_resume)

        st.success("Analysis complete! Scroll down to see your results.")

        # 1. ATS Fit Score
        st.header("1. ATS Fit Score")
        score_percent = max(0.0, min(1.0, score)) * 100
        
        col_a, col_b, col_c = st.columns([1, 3, 1])
        
        with col_a:
            st.metric("Overall Match", f"{score_percent:.1f}%")
        
        with col_b:
            st.progress(score_percent / 100.0)
        
        with col_c:
            if score_percent >= 80:
                st.success("Strong Match!")
            elif score_percent >= 60:
                st.info("Good Match")
            elif score_percent >= 40:
                st.warning("Moderate Match")
            else:
                st.error("Weak Match")

        st.caption(
            "This score indicates how closely your resume aligns with the job description using AI embeddings. "
            "Scores above 70% typically indicate strong alignment."
        )

        # 2. Actionable Feedback List
        st.markdown("---")
        st.header("2. Actionable Feedback")
        st.markdown(
            "Use these objective, skills-based suggestions to improve your resume's alignment with the job requirements."
        )
        st.markdown(applicant_feedback_list)
        
        st.info("💡 **Tip**: Focus on the top 2-3 suggestions first for the biggest impact on your ATS score.")

        # 3. Suggested Optimized Resume
        st.markdown("---")
        st.header("3. AI-Optimized Resume")
        st.warning(
            "⚠️ **Important**: This is an AI-generated optimization. "
            "Review carefully and ensure all information is accurate before using. "
            "Never include false information."
        )
        
        with st.expander("View Optimized Resume", expanded=True):
            st.code(optimized_resume_md, language="markdown")

        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            st.download_button(
                label="📩 Download Optimized Resume (Markdown)",
                data=optimized_resume_md,
                file_name="optimized_resume.md",
                mime="text/markdown",
            )
        
        with col_dl2:
            st.download_button(
                label="📋 Download Feedback List",
                data=applicant_feedback_list,
                file_name="resume_feedback.txt",
                mime="text/plain",
            )


# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(
    "⚖️ **Legal Disclaimer**: This system provides automated assistance only. "
    "All hiring decisions must involve human review and comply with applicable employment laws. "
    "Consult with legal counsel regarding your specific hiring practices."
)