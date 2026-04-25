from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.alert import AlertOriginType, AlertSeverity, AlertSource, AlertStatus
from app.models.work_order import WorkOrderPriority, WorkOrderType
from app.schemas.common import EquipmentSummary, TimestampedModel


class SuggestedWorkOrderData(BaseModel):
    suggested: bool
    type: WorkOrderType | None = None
    priority: WorkOrderPriority | None = None


class AlertResponse(TimestampedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_id: int
    origin_type: AlertOriginType
    origin_id: int | None
    source: AlertSource
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    recommendation: str | None
    possible_cause: str | None
    suggested_work_order: SuggestedWorkOrderData
    event_at: datetime
    equipment: EquipmentSummary

