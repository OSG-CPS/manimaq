from pydantic import BaseModel

from app.schemas.common import EquipmentSummary
from app.schemas.measurements import MeasurementResponse
from app.schemas.occurrences import OccurrenceResponse


class EquipmentHistoryResponse(BaseModel):
    equipment: EquipmentSummary
    occurrences: list[OccurrenceResponse]
    measurements: list[MeasurementResponse]
