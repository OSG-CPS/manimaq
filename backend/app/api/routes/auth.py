from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    normalized_login = payload.login.strip().lower()
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == normalized_login,
                User.email == normalized_login,
            )
        )
        .first()
    )

    if user is None or not user.active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
        )

    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user=UserProfile.model_validate(user),
    )


@router.get("/me", response_model=UserProfile)
def me(current_user: User = Depends(get_current_user)) -> UserProfile:
    return UserProfile.model_validate(current_user)
