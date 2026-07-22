"""UI-neutral auth service functions."""

from typing import Dict, Optional

from careerhub_db import get_user, sign_in, sign_up, update_user


def register_user(email: str, password: str, role: str = "candidate", full_name: str = "", job_title: str = "") -> Dict:
    """Create a new user account."""
    return sign_up(email, password, role, full_name, job_title)


def authenticate_user(email: str, password: str, otp_code: Optional[str] = None) -> Dict:
    """Authenticate a user account."""
    result = sign_in(email, password)
    if not result.get("success"):
        return result
    user_result = get_user(email)
    if user_result.get("user", {}).get("two_factor_enabled"):
        if not otp_code:
            return {"success": True, "requires_2fa": True, "user": email}
        from services.security_service import verify_second_factor
        if not verify_second_factor(email, otp_code):
            return {"success": False, "error": "Invalid authenticator or backup code"}
    return result


def fetch_user(email: str) -> Dict:
    """Fetch a user record."""
    return get_user(email)


def update_user_record(email: str, data: Dict) -> Dict:
    """Update a user record."""
    return update_user(email, data)


__all__ = [
    "authenticate_user",
    "fetch_user",
    "register_user",
    "update_user_record",
]
