"""CV generation and optimization routes."""

from fastapi import APIRouter, HTTPException, Response

from backend.schemas import CVOptimizeRequest, CVRequest
from services.ats_service import ATSConfigurationError
from services.cv_service import (
    generate_cv_pdf,
    generate_cv_word,
    optimize_cv_content,
    render_cv_text,
)

router = APIRouter(prefix="/cv", tags=["cv"])


def _service_error(error: Exception) -> HTTPException:
    status_code = 503 if isinstance(error, ATSConfigurationError) else 500
    return HTTPException(status_code=status_code, detail=str(error))


@router.post("/render")
def render(request: CVRequest):
    return {
        "text": render_cv_text(
            request.profile,
            request.work_experiences,
            request.achievements_by_experience,
            request.skills,
        )
    }


@router.post("/pdf")
def pdf(request: CVRequest):
    try:
        content, match_score = generate_cv_pdf(
            request.profile,
            request.work_experiences,
            request.achievements_by_experience,
            request.skills,
            request.job_description,
        )
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="truefit-cv.pdf"',
                "X-TrueFit-Match-Score": str(match_score),
            },
        )
    except Exception as error:
        raise _service_error(error) from error


@router.post("/docx")
def docx(request: CVRequest):
    try:
        content = generate_cv_word(
            request.profile,
            request.work_experiences,
            request.achievements_by_experience,
            request.skills,
        )
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": 'attachment; filename="truefit-cv.docx"'},
        )
    except Exception as error:
        raise _service_error(error) from error


@router.post("/optimize")
def optimize(request: CVOptimizeRequest):
    try:
        return optimize_cv_content(
            request.profile,
            request.work_experiences,
            request.achievements_by_experience,
            request.skills,
            request.job_description,
        )
    except Exception as error:
        raise _service_error(error) from error
