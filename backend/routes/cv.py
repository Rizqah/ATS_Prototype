"""CV generation and optimization routes."""

from fastapi import APIRouter, HTTPException, Response

from backend.routes._responses import require_success
from backend.schemas import CVHistoryCreate, CVOptimizeRequest, CVRequest, CVStatusUpdate
from services.ats_service import ATSConfigurationError
from services.profile_service import delete_cv, get_generated_cvs, save_generated_cv, update_cv_status
from services.cv_service import (
    generate_cv_pdf,
    generate_cv_word,
    optimize_cv_content,
    render_cv_text,
)

router = APIRouter(prefix="/cv", tags=["cv"])


@router.get("/history/{user_email}")
def history(user_email: str):
    return require_success(get_generated_cvs(user_email))


@router.post("/history/{user_email}", status_code=201)
def save_history_item(user_email: str, request: CVHistoryCreate):
    return require_success(save_generated_cv(user_email=user_email, **request.model_dump()))


@router.put("/history/{user_email}/{cv_id}")
def change_history_status(user_email: str, cv_id: str, request: CVStatusUpdate):
    return require_success(update_cv_status(user_email, cv_id, request.status), status_code=404)


@router.delete("/history/{user_email}/{cv_id}")
def remove_history_item(user_email: str, cv_id: str):
    return require_success(delete_cv(user_email, cv_id))


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
