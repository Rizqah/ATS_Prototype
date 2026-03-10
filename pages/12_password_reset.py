import streamlit as st
from styles import inject_global_css
from ui_components import show_success_toast, show_error_toast
from security_auth_helpers import (
    show_password_reset_request,
    show_password_reset_form
)

# Inject global CSS
inject_global_css()

st.set_page_config(
    page_title="TrueFit - Password Reset",
    page_icon="🔐",
    layout="centered"
)

st.title("🎯 TrueFit")
st.subheader("Reset Your Password")

# Check if user is already authenticated
if st.session_state.get("authenticated", False):
    st.warning("You're already logged in. No need to reset password!")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/04_careerhub_dashboard.py")
    st.stop()

# Initialize stage
if "reset_stage" not in st.session_state:
    st.session_state.reset_stage = "request"  # request or confirm

if st.session_state.reset_stage == "request":
    st.write("Enter your email address and we'll send you instructions to reset your password.")
    
    email = show_password_reset_request()
    
    if email:
        st.session_state.reset_email = email
        st.session_state.reset_stage = "confirm"
        st.rerun()

elif st.session_state.reset_stage == "confirm":
    email = st.session_state.get("reset_email", "")
    
    st.write(f"Resetting password for: **{email}**")
    st.info("Check your email for the reset link. You can also enter the token below:")
    
    token = st.text_input(
        "Enter reset token from email",
        placeholder="Token from password reset email"
    )
    
    if token:
        success, message = show_password_reset_form(email, token)
        
        if success:
            st.divider()
            if st.button("🔗 Return to Login"):
                st.session_state.reset_stage = "request"
                st.session_state.reset_email = None
                st.switch_page("pages/03_careerhub_auth.py")
        elif message:
            st.error(f"❌ {message}")

st.divider()

if st.button("← Back to Login", use_container_width=True):
    st.switch_page("pages/03_careerhub_auth.py")
