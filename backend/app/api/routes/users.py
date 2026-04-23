from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db, require_admin_or_manager
from app.core.security import hash_password
from app.models.team import Team
from app.models.user import User, UserRole
from app.schemas.common import TeamSummary
from app.schemas.users import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_username(value: str) -> str:
    return value.strip().lower()


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _get_active_team(team_id: int | None, db: Session) -> Team | None:
    if team_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario deve estar vinculado a uma equipe ativa",
        )

    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe nao encontrada")
    if not team.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipe inativa nao pode receber novos vinculos",
        )
    return team


def _serialize(user: User) -> UserResponse:
    team = None
    if user.team:
        team = TeamSummary.model_validate(user.team)

    return UserResponse(
        id=user.id,
        name=user.name,
        username=user.username,
        email=user.email,
        role=user.role,
        active=user.active,
        team_id=user.team_id,
        team=team,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("", response_model=list[UserResponse])
def list_users(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    active: bool | None = None,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    query = db.query(User).options(selectinload(User.team))

    if q:
        search = f"%{q.strip().lower()}%"
        query = query.filter(
            func.lower(User.name).like(search)
            | func.lower(User.username).like(search)
            | func.lower(User.email).like(search)
        )

    if active is not None:
        query = query.filter(User.active == active)

    users = query.order_by(User.name.asc()).all()
    return [_serialize(user) for user in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> UserResponse:
    normalized_email = _normalize_email(payload.email)
    normalized_username = _normalize_username(payload.username)

    existing_email = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ja cadastrado")

    existing_username = db.query(User).filter(func.lower(User.username) == normalized_username).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username ja cadastrado")

    _get_active_team(payload.team_id, db)

    user = User(
        name=_normalize_text(payload.name),
        username=normalized_username,
        email=normalized_email,
        role=payload.role,
        active=True,
        team_id=payload.team_id,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return get_user_by_id(user.id, _, db)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

    normalized_email = _normalize_email(payload.email)
    normalized_username = _normalize_username(payload.username)

    existing_email = (
        db.query(User).filter(func.lower(User.email) == normalized_email, User.id != user_id).first()
    )
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ja cadastrado")

    existing_username = (
        db.query(User)
        .filter(func.lower(User.username) == normalized_username, User.id != user_id)
        .first()
    )
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username ja cadastrado")

    _get_active_team(payload.team_id, db)

    user.name = _normalize_text(payload.name)
    user.username = normalized_username
    user.email = normalized_email
    user.role = payload.role
    user.team_id = payload.team_id
    user.active = payload.active

    db.commit()
    db.refresh(user)
    return get_user_by_id(user.id, _, db)


@router.patch("/{user_id}/inactive", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

    user.active = False
    db.commit()
    db.refresh(user)
    return get_user_by_id(user.id, _, db)


def get_user_by_id(user_id: int, _: User, db: Session) -> UserResponse:
    user = db.query(User).options(selectinload(User.team)).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")
    return _serialize(user)
