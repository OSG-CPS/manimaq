from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserProfile

router = APIRouter(tags=["protected"])


@router.get("/dashboard-summary")
def dashboard_summary(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "message": f"Bem-vindo, {current_user.name}",
        "role": current_user.role,
        "team": current_user.team.name if current_user.team else None,
    }


@router.get("/session", response_model=UserProfile)
def session_profile(current_user: User = Depends(get_current_user)) -> UserProfile:
    return UserProfile.model_validate(current_user)
