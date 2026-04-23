from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_or_manager
from app.models.team import Team
from app.models.user import User
from app.schemas.teams import TeamCreate, TeamResponse, TeamUpdate

router = APIRouter(prefix="/teams", tags=["teams"])


def _normalize_name(value: str) -> str:
    return " ".join(value.strip().split())


def _serialize(team: Team) -> TeamResponse:
    return TeamResponse(
        id=team.id,
        name=team.name,
        sector=team.sector,
        description=team.description,
        active=team.active,
        created_at=team.created_at,
        updated_at=team.updated_at,
        users_count=len(team.users),
        equipments_count=len(team.equipments),
    )


@router.get("", response_model=list[TeamResponse])
def list_teams(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    active: bool | None = None,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> list[TeamResponse]:
    query = db.query(Team)

    if q:
        search = f"%{q.strip().lower()}%"
        query = query.filter(
            func.lower(Team.name).like(search) | func.lower(Team.sector).like(search)
        )

    if active is not None:
        query = query.filter(Team.active == active)

    teams = query.order_by(Team.name.asc()).all()
    return [_serialize(team) for team in teams]


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> TeamResponse:
    normalized_name = _normalize_name(payload.name)
    existing_team = db.query(Team).filter(func.lower(Team.name) == normalized_name.lower()).first()
    if existing_team:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome de equipe ja cadastrado")

    team = Team(
        name=normalized_name,
        sector=_normalize_name(payload.sector),
        description=payload.description.strip() if payload.description else None,
        active=True,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return _serialize(team)


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    payload: TeamUpdate,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> TeamResponse:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe nao encontrada")

    normalized_name = _normalize_name(payload.name)
    existing_team = (
        db.query(Team)
        .filter(func.lower(Team.name) == normalized_name.lower(), Team.id != team_id)
        .first()
    )
    if existing_team:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome de equipe ja cadastrado")

    team.name = normalized_name
    team.sector = _normalize_name(payload.sector)
    team.description = payload.description.strip() if payload.description else None
    team.active = payload.active

    db.commit()
    db.refresh(team)
    return _serialize(team)


@router.patch("/{team_id}/inactive", response_model=TeamResponse)
def deactivate_team(
    team_id: int,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> TeamResponse:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe nao encontrada")

    team.active = False
    db.commit()
    db.refresh(team)
    return _serialize(team)
