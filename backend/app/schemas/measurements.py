from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.measurement import MeasurementType
from app.schemas.common import EquipmentSummary, TimestampedModel, UserSummary


DEFAULT_UNITS: dict[MeasurementType, str] = {
    MeasurementType.VIBRACAO: "mm/s",
    MeasurementType.TEMPERATURA: "C",
    MeasurementType.TENSAO: "V",
    MeasurementType.CORRENTE: "A",
}


class MeasurementBase(BaseModel):
    equipment_id: int
    measurement_type: MeasurementType
    value: float = Field(gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    measured_at: datetime | None = None

    @field_validator("unit")
    @classmethod
    def normalize_unit(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("measured_at")
    @classmethod
    def normalize_measured_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class MeasurementCreate(MeasurementBase):
    pass


class MeasurementResponse(TimestampedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_id: int
    measurement_type: MeasurementType
    value: float
    unit: str
    measured_at: datetime
    equipment: EquipmentSummary
    author: UserSummary
