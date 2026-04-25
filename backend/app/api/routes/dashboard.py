from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Literal

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
    DashboardTrendResponse,
    EquipmentRankingItem,
    MaintenanceTypeReportItem,
    TeamReportItem,
)
from app.services.analytics import build_dashboard_analytical_reading, build_dashboard_trend_reading

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
    period_days: int | None,
    equipment_id: int | None = None,
    team_id: int | None = None,
    maintenance_type: WorkOrderType | None = None,
) -> tuple[list[WorkOrder], list[Occurrence], list[Alert], list[Team]]:
    work_orders_query = _scoped_work_orders_query(db, current_user)
    if equipment_id is not None:
        work_orders_query = work_orders_query.filter(WorkOrder.equipment_id == equipment_id)
    if team_id is not None:
        work_orders_query = work_orders_query.filter(WorkOrder.team_id == team_id)
    if maintenance_type is not None:
        work_orders_query = work_orders_query.filter(WorkOrder.type == maintenance_type)

    occurrences_query = _scoped_occurrences_query(db, current_user)
    if equipment_id is not None:
        occurrences_query = occurrences_query.filter(Occurrence.equipment_id == equipment_id)

    alerts_query = _scoped_alerts_query(db, current_user)
    if equipment_id is not None:
        alerts_query = alerts_query.filter(Alert.equipment_id == equipment_id)

    if current_user.role in {UserRole.ADMIN, UserRole.GERENTE} and team_id is not None:
        occurrences_query = occurrences_query.join(Occurrence.equipment).filter(Equipment.team_id == team_id)
        alerts_query = alerts_query.join(Alert.equipment).filter(Equipment.team_id == team_id)

    teams_query = _scoped_teams_query(db, current_user)
    if team_id is not None:
        teams_query = teams_query.filter(Team.id == team_id)

    if period_days is not None:
        start = _period_start(period_days)
        work_orders_query = work_orders_query.filter(WorkOrder.created_at >= start)
        occurrences_query = occurrences_query.filter(Occurrence.occurred_at >= start)
        alerts_query = alerts_query.filter(Alert.event_at >= start)

    return (
        work_orders_query.all(),
        occurrences_query.all(),
        alerts_query.all(),
        teams_query.all(),
    )


def _validate_manager_filters(current_user: User, team_id: int | None, sector: str | None = None) -> None:
    if current_user.role != UserRole.OPERADOR:
        return
    if team_id is not None and team_id != current_user.team_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operador nao pode consultar outra equipe")
    if sector is not None and current_user.team is not None and sector != current_user.team.sector:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operador nao pode consultar outro setor")


def _window_to_days(window: str) -> int | None:
    if window == "7":
        return 7
    if window == "30":
        return 30
    if window == "total":
        return None
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Janela de tendencia invalida")


def _is_within_range(value: datetime, start: datetime | None, end: datetime | None) -> bool:
    normalized = ensure_utc_datetime(value)
    if start is not None and normalized < start:
        return False
    if end is not None and normalized >= end:
        return False
    return True


def _signal_direction(current_value: int, previous_value: int) -> str:
    if current_value >= previous_value + 1 and (previous_value == 0 or current_value >= previous_value * 1.25):
        return "subindo"
    if previous_value >= current_value + 1 and current_value <= previous_value * 0.75:
        return "reduzindo"
    return "estavel"


def _trend_group_key(
    analysis_scope: Literal["equipment", "sector"],
    equipment: Equipment,
) -> tuple[str, str]:
    if analysis_scope == "equipment":
        return (f"equipment:{equipment.id}", f"{equipment.tag} - {equipment.name}")
    return (f"sector:{equipment.sector}", equipment.sector)


def _build_trend_hot_spots(
    *,
    analysis_scope: Literal["equipment", "sector"],
    current_occurrences: list[Occurrence],
    current_alerts: list[Alert],
    current_work_orders: list[WorkOrder],
    previous_occurrences: list[Occurrence],
    previous_alerts: list[Alert],
    previous_work_orders: list[WorkOrder],
) -> list[dict[str, int | str]]:
    counters: dict[str, dict[str, int | str]] = {}

    def ensure_item(key: str, label: str) -> dict[str, int | str]:
        if key not in counters:
            counters[key] = {
                "label": label,
                "scope": analysis_scope,
                "occurrences": 0,
                "alerts": 0,
                "open_alerts": 0,
                "open_work_orders": 0,
                "completed_work_orders": 0,
                "previous_signal": 0,
            }
        return counters[key]

    for item in current_occurrences:
        key, label = _trend_group_key(analysis_scope, item.equipment)
        ensure_item(key, label)["occurrences"] += 1

    for item in current_alerts:
        key, label = _trend_group_key(analysis_scope, item.equipment)
        bucket = ensure_item(key, label)
        bucket["alerts"] += 1
        if item.status == AlertStatus.ABERTO:
            bucket["open_alerts"] += 1

    for item in current_work_orders:
        key, label = _trend_group_key(analysis_scope, item.equipment)
        bucket = ensure_item(key, label)
        if item.status in {WorkOrderStatus.ABERTA, WorkOrderStatus.EM_EXECUCAO}:
            bucket["open_work_orders"] += 1
        if item.status == WorkOrderStatus.CONCLUIDA:
            bucket["completed_work_orders"] += 1

    for item in previous_occurrences:
        key, label = _trend_group_key(analysis_scope, item.equipment)
        ensure_item(key, label)["previous_signal"] += 1

    for item in previous_alerts:
        key, label = _trend_group_key(analysis_scope, item.equipment)
        ensure_item(key, label)["previous_signal"] += 1

    for item in previous_work_orders:
        key, label = _trend_group_key(analysis_scope, item.equipment)
        ensure_item(key, label)["previous_signal"] += 1

    hot_spots: list[dict[str, int | str]] = []
    for bucket in counters.values():
        current_signal = int(bucket["occurrences"]) + int(bucket["alerts"]) + int(bucket["open_work_orders"])
        previous_signal = int(bucket.pop("previous_signal"))
        bucket["trend_direction"] = _signal_direction(current_signal, previous_signal)
        hot_spots.append(bucket)

    hot_spots.sort(
        key=lambda item: (
            -int(item["occurrences"]),
            -int(item["alerts"]),
            -int(item["open_work_orders"]),
            str(item["label"]),
        )
    )
    return hot_spots[:5]


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
    filters = {
        "equipment_id": equipment_id,
        "team_id": team_id,
        "maintenance_type": maintenance_type.value if maintenance_type else None,
    }
    kpis = _build_kpis(work_orders, occurrences, alerts)
    occurrences_by_equipment = _build_equipment_ranking(occurrences, work_orders, alerts)
    work_orders_by_team = _build_team_report(work_orders, teams)
    work_orders_by_type = _build_type_report(work_orders)

    return DashboardReportResponse(
        scope=scope,
        team_id=scoped_team_id,
        team_name=scoped_team_name,
        period_days=period_days,
        generated_at=datetime.now(timezone.utc),
        filters=filters,
        kpis=kpis,
        occurrences_by_equipment=occurrences_by_equipment,
        work_orders_by_team=work_orders_by_team,
        work_orders_by_type=work_orders_by_type,
        analytical_reading=build_dashboard_analytical_reading(
            scope=scope,
            team_name=scoped_team_name,
            period_days=period_days,
            filters=filters,
            kpis=kpis,
            occurrences_by_equipment=occurrences_by_equipment,
            work_orders_by_team=work_orders_by_team,
            work_orders_by_type=work_orders_by_type,
        ),
    )


@router.get("/trends", response_model=DashboardTrendResponse)
def dashboard_trends(
    analysis_scope: Literal["equipment", "sector"] = Query(default="equipment"),
    window: Literal["7", "30", "total"] = Query(default="30"),
    equipment_id: int | None = None,
    sector: str | None = None,
    maintenance_type: WorkOrderType | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardTrendResponse:
    if analysis_scope == "equipment" and equipment_id is None:
        sector = None
    if analysis_scope == "sector":
        equipment_id = None

    _validate_manager_filters(current_user, None, sector)
    scope, scoped_team_id, scoped_team_name = _scope_metadata(current_user)
    window_days = _window_to_days(window)
    work_orders, occurrences, alerts, _ = _load_dashboard_data(
        db,
        current_user,
        None,
        equipment_id=equipment_id,
        maintenance_type=maintenance_type,
    )

    if sector is not None:
        work_orders = [item for item in work_orders if item.equipment.sector == sector]
        occurrences = [item for item in occurrences if item.equipment.sector == sector]
        alerts = [item for item in alerts if item.equipment.sector == sector]

    now = datetime.now(timezone.utc)
    if window_days is None:
        current_start = None
        current_end = None
        previous_start = now - timedelta(days=60)
        previous_end = now - timedelta(days=30)
    else:
        current_end = now
        current_start = now - timedelta(days=window_days)
        previous_end = current_start
        previous_start = current_start - timedelta(days=window_days)

    current_work_orders = [
        item for item in work_orders if _is_within_range(item.created_at, current_start, current_end)
    ]
    current_occurrences = [
        item for item in occurrences if _is_within_range(item.occurred_at, current_start, current_end)
    ]
    current_alerts = [
        item for item in alerts if _is_within_range(item.event_at, current_start, current_end)
    ]
    previous_work_orders = [
        item for item in work_orders if _is_within_range(item.created_at, previous_start, previous_end)
    ]
    previous_occurrences = [
        item for item in occurrences if _is_within_range(item.occurred_at, previous_start, previous_end)
    ]
    previous_alerts = [
        item for item in alerts if _is_within_range(item.event_at, previous_start, previous_end)
    ]

    kpis = _build_kpis(current_work_orders, current_occurrences, current_alerts)
    hot_spots = _build_trend_hot_spots(
        analysis_scope=analysis_scope,
        current_occurrences=current_occurrences,
        current_alerts=current_alerts,
        current_work_orders=current_work_orders,
        previous_occurrences=previous_occurrences,
        previous_alerts=previous_alerts,
        previous_work_orders=previous_work_orders,
    )

    totals: dict[str, int | float | None] = {
        "occurrences": len(current_occurrences),
        "alerts": len(current_alerts),
        "open_alerts": sum(1 for item in current_alerts if item.status == AlertStatus.ABERTO),
        "reviewed_alerts": sum(1 for item in current_alerts if item.status == AlertStatus.REVISADO),
        "open_work_orders": sum(
            1 for item in current_work_orders if item.status in {WorkOrderStatus.ABERTA, WorkOrderStatus.EM_EXECUCAO}
        ),
        "completed_work_orders": sum(1 for item in current_work_orders if item.status == WorkOrderStatus.CONCLUIDA),
        "corrective_percentage": kpis.corrective_percentage,
        "preventive_percentage": kpis.preventive_percentage,
        "mean_resolution_hours": kpis.mean_resolution_hours,
    }

    filters = {
        "analysis_scope": analysis_scope,
        "window": window,
        "equipment_id": equipment_id,
        "sector": sector,
        "maintenance_type": maintenance_type.value if maintenance_type else None,
    }

    return DashboardTrendResponse(
        scope=scope,
        team_id=scoped_team_id,
        team_name=scoped_team_name,
        generated_at=datetime.now(timezone.utc),
        filters=filters,
        trend_reading=build_dashboard_trend_reading(
            scope=scope,
            team_name=scoped_team_name,
            analysis_scope=analysis_scope,
            window=window,
            equipment_id=equipment_id,
            sector=sector,
            maintenance_type=maintenance_type.value if maintenance_type else None,
            totals=totals,
            hot_spots=hot_spots,
        ),
    )
