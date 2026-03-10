"""
Help & FAQ Page
Central hub for tutorials and frequently asked questions
"""

import streamlit as st
from styles import inject_global_css
from ui_components import show_top_navigation

# Inject global CSS
inject_global_css()

st.set_page_config(
    page_title="TrueFit - Help & FAQ",
    page_icon="❓",
    layout="wide"
)

show_top_navigation("Help & FAQ")

st.title("❓ Help & Frequently Asked Questions")
st.subheader("Find answers to common questions and get started quickly")

# Navigation tabs
tab1, tab2, tab3, tab4 = st.tabs(["Getting Started", "Resume Tips", "Job Matching", "Troubleshooting"])

# ======================================================
# TAB 1: GETTING STARTED
# ======================================================
with tab1:
    st.header("🚀 Getting Started")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("For Candidates")
        st.markdown("""
        **Step 1: Create Your Account**
        - Sign up with your email
        - Set a secure password (min 8 characters)
        - Verify your email
        
        **Step 2: Build Your Profile**
        - Fill in basic information
        - Add your work experience
        - List your skills
        
        **Step 3: Match Your Resume**
        - Upload your resume (PDF)
        - Paste a job description
        - Get instant match score and suggestions
        """)
    
    with col2:
        st.subheader("For Recruiters")
        st.markdown("""
        **Step 1: Enter Job Description**
        - Write or paste the full JD
        - Include requirements and responsibilities
        - Use templates for faster setup
        
        **Step 2: Upload Resumes**
        - Upload candidate resumes (PDFs)
        - Batch process multiple resumes
        
        **Step 3: Review Rankings**
        - See candidates ranked by match
        - Read AI-generated feedback
        - Make informed decisions
        """)
    
    st.divider()
    
    with st.expander("How does the matching work?"):
        st.markdown("""
        TrueFit uses **semantic matching** - it understands the meaning behind words, not just keyword matching.
        
        **Score Interpretation:**
        - **80-100%**: Excellent match - High chance of success
        - **60-79%**: Good match - Candidate has most skills
        - **40-59%**: Fair match - Some gaps, but trainable
        - **Below 40%**: Poor match - Significant skill gaps
        
        The score considers:
        - Experience level alignment
        - Required skills match
        - Nice-to-have skills
        - Work history relevance
        - Industry experience
        """)


# ======================================================
# TAB 2: RESUME TIPS
# ======================================================
with tab2:
    st.header("📄 Resume Formatting & Optimization Tips")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("✅ Do's")
        st.markdown("""
        - **Use ATS-friendly formatting**
          - Simple fonts (Arial, Calibri)
          - Clear section headers
          - Standard bullet points
        
        - **Include relevant details**
          - Job titles and dates
          - Company names
          - Quantified achievements
        
        - **Optimize for keywords**
          - Use job description terms
          - Include technical skills
          - Mention relevant tools/platforms
        
        - **Keep it scannable**
          - One page (if possible)
          - White space and margins
          - Consistent formatting
        """)
    
    with col2:
        st.subheader("❌ Don'ts")
        st.markdown("""
        - **Avoid common mistakes**
          - Scanned/image PDFs
          - Complex graphics or colors
          - Tables for layout
          - Unusual fonts
        
        - **Skip these elements**
          - Images or photos
          - Headers/footers
          - Special characters
          - Multiple columns
        
        - **Don't overstate**
          - False claims
          - Inflated titles
          - Exaggerated responsibilities
        
        - **Avoid these formats**
          - Images saved as PDFs
          - Password-protected PDFs
          - Compressed/corrupted files
        """)
    
    st.divider()
    
    with st.expander("How to write strong achievement statements"):
        st.markdown("""
        **Formula: Action Verb + Task + Quantifiable Result**
        
        **❌ Weak:**
        "Worked on software development"
        
        **✅ Strong:**
        "Led development of microservices architecture, reducing API response time by 40% and improving system scalability for 500+ concurrent users"
        
        **More Examples:**
        - Increased sales by 35% through targeted market analysis
        - Reduced code review time by 2 hours/week via automation
        - Mentored 3 junior engineers, all promoted within 18 months
        - Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes
        - Optimized database queries achieving 60% faster report generation
        """)


# ======================================================
# TAB 3: JOB MATCHING
# ======================================================
with tab3:
    st.header("🎯 Understanding Match Scores")
    
    st.markdown("""
    ### What Affects Your Match Score?
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Required Skills", "40%", "Exact matches weight highest")
        st.caption("Technical skills, tools, programming languages")
    
    with col2:
        st.metric("Experience Level", "30%", "Years and seniority level")
        st.caption("Overall years, role progression, growth")
    
    with col3:
        st.metric("Nice-to-Have Skills", "20%", "Bonus points")
        st.caption("Additional qualifications and preferences")
    
    st.divider()
    
    with st.expander("How to improve your match score"):
        st.markdown("""
        **Quick wins (can improve overnight):**
        1. **Upload the right resume**
           - Tailor resume for the specific role
           - Include job description keywords
           - Highlight relevant experience
        
        2. **Optimize wording**
           - Use industry-standard terminology
           - Match job description language
           - Be specific about technologies
        
        **Long-term improvements (develop skills):**
        3. **Develop missing skills**
           - Take online courses
           - Work on side projects
           - Get relevant certifications
        
        4. **Gain relevant experience**
           - Seek roles using required tech
           - Contribute to open-source projects
           - Volunteer for skill-building opportunities
        """)
    
    with st.expander("Score scenarios"):
        st.markdown("""
        **Scenario 1: 95% Match**
        - Candidate has all required skills
        - Exact experience level match
        - Covers all nice-to-have items
        - ✅ Ready to apply immediately
        
        **Scenario 2: 72% Match**
        - Has core required skills
        - Some missing specializations
        - Experience level slightly below
        - 📝 Recommendation: Show learning in cover letter
        
        **Scenario 3: 45% Match**
        - Has transferable skills
        - Missing key experience
        - Different industry background
        - 🎓 Recommendation: Consider as strong potential with growth
        
        **Scenario 4: 28% Match**
        - Fundamentally different background
        - Major skill gaps
        - Would require significant training
        - ⏭️ Recommendation: Focus on roles closer to current skills
        """)


# ======================================================
# TAB 4: TROUBLESHOOTING
# ======================================================
with tab4:
    st.header("🔧 Troubleshooting")
    
    with st.expander("PDF Upload not working"):
        st.markdown("""
        **Problem:** "Could not extract text from resume"
        
        **Causes & Solutions:**
        1. **Scanned PDF (Image)**
            - The file is actually an image, not text
            - ❌ OCR is not supported
            - ✅ Solution: Re-save document as text-based PDF
        
        2. **Corrupted file**
            - File is damaged or incomplete
            - ✅ Solution: Try re-exporting from Word/Google Docs
        
        3. **Password-protected**
            - PDF requires password to open
            - ✅ Solution: Remove password before uploading
        
        4. **Unusual encoding**
            - Contains special formatting or fonts
            - ✅ Solution: Convert to standard PDF first
        
        **Quick Fix:** Export from Google Docs → Download as PDF
        """)
    
    with st.expander("Low match score even though I'm qualified"):
        st.markdown("""
        **Possible reasons:**
        
        1. **Wording mismatch**
            - Your resume uses different terms than job description
            - Solution: Use exact keywords from JD
        
        2. **Important experience not highlighted**
            - Relevant skills buried in description
            - Solution: Move key skills to top, use bullet points
        
        3. **Generic resume**
            - Resume is not tailored to this role
            - Solution: Customize for each job application
        
        4. **Formatting issues**
            - Complex formatting breaks text extraction
            - Solution: Use simple, clean formatting
        
        5. **Missing sections**
            - Skills section not included
            - Solution: Add dedicated skills section
        """)
    
    with st.expander("Can't login to my account"):
        st.markdown("""
        **Try these steps:**
        
        1. **Check email**
            - Make sure email is spelled correctly
            - Watch for extra spaces
        
        2. **Check password**
            - Verify CAPS LOCK is off
            - Password is case-sensitive
        
        3. **Use password reset**
            - Click "Forgot Password?" link
            - Follow email instructions
            - Create new password
        
        4. **Check email spam**
            - Verification email might be in spam
            - Add noreply@truefit.app to contacts
        
        5. **Try incognito mode**
            - Clear browser cache
            - Try private/incognito window
        
        **Still stuck?** Contact support with your email address.
        """)
    
    with st.expander("Other questions"):
        st.markdown("""
        **Q: Is my data secure?**
        A: Yes, all resumes and job descriptions are encrypted and not shared.
        
        **Q: Can I export my resume?**
        A: Yes, you can download generated CVs as PDF or Word documents.
        
        **Q: How long does analysis take?**
        A: Usually 5-30 seconds depending on document length.
        
        **Q: Are there limits on uploads?**
        A: Free tier: 10 analyses/month. Premium: Unlimited.
        
        **Q: Can I edit my profile?**
        A: Yes, go to Dashboard → Build Profile to edit anytime.
        """)


# ======================================================
# FOOTER
# ======================================================
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Quick Links**")
    st.markdown("[Go to Home](./)")
    st.markdown("[Build Profile](./pages/05_careerhub_profile.py)")

with col2:
    st.markdown("**Resources**")
    st.markdown("[Download Resume Template]()")
    st.markdown("[View Blog](#)")

with col3:
    st.markdown("**Support**")
    st.markdown("📧 Email: support@truefit.app")
    st.markdown("💬 Chat: Coming soon")

st.caption("🎯 TrueFit | Making hiring and job search smarter")
