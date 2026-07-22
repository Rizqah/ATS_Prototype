"""Account security and password recovery routes."""

from fastapi import APIRouter

from routes._responses import require_success
from schemas import AccountDeleteRequest, PasswordChangeRequest, PasswordResetConfirm, PasswordResetRequest, TwoFactorConfirm, TwoFactorDisable
from services.security_service import change_password, confirm_password_reset, confirm_two_factor_setup, delete_account, disable_two_factor, export_personal_data, request_password_reset, start_two_factor_setup, two_factor_status

router = APIRouter(prefix="/security", tags=["security"])


@router.post("/password/change")
def password_change(request: PasswordChangeRequest):
    return require_success(change_password(request.email, request.current_password, request.new_password), status_code=400)


@router.post("/password/reset/request")
def password_reset_request(request: PasswordResetRequest):
    return require_success(request_password_reset(request.email), status_code=429)


@router.post("/password/reset/confirm")
def password_reset_confirm(request: PasswordResetConfirm):
    return require_success(confirm_password_reset(request.email, request.token, request.new_password), status_code=400)


@router.get("/2fa/status/{email}")
def get_two_factor_status(email: str):
    return require_success(two_factor_status(email), status_code=404)


@router.post("/2fa/setup/{email}")
def setup_two_factor(email: str):
    return require_success(start_two_factor_setup(email), status_code=404)


@router.post("/2fa/confirm")
def confirm_two_factor(request: TwoFactorConfirm):
    return require_success(confirm_two_factor_setup(request.email, request.code), status_code=400)


@router.post("/2fa/disable")
def turn_off_two_factor(request: TwoFactorDisable):
    return require_success(disable_two_factor(request.email, request.password, request.code), status_code=400)


@router.get("/privacy")
def privacy_summary():
    return {"data_collected": ["Account details", "Career profile", "Skills and experience", "Generated CVs and application status"], "purposes": ["Authentication", "CV generation", "Job matching", "Application tracking"], "retention": "Data remains until the account owner deletes it."}


@router.get("/data/{email}")
def download_personal_data(email: str):
    return require_success(export_personal_data(email), status_code=404)


@router.post("/account/delete")
def remove_account(request: AccountDeleteRequest):
    if request.confirmation != request.email:
        return require_success({"success": False, "error": "Confirmation email does not match"}, status_code=400)
    return require_success(delete_account(request.email, request.password), status_code=400)
