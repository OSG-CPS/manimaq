from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.measurement import MeasurementType
from app.schemas.common import TeamSummary, TimestampedModel


class EquipmentBase(BaseModel):
    tag: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=120)
    sector: str = Field(min_length=2, max_length=100)
    criticality: str = Field(default="media", min_length=2, max_length=50)
    status: str = Field(default="ativo", min_length=2, max_length=50)
    team_id: int | None = None
    alert_measurement_type: MeasurementType | None = None
    measurement_unit: str | None = Field(default=None, min_length=1, max_length=20)
    alert_threshold_low: float | None = Field(default=None, gt=0)
    alert_threshold_medium: float | None = Field(default=None, gt=0)
    alert_threshold_high: float | None = Field(default=None, gt=0)
    alert_threshold_critical: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_alert_config(self):
        thresholds = [
            self.alert_threshold_low,
            self.alert_threshold_medium,
            self.alert_threshold_high,
            self.alert_threshold_critical,
        ]
        has_any_config = any(value is not None for value in thresholds) or bool(
            self.alert_measurement_type or self.measurement_unit
        )
        if not has_any_config:
            return self
        if self.alert_measurement_type is None:
            raise ValueError("Tipo principal de medicao e obrigatorio quando houver configuracao de alerta")
        if self.measurement_unit is None or not self.measurement_unit.strip():
            raise ValueError("Unidade de medida e obrigatoria quando houver configuracao de alerta")
        if any(value is None for value in thresholds):
            raise ValueError("Todos os limiares de alerta devem ser informados")
        assert self.alert_threshold_low is not None
        assert self.alert_threshold_medium is not None
        assert self.alert_threshold_high is not None
        assert self.alert_threshold_critical is not None
        if not (
            self.alert_threshold_low < self.alert_threshold_medium < self.alert_threshold_high < self.alert_threshold_critical
        ):
            raise ValueError("Os limiares devem respeitar a ordem baixo < medio < alto < critico")
        self.measurement_unit = self.measurement_unit.strip()
        return self


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(EquipmentBase):
    active: bool = True


class EquipmentResponse(EquipmentBase, TimestampedModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    team: TeamSummary | None = None
