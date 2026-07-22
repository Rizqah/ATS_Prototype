"""Candidate profile routes."""

from fastapi import APIRouter

from routes._responses import require_success
from schemas import AchievementCreate, ExperienceCreate, ExperienceUpdate, ProfileUpdate, SkillCreate, SkillUpdate
from services.profile_service import (
    add_skill,
    add_achievement,
    add_work_experience,
    delete_skill,
    delete_achievement,
    delete_work_experience,
    fetch_profile_bundle,
    get_or_create_profile,
    update_profile,
    update_work_experience,
    update_skill,
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


@router.put("/{user_email}/skills/{skill_id}")
def edit_skill(user_email: str, skill_id: str, request: SkillUpdate):
    return require_success(update_skill(user_email, skill_id, request.data), status_code=404)


@router.delete("/{user_email}/skills/{skill_id}")
def remove_skill(user_email: str, skill_id: str):
    return require_success(delete_skill(user_email, skill_id))


@router.post("/{user_email}/experiences/{experience_id}/achievements", status_code=201)
def create_achievement(user_email: str, experience_id: str, request: AchievementCreate):
    return require_success(add_achievement(experience_id, request.achievement, request.metric))


@router.delete("/{user_email}/experiences/{experience_id}/achievements/{achievement_id}")
def remove_achievement(user_email: str, experience_id: str, achievement_id: str):
    return require_success(delete_achievement(experience_id, achievement_id))
