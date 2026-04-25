import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib import error, request

from sqlalchemy.orm import Session, joinedload

from app.models.alert import Alert, AlertOriginType, AlertSeverity, AlertSource
from app.models.equipment import Equipment
from app.models.measurement import Measurement, MeasurementType
from app.models.occurrence import Occurrence, OccurrenceSeverity
from app.models.work_order import WorkOrder, WorkOrderPriority, WorkOrderStatus, WorkOrderType
from app.core.config import settings


@dataclass
class RuleAlertDraft:
    title: str
    message: str
    severity: AlertSeverity
    recommendation: str
    suggested_work_order: bool
    suggested_work_order_type: WorkOrderType | None
    suggested_work_order_priority: WorkOrderPriority | None
    event_at: datetime


def maybe_create_alert_for_occurrence(db: Session, occurrence: Occurrence) -> Alert | None:
    existing = _find_existing_alert(db, AlertOriginType.OCCURRENCE, occurrence.id)
    if existing is not None:
        return existing

    draft = _build_occurrence_rule_alert(occurrence)
    if draft is None:
        return None

    return _create_alert(
        db=db,
        equipment_id=occurrence.equipment_id,
        origin_type=AlertOriginType.OCCURRENCE,
        origin_id=occurrence.id,
        draft=draft,
        ai_context=_build_occurrence_ai_context(db, occurrence),
    )


def maybe_create_alert_for_measurement(db: Session, measurement: Measurement) -> Alert | None:
    existing = _find_existing_alert(db, AlertOriginType.MEASUREMENT, measurement.id)
    if existing is not None:
        return existing

    draft = _build_measurement_rule_alert(db, measurement)
    if draft is None:
        return None

    return _create_alert(
        db=db,
        equipment_id=measurement.equipment_id,
        origin_type=AlertOriginType.MEASUREMENT,
        origin_id=measurement.id,
        draft=draft,
        ai_context=_build_measurement_ai_context(db, measurement),
    )


def _find_existing_alert(db: Session, origin_type: AlertOriginType, origin_id: int | None) -> Alert | None:
    query = (
        db.query(Alert)
        .options(joinedload(Alert.equipment))
        .filter(Alert.origin_type == origin_type, Alert.origin_id == origin_id)
    )
    return query.first()


def _build_occurrence_rule_alert(occurrence: Occurrence) -> RuleAlertDraft | None:
    reasons: list[str] = []
    severity = AlertSeverity.MEDIA
    suggested_priority: WorkOrderPriority | None = None

    if occurrence.severity in {OccurrenceSeverity.ALTA, OccurrenceSeverity.CRITICA}:
        reasons.append(f"Ocorrencia registrada com severidade {occurrence.severity.value}")
        severity = _max_severity(severity, _map_occurrence_severity(occurrence.severity))
        suggested_priority = _max_priority(suggested_priority, _map_occurrence_priority(occurrence.severity))

    if occurrence.safety_risk:
        reasons.append("Risco a seguranca informado no registro operacional")
        severity = AlertSeverity.CRITICA
        suggested_priority = WorkOrderPriority.CRITICA

    if occurrence.production_stop:
        reasons.append("Parada de producao reportada para o equipamento")
        severity = _max_severity(severity, AlertSeverity.CRITICA)
        suggested_priority = _max_priority(suggested_priority, WorkOrderPriority.ALTA)

    if not reasons:
        return None

    return RuleAlertDraft(
        title=f"Alerta operacional para ocorrencia do equipamento #{occurrence.equipment_id}",
        message="; ".join(reasons) + ".",
        severity=severity,
        recommendation="Avaliar condicao do equipamento e confirmar se ha necessidade de acionar manutencao.",
        suggested_work_order=suggested_priority is not None,
        suggested_work_order_type=WorkOrderType.CORRETIVA if suggested_priority is not None else None,
        suggested_work_order_priority=suggested_priority,
        event_at=occurrence.occurred_at,
    )


def _build_measurement_rule_alert(db: Session, measurement: Measurement) -> RuleAlertDraft | None:
    equipment = db.get(Equipment, measurement.equipment_id)
    if equipment is None:
        return None

    threshold_severity = _severity_from_equipment_thresholds(equipment, measurement)
    if threshold_severity is None:
        return None

    recent_measurements = (
        db.query(Measurement)
        .filter(
            Measurement.equipment_id == measurement.equipment_id,
            Measurement.measurement_type == measurement.measurement_type,
        )
        .order_by(Measurement.measured_at.desc(), Measurement.created_at.desc())
        .limit(3)
        .all()
    )
    trend_text = _describe_measurement_trend(recent_measurements)

    return RuleAlertDraft(
        title=f"Medicao em faixa de alerta para {measurement.measurement_type.value}",
        message=(
            f"Valor {measurement.value:.2f} {measurement.unit} atingiu a faixa {threshold_severity.value} "
            f"configurada para o equipamento. {trend_text}"
        ),
        severity=threshold_severity,
        recommendation="Inspecionar o equipamento e confirmar se a variacao indica degradacao ou sobrecarga.",
        suggested_work_order=threshold_severity in {AlertSeverity.ALTA, AlertSeverity.CRITICA},
        suggested_work_order_type=(
            WorkOrderType.PREVENTIVA if threshold_severity in {AlertSeverity.ALTA, AlertSeverity.CRITICA} else None
        ),
        suggested_work_order_priority=_priority_from_alert_severity(threshold_severity),
        event_at=measurement.measured_at,
    )


def _describe_measurement_trend(measurements: list[Measurement]) -> str:
    if len(measurements) < 2:
        return "Sem historico suficiente para comparar tendencia recente."

    latest = measurements[0].value
    oldest = measurements[-1].value
    if latest > oldest:
        return "Os registros recentes mostram tendencia de alta."
    if latest < oldest:
        return "Os registros recentes mostram tendencia de reducao."
    return "Os registros recentes mostram estabilidade."


def _build_occurrence_ai_context(db: Session, occurrence: Occurrence) -> dict[str, Any]:
    open_work_orders = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.equipment_id == occurrence.equipment_id,
            WorkOrder.status.in_([WorkOrderStatus.ABERTA, WorkOrderStatus.EM_EXECUCAO]),
        )
        .count()
    )
    recent_occurrences = (
        db.query(Occurrence)
        .filter(Occurrence.equipment_id == occurrence.equipment_id)
        .order_by(Occurrence.occurred_at.desc(), Occurrence.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "kind": "occurrence",
        "equipment_id": occurrence.equipment_id,
        "event": {
            "severity": occurrence.severity.value,
            "safety_risk": occurrence.safety_risk,
            "production_stop": occurrence.production_stop,
            "description": occurrence.description,
            "occurred_at": occurrence.occurred_at.isoformat(),
        },
        "recent_occurrence_count": len(recent_occurrences),
        "open_work_orders": open_work_orders,
    }


def _build_measurement_ai_context(db: Session, measurement: Measurement) -> dict[str, Any]:
    equipment = db.get(Equipment, measurement.equipment_id)
    recent_measurements = (
        db.query(Measurement)
        .filter(
            Measurement.equipment_id == measurement.equipment_id,
            Measurement.measurement_type == measurement.measurement_type,
        )
        .order_by(Measurement.measured_at.desc(), Measurement.created_at.desc())
        .limit(5)
        .all()
    )
    open_work_orders = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.equipment_id == measurement.equipment_id,
            WorkOrder.status.in_([WorkOrderStatus.ABERTA, WorkOrderStatus.EM_EXECUCAO]),
        )
        .count()
    )
    return {
        "kind": "measurement",
        "equipment_id": measurement.equipment_id,
        "event": {
            "measurement_type": measurement.measurement_type.value,
            "value": measurement.value,
            "unit": measurement.unit,
            "measured_at": measurement.measured_at.isoformat(),
        },
        "equipment_thresholds": {
            "measurement_type": equipment.alert_measurement_type.value if equipment and equipment.alert_measurement_type else None,
            "unit": equipment.measurement_unit if equipment else None,
            "low": equipment.alert_threshold_low if equipment else None,
            "medium": equipment.alert_threshold_medium if equipment else None,
            "high": equipment.alert_threshold_high if equipment else None,
            "critical": equipment.alert_threshold_critical if equipment else None,
        },
        "recent_values": [item.value for item in recent_measurements],
        "open_work_orders": open_work_orders,
    }


def _create_alert(
    db: Session,
    equipment_id: int,
    origin_type: AlertOriginType,
    origin_id: int | None,
    draft: RuleAlertDraft,
    ai_context: dict[str, Any],
) -> Alert:
    ai_enrichment = _get_ai_enrichment(ai_context, draft)
    source = AlertSource.RULE
    recommendation = draft.recommendation
    possible_cause = None
    suggested_work_order = draft.suggested_work_order
    suggested_type = draft.suggested_work_order_type
    suggested_priority = draft.suggested_work_order_priority

    if ai_enrichment is not None:
        source = AlertSource.HYBRID
        recommendation = ai_enrichment.get("recommendation") or recommendation
        possible_cause = ai_enrichment.get("possible_cause")
        ai_should_suggest = bool(ai_enrichment.get("suggest_work_order"))
        suggested_work_order = suggested_work_order or ai_should_suggest
        if ai_should_suggest and suggested_type is None:
            suggested_type = WorkOrderType.CORRETIVA
        if ai_should_suggest and suggested_priority is None:
            suggested_priority = WorkOrderPriority.ALTA

    alert = Alert(
        equipment_id=equipment_id,
        origin_type=origin_type,
        origin_id=origin_id,
        source=source,
        severity=draft.severity,
        title=draft.title,
        message=draft.message,
        recommendation=recommendation,
        possible_cause=possible_cause,
        suggested_work_order=suggested_work_order,
        suggested_work_order_type=suggested_type if suggested_work_order else None,
        suggested_work_order_priority=suggested_priority if suggested_work_order else None,
        event_at=_ensure_utc_datetime(draft.event_at),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return (
        db.query(Alert)
        .options(joinedload(Alert.equipment))
        .filter(Alert.id == alert.id)
        .first()
    ) or alert


def _get_ai_enrichment(ai_context: dict[str, Any], draft: RuleAlertDraft) -> dict[str, Any] | None:
    if not settings.openai_api_key.strip():
        return None

    payload = {
        "model": "gpt-5.4-mini",
        "input": [
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Voce analisa alertas industriais para manutencao. Responda apenas com JSON valido "
                            "seguindo o schema solicitado, sem markdown."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(
                            {
                                "rule_alert": {
                                    "title": draft.title,
                                    "message": draft.message,
                                    "severity": draft.severity.value,
                                    "recommendation": draft.recommendation,
                                    "suggested_work_order": draft.suggested_work_order,
                                },
                                "context": ai_context,
                            },
                            ensure_ascii=True,
                        ),
                    }
                ],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "alert_enrichment",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "risk": {"type": "string"},
                        "possible_cause": {"type": "string"},
                        "recommendation": {"type": "string"},
                        "suggest_work_order": {"type": "boolean"},
                    },
                    "required": ["risk", "possible_cause", "recommendation", "suggest_work_order"],
                    "additionalProperties": False,
                },
            }
        },
    }

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (TimeoutError, error.URLError, error.HTTPError, json.JSONDecodeError):
        return None

    output_text = body.get("output_text")
    if not isinstance(output_text, str) or not output_text.strip():
        return None

    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None
    return parsed


def _map_occurrence_severity(severity: OccurrenceSeverity) -> AlertSeverity:
    mapping = {
        OccurrenceSeverity.BAIXA: AlertSeverity.BAIXA,
        OccurrenceSeverity.MEDIA: AlertSeverity.MEDIA,
        OccurrenceSeverity.ALTA: AlertSeverity.ALTA,
        OccurrenceSeverity.CRITICA: AlertSeverity.CRITICA,
    }
    return mapping[severity]


def _map_occurrence_priority(severity: OccurrenceSeverity) -> WorkOrderPriority | None:
    mapping = {
        OccurrenceSeverity.BAIXA: None,
        OccurrenceSeverity.MEDIA: None,
        OccurrenceSeverity.ALTA: WorkOrderPriority.ALTA,
        OccurrenceSeverity.CRITICA: WorkOrderPriority.CRITICA,
    }
    return mapping[severity]


def _max_severity(current: AlertSeverity, candidate: AlertSeverity) -> AlertSeverity:
    order = [AlertSeverity.BAIXA, AlertSeverity.MEDIA, AlertSeverity.ALTA, AlertSeverity.CRITICA]
    return max(current, candidate, key=order.index)


def _max_priority(
    current: WorkOrderPriority | None, candidate: WorkOrderPriority | None
) -> WorkOrderPriority | None:
    if current is None:
        return candidate
    if candidate is None:
        return current
    order = [
        WorkOrderPriority.BAIXA,
        WorkOrderPriority.MEDIA,
        WorkOrderPriority.ALTA,
        WorkOrderPriority.CRITICA,
    ]
    return max(current, candidate, key=order.index)


def _severity_from_equipment_thresholds(equipment: Equipment, measurement: Measurement) -> AlertSeverity | None:
    if (
        equipment.alert_measurement_type is None
        or equipment.measurement_unit is None
        or equipment.alert_threshold_low is None
        or equipment.alert_threshold_medium is None
        or equipment.alert_threshold_high is None
        or equipment.alert_threshold_critical is None
    ):
        return None
    if equipment.alert_measurement_type != measurement.measurement_type:
        return None
    if equipment.measurement_unit.strip().lower() != measurement.unit.strip().lower():
        return None

    value = measurement.value
    if value >= equipment.alert_threshold_critical:
        return AlertSeverity.CRITICA
    if value >= equipment.alert_threshold_high:
        return AlertSeverity.ALTA
    if value >= equipment.alert_threshold_medium:
        return AlertSeverity.MEDIA
    if value >= equipment.alert_threshold_low:
        return AlertSeverity.BAIXA
    return None


def _priority_from_alert_severity(severity: AlertSeverity) -> WorkOrderPriority | None:
    mapping = {
        AlertSeverity.BAIXA: None,
        AlertSeverity.MEDIA: None,
        AlertSeverity.ALTA: WorkOrderPriority.ALTA,
        AlertSeverity.CRITICA: WorkOrderPriority.CRITICA,
    }
    return mapping[severity]


def _ensure_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
