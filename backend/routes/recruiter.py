"""Recruiter workspace persistence routes."""

from fastapi import APIRouter

from routes._responses import require_success
from schemas import RecruiterWorkspaceUpdate
from services.recruiter_service import delete_workspace, get_workspace, save_workspace

router = APIRouter(prefix="/recruiter", tags=["recruiter"])


@router.get("/workspace/{email}")
def workspace(email: str):
    return require_success(get_workspace(email))


@router.put("/workspace/{email}")
def update_workspace(email: str, request: RecruiterWorkspaceUpdate):
    return require_success(save_workspace(email, request.workspace))


@router.delete("/workspace/{email}")
def remove_workspace(email: str):
    return require_success(delete_workspace(email))
