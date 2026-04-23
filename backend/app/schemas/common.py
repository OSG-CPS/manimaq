from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TeamSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sector: str
    active: bool


class EquipmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tag: str
    name: str
    sector: str
    active: bool


class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime
