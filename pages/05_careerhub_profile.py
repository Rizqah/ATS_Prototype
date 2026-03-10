import streamlit as st

from careerhub_db import (
    get_profile, update_profile, get_work_experience, 
    add_work_experience, update_work_experience, delete_work_experience,
    get_achievements, add_achievement, delete_achievement,
    get_skills, add_skill, delete_skill
)
from styles import inject_global_css
from form_helpers import (
    show_month_year_picker, show_date_range_picker,
    auto_save_form_field, get_saved_field, show_form_completion_bar,
    calculate_form_completion, validate_email, validate_phone
)
from ui_components import (
    show_success_toast, show_error_toast, confirm_delete, show_top_navigation
)

# Inject global CSS
inject_global_css()

st.set_page_config(
    page_title="TrueFit - Profile Builder",
    page_icon="👤",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Please login first")
    st.switch_page("pages/03_careerhub_auth.py")

user_email = st.session_state.user_email

show_top_navigation("Profile")

st.title("👤 Build Your Profile")
st.subheader("Create a comprehensive career profile to unlock all features")

# Get current profile
profile_result = get_profile(user_email)
profile = profile_result.get("profile", {})

# Calculate profile completion
required_fields = ["full_name", "email", "phone", "location", "professional_summary"]
completion_pct = calculate_form_completion(profile, required_fields)
show_form_completion_bar(completion_pct, "Profile Completion")

# ======================================================
# SECTION 1: BASIC INFO
# ======================================================
with st.expander("📋 Basic Information", expanded=completion_pct < 100):
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input(
            "Full Name",
            value=profile.get("full_name", ""),
            placeholder="John Doe"
        )
        auto_save_form_field("profile_basic", "full_name", full_name)
    
    with col2:
        email_val = st.text_input(
            "Email",
            value=profile.get("email", ""),
            placeholder="john@example.com"
        )
        auto_save_form_field("profile_basic", "email", email_val)
        if email_val and not validate_email(email_val):
            st.warning("⚠️ Please enter a valid email address")
    
    col1, col2 = st.columns(2)
    
    with col1:
        phone_val = st.text_input(
            "Phone",
            value=profile.get("phone", ""),
            placeholder="+1 (555) 123-4567"
        )
        auto_save_form_field("profile_basic", "phone", phone_val)
        if phone_val and not validate_phone(phone_val):
            st.warning("⚠️ Please enter a valid phone number")
    
    with col2:
        location = st.text_input(
            "Location",
            value=profile.get("location", ""),
            placeholder="New York, USA"
        )
        auto_save_form_field("profile_basic", "location", location)
    
    professional_summary = st.text_area(
        "Professional Summary",
        value=profile.get("professional_summary", ""),
        placeholder="Brief 2-3 sentence overview of your career and goals...",
        height=100
    )
    auto_save_form_field("profile_basic", "professional_summary", professional_summary)
    
    st.caption("💾 Auto-saves as you type")
    
    if st.button("💾 Save Basic Info", use_container_width=True, type="primary"):
        update_result = update_profile(user_email, {
            "full_name": full_name,
            "email": email_val,
            "phone": phone_val,
            "location": location,
            "professional_summary": professional_summary
        })
        
        if update_result["success"]:
            show_success_toast("Basic info saved!")
        else:
            show_error_toast(update_result['error'])

# ======================================================
# SECTION 2: WORK EXPERIENCE
# ======================================================
st.divider()
st.header("2️⃣ Work Experience")

work_exp_result = get_work_experience(user_email)
work_experiences = work_exp_result.get("experiences", [])

# Display existing work experiences
if work_experiences:
    st.subheader(f"Your Experience ({len(work_experiences)} entries)")
    
    for idx, exp in enumerate(work_experiences):
        with st.expander(f"🏢 {exp.get('position')} at {exp.get('company')}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                pos = st.text_input(
                    "Position",
                    value=exp.get("position", ""),
                    placeholder="e.g., Senior Software Engineer",
                    key=f"pos_{exp['id']}"
                )
            
            with col2:
                comp = st.text_input(
                    "Company",
                    value=exp.get("company", ""),
                    placeholder="e.g., Tech Corp",
                    key=f"comp_{exp['id']}"
                )
            
            # Use month/year picker instead of date_input
            emp_type = st.selectbox(
                "Employment Type",
                ["Full-time", "Part-time", "Contract", "Freelance", "Internship"],
                index=0,
                key=f"emp_type_{exp['id']}"
            )
            
            st.write("**Employment Dates**")
            start_month, start_year = show_month_year_picker(
                "Start Date",
                f"exp_start_{exp['id']}",
                1, 2020
            )
            
            is_current = st.checkbox(
                "Currently working here",
                value=exp.get("current_job", False),
                key=f"current_{exp['id']}"
            )
            
            if not is_current:
                end_month, end_year = show_month_year_picker(
                    "End Date",
                    f"exp_end_{exp['id']}",
                    1, 2023
                )
            else:
                end_month, end_year = None, None
            
            desc = st.text_area(
                "Key Responsibilities & Achievements",
                value=exp.get("description", ""),
                placeholder="Describe your main responsibilities and quantifiable achievements...",
                key=f"desc_{exp['id']}",
                height=100
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Update", key=f"update_{exp['id']}", use_container_width=True, type="primary"):
                    update_work_experience(user_email, exp['id'], {
                        "position": pos,
                        "company": comp,
                        "employment_type": emp_type,
                        "start_date": f"{start_month}/20{start_year % 100}" if start_month else "",
                        "end_date": None if is_current else f"{end_month}/20{end_year % 100}" if end_month else "",
                        "current_job": is_current,
                        "description": desc
                    })
                    show_success_toast("Experience updated!")
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{exp['id']}", use_container_width=True):
                    if confirm_delete(f"{pos} at {comp}"):
                        delete_work_experience(user_email, exp['id'])
                        show_success_toast("Experience deleted!")
                        st.rerun()
else:
    st.info("📝 No work experience added yet. Add your first entry below!")

col1, col2 = st.columns(2)

with col1:
    new_position = st.text_input("Position")
    new_start = st.date_input("Start Date", key="new_start")

with col2:
    new_company = st.text_input("Company")
    new_end = st.date_input("End Date", key="new_end")

new_current = st.checkbox("Currently working here", key="new_current")
new_desc = st.text_area("Description", height=80, placeholder="What did you do?")

if st.button("➕ Add Experience", use_container_width=True):
    if new_position and new_company:
        add_work_experience(
            user_email, new_company, new_position,
            str(new_start) if new_start else "",
            str(new_end) if new_end else "",
            new_current, new_desc
        )
        st.success("✅ Experience added!")
        st.rerun()
    else:
        st.error("❌ Please fill in position and company")

# ======================================================
# SECTION 3: SKILLS
# ======================================================
st.divider()
st.header("3️⃣ Skills")

skills_result = get_skills(user_email)
skills = skills_result.get("skills", [])

if skills:
    st.subheader("Your Skills")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.caption("**Skill**")
    with col2:
        st.caption("**Proficiency**")
    with col3:
        st.caption("**Action**")
    
    for skill in skills:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(skill.get("skill_name"))
        with col2:
            st.write(skill.get("proficiency"))
        with col3:
            if st.button("❌", key=f"del_skill_{skill['id']}"):
                delete_skill(user_email, skill['id'])
                st.rerun()

st.subheader("Add New Skill")

col1, col2 = st.columns(2)

with col1:
    new_skill = st.text_input("Skill Name", placeholder="e.g., Python, Leadership, etc.")

with col2:
    proficiency = st.selectbox(
        "Proficiency Level",
        ["Beginner", "Intermediate", "Advanced", "Expert"]
    )

if st.button("➕ Add Skill", use_container_width=True):
    if new_skill:
        add_skill(user_email, new_skill, proficiency)
        st.success("✅ Skill added!")
        st.rerun()
    else:
        st.error("❌ Please enter a skill name")

# Navigation
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.switch_page("pages/04_careerhub_dashboard.py")

with col2:
    if st.button("➡️ Generate CV", use_container_width=True):
        st.switch_page("pages/06_careerhub_cv_generator.py")
with col3:
    st.write("")
