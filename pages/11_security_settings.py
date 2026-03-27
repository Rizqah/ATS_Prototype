import streamlit as st
from styles import inject_global_css
from ui_components import show_top_navigation, show_success_toast, show_error_toast
from security_auth_helpers import (
    show_password_reset_request,
    show_password_reset_form,
    check_password_strength,
    show_2fa_setup_screen,
    verify_2fa_code,
    show_privacy_settings_modal,
    show_privacy_policy,
    show_terms_of_service,
    is_email_verified,
    show_email_verification_prompt
)

# Inject global CSS
inject_global_css()

st.set_page_config(
    page_title="TrueFit - Security Settings",
    page_icon="🔒",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Please log in first")
    st.switch_page("pages/03_careerhub_auth.py")

user_email = st.session_state.user_email

# Show top navigation
show_top_navigation("Security Settings")

st.title("🔒 Security & Privacy")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Password",
    "Email Verification",
    "Two-Factor Auth",
    "Privacy",
    "Account"
])

# ======================================================
# TAB 1: PASSWORD MANAGEMENT
# ======================================================
with tab1:
    st.subheader("🔐 Password Management")
    
    mode = st.radio(
        "What would you like to do?",
        ["Change Password", "Password Strength Guidelines"],
        horizontal=True
    )
    
    if mode == "Change Password":
        st.write("Update your password regularly to keep your account secure.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_password = st.text_input(
                "Current Password",
                type="password",
                placeholder="Enter your current password"
            )
        
        with col2:
            st.empty()
        
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="At least 8 characters"
        )
        
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your new password"
        )
        
        # Password strength display
        if new_password:
            strength = check_password_strength(new_password)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Strength", strength["indicator"])
            with col2:
                if strength["feedback"]:
                    for tip in strength["feedback"]:
                        st.caption(f"💡 {tip}")
        
        st.divider()
        
        if st.button("✓ Update Password", use_container_width=True, type="primary"):
            # Validation
            if not current_password or not new_password or not confirm_password:
                st.error("❌ Please fill in all fields")
            elif new_password != confirm_password:
                st.error("❌ Passwords don't match")
            elif len(new_password) < 8:
                st.error("❌ Password must be at least 8 characters")
            else:
                strength = check_password_strength(new_password)
                if strength["score"] < 2:
                    st.error(f"❌ Password is too weak. {strength['message']}")
                else:
                    # In production: verify current password, hash new password, update DB
                    st.success("✅ Password updated successfully!")
                    show_success_toast("Password changed")
    
    else:  # Password Strength Guidelines
        st.write("**Create a strong password that is:**")
        
        guidelines = [
            ("✓ At least 12 characters long", "Longer passwords are harder to crack"),
            ("✓ Contains uppercase letters (A-Z)", "Mix of cases makes it stronger"),
            ("✓ Contains lowercase letters (a-z)", "Adds variety to character set"),
            ("✓ Contains numbers (0-9)", "Increases complexity"),
            ("✓ Contains special characters (!@#$)", "Maximum security boost"),
            ("✗ Not your name or email", "Personal info is easy to guess"),
            ("✗ Not dictionary words", "Dictionary attacks exist"),
            ("✗ Not repeated patterns (aaaa, 1234)", "Patterns are easy to guess"),
        ]
        
        for guideline, explanation in guidelines:
            st.markdown(f"**{guideline}**")
            st.caption(f"_{explanation}_")
            st.write("")

# ======================================================
# TAB 2: EMAIL VERIFICATION
# ======================================================
with tab2:
    st.subheader("📧 Email Verification")
    
    st.write(f"**Current Email:** {user_email}")
    
    verified = is_email_verified(user_email)
    
    if verified:
        st.success("✅ Email verified")
        
        if st.button("📧 Use Different Email", use_container_width=True):
            st.session_state.change_email = True
            st.rerun()
    else:
        st.warning("⚠️ Email not yet verified")
        if show_email_verification_prompt(user_email):
            show_success_toast("Email verified")
            st.rerun()

        if (
            st.session_state.get("verification_preview_email") == user_email
            and st.session_state.get("verification_preview_token")
        ):
            st.info(
                "Development verification code: "
                f"`{st.session_state['verification_preview_token']}`"
            )

# ======================================================
# TAB 3: TWO-FACTOR AUTHENTICATION
# ======================================================
with tab3:
    st.subheader("🔐 Two-Factor Authentication (2FA)")
    
    st.info("""
    Two-factor authentication adds an extra layer of security. 
    You'll need to enter a code from your authenticator app when logging in.
    """)
    
    # Check if 2FA is enabled
    has_2fa = st.session_state.get("has_2fa", False)
    
    if has_2fa:
        st.success("✅ Two-factor authentication is enabled")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 View Backup Codes", use_container_width=True):
                st.info("Backup codes shown below (keep these safe):")
                st.code("1A2B3C4D\n5E6F7G8H\n9I0J1K2L\n3M4N5O6P\n7Q8R9S0T")
        
        with col2:
            if st.button("🔓 Disable 2FA", use_container_width=True, type="secondary"):
                if st.checkbox("I understand this reduces security"):
                    if st.button("Confirm Disable 2FA", key="confirm_disable_2fa"):
                        st.session_state.has_2fa = False
                        st.success("✅ Two-factor authentication disabled")
                        st.rerun()
    else:
        st.write("Two-factor authentication is not enabled on your account.")
        
        if st.button("🛡️ Enable 2FA Now", use_container_width=True, type="primary"):
            st.session_state.setup_2fa = True
        
        if st.session_state.get("setup_2fa", False):
            st.divider()
            success = show_2fa_setup_screen(user_email)
            if success:
                st.session_state.has_2fa = True
                st.session_state.setup_2fa = False
                st.rerun()

# ======================================================
# TAB 4: PRIVACY & DATA
# ======================================================
with tab4:
    st.subheader("🔒 Privacy & Data Management")
    
    mode = st.radio(
        "What would you like to view?",
        ["Privacy Settings", "Privacy Policy", "Terms of Service"],
        horizontal=True
    )
    
    if mode == "Privacy Settings":
        show_privacy_settings_modal(user_email)
    
    elif mode == "Privacy Policy":
        st.divider()
        show_privacy_policy()
    
    else:  # Terms of Service
        st.divider()
        show_terms_of_service()

# ======================================================
# TAB 5: ACCOUNT MANAGEMENT
# ======================================================
with tab5:
    st.subheader("👤 Account Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Account Information**")
        st.write(f"Email: {user_email}")
        st.write("Account Type: Free")
        st.write("Member Since: January 2026")
        
        st.divider()
        
        st.write("**Session**")
        if st.button("🚪 Logout", key="security_account_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.success("Logged out successfully!")
            st.switch_page("pages/03_careerhub_auth.py")
    
    with col2:
        st.write("**Account Actions**")
        
        if st.button("📥 Download My Data", key="security_download_data", use_container_width=True):
            st.info("Your data export is being prepared. Check your email for the download link.")
        
        st.divider()
        
        st.write("**Dangerous Zone**")
        
        if st.checkbox("I want to delete my account"):
            st.warning("""
            ⚠️ **This action cannot be undone!**
            - All your data will be permanently deleted
            - Your account cannot be recovered
            - Generated CVs will be removed
            """)
            
            if st.text_input("Type your email to confirm: ") == user_email:
                if st.button(
                    "🗑️ Delete My Account Permanently",
                    key="security_delete_account",
                    use_container_width=True,
                    type="secondary",
                ):
                    st.error("Account deletion requested. Please check your email to confirm.")
                    # In production: send confirmation email before actual deletion

# Back button
st.divider()

if st.button("← Back to Dashboard", key="security_back_dashboard", use_container_width=True):
    st.switch_page("pages/04_careerhub_dashboard.py")
