from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.equipment import Equipment
from app.models.measurement import Measurement
from app.models.occurrence import Occurrence
from app.models.user import User
from app.schemas.common import EquipmentSummary, UserSummary, ensure_utc_datetime
from app.schemas.history import EquipmentHistoryResponse
from app.schemas.measurements import MeasurementResponse
from app.schemas.occurrences import OccurrenceResponse

router = APIRouter(prefix="/equipment-history", tags=["equipment-history"])


@router.get("/catalog", response_model=list[EquipmentSummary])
def list_equipment_catalog(
    active: bool | None = Query(default=True),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[EquipmentSummary]:
    query = db.query(Equipment)
    if active is not None:
        query = query.filter(Equipment.active == active)
    return [EquipmentSummary.model_validate(item) for item in query.order_by(Equipment.tag.asc()).all()]


@router.get("/{equipment_id}", response_model=EquipmentHistoryResponse)
def get_equipment_history(
    equipment_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EquipmentHistoryResponse:
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")

    occurrences = (
        db.query(Occurrence)
        .options(joinedload(Occurrence.equipment), joinedload(Occurrence.author))
        .filter(Occurrence.equipment_id == equipment_id)
        .order_by(Occurrence.occurred_at.desc(), Occurrence.created_at.desc())
        .all()
    )
    measurements = (
        db.query(Measurement)
        .options(joinedload(Measurement.equipment), joinedload(Measurement.author))
        .filter(Measurement.equipment_id == equipment_id)
        .order_by(Measurement.measured_at.desc(), Measurement.created_at.desc())
        .all()
    )

    return EquipmentHistoryResponse(
        equipment=EquipmentSummary.model_validate(equipment),
        occurrences=[
            OccurrenceResponse(
                id=item.id,
                equipment_id=item.equipment_id,
                severity=item.severity,
                safety_risk=item.safety_risk,
                production_stop=item.production_stop,
                description=item.description,
                occurred_at=ensure_utc_datetime(item.occurred_at),
                created_at=ensure_utc_datetime(item.created_at),
                updated_at=ensure_utc_datetime(item.updated_at),
                equipment=EquipmentSummary.model_validate(item.equipment),
                author=UserSummary.model_validate(item.author),
            )
            for item in occurrences
        ],
        measurements=[
            MeasurementResponse(
                id=item.id,
                equipment_id=item.equipment_id,
                measurement_type=item.measurement_type,
                value=item.value,
                unit=item.unit,
                measured_at=ensure_utc_datetime(item.measured_at),
                created_at=ensure_utc_datetime(item.created_at),
                updated_at=ensure_utc_datetime(item.updated_at),
                equipment=EquipmentSummary.model_validate(item.equipment),
                author=UserSummary.model_validate(item.author),
            )
            for item in measurements
        ],
    )
