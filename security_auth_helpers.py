"""
Security & Authentication Helpers - Email verification, password reset, 2FA, rate limiting, privacy
Provides utilities for enhanced authentication and security features.
"""

import streamlit as st
from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta
import hashlib
import secrets
import re
import json
from pathlib import Path

# ======================================================
# EMAIL VERIFICATION SYSTEM (Task 25)
# ======================================================

VERIFICATION_CONFIG = {
    "token_expiry_hours": 24,
    "max_resend_attempts": 3,
    "resend_cooldown_minutes": 5,
    "token_length": 32
}


def generate_verification_token() -> str:
    """Generate secure verification token"""
    return secrets.token_urlsafe(VERIFICATION_CONFIG["token_length"])


def send_verification_email(email: str, full_name: str, token: str) -> Tuple[bool, str]:
    """
    Send verification email to user.
    
    Note: In production, this would use SendGrid, AWS SES, or similar.
    For development, we simulate the send.
    
    Args:
        email: User's email address
        full_name: User's full name
        token: Verification token
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    
    # Simulate email send
    try:
        # In production, would use:
        # sendgrid_client.mail.send(Mail(...))
        # or
        # boto3_client.send_email(...)
        
        # For now, store token in session/database
        verification_data = {
            "email": email,
            "token": token,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=VERIFICATION_CONFIG["token_expiry_hours"])).isoformat(),
            "verified": False,
            "resend_count": 0,
            "last_resend_at": None
        }
        
        # Store in session for demo
        if "verification_tokens" not in st.session_state:
            st.session_state.verification_tokens = {}
        st.session_state.verification_tokens[email] = verification_data
        
        return True, f"Verification email sent to {email}"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


def show_email_verification_prompt(email: str) -> bool:
    """
    Display email verification UI.
    
    Args:
        email: Email to verify
        
    Returns:
        True if verified, False otherwise
    """
    
    st.info(f"📧 Please verify your email: **{email}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        verification_code = st.text_input(
            "Enter verification code",
            placeholder="6-digit code from your email",
            max_chars=32
        )
    
    with col2:
        if st.button("✓ Verify", use_container_width=True):
            if verify_email_token(email, verification_code):
                st.success("✅ Email verified successfully!")
                return True
            else:
                st.error("❌ Invalid or expired code. Please try again.")
                return False
    
    # Resend option
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Resend Code", use_container_width=True):
            success, message = resend_verification_email(email)
            if success:
                st.success(message)
            else:
                st.warning(message)
    
    with col2:
        if st.button("📧 Change Email", use_container_width=True):
            st.session_state.change_email = True
            st.rerun()
    
    return False


def verify_email_token(email: str, token: str) -> bool:
    """
    Verify email token.
    
    Args:
        email: Email address
        token: Verification token
        
    Returns:
        True if token is valid, False otherwise
    """
    
    if "verification_tokens" not in st.session_state:
        return False
    
    if email not in st.session_state.verification_tokens:
        return False
    
    token_data = st.session_state.verification_tokens[email]
    
    # Check expiry
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.now() > expires_at:
        return False
    
    # Check token match
    if token_data["token"] != token:
        return False
    
    # Mark as verified
    token_data["verified"] = True
    return True


def resend_verification_email(email: str) -> Tuple[bool, str]:
    """
    Resend verification email with cooldown check.
    
    Args:
        email: Email address
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    
    if "verification_tokens" not in st.session_state:
        st.session_state.verification_tokens = {}
    
    if email not in st.session_state.verification_tokens:
        return False, "Email not found in verification system"
    
    token_data = st.session_state.verification_tokens[email]
    
    # Check resend limit
    if token_data["resend_count"] >= VERIFICATION_CONFIG["max_resend_attempts"]:
        return False, f"Maximum resend attempts reached. Please contact support."
    
    # Check cooldown
    if token_data["last_resend_at"]:
        last_resend = datetime.fromisoformat(token_data["last_resend_at"])
        cooldown_time = timedelta(minutes=VERIFICATION_CONFIG["resend_cooldown_minutes"])
        if datetime.now() < last_resend + cooldown_time:
            remaining = int((last_resend + cooldown_time - datetime.now()).total_seconds() / 60)
            return False, f"Please wait {remaining} minutes before resending"
    
    # Generate new token
    new_token = generate_verification_token()
    token_data["token"] = new_token
    token_data["resend_count"] += 1
    token_data["last_resend_at"] = datetime.now().isoformat()
    token_data["expires_at"] = (datetime.now() + timedelta(hours=VERIFICATION_CONFIG["token_expiry_hours"])).isoformat()
    
    return True, "Verification email resent successfully"


def is_email_verified(email: str) -> bool:
    """Check if email is verified"""
    if "verification_tokens" not in st.session_state:
        return False
    if email not in st.session_state.verification_tokens:
        return False
    return st.session_state.verification_tokens[email].get("verified", False)


# ======================================================
# PASSWORD RESET FLOW (Task 2)
# ======================================================

def show_password_reset_request() -> Optional[str]:
    """
    Display password reset request form.
    
    Returns:
        Email if user submits, None otherwise
    """
    
    st.subheader("🔐 Reset Your Password")
    
    email = st.text_input(
        "Enter your email address",
        placeholder="your.email@example.com"
    )
    
    if st.button("📧 Send Reset Link", use_container_width=True, type="primary"):
        if email and "@" in email:
            # In production: send actual email with reset link
            reset_token = generate_verification_token()
            
            # Store reset token
            if "password_reset_tokens" not in st.session_state:
                st.session_state.password_reset_tokens = {}
            
            st.session_state.password_reset_tokens[email] = {
                "token": reset_token,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
                "used": False
            }
            
            st.success(f"✅ Reset link sent to {email}")
            st.info(f"🔗 Reset token (development): `{reset_token}`")
            return email
        else:
            st.error("❌ Please enter a valid email address")
    
    return None


def show_password_reset_form(email: str, token: str) -> Tuple[bool, str]:
    """
    Display password reset form.
    
    Args:
        email: User's email
        token: Reset token
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    
    st.subheader("🔓 Create New Password")
    st.write(f"Resetting password for: **{email}**")
    
    # Validate token
    if "password_reset_tokens" not in st.session_state or email not in st.session_state.password_reset_tokens:
        return False, "Invalid or expired reset link"
    
    token_data = st.session_state.password_reset_tokens[email]
    
    # Check token expiry
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.now() > expires_at:
        return False, "Reset link has expired. Please request a new one."
    
    # Check token match
    if token_data["token"] != token:
        return False, "Invalid reset token"
    
    # Check if already used
    if token_data["used"]:
        return False, "This reset link has already been used"
    
    # Password form
    new_password = st.text_input(
        "New Password",
        type="password",
        placeholder="At least 8 characters"
    )
    
    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password"
    )
    
    # Password strength indicator
    if new_password:
        strength = check_password_strength(new_password)
        st.markdown(f"**Password Strength:** {strength['indicator']} {strength['message']}")
    
    if st.button("🔐 Reset Password", use_container_width=True, type="primary"):
        # Validate
        if not new_password or not confirm_password:
            st.error("❌ Please fill in all fields")
            return False, "Empty fields"
        
        if new_password != confirm_password:
            st.error("❌ Passwords don't match")
            return False, "Passwords don't match"
        
        if len(new_password) < 8:
            st.error("❌ Password must be at least 8 characters")
            return False, "Password too short"
        
        strength = check_password_strength(new_password)
        if strength["score"] < 2:
            st.error(f"❌ Password is too weak. {strength['message']}")
            return False, "Weak password"
        
        # Update password (in production: hash and store in database)
        token_data["used"] = True
        st.success("✅ Password reset successfully! Please log in with your new password.")
        return True, "Password reset successfully"
    
    return False, ""


def check_password_strength(password: str) -> Dict:
    """
    Check password strength.
    
    Args:
        password: Password to check
        
    Returns:
        Dict with score and indicator
    """
    
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    else:
        feedback.append("Use at least 12 characters")
    
    # Uppercase
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    # Lowercase
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    # Numbers
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    # Special characters
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    else:
        feedback.append("Add special characters")
    
    # Indicator
    if score >= 4:
        indicator = "🟢 Strong"
    elif score >= 3:
        indicator = "🟡 Fair"
    else:
        indicator = "🔴 Weak"
    
    message = " | ".join(feedback) if feedback else "Great password!"
    
    return {
        "score": score,
        "indicator": indicator,
        "message": message,
        "feedback": feedback
    }


# ======================================================
# TWO-FACTOR AUTHENTICATION (Task 26)
# ======================================================

def enable_2fa_setup(email: str) -> str:
    """
    Setup two-factor authentication.
    
    Args:
        email: User's email
        
    Returns:
        Secret key for QR code generation
    """
    
    import pyotp
    
    # Generate secret
    secret = pyotp.random_base32()
    
    # Store in session
    if "2fa_setup" not in st.session_state:
        st.session_state["2fa_setup"] = {}
    
    st.session_state["2fa_setup"][email] = {
        "secret": secret,
        "created_at": datetime.now().isoformat(),
        "verified": False,
        "backup_codes": generate_backup_codes(5)
    }
    
    return secret


def generate_backup_codes(count: int = 5) -> List[str]:
    """Generate backup codes for 2FA"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def show_2fa_setup_screen(email: str) -> bool:
    """
    Display 2FA setup UI with QR code.
    
    Args:
        email: User's email
        
    Returns:
        True if setup successful
    """
    
    st.subheader("🔐 Enable Two-Factor Authentication")
    
    if email not in st.session_state.get("2fa_setup", {}):
        secret = enable_2fa_setup(email)
    else:
        secret = st.session_state["2fa_setup"][email]["secret"]
    
    # Display secret and QR code info
    st.info("""
    Two-factor authentication adds an extra layer of security to your account.
    You'll need to enter a code from your authenticator app (Google Authenticator, Authy, etc.) 
    along with your password when logging in.
    """)
    
    # Step 1: Scan QR code
    st.write("**Step 1: Scan QR Code**")
    st.write("Use an authenticator app (Google Authenticator, Authy, Microsoft Authenticator) to scan:")
    st.code(f"otpauth://totp/{email}?secret={secret}&issuer=CareerHub")
    st.write("Or enter this code manually:")
    st.code(secret)
    
    st.divider()
    
    # Step 2: Verify code
    st.write("**Step 2: Verify with Code**")
    verification_code = st.text_input(
        "Enter 6-digit code from authenticator app",
        placeholder="000000",
        max_chars=6
    )
    
    if st.button("✓ Verify & Enable 2FA", use_container_width=True, type="primary"):
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            if totp.verify(verification_code):
                st.session_state["2fa_setup"][email]["verified"] = True
                st.success("✅ Two-factor authentication enabled successfully!")
                
                # Show backup codes
                st.warning("**⚠️ Save Your Backup Codes**")
                st.write("Keep these codes in a safe place. You can use them if you lose access to your authenticator.")
                backup_codes = st.session_state["2fa_setup"][email]["backup_codes"]
                st.code("\n".join(backup_codes))
                
                return True
            else:
                st.error("❌ Invalid code. Please try again.")
                return False
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return False
    
    return False


def verify_2fa_code(email: str, code: str) -> bool:
    """
    Verify 2FA code during login.
    
    Args:
        email: User's email
        code: 6-digit code
        
    Returns:
        True if valid
    """
    
    try:
        import pyotp
        
        if email not in st.session_state.get("2fa_setup", {}):
            return False
        
        setup_data = st.session_state["2fa_setup"][email]
        if not setup_data.get("verified"):
            return False
        
        secret = setup_data["secret"]
        totp = pyotp.TOTP(secret)
        
        # Allow code from current window and previous 30 seconds
        return totp.verify(code, valid_window=1)
        
    except Exception as e:
        return False


# ======================================================
# RATE LIMITING (Task 27)
# ======================================================

RATE_LIMIT_CONFIG = {
    "login_attempts": {"max": 5, "window_minutes": 15},
    "password_reset": {"max": 3, "window_minutes": 60},
    "api_calls": {"max": 100, "window_minutes": 60},
    "cv_generation": {"max": 20, "window_minutes": 1440},  # Daily
}


def check_rate_limit(action: str, identifier: str) -> Tuple[bool, str]:
    """
    Check if action is rate limited.
    
    Args:
        action: Type of action (login_attempts, password_reset, etc.)
        identifier: User identifier (email, IP, etc.)
        
    Returns:
        Tuple of (allowed: bool, message: str)
    """
    
    if action not in RATE_LIMIT_CONFIG:
        return True, ""
    
    config = RATE_LIMIT_CONFIG[action]
    
    if "rate_limits" not in st.session_state:
        st.session_state.rate_limits = {}
    
    key = f"{action}:{identifier}"
    
    if key not in st.session_state.rate_limits:
        st.session_state.rate_limits[key] = {
            "count": 0,
            "first_attempt": datetime.now(),
            "attempts": []
        }
    
    limit_data = st.session_state.rate_limits[key]
    window = timedelta(minutes=config["window_minutes"])
    
    # Remove old attempts outside window
    cutoff_time = datetime.now() - window
    limit_data["attempts"] = [
        attempt for attempt in limit_data["attempts"]
        if datetime.fromisoformat(attempt) > cutoff_time
    ]
    
    # Check if at limit
    if len(limit_data["attempts"]) >= config["max"]:
        oldest_attempt = datetime.fromisoformat(limit_data["attempts"][0])
        reset_time = oldest_attempt + window
        remaining = int((reset_time - datetime.now()).total_seconds() / 60) + 1
        
        return False, f"Too many attempts. Please try again in {remaining} minute(s)."
    
    # Record this attempt
    limit_data["attempts"].append(datetime.now().isoformat())
    
    return True, ""


def record_failed_attempt(action: str, identifier: str) -> None:
    """Record a failed attempt for rate limiting"""
    check_rate_limit(action, identifier)


# ======================================================
# PRIVACY POLICY & DATA RETENTION (Task 28)
# ======================================================

PRIVACY_POLICY = """
# Privacy Policy

**Last Updated:** February 2026

## 1. Data We Collect

We collect the following types of information:
- **Account Information:** Name, email, phone number, location
- **Profile Data:** Work experience, skills, achievements, qualifications
- **Usage Data:** Pages visited, features used, CV generation records
- **Technical Data:** IP address, browser type, device information

## 2. How We Use Your Data

Your data is used to:
- Provide and improve our services
- Generate tailored CVs and match scores
- Send service emails (verification, password reset, notifications)
- Analyze usage patterns to improve UX
- Comply with legal obligations

## 3. Data Security

- All data is encrypted in transit (HTTPS/TLS)
- Passwords are hashed using bcrypt
- Database access is restricted and logged
- Regular security audits are conducted
- Sensitive data is masked in logs

## 4. Data Retention

- **Active Accounts:** Data retained while account is active
- **Inactive Accounts:** Deleted after 12 months of inactivity
- **Generated CVs:** Retained for 24 months, then archived
- **Logs:** Retained for 90 days for security purposes
- **Email Records:** Retained for 30 days

## 5. Data Sharing

We do NOT share your personal data with third parties, except:
- Service providers (payment processors, email services) under contract
- Legal authorities when required by law
- With your explicit consent

## 6. Your Rights

You have the right to:
- Access your personal data
- Request corrections to your data
- Delete your account and associated data
- Export your data
- Opt-out of non-essential communications

## 7. Contact

For privacy concerns, contact: privacy@careerhub.example.com
"""

TERMS_OF_SERVICE = """
# Terms of Service

**Last Updated:** February 2026

## 1. Acceptance of Terms

By using CareerHub, you agree to these terms and conditions.

## 2. Use License

You are granted a limited, non-exclusive license to use this service for personal use only.

## 3. Disclaimer

The service is provided "as-is". We make no guarantees about:
- Job matching accuracy
- Match scores
- Interview outcomes
- Hiring decisions

## 4. User Responsibilities

You agree to:
- Provide accurate information
- Not use the service for unlawful purposes
- Not reverse-engineer or scrape the platform
- Not share your account with others
- Comply with all applicable laws

## 5. Limitation of Liability

We are not liable for any indirect, incidental, special, or consequential damages.

## 6. Changes to Terms

We may update these terms. Continued use means acceptance of new terms.

## 7. Governing Law

These terms are governed by applicable jurisdiction laws.
"""


def show_privacy_policy() -> None:
    """Display privacy policy"""
    st.markdown(PRIVACY_POLICY)


def show_terms_of_service() -> None:
    """Display terms of service"""
    st.markdown(TERMS_OF_SERVICE)


def show_privacy_settings_modal(user_email: str) -> None:
    """
    Display privacy and data management settings.
    
    Args:
        user_email: User's email
    """
    
    st.subheader("🔒 Privacy & Data Settings")
    
    tab1, tab2, tab3 = st.tabs(["Data Usage", "Communications", "Account"])
    
    with tab1:
        st.write("**Data Usage Preferences**")
        
        use_analytics = st.checkbox(
            "Allow usage analytics to improve the service",
            value=True,
            help="We track which features you use to make CareerHub better"
        )
        
        use_recommendations = st.checkbox(
            "Allow job recommendations based on your profile",
            value=True,
            help="We suggest job titles and industries based on your skills"
        )
        
        show_testimonial = st.checkbox(
            "Allow anonymized usage as testimonial/case study",
            value=False,
            help="We may show 'User improved match score by X%' without identifying you"
        )
        
        st.divider()
        st.info("💾 Your data is encrypted and never sold to third parties.")
    
    with tab2:
        st.write("**Communication Preferences**")
        
        email_updates = st.checkbox(
            "Receive product updates and feature announcements",
            value=True
        )
        
        email_job_tips = st.checkbox(
            "Receive email tips for better CVs",
            value=True
        )
        
        email_premium = st.checkbox(
            "Receive Premium upgrade offers",
            value=True
        )
        
        st.divider()
        
        if st.button("📧 Manage Email Preferences", use_container_width=True):
            st.success("Email preferences updated!")
    
    with tab3:
        st.write("**Account & Data Management**")
        
        st.write("**Download Your Data**")
        st.write("Download a copy of all your data in JSON format.")
        
        if st.button("📥 Download My Data", use_container_width=True):
            st.info("📦 Your data export is ready. Check your email for the download link.")
        
        st.divider()
        
        st.write("**Delete Account & Data**")
        st.warning("⚠️ This action is irreversible. All your data will be permanently deleted.")
        
        if st.checkbox("I understand this action cannot be undone"):
            if st.button("🗑️ Delete My Account", use_container_width=True, type="secondary"):
                st.error("Account deletion requested. We'll send a confirmation email.")
        
        st.divider()
        
        st.write("**Data Retention**")
        st.info("""
        - Active account data: Retained indefinitely
        - Inactive account (12+ months): Automatically deleted
        - Generated CVs: Retained for 24 months
        - Backup copies: Kept for 30 days
        """)
