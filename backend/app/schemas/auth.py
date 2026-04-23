from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole
from app.schemas.common import TeamSummary


class LoginRequest(BaseModel):
    login: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=4, max_length=128)


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: str
    role: UserRole
    active: bool
    team_id: int | None
    team: TeamSummary | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
