"""Recruiter communication delivery routes."""

from fastapi import APIRouter

from backend.routes._responses import require_success
from backend.schemas import EmailSendRequest
from services.email_service import send_recruiter_email

router = APIRouter(prefix="/communications", tags=["communications"])


@router.post("/email/send")
def send_email(request: EmailSendRequest):
    return require_success(send_recruiter_email(request.to_email, request.subject, request.body, request.recruiter_email), status_code=503)
