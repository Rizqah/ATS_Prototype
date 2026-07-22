"""UI-neutral account security and password recovery services."""

import hmac
import os
import secrets
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, Dict

from careerhub_db import ACHIEVEMENTS_FILE, CVS_FILE, PROFILES_FILE, SKILLS_FILE, USAGE_FILE, USERS_FILE, WORK_EXP_FILE, hash_password, load_json, save_json
from services.recruiter_service import delete_workspace, get_workspace


_attempts: Dict[str, Deque[datetime]] = defaultdict(deque)


def _rate_limit(key: str, maximum: int, window_minutes: int) -> Dict:
    now = datetime.now()
    cutoff = now - timedelta(minutes=window_minutes)
    bucket = _attempts[key]
    while bucket and bucket[0] < cutoff:
        bucket.popleft()
    if len(bucket) >= maximum:
        retry_after = max(1, int((bucket[0] + timedelta(minutes=window_minutes) - now).total_seconds() / 60) + 1)
        return {"success": False, "error": f"Too many attempts. Try again in {retry_after} minute(s)."}
    bucket.append(now)
    return {"success": True}


def validate_password(password: str) -> Dict:
    feedback = []
    if len(password) < 8:
        feedback.append("Use at least 8 characters")
    if not any(character.isupper() for character in password):
        feedback.append("Add an uppercase letter")
    if not any(character.islower() for character in password):
        feedback.append("Add a lowercase letter")
    if not any(character.isdigit() for character in password):
        feedback.append("Add a number")
    return {"valid": not feedback, "feedback": feedback}


def change_password(email: str, current_password: str, new_password: str) -> Dict:
    limited = _rate_limit(f"password-change:{email.lower()}", 5, 15)
    if not limited["success"]:
        return limited
    strength = validate_password(new_password)
    if not strength["valid"]:
        return {"success": False, "error": ". ".join(strength["feedback"])}
    users = load_json(USERS_FILE)
    user = users.get(email)
    if not user or not hmac.compare_digest(user.get("password_hash", ""), hash_password(current_password)):
        return {"success": False, "error": "Current password is incorrect"}
    if hmac.compare_digest(user["password_hash"], hash_password(new_password)):
        return {"success": False, "error": "New password must be different"}
    user["password_hash"] = hash_password(new_password)
    user["password_changed_at"] = datetime.now().isoformat()
    save_json(USERS_FILE, users)
    return {"success": True, "message": "Password changed successfully"}


def request_password_reset(email: str) -> Dict:
    normalized_email = email.strip().lower()
    limited = _rate_limit(f"password-reset:{normalized_email}", 3, 60)
    if not limited["success"]:
        return limited
    users = load_json(USERS_FILE)
    user = users.get(normalized_email)
    response = {"success": True, "message": "If that account exists, a reset code has been created."}
    if not user:
        return response
    token = str(secrets.randbelow(1_000_000)).zfill(6)
    user["password_reset_token_hash"] = hash_password(token)
    user["password_reset_expires_at"] = (datetime.now() + timedelta(hours=1)).isoformat()
    save_json(USERS_FILE, users)
    if os.getenv("TRUEFIT_ENV", "development").lower() != "production":
        response["development_token"] = token
    return response


def confirm_password_reset(email: str, token: str, new_password: str) -> Dict:
    normalized_email = email.strip().lower()
    limited = _rate_limit(f"password-reset-confirm:{normalized_email}", 5, 15)
    if not limited["success"]:
        return limited
    strength = validate_password(new_password)
    if not strength["valid"]:
        return {"success": False, "error": ". ".join(strength["feedback"])}
    users = load_json(USERS_FILE)
    user = users.get(normalized_email)
    if not user or not user.get("password_reset_token_hash") or not user.get("password_reset_expires_at"):
        return {"success": False, "error": "Invalid or expired reset code"}
    if datetime.now() > datetime.fromisoformat(user["password_reset_expires_at"]):
        return {"success": False, "error": "Invalid or expired reset code"}
    if not hmac.compare_digest(user["password_reset_token_hash"], hash_password(token)):
        return {"success": False, "error": "Invalid or expired reset code"}
    user["password_hash"] = hash_password(new_password)
    user["password_changed_at"] = datetime.now().isoformat()
    user.pop("password_reset_token_hash", None)
    user.pop("password_reset_expires_at", None)
    save_json(USERS_FILE, users)
    return {"success": True, "message": "Password reset successfully"}


def two_factor_status(email: str) -> Dict:
    user = load_json(USERS_FILE).get(email)
    if not user:
        return {"success": False, "error": "Account not found"}
    return {"success": True, "enabled": bool(user.get("two_factor_enabled"))}


def start_two_factor_setup(email: str) -> Dict:
    import pyotp
    users = load_json(USERS_FILE)
    user = users.get(email)
    if not user:
        return {"success": False, "error": "Account not found"}
    secret = pyotp.random_base32()
    user["two_factor_pending_secret"] = secret
    save_json(USERS_FILE, users)
    return {"success": True, "secret": secret, "otpauth_uri": pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="Fydara")}


def confirm_two_factor_setup(email: str, code: str) -> Dict:
    import pyotp
    users = load_json(USERS_FILE)
    user = users.get(email)
    secret = user.get("two_factor_pending_secret") if user else None
    if not secret or not pyotp.TOTP(secret).verify(code, valid_window=1):
        return {"success": False, "error": "Invalid authenticator code"}
    backup_codes = [secrets.token_hex(4).upper() for _ in range(6)]
    user["two_factor_secret"] = secret
    user["two_factor_enabled"] = True
    user["two_factor_backup_hashes"] = [hash_password(item) for item in backup_codes]
    user.pop("two_factor_pending_secret", None)
    save_json(USERS_FILE, users)
    return {"success": True, "message": "Two-factor authentication enabled", "backup_codes": backup_codes}


def verify_second_factor(email: str, code: str, consume_backup: bool = True) -> bool:
    import pyotp
    users = load_json(USERS_FILE)
    user = users.get(email)
    if not user or not user.get("two_factor_enabled"):
        return False
    if pyotp.TOTP(user.get("two_factor_secret", "")).verify(code.replace(" ", ""), valid_window=1):
        return True
    code_hash = hash_password(code.strip().upper())
    backup_hashes = user.get("two_factor_backup_hashes", [])
    for stored_hash in backup_hashes:
        if hmac.compare_digest(stored_hash, code_hash):
            if consume_backup:
                backup_hashes.remove(stored_hash)
                save_json(USERS_FILE, users)
            return True
    return False


def disable_two_factor(email: str, password: str, code: str) -> Dict:
    users = load_json(USERS_FILE)
    user = users.get(email)
    if not user or not hmac.compare_digest(user.get("password_hash", ""), hash_password(password)):
        return {"success": False, "error": "Password is incorrect"}
    if not verify_second_factor(email, code, consume_backup=False):
        return {"success": False, "error": "Invalid authenticator or backup code"}
    user = load_json(USERS_FILE)[email]
    for key in ["two_factor_enabled", "two_factor_secret", "two_factor_backup_hashes", "two_factor_pending_secret"]:
        user.pop(key, None)
    users = load_json(USERS_FILE)
    users[email] = user
    save_json(USERS_FILE, users)
    return {"success": True, "message": "Two-factor authentication disabled"}


def export_personal_data(email: str) -> Dict:
    users = load_json(USERS_FILE)
    if email not in users:
        return {"success": False, "error": "Account not found"}
    safe_user = {key: value for key, value in users[email].items() if key not in {"password_hash", "password_reset_token_hash", "two_factor_secret", "two_factor_pending_secret", "two_factor_backup_hashes"}}
    experiences = load_json(WORK_EXP_FILE).get(email, {})
    achievements = load_json(ACHIEVEMENTS_FILE)
    return {
        "success": True,
        "exported_at": datetime.now().isoformat(),
        "account": safe_user,
        "profile": load_json(PROFILES_FILE).get(email),
        "work_experiences": list(experiences.values()),
        "achievements": {experience_id: achievements.get(experience_id, {}) for experience_id in experiences},
        "skills": list(load_json(SKILLS_FILE).get(email, {}).values()),
        "generated_cvs": list(load_json(CVS_FILE).get(email, {}).values()),
        "usage": load_json(USAGE_FILE).get(email),
        "recruiter_workspace": get_workspace(email).get("workspace"),
    }


def delete_account(email: str, password: str) -> Dict:
    users = load_json(USERS_FILE)
    user = users.get(email)
    if not user or not hmac.compare_digest(user.get("password_hash", ""), hash_password(password)):
        return {"success": False, "error": "Password is incorrect"}
    experiences_store = load_json(WORK_EXP_FILE)
    experience_ids = list(experiences_store.get(email, {}).keys())
    achievements_store = load_json(ACHIEVEMENTS_FILE)
    for experience_id in experience_ids:
        achievements_store.pop(experience_id, None)
    save_json(ACHIEVEMENTS_FILE, achievements_store)
    for path in [PROFILES_FILE, WORK_EXP_FILE, SKILLS_FILE, CVS_FILE, USAGE_FILE]:
        data = load_json(path)
        data.pop(email, None)
        save_json(path, data)
    users.pop(email, None)
    save_json(USERS_FILE, users)
    delete_workspace(email)
    return {"success": True, "message": "Account and associated data deleted"}


__all__ = ["change_password", "confirm_password_reset", "confirm_two_factor_setup", "delete_account", "disable_two_factor", "export_personal_data", "request_password_reset", "start_two_factor_setup", "two_factor_status", "validate_password", "verify_second_factor"]
