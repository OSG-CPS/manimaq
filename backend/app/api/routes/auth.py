from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import (
    BootstrapAdminRequest,
    BootstrapStatusResponse,
    LoginRequest,
    TokenResponse,
    UserProfile,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _users_count(db: Session) -> int:
    return db.scalar(select(func.count(User.id))) or 0


@router.get("/bootstrap-status", response_model=BootstrapStatusResponse)
def bootstrap_status(db: Session = Depends(get_db)) -> BootstrapStatusResponse:
    users_count = _users_count(db)
    return BootstrapStatusResponse(bootstrap_required=users_count == 0, users_count=users_count)


@router.post("/bootstrap-admin", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(payload: BootstrapAdminRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if _users_count(db) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bootstrap inicial indisponivel: ja existem usuarios cadastrados.",
        )

    user = User(
        name=payload.name.strip(),
        username=payload.username,
        email=payload.email,
        role=UserRole.ADMIN,
        active=True,
        team_id=None,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user=UserProfile.model_validate(user),
    )


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
