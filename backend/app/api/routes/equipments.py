from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db, require_admin_or_manager
from app.models.equipment import Equipment
from app.models.team import Team
from app.models.user import User
from app.schemas.common import TeamSummary
from app.schemas.equipments import EquipmentCreate, EquipmentResponse, EquipmentUpdate

router = APIRouter(prefix="/equipments", tags=["equipments"])


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_tag(value: str) -> str:
    return value.strip().upper()


def _get_active_team(team_id: int | None, db: Session) -> Team | None:
    if team_id is None:
        return None

    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe nao encontrada")
    if not team.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipe inativa nao pode receber novos vinculos",
        )
    return team


def _serialize(equipment: Equipment) -> EquipmentResponse:
    team = None
    if equipment.team:
        team = TeamSummary.model_validate(equipment.team)

    return EquipmentResponse(
        id=equipment.id,
        tag=equipment.tag,
        name=equipment.name,
        sector=equipment.sector,
        criticality=equipment.criticality,
        status=equipment.status,
        active=equipment.active,
        team_id=equipment.team_id,
        team=team,
        created_at=equipment.created_at,
        updated_at=equipment.updated_at,
    )


@router.get("", response_model=list[EquipmentResponse])
def list_equipments(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    active: bool | None = None,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> list[EquipmentResponse]:
    query = db.query(Equipment).options(selectinload(Equipment.team))

    if q:
        search = f"%{q.strip().lower()}%"
        query = query.filter(
            func.lower(Equipment.name).like(search)
            | func.lower(Equipment.tag).like(search)
            | func.lower(Equipment.sector).like(search)
        )

    if active is not None:
        query = query.filter(Equipment.active == active)

    equipments = query.order_by(Equipment.tag.asc()).all()
    return [_serialize(equipment) for equipment in equipments]


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(
    equipment_id: int,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> EquipmentResponse:
    equipment = (
        db.query(Equipment)
        .options(selectinload(Equipment.team))
        .filter(Equipment.id == equipment_id)
        .first()
    )
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")
    return _serialize(equipment)


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    payload: EquipmentCreate,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> EquipmentResponse:
    normalized_tag = _normalize_tag(payload.tag)
    existing_equipment = (
        db.query(Equipment).filter(func.lower(Equipment.tag) == normalized_tag.lower()).first()
    )
    if existing_equipment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="TAG ja cadastrada")

    _get_active_team(payload.team_id, db)

    equipment = Equipment(
        tag=normalized_tag,
        name=_normalize_text(payload.name),
        sector=_normalize_text(payload.sector),
        criticality=_normalize_text(payload.criticality),
        status=_normalize_text(payload.status),
        team_id=payload.team_id,
        active=True,
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return get_equipment(equipment.id, _, db)


@router.put("/{equipment_id}", response_model=EquipmentResponse)
def update_equipment(
    equipment_id: int,
    payload: EquipmentUpdate,
    _: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> EquipmentResponse:
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")

    normalized_tag = _normalize_tag(payload.tag)
    existing_equipment = (
        db.query(Equipment)
        .filter(func.lower(Equipment.tag) == normalized_tag.lower(), Equipment.id != equipment_id)
        .first()
    )
    if existing_equipment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="TAG ja cadastrada")

    _get_active_team(payload.team_id, db)

    equipment.tag = normalized_tag
    equipment.name = _normalize_text(payload.name)
    equipment.sector = _normalize_text(payload.sector)
    equipment.criticality = _normalize_text(payload.criticality)
    equipment.status = _normalize_text(payload.status)
    equipment.team_id = payload.team_id
    equipment.active = payload.active

    db.commit()
    db.refresh(equipment)
    return get_equipment(equipment.id, _, db)
