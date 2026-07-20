"""Candidate profile routes."""

from fastapi import APIRouter

from backend.routes._responses import require_success
from backend.schemas import ExperienceCreate, ExperienceUpdate, ProfileUpdate, SkillCreate
from services.profile_service import (
    add_skill,
    add_work_experience,
    delete_skill,
    delete_work_experience,
    fetch_profile_bundle,
    get_or_create_profile,
    update_profile,
    update_work_experience,
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


@router.post("/{user_email}/experiences", status_code=201)
def create_experience(user_email: str, request: ExperienceCreate):
    return require_success(add_work_experience(user_email, **request.model_dump()))


@router.put("/{user_email}/experiences/{experience_id}")
def edit_experience(user_email: str, experience_id: str, request: ExperienceUpdate):
    return require_success(update_work_experience(user_email, experience_id, request.data), status_code=404)


@router.delete("/{user_email}/experiences/{experience_id}")
def remove_experience(user_email: str, experience_id: str):
    return require_success(delete_work_experience(user_email, experience_id))


@router.post("/{user_email}/skills", status_code=201)
def create_skill(user_email: str, request: SkillCreate):
    return require_success(add_skill(user_email, request.skill_name, request.proficiency))


@router.delete("/{user_email}/skills/{skill_id}")
def remove_skill(user_email: str, skill_id: str):
    return require_success(delete_skill(user_email, skill_id))
