from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.occurrence import OccurrenceSeverity
from app.schemas.common import EquipmentSummary, TimestampedModel, UserSummary


class OccurrenceBase(BaseModel):
    equipment_id: int
    severity: OccurrenceSeverity
    safety_risk: bool = False
    production_stop: bool = False
    description: str = Field(min_length=5, max_length=2000)
    occurred_at: datetime | None = None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if len(normalized) < 5:
            raise ValueError("Descricao deve ter pelo menos 5 caracteres")
        return normalized

    @field_validator("occurred_at")
    @classmethod
    def normalize_occurred_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class OccurrenceCreate(OccurrenceBase):
    pass


class OccurrenceUpdate(OccurrenceBase):
    pass


class OccurrenceResponse(OccurrenceBase, TimestampedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment: EquipmentSummary
    author: UserSummary
