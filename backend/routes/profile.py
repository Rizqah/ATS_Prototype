"""Candidate profile routes."""

from fastapi import APIRouter

from backend.routes._responses import require_success
from backend.schemas import ProfileUpdate
from services.profile_service import (
    fetch_profile_bundle,
    get_or_create_profile,
    update_profile,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/{user_email}")
def get_profile_bundle(user_email: str):
    result = fetch_profile_bundle(user_email)
    return require_success(result, status_code=404)


@router.post("/{user_email}", status_code=201)
def create_profile(user_email: str, full_name: str = ""):
    return require_success(get_or_create_profile(user_email, full_name))


@router.put("/{user_email}")
def edit_profile(user_email: str, request: ProfileUpdate):
    return require_success(update_profile(user_email, request.data), status_code=404)
