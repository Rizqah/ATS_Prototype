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

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=201)
def signup(credentials: Credentials):
    return require_success(register_user(credentials.email, credentials.password))


@router.post("/login")
def login(credentials: Credentials):
    return require_success(authenticate_user(credentials.email, credentials.password), status_code=401)


@router.get("/users/{email}")
def get_user(email: str):
    return require_success(fetch_user(email), status_code=404)


@router.put("/users/{email}")
def update_user(email: str, request: UserUpdate):
    return require_success(update_user_record(email, request.data), status_code=404)
