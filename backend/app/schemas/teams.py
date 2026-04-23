from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TimestampedModel


class TeamBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    sector: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    active: bool = True


class TeamResponse(TeamBase, TimestampedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    users_count: int = 0
    equipments_count: int = 0
