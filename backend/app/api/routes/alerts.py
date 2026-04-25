from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db, require_admin_or_manager
from app.models.alert import Alert, AlertSeverity, AlertSource, AlertStatus
from app.models.user import User, UserRole
from app.schemas.alerts import AlertResponse, SuggestedWorkOrderData
from app.schemas.common import EquipmentSummary, ensure_utc_datetime

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _serialize(alert: Alert) -> AlertResponse:
    return AlertResponse(
        id=alert.id,
        equipment_id=alert.equipment_id,
        origin_type=alert.origin_type,
        origin_id=alert.origin_id,
        source=alert.source,
        severity=alert.severity,
        status=alert.status,
        title=alert.title,
        message=alert.message,
        recommendation=alert.recommendation,
        possible_cause=alert.possible_cause,
        suggested_work_order=SuggestedWorkOrderData(
            suggested=alert.suggested_work_order,
            type=alert.suggested_work_order_type,
            priority=alert.suggested_work_order_priority,
        ),
        event_at=ensure_utc_datetime(alert.event_at),
        created_at=ensure_utc_datetime(alert.created_at),
        updated_at=ensure_utc_datetime(alert.updated_at),
        equipment=EquipmentSummary.model_validate(alert.equipment),
    )


def _base_query(db: Session):
    return db.query(Alert).options(joinedload(Alert.equipment))


def _apply_operator_scope(query, current_user: User):
    if current_user.role != UserRole.OPERADOR:
        return query
    if current_user.team_id is None:
        return query.filter(Alert.id == -1)
    return query.filter(Alert.equipment.has(team_id=current_user.team_id))


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    equipment_id: int | None = None,
    severity: AlertSeverity | None = None,
    source: AlertSource | None = None,
    status_filter: AlertStatus | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AlertResponse]:
    query = _apply_operator_scope(_base_query(db), current_user)

    if equipment_id is not None:
        query = query.filter(Alert.equipment_id == equipment_id)
    if severity is not None:
        query = query.filter(Alert.severity == severity)
    if source is not None:
        query = query.filter(Alert.source == source)
    if status_filter is not None:
        query = query.filter(Alert.status == status_filter)

    alerts = query.order_by(Alert.event_at.desc(), Alert.created_at.desc()).all()
    return [_serialize(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AlertResponse:
    query = _apply_operator_scope(_base_query(db), current_user)
    alert = query.filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta nao encontrado")
    return _serialize(alert)


@router.post("/{alert_id}/review", response_model=AlertResponse)
def mark_alert_as_reviewed(
    alert_id: int,
    _current_user: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db),
) -> AlertResponse:
    alert = _base_query(db).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta nao encontrado")
    alert.status = AlertStatus.REVISADO
    db.commit()
    db.refresh(alert)
    return _serialize(alert)
