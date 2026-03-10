"""
Form Input Improvements & Helpers
Job description templates, form auto-save, tooltips, and breadcrumbs
"""

import streamlit as st
from typing import Optional, Dict, List
from datetime import datetime

# ======================================================
# JOB DESCRIPTION TEMPLATES
# ======================================================

JOB_DESCRIPTION_TEMPLATES = {
    "Software Engineer": """# Senior Software Engineer

## About the Role
We are seeking an experienced Software Engineer to join our growing team...

## Responsibilities
- Design and develop scalable software solutions
- Collaborate with cross-functional teams
- Review and improve code quality
- Mentor junior developers
- Participate in technical discussions and code reviews

## Required Skills
- 5+ years of software development experience
- Proficiency in Python, Java, or C++
- Experience with cloud platforms (AWS, GCP, Azure)
- Strong problem-solving abilities
- Excellent communication skills
- Experience with agile development

## Nice to Have
- Machine learning experience
- Open source contributions
- DevOps experience

## Qualifications
- Bachelor's degree in Computer Science or related field
- Experience with microservices architecture
- Familiarity with Docker and Kubernetes

## Benefits
- Competitive salary
- Flexible work arrangements
- Professional development opportunities
- Health insurance
""",
    
    "Product Manager": """# Product Manager

## About the Role
Lead the vision and execution of our product roadmap...

## Responsibilities
- Define and communicate product vision and roadmap
- Conduct market research and competitive analysis
- Gather and prioritize customer feedback
- Work with engineering and design teams
- Launch features and analyze product metrics
- Make data-driven decisions

## Required Skills
- 3+ years of product management experience
- Strong analytical and problem-solving skills
- Experience with product metrics and analytics
- Excellent written and verbal communication
- Leadership and collaboration abilities
- Experience with Agile/Scrum methodology

## Technical Skills
- Proficiency with product management tools (Jira, Confluence, etc.)
- Understanding of software development processes
- Experience with analytics platforms (Mixpanel, Amplitude, etc.)
- SQL or data analysis experience preferred

## Qualifications
- Bachelor's degree in Business, Computer Science, or related field
- Track record of launching successful products
- Experience with B2B or B2C products

## Benefits
- Competitive salary and equity
- Flexible work hours
- Professional development budget
- Health and wellness benefits
""",
    
    "Data Scientist": """# Data Scientist

## About the Role
Join our data team to uncover insights that drive business decisions...

## Responsibilities
- Design and implement machine learning models
- Analyze complex datasets
- Create data visualizations and reports
- Collaborate with product and engineering teams
- Optimize model performance and scalability
- Document and present findings

## Required Skills
- 3+ years of data science experience
- Proficiency in Python or R
- Strong SQL knowledge
- Experience with machine learning frameworks
- Statistical analysis expertise
- Data visualization skills

## Technical Requirements
- Familiarity with cloud platforms (AWS/GCP/Azure)
- Version control (Git)
- Experience with Jupyter notebooks
- Ability to work with large datasets

## Qualifications
- Master's degree in Data Science, Statistics, or related field
- Published research or portfolio projects
- Experience with feature engineering
- Knowledge of deep learning (preferred)

## Benefits
- Competitive salary
- Remote work options
- Learning and development allowance
- Health insurance
""",
    
    "Marketing Manager": """# Marketing Manager

## About the Role
Lead our marketing initiatives to drive growth and brand awareness...

## Responsibilities
- Develop and execute marketing strategies
- Manage marketing campaigns across channels
- Analyze campaign performance and ROI
- Create content and marketing materials
- Collaborate with sales and product teams
- Manage marketing budget

## Required Skills
- 4+ years of marketing experience
- Strong project management skills
- Experience with digital marketing channels
- Analytics and data interpretation
- Creative thinking and problem-solving
- Excellent communication abilities

## Tools & Technologies
- Marketing automation platforms (HubSpot, Marketo)
- Google Analytics and advertising platforms
- Social media management tools
- CRM systems
- Content management systems

## Qualifications
- Bachelor's degree in Marketing, Business, or related field
- Proven track record of successful campaigns
- Experience with multi-channel marketing
- SEO/SEM experience preferred

## Benefits
- Competitive salary
- Performance bonuses
- Flexible schedule
- Professional development opportunities
"""
}


def show_jd_templates():
    """
    Show job description template selector.
    
    Returns:
        str: Selected template or empty string if none selected
    """
    st.subheader("📋 Use a Template (Optional)")
    
    template_choice = st.selectbox(
        "Or start with a template:",
        ["--Select a template--"] + list(JOB_DESCRIPTION_TEMPLATES.keys()),
        key="jd_template_selector"
    )
    
    if template_choice != "--Select a template--":
        template_text = JOB_DESCRIPTION_TEMPLATES[template_choice]
        
        with st.expander("📖 View Template Preview"):
            st.markdown(template_text)
        
        if st.button("✅ Use This Template", use_container_width=True, type="primary"):
            return template_text
    
    return ""


def display_jd_helper_tips():
    """Display tips for writing effective job descriptions."""
    with st.expander("💡 Tips for Better Job Descriptions"):
        st.markdown("""
        ### Best Practices:
        - **Be specific**: Include required experience, skills, and responsibilities
        - **Add details**: Salary range, work environment, team size
        - **Use keywords**: Include technical terms and role-specific terminology
        - **Be realistic**: List actual requirements, not unrealistic expectations
        - **Include benefits**: Remote flexibility, professional development, etc.
        
        ### Structure:
        1. Role title and summary
        2. Key responsibilities (5-8 items)
        3. Required skills and qualifications
        4. Nice-to-have skills
        5. Benefits and work environment
        
        ### Length:
        - Minimum: 200 words
        - Ideal: 400-600 words
        - Better for matching: More detailed descriptions
        """)


# ======================================================
# FORM AUTO-SAVE
# ======================================================

def auto_save_form_field(form_key: str, field_name: str, field_value: str) -> None:
    """
    Auto-save a form field to session state.
    
    Args:
        form_key: Unique identifier for the form
        field_name: Name of the field
        field_value: Value to save
    """
    if f"form_{form_key}" not in st.session_state:
        st.session_state[f"form_{form_key}"] = {}
    
    st.session_state[f"form_{form_key}"][field_name] = field_value


def get_saved_field(form_key: str, field_name: str, default: str = "") -> str:
    """
    Retrieve a saved form field from session state.
    
    Args:
        form_key: Unique identifier for the form
        field_name: Name of the field to retrieve
        default: Default value if not found
        
    Returns:
        Saved field value or default
    """
    if f"form_{form_key}" in st.session_state:
        return st.session_state[f"form_{form_key}"].get(field_name, default)
    return default


def show_form_autosave_indicator():
    """Show a visual indicator that form is auto-saving."""
    st.caption("💾 Form auto-saves as you type")


def clear_form(form_key: str):
    """Clear all saved fields for a form."""
    if f"form_{form_key}" in st.session_state:
        del st.session_state[f"form_{form_key}"]


def show_unsaved_changes_warning():
    """Show warning about unsaved changes."""
    st.warning("⚠️ You have unsaved changes. They will be saved automatically.")


# ======================================================
# TOOLTIPS & HELP SYSTEM
# ======================================================

HELP_TEXTS = {
    # Resume-related
    "resume_file": "Upload a text-based PDF resume. Scanned images won't work. Max 10 MB.",
    "job_description": "Paste the complete job description including responsibilities, requirements, and nice-to-have skills. Minimum 200 characters.",
    
    # Profile-related
    "full_name": "Your first and last name as you'd like it to appear on official documents.",
    "email": "Your primary email address. We'll use this for account verification and communications.",
    "phone": "Your contact phone number including country code (e.g., +1-234-567-8900).",
    "location": "Your current city/state or country. Used for location-based job matching.",
    "professional_summary": "A brief 2-3 sentence overview of your professional background and goals.",
    
    # Work experience
    "job_title": "Your official job title at this position (e.g., Senior Software Engineer).",
    "company_name": "The name of the company where you worked.",
    "employment_type": "Type of employment: Full-time, Part-time, Contract, Freelance, etc.",
    "start_date": "When you started this position (Month/Year).",
    "end_date": "When you left, or 'Present' if you still work there.",
    "job_description_field": "Key responsibilities, achievements, and technologies used. Be specific and quantify results.",
    
    # Skills
    "skill_name": "Name of the skill (e.g., Python, Project Management, Graphic Design).",
    "skill_level": "Your proficiency level: Beginner, Intermediate, Advanced, Expert.",
    "years_of_experience": "How many years of experience with this skill.",
}


def show_help_tooltip(help_key: str, width: str = "full"):
    """
    Show a help tooltip with additional information.
    
    Args:
        help_key: Key to look up in HELP_TEXTS
        width: Width of tooltip ('full', 'column', or specific width)
    """
    if help_key in HELP_TEXTS:
        st.info(f"**💡 Tip:** {HELP_TEXTS[help_key]}")


def show_field_with_tooltip(label: str, help_key: str, input_type: str = "text", **kwargs) -> str:
    """
    Show a form field with integrated tooltip.
    
    Args:
        label: Field label
        help_key: Key for help text lookup
        input_type: Type of input ('text', 'textarea', 'slider', 'select')
        **kwargs: Additional arguments to pass to input
        
    Returns:
        Input value
    """
    col1, col2 = st.columns([5, 1])
    
    with col1:
        if input_type == "text":
            value = st.text_input(label, **kwargs)
        elif input_type == "textarea":
            value = st.text_area(label, **kwargs)
        elif input_type == "number":
            value = st.number_input(label, **kwargs)
        elif input_type == "select":
            value = st.selectbox(label, **kwargs)
        else:
            value = st.text_input(label, **kwargs)
    
    with col2:
        if st.button("❓", key=f"help_{label}", help="Show help"):
            show_help_tooltip(help_key)
    
    return value


# ======================================================
# BREADCRUMB NAVIGATION
# ======================================================

def show_breadcrumb_wizard(current_step: int, total_steps: int, step_names: List[str]):
    """
    Show breadcrumb navigation for multi-step wizards.
    
    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        step_names: List of step names
    """
    st.markdown(f"**Step {current_step} of {total_steps}**")
    
    # Create breadcrumb
    breadcrumb = " → ".join(
        f"**{step}**" if i + 1 == current_step
        else f"✅ {step}" if i + 1 < current_step
        else step
        for i, step in enumerate(step_names)
    )
    st.markdown(breadcrumb)
    
    # Progress bar
    progress = current_step / total_steps
    st.progress(progress)


def wizard_navigation(current_step: int, total_steps: int):
    """
    Show next/previous buttons for wizard navigation.
    
    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        
    Returns:
        Tuple of (prev_clicked, next_clicked)
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    prev_clicked = False
    next_clicked = False
    
    with col1:
        if current_step > 1:
            if st.button("⬅️ Previous", use_container_width=True):
                prev_clicked = True
    
    with col3:
        if current_step < total_steps:
            if st.button("Next ➡️", use_container_width=True, type="primary"):
                next_clicked = True
    
    return prev_clicked, next_clicked


# ======================================================
# DATE PICKER HELPERS
# ======================================================

def show_month_year_picker(label: str, key: str, default_month: int = None, default_year: int = None):
    """
    Show a month/year picker (two columns).
    
    Args:
        label: Label for the picker
        key: Unique key for the picker
        default_month: Default month (1-12)
        default_year: Default year
        
    Returns:
        Tuple of (month, year) or (None, None) if not set
    """
    st.write(label)
    
    col1, col2 = st.columns(2)
    
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    with col1:
        month = st.selectbox(
            "Month",
            months,
            index=default_month - 1 if default_month else 0,
            key=f"{key}_month"
        )
    
    with col2:
        current_year = datetime.now().year
        year = st.number_input(
            "Year",
            min_value=1980,
            max_value=current_year + 1,
            value=default_year or current_year,
            key=f"{key}_year"
        )
    
    return month, int(year)


def show_date_range_picker(label: str, key: str):
    """
    Show start and end date pickers.
    
    Args:
        label: Label for the date range
        key: Unique key for the picker
        
    Returns:
        Tuple of (start_month, start_year, end_month, end_year)
    """
    st.write(label)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Start Date**")
        start_month, start_year = show_month_year_picker(
            "From", f"{key}_start", 1, 2020
        )
    
    with col2:
        st.write("**End Date**")
        end_month, end_year = show_month_year_picker(
            "To", f"{key}_end", 1, datetime.now().year
        )
        
        # Add "Present" checkbox
        is_present = st.checkbox("Currently working here", key=f"{key}_present")
        if is_present:
            end_month, end_year = None, None
    
    return start_month, start_year, end_month, end_year, is_present


# ======================================================
# FORM VALIDATION HELPERS
# ======================================================

def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    import re
    # Accepts various formats: +1-234-567-8900, (123) 456-7890, 1234567890
    pattern = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
    return re.match(pattern, phone) is not None


def validate_url(url: str) -> bool:
    """Validate URL format."""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


# ======================================================
# PROGRESS TRACKING FOR FORMS
# ======================================================

def calculate_form_completion(field_dict: Dict, required_fields: List[str]) -> int:
    """
    Calculate form completion percentage.
    
    Args:
        field_dict: Dictionary of form fields
        required_fields: List of required field names
        
    Returns:
        Completion percentage (0-100)
    """
    if not required_fields:
        return 0
    
    completed = sum(1 for field in required_fields if field_dict.get(field))
    return int((completed / len(required_fields)) * 100)


def show_form_completion_bar(completion_pct: int, label: str = "Form Completion"):
    """Show a progress bar for form completion."""
    st.progress(completion_pct / 100, text=f"{label}: {completion_pct}%")
