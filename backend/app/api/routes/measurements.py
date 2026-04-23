from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.equipment import Equipment
from app.models.measurement import Measurement, MeasurementType
from app.models.user import User, UserRole
from app.schemas.common import EquipmentSummary, UserSummary, ensure_utc_datetime
from app.schemas.measurements import DEFAULT_UNITS, MeasurementCreate, MeasurementResponse

router = APIRouter(prefix="/measurements", tags=["measurements"])


def _get_equipment_or_404(equipment_id: int, db: Session) -> Equipment:
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")
    return equipment


def _serialize(measurement: Measurement) -> MeasurementResponse:
    return MeasurementResponse(
        id=measurement.id,
        equipment_id=measurement.equipment_id,
        measurement_type=measurement.measurement_type,
        value=measurement.value,
        unit=measurement.unit,
        measured_at=ensure_utc_datetime(measurement.measured_at),
        created_at=ensure_utc_datetime(measurement.created_at),
        updated_at=ensure_utc_datetime(measurement.updated_at),
        equipment=EquipmentSummary.model_validate(measurement.equipment),
        author=UserSummary.model_validate(measurement.author),
    )


@router.get("", response_model=list[MeasurementResponse])
def list_measurements(
    equipment_id: int | None = None,
    measurement_type: MeasurementType | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MeasurementResponse]:
    query = db.query(Measurement).options(
        joinedload(Measurement.equipment),
        joinedload(Measurement.author),
    )

    if equipment_id is not None:
        query = query.filter(Measurement.equipment_id == equipment_id)
    if measurement_type is not None:
        query = query.filter(Measurement.measurement_type == measurement_type)

    if current_user.role == UserRole.OPERADOR:
        query = query.filter(Measurement.author_id == current_user.id)

    measurements = query.order_by(Measurement.measured_at.desc(), Measurement.created_at.desc()).all()
    return [_serialize(measurement) for measurement in measurements]


@router.post("", response_model=MeasurementResponse, status_code=status.HTTP_201_CREATED)
def create_measurement(
    payload: MeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeasurementResponse:
    _get_equipment_or_404(payload.equipment_id, db)

    measurement = Measurement(
        equipment_id=payload.equipment_id,
        author_id=current_user.id,
        measurement_type=payload.measurement_type,
        value=payload.value,
        unit=payload.unit or DEFAULT_UNITS[payload.measurement_type],
        measured_at=payload.measured_at or datetime.now(timezone.utc),
    )
    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    measurement = (
        db.query(Measurement)
        .options(joinedload(Measurement.equipment), joinedload(Measurement.author))
        .filter(Measurement.id == measurement.id)
        .first()
    )
    assert measurement is not None
    return _serialize(measurement)
