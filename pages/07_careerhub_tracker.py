import streamlit as st

from careerhub_db import (
    get_generated_cvs, update_cv_status, delete_cv
)
from datetime import datetime
from ui_components import show_top_navigation

st.set_page_config(
    page_title="TrueFit - CV Tracker",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Please login first")
    st.switch_page("pages/03_careerhub_auth.py")

user_email = st.session_state.user_email
show_top_navigation("CV Tracker")

st.title("📊 Application Tracker")
st.subheader("Track all your generated CVs and applications")

# Get all CVs
cvs_result = get_generated_cvs(user_email)
cvs = cvs_result.get("cvs", [])

if not cvs:
    st.info("📝 No CVs generated yet. Start by generating your first CV!")
    
    if st.button("📄 Generate CV Now"):
        st.switch_page("pages/06_careerhub_cv_generator.py")
    st.stop()

# ======================================================
# FILTER & STATS
# ======================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total CVs", len(cvs))

with col2:
    draft_count = sum(1 for cv in cvs if cv.get("application_status") == "Draft")
    st.metric("Draft", draft_count)

with col3:
    applied_count = sum(1 for cv in cvs if cv.get("application_status") == "Applied")
    st.metric("Applied", applied_count)

with col4:
    interview_count = sum(1 for cv in cvs if cv.get("application_status") == "Interview")
    st.metric("In Interview", interview_count)

st.divider()

# ======================================================
# FILTER OPTIONS
# ======================================================
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All Statuses", "Draft", "Applied", "Interview", "Rejected", "Hired"]
    )

with filter_col2:
    sort_by = st.selectbox(
        "Sort by",
        ["Newest First", "Match Score (High to Low)", "Match Score (Low to High)"]
    )

# Apply filters
if status_filter != "All Statuses":
    filtered_cvs = [cv for cv in cvs if cv.get("application_status") == status_filter]
else:
    filtered_cvs = cvs

# Apply sorting
if sort_by == "Match Score (High to Low)":
    filtered_cvs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
elif sort_by == "Match Score (Low to High)":
    filtered_cvs.sort(key=lambda x: x.get("match_score", 0))

st.divider()

# ======================================================
# CV LIST
# ======================================================
st.header(f"📋 Your CVs ({len(filtered_cvs)})")

if not filtered_cvs:
    st.info(f"No CVs found with status: {status_filter}")
else:
    # Display CVs in grid format
    for idx, cv in enumerate(filtered_cvs):
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])
            
            # Job Title
            with col1:
                st.markdown(f"### {cv.get('job_title', 'Untitled')}")
                created_date = cv.get("created_at", "").split("T")[0]
                st.caption(f"📅 Created: {created_date}")
            
            # Match Score
            with col2:
                match_score = cv.get("match_score", 0)
                if match_score >= 0.8:
                    color = "🟢"
                elif match_score >= 0.6:
                    color = "🟡"
                elif match_score >= 0.4:
                    color = "🟠"
                else:
                    color = "🔴"
                
                st.metric("Match", f"{match_score*100:.1f}%", color)
            
            # Status
            with col3:
                current_status = cv.get("application_status", "Draft")
                new_status = st.selectbox(
                    "Status",
                    ["Draft", "Applied", "Interview", "Rejected", "Hired"],
                    index=["Draft", "Applied", "Interview", "Rejected", "Hired"].index(current_status),
                    key=f"status_{cv['id']}"
                )
                
                if new_status != current_status:
                    update_cv_status(user_email, cv['id'], new_status)
                    st.success(f"Status updated to {new_status}")
                    st.rerun()
            
            # Actions
            with col4:
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("👁️", key=f"view_{cv['id']}", help="View CV Details"):
                        st.session_state.selected_cv_id = cv['id']
                        st.session_state.show_cv_detail = True
                
                with col_b:
                    if st.button("🗑️", key=f"delete_{cv['id']}", help="Delete CV"):
                        delete_cv(user_email, cv['id'])
                        st.success("CV deleted!")
                        st.rerun()
        
        st.divider()

# ======================================================
# CV DETAIL VIEW
# ======================================================
if st.session_state.get("show_cv_detail"):
    selected_cv_id = st.session_state.get("selected_cv_id")
    selected_cv = next((cv for cv in cvs if cv['id'] == selected_cv_id), None)
    
    if selected_cv:
        st.header(f"📄 {selected_cv.get('job_title', 'Untitled')} - Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Your CV")
            st.text_area(
                "CV Content",
                value=selected_cv.get("cv_content", ""),
                height=300,
                disabled=True
            )
        
        with col2:
            st.subheader("Job Description")
            st.text_area(
                "Job Description",
                value=selected_cv.get("job_description", ""),
                height=300,
                disabled=True
            )
        
        st.divider()
        
        # Summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Match Score", f"{selected_cv.get('match_score', 0)*100:.1f}%")
        
        with col2:
            st.metric("Status", selected_cv.get("application_status", "Draft"))
        
        with col3:
            created_date = selected_cv.get("created_at", "").split("T")[0]
            st.metric("Created", created_date)
        
        if st.button("⬅️ Back to List"):
            st.session_state.show_cv_detail = False
            st.rerun()

# ======================================================
# NAVIGATION
# ======================================================
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.switch_page("pages/04_careerhub_dashboard.py")

with col2:
    if st.button("📄 Generate New CV", use_container_width=True):
        st.switch_page("pages/06_careerhub_cv_generator.py")

with col3:
    if st.button("👤 Update Profile", use_container_width=True):
        st.switch_page("pages/05_careerhub_profile.py")
