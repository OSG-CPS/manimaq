from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.equipment import Equipment
from app.models.occurrence import Occurrence, OccurrenceSeverity
from app.models.user import User, UserRole
from app.schemas.common import EquipmentSummary, UserSummary, ensure_utc_datetime
from app.schemas.occurrences import OccurrenceCreate, OccurrenceResponse, OccurrenceUpdate

router = APIRouter(prefix="/occurrences", tags=["occurrences"])

EDIT_WINDOW_HOURS = 24


def _get_equipment_or_404(equipment_id: int, db: Session) -> Equipment:
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")
    return equipment


def _serialize(occurrence: Occurrence) -> OccurrenceResponse:
    return OccurrenceResponse(
        id=occurrence.id,
        equipment_id=occurrence.equipment_id,
        severity=occurrence.severity,
        safety_risk=occurrence.safety_risk,
        production_stop=occurrence.production_stop,
        description=occurrence.description,
        occurred_at=ensure_utc_datetime(occurrence.occurred_at),
        created_at=ensure_utc_datetime(occurrence.created_at),
        updated_at=ensure_utc_datetime(occurrence.updated_at),
        equipment=EquipmentSummary.model_validate(occurrence.equipment),
        author=UserSummary.model_validate(occurrence.author),
    )


def _can_edit(occurrence: Occurrence, current_user: User) -> bool:
    if current_user.role in {UserRole.ADMIN, UserRole.GERENTE}:
        return True
    if occurrence.author_id != current_user.id:
        return False
    return datetime.now(timezone.utc) - occurrence.created_at <= timedelta(hours=EDIT_WINDOW_HOURS)


@router.get("", response_model=list[OccurrenceResponse])
def list_occurrences(
    equipment_id: int | None = None,
    severity: OccurrenceSeverity | None = None,
    production_stop: bool | None = None,
    safety_risk: bool | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OccurrenceResponse]:
    query = db.query(Occurrence).options(
        joinedload(Occurrence.equipment),
        joinedload(Occurrence.author),
    )

    if equipment_id is not None:
        query = query.filter(Occurrence.equipment_id == equipment_id)
    if severity is not None:
        query = query.filter(Occurrence.severity == severity)
    if production_stop is not None:
        query = query.filter(Occurrence.production_stop == production_stop)
    if safety_risk is not None:
        query = query.filter(Occurrence.safety_risk == safety_risk)

    if current_user.role == UserRole.OPERADOR:
        query = query.filter(Occurrence.author_id == current_user.id)

    occurrences = query.order_by(Occurrence.occurred_at.desc(), Occurrence.created_at.desc()).all()
    return [_serialize(occurrence) for occurrence in occurrences]


@router.get("/{occurrence_id}", response_model=OccurrenceResponse)
def get_occurrence(
    occurrence_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OccurrenceResponse:
    occurrence = (
        db.query(Occurrence)
        .options(joinedload(Occurrence.equipment), joinedload(Occurrence.author))
        .filter(Occurrence.id == occurrence_id)
        .first()
    )
    if occurrence is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ocorrencia nao encontrada")
    if current_user.role == UserRole.OPERADOR and occurrence.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissao para acessar este recurso")
    return _serialize(occurrence)


@router.post("", response_model=OccurrenceResponse, status_code=status.HTTP_201_CREATED)
def create_occurrence(
    payload: OccurrenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OccurrenceResponse:
    _get_equipment_or_404(payload.equipment_id, db)

    occurrence = Occurrence(
        equipment_id=payload.equipment_id,
        author_id=current_user.id,
        severity=payload.severity,
        safety_risk=payload.safety_risk,
        production_stop=payload.production_stop,
        description=payload.description,
        occurred_at=payload.occurred_at or datetime.now(timezone.utc),
    )
    db.add(occurrence)
    db.commit()
    db.refresh(occurrence)
    return get_occurrence(occurrence.id, current_user, db)


@router.put("/{occurrence_id}", response_model=OccurrenceResponse)
def update_occurrence(
    occurrence_id: int,
    payload: OccurrenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OccurrenceResponse:
    occurrence = db.get(Occurrence, occurrence_id)
    if occurrence is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ocorrencia nao encontrada")
    if not _can_edit(occurrence, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Edicao permitida apenas para o autor nas primeiras 24h ou para admin/gerente",
        )

    _get_equipment_or_404(payload.equipment_id, db)

    occurrence.equipment_id = payload.equipment_id
    occurrence.severity = payload.severity
    occurrence.safety_risk = payload.safety_risk
    occurrence.production_stop = payload.production_stop
    occurrence.description = payload.description
    occurrence.occurred_at = payload.occurred_at or occurrence.occurred_at

    db.commit()
    db.refresh(occurrence)
    return get_occurrence(occurrence.id, current_user, db)
