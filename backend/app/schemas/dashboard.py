from datetime import datetime

from pydantic import BaseModel


class DashboardKpis(BaseModel):
    open_work_orders: int
    completed_work_orders: int
    work_order_backlog: int
    corrective_work_orders: int
    preventive_work_orders: int
    corrective_percentage: float
    preventive_percentage: float
    mean_resolution_hours: float | None
    total_occurrences: int
    open_alerts: int
    reviewed_alerts: int


class EquipmentRankingItem(BaseModel):
    equipment_id: int
    equipment_tag: str
    equipment_name: str
    occurrences: int
    open_work_orders: int
    alerts: int


class TeamReportItem(BaseModel):
    team_id: int
    team_name: str
    sector: str
    work_orders: int
    open_work_orders: int
    completed_work_orders: int


class MaintenanceTypeReportItem(BaseModel):
    type: str
    total: int
    percentage: float


class DashboardOverviewResponse(BaseModel):
    scope: str
    team_id: int | None
    team_name: str | None
    period_days: int
    generated_at: datetime
    kpis: DashboardKpis
    top_failure_equipments: list[EquipmentRankingItem]
    work_orders_by_team: list[TeamReportItem]
    work_orders_by_type: list[MaintenanceTypeReportItem]


class DashboardReportResponse(BaseModel):
    scope: str
    team_id: int | None
    team_name: str | None
    period_days: int
    generated_at: datetime
    filters: dict[str, int | str | None]
    kpis: DashboardKpis
    occurrences_by_equipment: list[EquipmentRankingItem]
    work_orders_by_team: list[TeamReportItem]
    work_orders_by_type: list[MaintenanceTypeReportItem]
