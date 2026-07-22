"""UI-neutral profile and application data service functions."""

from typing import Dict

from careerhub_db import (
    add_achievement,
    add_skill,
    add_work_experience,
    check_cv_limit,
    create_or_get_profile,
    delete_achievement,
    delete_cv,
    delete_skill,
    delete_work_experience,
    get_achievements,
    get_generated_cvs,
    get_profile,
    get_skills,
    get_work_experience,
    increment_cv_count,
    save_generated_cv,
    update_cv_status,
    update_profile,
    update_skill,
    update_work_experience,
)


def get_or_create_profile(user_email: str, full_name: str = "") -> Dict:
    """Fetch a profile or create it if missing."""
    return create_or_get_profile(user_email, full_name)


def fetch_profile_bundle(user_email: str) -> Dict:
    """Fetch the profile data commonly needed by candidate pages."""
    profile = get_profile(user_email)
    experiences = get_work_experience(user_email)
    skills = get_skills(user_email)
    cvs = get_generated_cvs(user_email)
    achievements_by_experience = {}
    achievement_errors = []
    for experience in experiences.get("experiences", []):
        achievement_result = get_achievements(experience["id"])
        achievements_by_experience[experience["id"]] = achievement_result.get("achievements", [])
        if not achievement_result.get("success"):
            achievement_errors.append(achievement_result.get("error"))

    return {
        "success": all(item.get("success") for item in [profile, experiences, skills, cvs]),
        "profile": profile.get("profile"),
        "experiences": experiences.get("experiences", []),
        "skills": skills.get("skills", []),
        "cvs": cvs.get("cvs", []),
        "achievements_by_experience": achievements_by_experience,
        "errors": [
            item.get("error")
            for item in [profile, experiences, skills, cvs]
            if not item.get("success")
        ] + achievement_errors,
    }


__all__ = [
    "add_achievement",
    "add_skill",
    "add_work_experience",
    "check_cv_limit",
    "create_or_get_profile",
    "delete_achievement",
    "delete_cv",
    "delete_skill",
    "delete_work_experience",
    "fetch_profile_bundle",
    "get_achievements",
    "get_generated_cvs",
    "get_or_create_profile",
    "get_profile",
    "get_skills",
    "get_work_experience",
    "increment_cv_count",
    "save_generated_cv",
    "update_cv_status",
    "update_profile",
    "update_skill",
    "update_work_experience",
]
