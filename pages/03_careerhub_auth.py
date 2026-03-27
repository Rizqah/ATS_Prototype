import streamlit as st
import re
from careerhub_db import sign_up, sign_in, update_profile
from styles import inject_global_css
from ui_components import show_success_toast, show_error_toast, show_info_toast, show_error
from security_auth_helpers import (
    check_rate_limit,
    record_failed_attempt,
    verify_2fa_code,
    generate_verification_token,
    send_verification_email,
    show_email_verification_prompt,
    is_email_verified,
)

# Inject global CSS
inject_global_css()

st.set_page_config(
    page_title="TrueFit - Authentication",
    page_icon="TF",
    layout="centered"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'
if "pending_verification_email" not in st.session_state:
    st.session_state.pending_verification_email = None

# Check if user is already authenticated
if st.session_state.authenticated:
    st.success(f"Welcome back, {st.session_state.user_email}!")
    next_page = "pages/02_recruiter.py" if st.session_state.get("user_role") == "recruiter" else "pages/04_careerhub_dashboard.py"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Dashboard", use_container_width=True, type="primary"):
            st.switch_page(next_page)

    with col2:
        if st.button("Logout", use_container_width=True):
            if st.button("Are you sure?", key="confirm_logout"):
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.session_state.user_role = None
                st.success("Logged out successfully!")
                st.rerun()
    st.stop()

# Auth UI
st.title("TrueFit")
st.subheader("Your AI-Powered Career Hub")

pending_verification_email = st.session_state.get("pending_verification_email")
if pending_verification_email and not is_email_verified(pending_verification_email):
    st.warning("Verify your email before accessing your dashboard.")
    if show_email_verification_prompt(pending_verification_email):
        from_recruiter = st.session_state.get("auth_source") == "recruiter"
        st.session_state.authenticated = True
        st.session_state.user_email = pending_verification_email
        st.session_state.user_role = "recruiter" if from_recruiter else "applicant_careerhub"
        st.session_state.pending_verification_email = None
        show_success_toast("Email verified. You can now access your account.")
        st.switch_page("pages/02_recruiter.py" if from_recruiter else "pages/04_careerhub_dashboard.py")

    if (
        st.session_state.get("verification_preview_email") == pending_verification_email
        and st.session_state.get("verification_preview_token")
    ):
        st.info(
            "Development verification code: "
            f"`{st.session_state['verification_preview_token']}`"
        )

    st.divider()
    st.stop()

st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 760px;
        padding-top: 1.6rem;
    }
    button[data-baseweb="tab"] p {
        font-weight: 700 !important;
    }
    div[data-testid="stTextInput"] label p {
        font-weight: 700 !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        font-weight: 600 !important;
        opacity: 0.95 !important;
    }
    [data-testid="stBaseButton-primary"] > button {
        min-height: 42px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["Login", "Sign Up"])

# ======================================================
# EMAIL VALIDATION
# ======================================================
def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ======================================================
# LOGIN TAB
# ======================================================
with tab1:
    st.markdown("### Login to Your Account")

    login_email = st.text_input(
        "Email",
        placeholder="your@email.com",
        key="login_email"
    )

    login_password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    if st.button("Login", use_container_width=True, type="primary"):
        # Check rate limiting
        allowed, msg = check_rate_limit("login_attempts", login_email)
        if not allowed:
            show_error_toast(f"Too many login attempts. {msg}")
        # Validation
        elif not login_email or not login_password:
            show_error_toast("Please enter both email and password")
        elif not is_valid_email(login_email):
            show_error("invalid_email")
        else:
            with st.spinner("Logging in..."):
                result = sign_in(login_email, login_password)

                if result["success"]:
                    if not result.get("email_verified", False):
                        st.session_state.pending_verification_email = login_email
                        show_info_toast("Verify your email to finish logging in.")
                        resend_needed = st.session_state.get("verification_preview_email") != login_email
                        if resend_needed:
                            send_verification_email(login_email, "", generate_verification_token())
                        st.rerun()

                    from_recruiter = st.session_state.get("auth_source") == "recruiter"
                    st.session_state.authenticated = True
                    st.session_state.user_email = login_email
                    st.session_state.user_role = "recruiter" if from_recruiter else "applicant_careerhub"
                    show_success_toast("Login successful!")
                    st.balloons()
                    st.switch_page("pages/02_recruiter.py" if from_recruiter else "pages/04_careerhub_dashboard.py")
                else:
                    show_error_toast(result['error'])

    st.divider()
    st.caption("Don't have an account? Sign up in the tab above!")

    # Password reset link
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Forgot Password?", use_container_width=True):
            st.switch_page("pages/12_password_reset.py")
    with col2:
        if st.button("Security Settings", use_container_width=True):
            st.switch_page("pages/11_security_settings.py")

# ======================================================
# SIGN UP TAB
# ======================================================
with tab2:
    st.markdown("### Create Your Account")

    signup_email = st.text_input(
        "Email",
        placeholder="your@email.com",
        key="signup_email"
    )

    signup_password = st.text_input(
        "Password",
        type="password",
        placeholder="Create a password (min 8 characters)",
        key="signup_password"
    )

    signup_password_confirm = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Confirm your password",
        key="signup_password_confirm"
    )

    signup_fullname = st.text_input(
        "Full Name",
        placeholder="John Doe",
        key="signup_fullname"
    )

    if st.button("Create Account", use_container_width=True, type="primary"):
        # Validation
        if not signup_email or not signup_password or not signup_fullname:
            show_error_toast("Please fill in all fields")
        elif not is_valid_email(signup_email):
            show_error("invalid_email")
        elif len(signup_password) < 8:
            show_error_toast("Password must be at least 8 characters")
        elif signup_password != signup_password_confirm:
            show_error("password_mismatch")
        else:
            with st.spinner("Creating account..."):
                result = sign_up(signup_email, signup_password)

                if result["success"]:
                    update_profile(signup_email, {"full_name": signup_fullname})
                    st.session_state.pending_verification_email = signup_email

                    email_sent, message = send_verification_email(
                        signup_email,
                        signup_fullname,
                        generate_verification_token(),
                    )
                    if email_sent:
                        show_success_toast("Account created. Check your email for the verification code.")
                        st.balloons()
                        st.rerun()
                    else:
                        show_error_toast(message)
                else:
                    show_error_toast(result['error'])

    st.divider()
    st.caption("Already have an account? Login in the tab above!")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #999; margin-top: 30px;">
        <small>TrueFit | Helping candidates improve their resumes</small>
    </div>
    """, unsafe_allow_html=True)
