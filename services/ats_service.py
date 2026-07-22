"""UI-neutral ATS service functions.

Framework-neutral access to the existing matching and document logic. It does
not depend on a frontend framework.
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
from services.matching_analysis import analyse_role_fit


def extract_resume_text(uploaded_file) -> str:
    """Extract text from a PDF-like uploaded file object."""
    return extract_text_from_pdf(uploaded_file)


def rank_resumes(job_description: str, candidates_data: List[Dict[str, str]]) -> List[Dict]:
    """Rank candidate resumes against a job description."""
    ranked = rank_candidates(job_description, candidates_data)
    for candidate in ranked:
        analysis = analyse_role_fit(job_description, candidate.get("resume", ""))
        semantic_score = max(0.0, min(1.0, float(candidate.get("score", 0))))
        candidate.update(analysis)
        candidate["semantic_score"] = semantic_score
        candidate["score"] = round((semantic_score * 0.35) + ((analysis["evidence_score"] / 100) * 0.65), 4)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


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
    "analyse_role_fit",
    "validate_resume_document",
]
