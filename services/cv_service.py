"""UI-neutral CV generation service functions."""

from typing import Dict, List, Optional, Tuple

from cv_generator import (
    format_cv_for_display,
    generate_ats_optimized_cv,
    generate_cv_docx,
    generate_optimized_cv_content,
)


def generate_cv_pdf(
    profile: Dict,
    work_experiences: List[Dict],
    achievements_by_experience: Dict[str, List[Dict]],
    skills: List[Dict],
    job_description: Optional[str] = None,
) -> Tuple[bytes, float]:
    """Generate an ATS-optimized PDF CV and optional match score."""
    return generate_ats_optimized_cv(
        profile,
        work_experiences,
        achievements_by_experience,
        skills,
        job_description,
    )


def generate_cv_word(
    profile: Dict,
    work_experiences: List[Dict],
    achievements_by_experience: Dict[str, List[Dict]],
    skills: List[Dict],
) -> bytes:
    """Generate an editable DOCX CV."""
    return generate_cv_docx(profile, work_experiences, achievements_by_experience, skills)


def render_cv_text(
    profile: Dict,
    work_experiences: List[Dict],
    achievements_by_experience: Dict[str, List[Dict]],
    skills: List[Dict],
) -> str:
    """Render CV content as plain text for storage or previews."""
    return format_cv_for_display(profile, work_experiences, achievements_by_experience, skills)


def optimize_cv_content(
    profile: Dict,
    work_experiences: List[Dict],
    achievements_by_experience: Dict[str, List[Dict]],
    skills: List[Dict],
    job_description: str,
) -> Dict:
    """Generate AI-optimized CV content for a job description."""
    return generate_optimized_cv_content(
        profile,
        work_experiences,
        achievements_by_experience,
        skills,
        job_description,
    )


__all__ = [
    "generate_cv_pdf",
    "generate_cv_word",
    "optimize_cv_content",
    "render_cv_text",
]
