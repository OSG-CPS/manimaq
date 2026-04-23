from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TeamSummary, TimestampedModel


class EquipmentBase(BaseModel):
    tag: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=120)
    sector: str = Field(min_length=2, max_length=100)
    criticality: str = Field(default="media", min_length=2, max_length=50)
    status: str = Field(default="ativo", min_length=2, max_length=50)
    team_id: int | None = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(EquipmentBase):
    active: bool = True


class EquipmentResponse(EquipmentBase, TimestampedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    team: TeamSummary | None = None
