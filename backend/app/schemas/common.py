from datetime import datetime, timezone

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
    team_id: int | None = None


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    role: str
    active: bool


class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime


def ensure_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
