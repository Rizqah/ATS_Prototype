"""UI-neutral auth service functions."""

from typing import Dict

from careerhub_db import get_user, sign_in, sign_up, update_user


def register_user(email: str, password: str) -> Dict:
    """Create a new user account."""
    return sign_up(email, password)


def authenticate_user(email: str, password: str) -> Dict:
    """Authenticate a user account."""
    return sign_in(email, password)


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
