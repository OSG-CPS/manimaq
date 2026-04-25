from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.work_order import WorkOrderOrigin, WorkOrderPriority, WorkOrderStatus, WorkOrderType
from app.schemas.common import EquipmentSummary, TeamSummary, TimestampedModel, UserSummary


class WorkOrderStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    previous_status: WorkOrderStatus | None = None
    new_status: WorkOrderStatus
    note: str | None = None
    transition_at: datetime
    created_at: datetime
    author: UserSummary


class WorkOrderBase(BaseModel):
    equipment_id: int
    team_id: int
    type: WorkOrderType
    priority: WorkOrderPriority = WorkOrderPriority.MEDIA
    description: str = Field(min_length=5, max_length=500)
    origin: WorkOrderOrigin = WorkOrderOrigin.MANUAL
    planned_start_at: datetime | None = None
    estimated_duration_hours: int | None = Field(default=None, ge=1, le=720)


class WorkOrderCreate(WorkOrderBase):
    status: WorkOrderStatus = WorkOrderStatus.ABERTA
    initial_note: str | None = Field(default=None, max_length=500)


class WorkOrderEdit(BaseModel):
    equipment_id: int
    team_id: int
    type: WorkOrderType
    priority: WorkOrderPriority = WorkOrderPriority.MEDIA
    description: str = Field(min_length=5, max_length=500)
    planned_start_at: datetime | None = None
    estimated_duration_hours: int | None = Field(default=None, ge=1, le=720)


class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatus
    note: str | None = Field(default=None, max_length=500)
    transition_at: datetime | None = None


class WorkOrderResponse(WorkOrderBase, TimestampedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: WorkOrderStatus
    equipment: EquipmentSummary
    team: TeamSummary
    created_by: UserSummary
    status_history: list[WorkOrderStatusHistoryResponse] = []
