from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole
from app.schemas.common import TeamSummary, TimestampedModel


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=120)
    role: UserRole
    team_id: int | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("Email invalido")

        local_part, domain = normalized.split("@", 1)
        if not local_part or not domain or "." not in domain:
            raise ValueError("Email invalido")

        return normalized


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(UserBase):
    active: bool = True


class UserResponse(UserBase, TimestampedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    team: TeamSummary | None = None
