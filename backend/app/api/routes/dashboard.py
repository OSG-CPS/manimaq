from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.alert import Alert, AlertStatus
from app.models.equipment import Equipment
from app.models.occurrence import Occurrence
from app.models.team import Team
from app.models.user import User, UserRole
from app.models.work_order import WorkOrder, WorkOrderStatus, WorkOrderType
from app.models.work_order_status_history import WorkOrderStatusHistory
from app.schemas.common import ensure_utc_datetime
from app.schemas.dashboard import (
    DashboardKpis,
    DashboardOverviewResponse,
    DashboardReportResponse,
    EquipmentRankingItem,
    MaintenanceTypeReportItem,
    TeamReportItem,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _scope_metadata(current_user: User) -> tuple[str, int | None, str | None]:
    if current_user.role in {UserRole.ADMIN, UserRole.GERENTE}:
        return ("global", None, None)
    return ("team", current_user.team_id, current_user.team.name if current_user.team else None)


def _period_start(period_days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=period_days)


def _scoped_work_orders_query(db: Session, current_user: User):
    query = db.query(WorkOrder).options(
        joinedload(WorkOrder.team),
        joinedload(WorkOrder.equipment),
        joinedload(WorkOrder.status_history),
    )
    if current_user.role == UserRole.OPERADOR:
        if current_user.team_id is None:
            return query.filter(WorkOrder.id == -1)
        query = query.filter(WorkOrder.team_id == current_user.team_id)
    return query


def _scoped_occurrences_query(db: Session, current_user: User):
    query = db.query(Occurrence).options(joinedload(Occurrence.equipment))
    if current_user.role == UserRole.OPERADOR:
        if current_user.team_id is None:
            return query.filter(Occurrence.id == -1)
        query = query.join(Occurrence.equipment).filter(Equipment.team_id == current_user.team_id)
    return query


def _scoped_alerts_query(db: Session, current_user: User):
    query = db.query(Alert).options(joinedload(Alert.equipment))
    if current_user.role == UserRole.OPERADOR:
        if current_user.team_id is None:
            return query.filter(Alert.id == -1)
        query = query.join(Alert.equipment).filter(Equipment.team_id == current_user.team_id)
    return query


def _scoped_teams_query(db: Session, current_user: User):
    query = db.query(Team)
    if current_user.role == UserRole.OPERADOR:
        if current_user.team_id is None:
            return query.filter(Team.id == -1)
        query = query.filter(Team.id == current_user.team_id)
    return query


def _resolved_at(work_order: WorkOrder) -> datetime | None:
    concluded_entries = [
        ensure_utc_datetime(entry.transition_at)
        for entry in work_order.status_history
        if entry.new_status == WorkOrderStatus.CONCLUIDA
    ]
    if not concluded_entries:
        return None
    return min(concluded_entries)


def _build_kpis(
    work_orders: list[WorkOrder],
    occurrences: list[Occurrence],
    alerts: list[Alert],
) -> DashboardKpis:
    open_statuses = {WorkOrderStatus.ABERTA, WorkOrderStatus.EM_EXECUCAO}
    open_work_orders = sum(1 for item in work_orders if item.status in open_statuses)
    completed_work_orders = sum(1 for item in work_orders if item.status == WorkOrderStatus.CONCLUIDA)
    corrective_total = sum(1 for item in work_orders if item.type == WorkOrderType.CORRETIVA)
    preventive_total = sum(1 for item in work_orders if item.type == WorkOrderType.PREVENTIVA)
    total_with_type = corrective_total + preventive_total

    resolution_hours: list[float] = []
    for work_order in work_orders:
        resolved_at = _resolved_at(work_order)
        if resolved_at is None:
            continue
        created_at = ensure_utc_datetime(work_order.created_at)
        resolution_hours.append((resolved_at - created_at).total_seconds() / 3600)

    mean_resolution_hours = None
    if resolution_hours:
        mean_resolution_hours = round(sum(resolution_hours) / len(resolution_hours), 2)

    return DashboardKpis(
        open_work_orders=open_work_orders,
        completed_work_orders=completed_work_orders,
        work_order_backlog=open_work_orders,
        corrective_work_orders=corrective_total,
        preventive_work_orders=preventive_total,
        corrective_percentage=round((corrective_total / total_with_type) * 100, 2) if total_with_type else 0,
        preventive_percentage=round((preventive_total / total_with_type) * 100, 2) if total_with_type else 0,
        mean_resolution_hours=mean_resolution_hours,
        total_occurrences=len(occurrences),
        open_alerts=sum(1 for item in alerts if item.status == AlertStatus.ABERTO),
        reviewed_alerts=sum(1 for item in alerts if item.status == AlertStatus.REVISADO),
    )


def _build_equipment_ranking(
    occurrences: list[Occurrence],
    work_orders: list[WorkOrder],
    alerts: list[Alert],
) -> list[EquipmentRankingItem]:
    occurrence_counter = Counter(item.equipment_id for item in occurrences)
    open_work_order_counter = Counter(
        item.equipment_id for item in work_orders if item.status in {WorkOrderStatus.ABERTA, WorkOrderStatus.EM_EXECUCAO}
    )
    alert_counter = Counter(item.equipment_id for item in alerts)

    equipment_lookup: dict[int, Equipment] = {}
    for source in occurrences:
        equipment_lookup[source.equipment_id] = source.equipment
    for source in alerts:
        equipment_lookup[source.equipment_id] = source.equipment
    for source in work_orders:
        equipment_lookup[source.equipment_id] = source.equipment

    items: list[EquipmentRankingItem] = []
    for equipment_id, count in occurrence_counter.items():
        equipment = equipment_lookup.get(equipment_id)
        if equipment is None:
            continue
        items.append(
            EquipmentRankingItem(
                equipment_id=equipment.id,
                equipment_tag=equipment.tag,
                equipment_name=equipment.name,
                occurrences=count,
                open_work_orders=open_work_order_counter.get(equipment_id, 0),
                alerts=alert_counter.get(equipment_id, 0),
            )
        )

    items.sort(key=lambda item: (-item.occurrences, -item.open_work_orders, item.equipment_tag))
    return items[:5]


def _build_team_report(work_orders: list[WorkOrder], teams: list[Team]) -> list[TeamReportItem]:
    counters: dict[int, dict[str, int]] = defaultdict(lambda: {"total": 0, "open": 0, "completed": 0})
    for work_order in work_orders:
        counters[work_order.team_id]["total"] += 1
        if work_order.status in {WorkOrderStatus.ABERTA, WorkOrderStatus.EM_EXECUCAO}:
            counters[work_order.team_id]["open"] += 1
        if work_order.status == WorkOrderStatus.CONCLUIDA:
            counters[work_order.team_id]["completed"] += 1

    team_lookup = {team.id: team for team in teams}
    items: list[TeamReportItem] = []
    for team_id, values in counters.items():
        team = team_lookup.get(team_id)
        if team is None:
            continue
        items.append(
            TeamReportItem(
                team_id=team.id,
                team_name=team.name,
                sector=team.sector,
                work_orders=values["total"],
                open_work_orders=values["open"],
                completed_work_orders=values["completed"],
            )
        )

    items.sort(key=lambda item: (-item.work_orders, -item.open_work_orders, item.team_name))
    return items


def _build_type_report(work_orders: list[WorkOrder]) -> list[MaintenanceTypeReportItem]:
    counter = Counter(item.type.value for item in work_orders)
    total = sum(counter.values())
    items = [
        MaintenanceTypeReportItem(
            type=work_order_type,
            total=count,
            percentage=round((count / total) * 100, 2) if total else 0,
        )
        for work_order_type, count in sorted(counter.items())
    ]
    items.sort(key=lambda item: (-item.total, item.type))
    return items


def _load_dashboard_data(
    db: Session,
    current_user: User,
    period_days: int,
    equipment_id: int | None = None,
    team_id: int | None = None,
    maintenance_type: WorkOrderType | None = None,
) -> tuple[list[WorkOrder], list[Occurrence], list[Alert], list[Team]]:
    start = _period_start(period_days)

    work_orders_query = _scoped_work_orders_query(db, current_user).filter(WorkOrder.created_at >= start)
    if equipment_id is not None:
        work_orders_query = work_orders_query.filter(WorkOrder.equipment_id == equipment_id)
    if team_id is not None:
        work_orders_query = work_orders_query.filter(WorkOrder.team_id == team_id)
    if maintenance_type is not None:
        work_orders_query = work_orders_query.filter(WorkOrder.type == maintenance_type)

    occurrences_query = _scoped_occurrences_query(db, current_user).filter(Occurrence.occurred_at >= start)
    if equipment_id is not None:
        occurrences_query = occurrences_query.filter(Occurrence.equipment_id == equipment_id)

    alerts_query = _scoped_alerts_query(db, current_user).filter(Alert.event_at >= start)
    if equipment_id is not None:
        alerts_query = alerts_query.filter(Alert.equipment_id == equipment_id)

    if current_user.role in {UserRole.ADMIN, UserRole.GERENTE} and team_id is not None:
        occurrences_query = occurrences_query.join(Occurrence.equipment).filter(Equipment.team_id == team_id)
        alerts_query = alerts_query.join(Alert.equipment).filter(Equipment.team_id == team_id)

    teams_query = _scoped_teams_query(db, current_user)
    if team_id is not None:
        teams_query = teams_query.filter(Team.id == team_id)

    return (
        work_orders_query.all(),
        occurrences_query.all(),
        alerts_query.all(),
        teams_query.all(),
    )


def _validate_manager_filters(current_user: User, team_id: int | None) -> None:
    if current_user.role != UserRole.OPERADOR:
        return
    if team_id is not None and team_id != current_user.team_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operador nao pode consultar outra equipe")


@router.get("/overview", response_model=DashboardOverviewResponse)
def dashboard_overview(
    period_days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardOverviewResponse:
    work_orders, occurrences, alerts, teams = _load_dashboard_data(db, current_user, period_days)
    scope, scoped_team_id, scoped_team_name = _scope_metadata(current_user)

    return DashboardOverviewResponse(
        scope=scope,
        team_id=scoped_team_id,
        team_name=scoped_team_name,
        period_days=period_days,
        generated_at=datetime.now(timezone.utc),
        kpis=_build_kpis(work_orders, occurrences, alerts),
        top_failure_equipments=_build_equipment_ranking(occurrences, work_orders, alerts),
        work_orders_by_team=_build_team_report(work_orders, teams),
        work_orders_by_type=_build_type_report(work_orders),
    )


@router.get("/reports", response_model=DashboardReportResponse)
def dashboard_reports(
    period_days: int = Query(default=30, ge=1, le=365),
    equipment_id: int | None = None,
    team_id: int | None = None,
    maintenance_type: WorkOrderType | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardReportResponse:
    _validate_manager_filters(current_user, team_id)
    work_orders, occurrences, alerts, teams = _load_dashboard_data(
        db,
        current_user,
        period_days,
        equipment_id=equipment_id,
        team_id=team_id,
        maintenance_type=maintenance_type,
    )
    scope, scoped_team_id, scoped_team_name = _scope_metadata(current_user)

    return DashboardReportResponse(
        scope=scope,
        team_id=scoped_team_id,
        team_name=scoped_team_name,
        period_days=period_days,
        generated_at=datetime.now(timezone.utc),
        filters={
            "equipment_id": equipment_id,
            "team_id": team_id,
            "maintenance_type": maintenance_type.value if maintenance_type else None,
        },
        kpis=_build_kpis(work_orders, occurrences, alerts),
        occurrences_by_equipment=_build_equipment_ranking(occurrences, work_orders, alerts),
        work_orders_by_team=_build_team_report(work_orders, teams),
        work_orders_by_type=_build_type_report(work_orders),
    )
