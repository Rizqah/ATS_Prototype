import streamlit as st
from careerhub_db import (
    get_profile, get_work_experience, get_skills, 
    get_generated_cvs, check_cv_limit, delete_cv
)
from styles import inject_global_css
from ui_components import (
    show_top_navigation, show_progress_bar, show_empty_state,
    show_success_toast, confirm_delete
)
from cv_helpers import (
    show_cv_dashboard_empty_state, show_cv_version_history,
    show_cv_quick_actions, show_cv_statistics
)
from security_auth_helpers import is_email_verified

# Inject global CSS
inject_global_css()

st.set_page_config(
    page_title="TrueFit - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Please login first")
    st.switch_page("pages/03_careerhub_auth.py")

user_email = st.session_state.user_email

# Show top navigation
show_top_navigation("Dashboard")

# Get user data
profile_result = get_profile(user_email)
profile = profile_result.get("profile", {})

cvs_result = get_generated_cvs(user_email)
cvs = cvs_result.get("cvs", [])

limit_result = check_cv_limit(user_email)
cvs_generated = limit_result.get("cvs_generated", 0)
cvs_limit = limit_result.get("limit", 20)

# ======================================================
# DASHBOARD VIEW
# ======================================================

st.title("📊 Dashboard")
st.subheader(f"Welcome back, {profile.get('full_name', user_email)}! 👋")

# Security Status
st.header("🔐 Account Security")

sec_col1, sec_col2, sec_col3 = st.columns(3)

email_verified = is_email_verified(user_email)

with sec_col1:
    if email_verified:
        st.success("✅ Email Verified")
    else:
        st.warning("⚠️ Email Not Verified")

with sec_col2:
    st.info("🔑 Password: Secure")

with sec_col3:
    if st.button("🔐 Manage Security", use_container_width=True):
        st.switch_page("pages/11_security_settings.py")

st.divider()

# Profile Completion Status
st.header("1️⃣ Profile Status")

col1, col2, col3 = st.columns(3)

profile_complete = 0
profile_items = [
    ("Full Name", profile.get("full_name") != ""),
    ("Email", profile.get("email") != ""),
    ("Phone", profile.get("phone") != ""),
    ("Location", profile.get("location") != ""),
    ("Summary", profile.get("professional_summary") != ""),
]

for item, completed in profile_items:
    if completed:
        profile_complete += 1

completion_pct = int((profile_complete / len(profile_items)) * 100)

with col1:
    st.metric("Profile Completion", f"{completion_pct}%")

with col2:
    work_exp_result = get_work_experience(user_email)
    work_experiences = work_exp_result.get("experiences", [])
    st.metric("Work Experience Entries", len(work_experiences))

with col3:
    skills_result = get_skills(user_email)
    skills = skills_result.get("skills", [])
    st.metric("Skills Added", len(skills))

# Profile progress bar
show_progress_bar(profile_complete, len(profile_items), "Profile Completion")

if completion_pct < 100:
    st.info(f"📝 Complete your profile to unlock more features! ({profile_complete}/{len(profile_items)} steps done)")

st.divider()

# CV Generation Status
st.header("2️⃣ CV Generation Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("CVs Generated", f"{cvs_generated}/{cvs_limit}")

with col2:
    remaining = cvs_limit - cvs_generated if isinstance(cvs_limit, int) else "Unlimited"
    st.metric("Remaining This Month", remaining)

with col3:
    tier = limit_result.get("tier", "free")
    tier_display = "🆓 Free" if tier == "free" else "⭐ Premium"
    st.metric("Current Tier", tier_display)

# CV Limit Warning
if cvs_generated >= cvs_limit and tier == "free":
    st.warning(
        f"⚠️ You've reached your limit of {cvs_limit} CVs this month. "
        "Upgrade to Premium for unlimited CV generation!"
    )

st.divider()

# Recent CVs
st.header("3️⃣ Recent Generated CVs")

# Load raw CV data for new features
try:
    import json
    with open('careerhub_data/generated_cvs.json', 'r') as f:
        raw_cvs_data = json.load(f)
except:
    raw_cvs_data = {}

if cvs:
    # Show version history
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**You have {len(cvs)} CV versions**")
    with col2:
        if st.button("📊 View Statistics", use_container_width=True):
            st.session_state.show_cv_stats = True
    
    if st.session_state.get("show_cv_stats", False):
        show_cv_statistics(raw_cvs_data)
        st.divider()
    
    # Display version history
    show_cv_version_history(user_email, raw_cvs_data)
else:
    # Show empty state with helpful CTAs
    show_cv_dashboard_empty_state()

st.divider()

# Quick Actions
st.header("4️⃣ Quick Actions")
show_cv_quick_actions()

# Upgrade Section
if tier == "free":
    st.info(
        "⭐ **Upgrade to Premium**\n\n"
        "Enjoy unlimited CV generation and more features coming soon!\n\n"
        "Coming soon: Pricing plans"
    )
    
