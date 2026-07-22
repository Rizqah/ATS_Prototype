"""Authentication routes using the current prototype auth service."""

from fastapi import APIRouter

from backend.routes._responses import require_success
from backend.schemas import Credentials, UserUpdate
from services.auth_service import (
    authenticate_user,
    fetch_user,
    register_user,
    update_user_record,
)
from services.recruiter_service import save_workspace

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=201)
def signup(credentials: Credentials):
    result = register_user(
        credentials.email,
        credentials.password,
        credentials.role or "candidate",
        credentials.full_name or "",
        credentials.job_title or "",
    )
    if result.get("success") and credentials.role == "recruiter":
        save_workspace(credentials.email, {
            "recruiter_profile": {
                "full_name": credentials.full_name or "",
                "job_title": credentials.job_title or "",
            }
        })
    return require_success(result)


@router.post("/login")
def login(credentials: Credentials):
    return require_success(authenticate_user(credentials.email, credentials.password, credentials.otp_code), status_code=401)


@router.get("/users/{email}")
def get_user(email: str):
    return require_success(fetch_user(email), status_code=404)


@router.put("/users/{email}")
def update_user(email: str, request: UserUpdate):
    return require_success(update_user_record(email, request.data), status_code=404)
