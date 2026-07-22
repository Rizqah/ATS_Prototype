"""ATS matching, extraction, and feedback routes."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from schemas import BatchMatchRequest, FeedbackRequest, ProfileMatchRequest
from services.ats_service import (
    ATSConfigurationError,
    extract_resume_text,
    generate_candidate_feedback,
    generate_candidate_improvements,
    match_profile_to_jd,
    rank_resumes,
    analyse_role_fit,
)

router = APIRouter(prefix="/matching", tags=["matching"])


def _service_error(error: Exception) -> HTTPException:
    status_code = 503 if isinstance(error, ATSConfigurationError) else 500
    return HTTPException(status_code=status_code, detail=str(error))


@router.post("/resume/extract")
async def extract_resume(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=415, detail="Only PDF resumes are supported")
    try:
        return {"filename": file.filename, "text": extract_resume_text(file.file)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/batch")
def match_batch(request: BatchMatchRequest):
    try:
        candidates = [candidate.dict() for candidate in request.candidates]
        return {"candidates": rank_resumes(request.job_description, candidates)}
    except Exception as error:
        raise _service_error(error) from error


@router.post("/analysis")
def analyse_match(request: FeedbackRequest):
    return analyse_role_fit(request.job_description, request.candidate_resume)


@router.post("/profile")
def match_profile(request: ProfileMatchRequest):
    try:
        return match_profile_to_jd(
            request.profile,
            request.work_experiences,
            request.achievements_by_experience,
            request.skills,
            request.job_description,
        )
    except Exception as error:
        raise _service_error(error) from error


@router.post("/feedback")
def create_feedback(request: FeedbackRequest):
    try:
        return {
            "feedback": generate_candidate_feedback(
                request.job_description,
                request.candidate_resume,
                request.candidate_name,
            )
        }
    except Exception as error:
        raise _service_error(error) from error


@router.post("/invite")
def create_interview_invite(request: FeedbackRequest):
    candidate_name = request.candidate_name or "there"
    first_name = candidate_name.split()[0] if candidate_name else "there"
    subject = "Interview invitation for your application"
    invite = f"""Hi {first_name},

Thank you for applying. We have reviewed your CV against the role requirements and your profile meets the shortlist threshold for this position.

We would like to invite you to the next stage of the process. In the interview, we will focus on the experience and skills most relevant to this role, including the areas highlighted in the job description.

Please reply with your availability for a first conversation this week.

Best regards,
Fydara Hiring Team"""
    return {"subject": subject, "invite": invite}


@router.post("/improvements")
def create_improvements(request: FeedbackRequest):
    try:
        return {
            "improvements": generate_candidate_improvements(
                request.job_description,
                request.candidate_resume,
            )
        }
    except Exception as error:
        raise _service_error(error) from error
