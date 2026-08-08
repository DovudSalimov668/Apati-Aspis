from fastapi import APIRouter
from app.schemas.password import PasswordCheckRequest, PasswordCheckResponse
from app.services.password_service import check_password_pwned
from app.core.errors import ValidationException

password_router = APIRouter(prefix="/password", tags=["Password Security"])

@password_router.post("/check", response_model=PasswordCheckResponse)
async def check_password(payload: PasswordCheckRequest):
    if not payload.password or not payload.password.strip():
        raise ValidationException("Password input parameter cannot be empty.")

    # Execute K-Anonymity check locally in memory without logging or storing password
    result = await check_password_pwned(payload.password)
    return PasswordCheckResponse(**result.model_dump())
