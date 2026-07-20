"""UI-neutral ATS service functions.

This module is the first migration boundary between the current Streamlit app
and a future FastAPI backend. It keeps the existing ATS behavior available
without importing Streamlit pages.
"""

from typing import Dict, List, Optional

from ats_engine import (
    ATSConfigurationError,
    clean_and_structure_resume,
    extract_candidate_name,
    extract_text_from_pdf,
    generate_compliant_feedback,
    generate_resume_improvement_suggestions,
    get_embedding,
    match_profile_to_jd,
    optimize_cv_for_jd,
    rank_candidates,
    validate_resume_document,
)


def extract_resume_text(uploaded_file) -> str:
    """Extract text from a PDF-like uploaded file object."""
    return extract_text_from_pdf(uploaded_file)


def rank_resumes(job_description: str, candidates_data: List[Dict[str, str]]) -> List[Dict]:
    """Rank candidate resumes against a job description."""
    return rank_candidates(job_description, candidates_data)


def generate_candidate_feedback(
    job_description: str,
    candidate_resume: str,
    candidate_name: Optional[str] = None,
) -> str:
    """Generate compliant candidate feedback for a role/resume pair."""
    return generate_compliant_feedback(job_description, candidate_resume, candidate_name)


def generate_candidate_improvements(job_description: str, candidate_resume: str) -> str:
    """Generate candidate-facing resume improvement suggestions."""
    return generate_resume_improvement_suggestions(job_description, candidate_resume)


__all__ = [
    "ATSConfigurationError",
    "clean_and_structure_resume",
    "extract_candidate_name",
    "extract_resume_text",
    "extract_text_from_pdf",
    "generate_candidate_feedback",
    "generate_candidate_improvements",
    "generate_compliant_feedback",
    "generate_resume_improvement_suggestions",
    "get_embedding",
    "match_profile_to_jd",
    "optimize_cv_for_jd",
    "rank_candidates",
    "rank_resumes",
    "validate_resume_document",
]
