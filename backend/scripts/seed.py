import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from random import Random

from sqlalchemy import delete, func, select

from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.models.alert import Alert, AlertOriginType, AlertSeverity, AlertSource, AlertStatus
from app.models.equipment import Equipment
from app.models.measurement import Measurement, MeasurementType
from app.models.occurrence import Occurrence, OccurrenceSeverity
from app.models.team import Team
from app.models.user import User, UserRole
from app.models.work_order import WorkOrder, WorkOrderOrigin, WorkOrderPriority, WorkOrderStatus, WorkOrderType
from app.models.work_order_status_history import WorkOrderStatusHistory

DEFAULT_PASSWORD = "Manimaq@123"


@dataclass(frozen=True)
class EquipmentSeed:
    tag: str
    name: str
    sector: str
    team_name: str
    profile: str
    criticality: str
    measurement_type: MeasurementType | None = None
    unit: str | None = None
    thresholds: tuple[float, float, float, float] | None = None
    status: str = "ativo"


TEAM_SEEDS = [
    {"name": "Administracao", "sector": "Administracao", "description": "Equipe administrativa"},
    {"name": "Producao", "sector": "Producao", "description": "Equipe operacional da producao"},
    {"name": "Expedicao", "sector": "Expedicao", "description": "Equipe de expedicao"},
    {"name": "Elétrica", "sector": "Elétrica", "description": "Equipe de Elétrica"},
    {"name": "Mecânica", "sector": "Mecânica", "description": "Equipe de Mecânica"},
    {"name": "Utilidades", "sector": "Utilidades", "description": "Equipe de utilidades"},
]

USER_SEEDS = [
    {
        "name": "Otavio",
        "username": "otavio",
        "email": "otavio@manimaq.local",
        "role": UserRole.ADMIN,
        "team_name": "Administracao",
    },
    {
        "name": "Taina",
        "username": "taina",
        "email": "taina@manimaq.local",
        "role": UserRole.GERENTE,
        "team_name": "Administracao",
    },
    {
        "name": "Michael",
        "username": "michael",
        "email": "michael@manimaq.local",
        "role": UserRole.OPERADOR,
        "team_name": "Mecânica",
    },
    {
        "name": "Leonardo",
        "username": "leonardo",
        "email": "leonardo@manimaq.local",
        "role": UserRole.OPERADOR,
        "team_name": "Elétrica",
    },
    {
        "name": "Murillo",
        "username": "murillo",
        "email": "murillo@manimaq.local",
        "role": UserRole.OPERADOR,
        "team_name": "Utilidades",
    },
    {
        "name": "Bruno",
        "username": "bruno",
        "email": "bruno@manimaq.local",
        "role": UserRole.OPERADOR,
        "team_name": "Expedicao",
    },
]

EQUIPMENT_SEEDS = [
    EquipmentSeed(
        tag="PC-01",
        name="Computador administrativo",
        sector="Administracao",
        team_name="Administracao",
        profile="tranquilo",
        criticality="baixa",
        measurement_type=MeasurementType.TEMPERATURA,
        unit="C",
        thresholds=(55.0, 60.0, 68.0, 75.0),
    ),
    EquipmentSeed(
        tag="LAMP-01",
        name="Iluminacao corredor",
        sector="Administracao",
        team_name="Administracao",
        profile="tranquilo",
        criticality="baixa",
        measurement_type=MeasurementType.CORRENTE,
        unit="A",
        thresholds=(0.7, 0.9, 1.1, 1.3),
    ),
    EquipmentSeed(
        tag="MAQ-01",
        name="Prensa hidraulica principal",
        sector="Producao",
        team_name="Producao",
        profile="problematico",
        criticality="critica",
        measurement_type=MeasurementType.VIBRACAO,
        unit="mm/s",
        thresholds=(4.5, 6.0, 8.0, 10.5),
    ),
    EquipmentSeed(
        tag="MAQ-02",
        name="Esteira principal",
        sector="Producao",
        team_name="Producao",
        profile="intermediario",
        criticality="alta",
        measurement_type=MeasurementType.CORRENTE,
        unit="A",
        thresholds=(18.0, 21.0, 25.0, 29.0),
    ),
    EquipmentSeed(
        tag="MAQ-03",
        name="Seladora automatica",
        sector="Producao",
        team_name="Producao",
        profile="tranquilo",
        criticality="media",
        measurement_type=MeasurementType.TEMPERATURA,
        unit="C",
        thresholds=(58.0, 63.0, 70.0, 78.0),
    ),
    EquipmentSeed(
        tag="MAQ-04",
        name="Misturador industrial",
        sector="Producao",
        team_name="Producao",
        profile="problematico",
        criticality="critica",
        measurement_type=MeasurementType.TEMPERATURA,
        unit="C",
        thresholds=(72.0, 78.0, 85.0, 92.0),
    ),
    EquipmentSeed(
        tag="MAQ-05",
        name="Empacotadora secundaria",
        sector="Producao",
        team_name="Producao",
        profile="intermediario",
        criticality="media",
        measurement_type=MeasurementType.VIBRACAO,
        unit="mm/s",
        thresholds=(3.8, 5.0, 6.6, 8.2),
    ),
    EquipmentSeed(
        tag="EMP-01",
        name="Esteira de expedicao",
        sector="Expedicao",
        team_name="Expedicao",
        profile="intermediario",
        criticality="media",
        measurement_type=MeasurementType.CORRENTE,
        unit="A",
        thresholds=(8.0, 9.5, 11.5, 13.0),
    ),
    EquipmentSeed(
        tag="EMP-02",
        name="Mesa de roletes",
        sector="Expedicao",
        team_name="Expedicao",
        profile="tranquilo",
        criticality="baixa",
        measurement_type=MeasurementType.VIBRACAO,
        unit="mm/s",
        thresholds=(2.5, 3.2, 4.4, 5.2),
    ),
    EquipmentSeed(
        tag="PLT-01",
        name="Paletizadora automatica",
        sector="Expedicao",
        team_name="Expedicao",
        profile="problematico",
        criticality="alta",
        measurement_type=MeasurementType.VIBRACAO,
        unit="mm/s",
        thresholds=(4.2, 5.8, 7.8, 9.4),
    ),
    EquipmentSeed(
        tag="COMP-01",
        name="Compressor principal",
        sector="Utilidades",
        team_name="Utilidades",
        profile="problematico",
        criticality="critica",
        measurement_type=MeasurementType.VIBRACAO,
        unit="mm/s",
        thresholds=(5.0, 6.8, 8.8, 10.8),
    ),
    EquipmentSeed(
        tag="COMP-02",
        name="Compressor reserva",
        sector="Utilidades",
        team_name="Utilidades",
        profile="tranquilo",
        criticality="media",
        measurement_type=MeasurementType.VIBRACAO,
        unit="mm/s",
        thresholds=(4.0, 5.2, 6.5, 8.0),
    ),
    EquipmentSeed(
        tag="GER-01",
        name="Gerador reserva",
        sector="Utilidades",
        team_name="Utilidades",
        profile="intermediario",
        criticality="alta",
        measurement_type=MeasurementType.TENSAO,
        unit="V",
        thresholds=(225.0, 232.0, 242.0, 250.0),
    ),
    EquipmentSeed(
        tag="AR-01",
        name="Ar-condicionado sala tecnica",
        sector="Utilidades",
        team_name="Utilidades",
        profile="tranquilo",
        criticality="baixa",
        measurement_type=MeasurementType.CORRENTE,
        unit="A",
        thresholds=(7.0, 8.0, 9.5, 11.0),
    ),
]

PROFILE_MEASUREMENT_COUNTS = {"tranquilo": 12, "intermediario": 24, "problematico": 36}
PROFILE_OCCURRENCE_COUNTS = {"tranquilo": 1, "intermediario": 5, "problematico": 10}
PROFILE_WORK_ORDER_COUNTS = {"tranquilo": 1, "intermediario": 3, "problematico": 7}

MEASUREMENT_BASELINES = {
    "PC-01": 49.0,
    "LAMP-01": 0.45,
    "MAQ-01": 4.2,
    "MAQ-02": 17.5,
    "MAQ-03": 56.0,
    "MAQ-04": 71.0,
    "MAQ-05": 3.7,
    "EMP-01": 7.8,
    "EMP-02": 2.3,
    "PLT-01": 4.0,
    "COMP-01": 4.8,
    "COMP-02": 3.6,
    "GER-01": 220.0,
    "AR-01": 6.1,
}

OCCURRENCE_DESCRIPTIONS = {
    "tranquilo": [
        "Inspecao registrou pequena variacao sem impacto operacional.",
        "Ocorrencia leve observada durante rotina, sem parada do equipamento.",
    ],
    "intermediario": [
        "Oscilacao operacional identificada durante a producao com necessidade de acompanhamento.",
        "Ruido fora do padrao detectado pela operacao, sem risco imediato.",
        "Desvio moderado em funcionamento exigiu verificacao da equipe responsavel.",
    ],
    "problematico": [
        "Parada de producao apos falha recorrente em componente critico.",
        "Aquecimento excessivo com risco operacional e necessidade de intervencao rapida.",
        "Vibracao anormal persistente associada a degradacao progressiva do conjunto.",
        "Falha repetitiva detectada no turno com impacto direto no processo.",
    ],
}

WORK_ORDER_DESCRIPTIONS = {
    "tranquilo": [
        "Inspecao preventiva programada para manter estabilidade operacional.",
        "Ajuste leve e verificacao de rotina sem impacto relevante.",
    ],
    "intermediario": [
        "Intervencao preventiva para conter desvio identificado em medicao recente.",
        "Correcao localizada apos ocorrencia recorrente no equipamento.",
        "Reaperto, alinhamento e verificacao funcional do conjunto.",
    ],
    "problematico": [
        "Corretiva prioritaria para falha recorrente com historico de interrupcao.",
        "Intervencao corretiva em componente com tendencia de deterioracao.",
        "Revisao completa do conjunto apos repeticao de alertas criticos.",
        "Ajuste emergencial e inspecao aprofundada em equipamento sensivel.",
    ],
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed base e historico operacional do Manimaq.")
    parser.add_argument(
        "--reset-operational",
        action="store_true",
        help="Apaga ocorrencias, medicoes, alertas e OS antes de gerar o historico novamente.",
    )
    return parser.parse_args()


def ensure_teams(db) -> dict[str, Team]:
    teams_by_name: dict[str, Team] = {}
    for payload in TEAM_SEEDS:
        team = db.execute(select(Team).where(Team.name == payload["name"])).scalar_one_or_none()
        if team is None:
            team = Team(**payload)
            db.add(team)
            db.flush()
        else:
            team.sector = payload["sector"]
            team.description = payload["description"]
            team.active = True
        teams_by_name[payload["name"]] = team
    return teams_by_name


def ensure_users(db, teams_by_name: dict[str, Team]) -> dict[str, User]:
    users_by_username: dict[str, User] = {}
    for payload in USER_SEEDS:
        user = db.execute(select(User).where(User.username == payload["username"])).scalar_one_or_none()
        team = teams_by_name[payload["team_name"]]
        if user is None:
            user = User(
                name=payload["name"],
                username=payload["username"],
                email=payload["email"],
                role=payload["role"],
                team_id=team.id,
                password_hash=hash_password(DEFAULT_PASSWORD),
                active=True,
            )
            db.add(user)
            db.flush()
        else:
            user.name = payload["name"]
            user.email = payload["email"]
            user.role = payload["role"]
            user.team_id = team.id
            user.active = True
        users_by_username[payload["username"]] = user
    return users_by_username


def ensure_equipments(db, teams_by_name: dict[str, Team]) -> dict[str, Equipment]:
    equipments_by_tag: dict[str, Equipment] = {}
    for spec in EQUIPMENT_SEEDS:
        equipment = db.execute(select(Equipment).where(Equipment.tag == spec.tag)).scalar_one_or_none()
        team = teams_by_name[spec.team_name]
        threshold_low, threshold_medium, threshold_high, threshold_critical = spec.thresholds or (None, None, None, None)
        if equipment is None:
            equipment = Equipment(
                tag=spec.tag,
                name=spec.name,
                sector=spec.sector,
                criticality=spec.criticality,
                status=spec.status,
                active=True,
                team_id=team.id,
                alert_measurement_type=spec.measurement_type,
                measurement_unit=spec.unit,
                alert_threshold_low=threshold_low,
                alert_threshold_medium=threshold_medium,
                alert_threshold_high=threshold_high,
                alert_threshold_critical=threshold_critical,
            )
            db.add(equipment)
            db.flush()
        else:
            equipment.name = spec.name
            equipment.sector = spec.sector
            equipment.criticality = spec.criticality
            equipment.status = spec.status
            equipment.active = True
            equipment.team_id = team.id
            equipment.alert_measurement_type = spec.measurement_type
            equipment.measurement_unit = spec.unit
            equipment.alert_threshold_low = threshold_low
            equipment.alert_threshold_medium = threshold_medium
            equipment.alert_threshold_high = threshold_high
            equipment.alert_threshold_critical = threshold_critical
        equipments_by_tag[spec.tag] = equipment
    return equipments_by_tag


def reset_operational_data(db) -> None:
    db.execute(delete(WorkOrderStatusHistory))
    db.execute(delete(WorkOrder))
    db.execute(delete(Alert))
    db.execute(delete(Measurement))
    db.execute(delete(Occurrence))
    db.flush()


def severity_rank(value: str) -> int:
    return {"baixa": 0, "media": 1, "alta": 2, "critica": 3}[value]


def measurement_severity(equipment: Equipment, value: float) -> AlertSeverity | None:
    if equipment.alert_threshold_low is None:
        return None
    if value >= (equipment.alert_threshold_critical or float("inf")):
        return AlertSeverity.CRITICA
    if value >= (equipment.alert_threshold_high or float("inf")):
        return AlertSeverity.ALTA
    if value >= (equipment.alert_threshold_medium or float("inf")):
        return AlertSeverity.MEDIA
    if value >= equipment.alert_threshold_low:
        return AlertSeverity.BAIXA
    return None


def create_measurement_events(
    db,
    rng: Random,
    equipment: Equipment,
    author: User,
    spec: EquipmentSeed,
    end_at: datetime,
) -> list[Measurement]:
    if spec.measurement_type is None or spec.unit is None:
        return []

    total = PROFILE_MEASUREMENT_COUNTS[spec.profile]
    start_at = end_at - timedelta(days=180)
    span_seconds = (end_at - start_at).total_seconds()
    baseline = MEASUREMENT_BASELINES[spec.tag]
    measurements: list[Measurement] = []

    for index in range(total):
        ratio = index / max(total - 1, 1)
        measured_at = start_at + timedelta(seconds=span_seconds * ratio)
        jitter_days = rng.uniform(-1.2, 1.2)
        measured_at = measured_at + timedelta(days=jitter_days)

        if spec.profile == "tranquilo":
            noise = rng.uniform(-0.08, 0.08)
            value = baseline * (1 + noise)
        elif spec.profile == "intermediario":
            trend = 0.18 * ratio
            noise = rng.uniform(-0.10, 0.12)
            value = baseline * (1 + trend + noise)
        else:
            trend = 0.55 * ratio
            noise = rng.uniform(-0.07, 0.15)
            value = baseline * (1 + trend + noise)

        if spec.profile == "problematico" and index >= total - 4:
            value *= 1.08 + 0.03 * (index - (total - 4))

        measurement = Measurement(
            equipment_id=equipment.id,
            author_id=author.id,
            measurement_type=spec.measurement_type,
            value=round(value, 2),
            unit=spec.unit,
            measured_at=measured_at,
            created_at=measured_at + timedelta(minutes=5),
            updated_at=measured_at + timedelta(minutes=5),
        )
        db.add(measurement)
        measurements.append(measurement)

    db.flush()
    return measurements


def create_occurrence_events(
    db,
    rng: Random,
    equipment: Equipment,
    author: User,
    spec: EquipmentSeed,
    end_at: datetime,
) -> list[Occurrence]:
    total = PROFILE_OCCURRENCE_COUNTS[spec.profile]
    start_at = end_at - timedelta(days=180)
    span_seconds = (end_at - start_at).total_seconds()
    occurrences: list[Occurrence] = []

    for index in range(total):
        ratio = index / max(total - 1, 1)
        occurred_at = start_at + timedelta(seconds=span_seconds * ratio)
        occurred_at = occurred_at + timedelta(days=rng.uniform(-2.0, 2.0))

        if spec.profile == "tranquilo":
            severity = OccurrenceSeverity.BAIXA
            safety_risk = False
            production_stop = False
        elif spec.profile == "intermediario":
            severity = OccurrenceSeverity.MEDIA if ratio < 0.75 else OccurrenceSeverity.ALTA
            safety_risk = ratio > 0.85 and rng.random() > 0.5
            production_stop = ratio > 0.8 and rng.random() > 0.55
        else:
            severity = OccurrenceSeverity.ALTA if ratio < 0.7 else OccurrenceSeverity.CRITICA
            safety_risk = ratio > 0.45 or rng.random() > 0.7
            production_stop = ratio > 0.35 or rng.random() > 0.75

        description_pool = OCCURRENCE_DESCRIPTIONS[spec.profile]
        description = description_pool[index % len(description_pool)]
        if spec.profile != "tranquilo":
            description = f"{description} Equipamento {equipment.tag} em observacao."

        occurrence = Occurrence(
            equipment_id=equipment.id,
            author_id=author.id,
            severity=severity,
            safety_risk=safety_risk,
            production_stop=production_stop,
            description=description,
            occurred_at=occurred_at,
            created_at=occurred_at + timedelta(minutes=8),
            updated_at=occurred_at + timedelta(minutes=8),
        )
        db.add(occurrence)
        occurrences.append(occurrence)

    db.flush()
    return occurrences


def create_alert_for_measurement(db, equipment: Equipment, measurement: Measurement) -> Alert | None:
    severity = measurement_severity(equipment, measurement.value)
    if severity is None or severity == AlertSeverity.BAIXA and equipment.criticality == "baixa":
        return None

    alert = Alert(
        equipment_id=equipment.id,
        origin_type=AlertOriginType.MEASUREMENT,
        origin_id=measurement.id,
        source=AlertSource.HYBRID if severity_rank(severity.value) >= severity_rank("alta") else AlertSource.RULE,
        severity=severity,
        status=AlertStatus.ABERTO,
        title=f"Leitura elevada em {equipment.tag}",
        message=f"{measurement.measurement_type.value.capitalize()} em {measurement.value} {measurement.unit} no equipamento {equipment.tag}.",
        recommendation=(
            "Monitorar e programar inspecao."
            if severity in {AlertSeverity.BAIXA, AlertSeverity.MEDIA}
            else "Avaliar abertura de OS e inspecionar o equipamento."
        ),
        possible_cause="Sinal de degradacao progressiva no comportamento da medicao."
        if severity in {AlertSeverity.ALTA, AlertSeverity.CRITICA}
        else "Oscilacao operacional acima do padrao esperado.",
        suggested_work_order=severity in {AlertSeverity.ALTA, AlertSeverity.CRITICA},
        suggested_work_order_type=WorkOrderType.CORRETIVA if severity in {AlertSeverity.ALTA, AlertSeverity.CRITICA} else None,
        suggested_work_order_priority=(
            WorkOrderPriority.ALTA if severity == AlertSeverity.ALTA else WorkOrderPriority.CRITICA
            if severity == AlertSeverity.CRITICA
            else None
        ),
        event_at=measurement.measured_at,
        created_at=measurement.measured_at + timedelta(minutes=6),
        updated_at=measurement.measured_at + timedelta(minutes=6),
    )
    db.add(alert)
    return alert


def create_alert_for_occurrence(db, equipment: Equipment, occurrence: Occurrence) -> Alert | None:
    if not occurrence.safety_risk and not occurrence.production_stop and occurrence.severity not in {
        OccurrenceSeverity.ALTA,
        OccurrenceSeverity.CRITICA,
    }:
        return None

    severity = {
        OccurrenceSeverity.BAIXA: AlertSeverity.BAIXA,
        OccurrenceSeverity.MEDIA: AlertSeverity.MEDIA,
        OccurrenceSeverity.ALTA: AlertSeverity.ALTA,
        OccurrenceSeverity.CRITICA: AlertSeverity.CRITICA,
    }[occurrence.severity]

    if occurrence.production_stop:
        severity = AlertSeverity.CRITICA if severity_rank(severity.value) < severity_rank("critica") else severity

    alert = Alert(
        equipment_id=equipment.id,
        origin_type=AlertOriginType.OCCURRENCE,
        origin_id=occurrence.id,
        source=AlertSource.RULE,
        severity=severity,
        status=AlertStatus.REVISADO if occurrence.occurred_at < utc_now() - timedelta(days=21) else AlertStatus.ABERTO,
        title=f"Ocorrencia relevante em {equipment.tag}",
        message=occurrence.description,
        recommendation=(
            "Abrir OS e priorizar avaliacao."
            if severity in {AlertSeverity.ALTA, AlertSeverity.CRITICA}
            else "Acompanhar e registrar recorrencia."
        ),
        possible_cause="Ocorrencia operacional associada a reincidencia ou desvio de processo.",
        suggested_work_order=severity in {AlertSeverity.ALTA, AlertSeverity.CRITICA},
        suggested_work_order_type=WorkOrderType.CORRETIVA if severity in {AlertSeverity.ALTA, AlertSeverity.CRITICA} else None,
        suggested_work_order_priority=(
            WorkOrderPriority.ALTA if severity == AlertSeverity.ALTA else WorkOrderPriority.CRITICA
            if severity == AlertSeverity.CRITICA
            else None
        ),
        event_at=occurrence.occurred_at,
        created_at=occurrence.occurred_at + timedelta(minutes=12),
        updated_at=occurrence.occurred_at + timedelta(minutes=12),
    )
    db.add(alert)
    return alert


def create_work_order(
    db,
    equipment: Equipment,
    team: Team,
    created_by: User,
    executor: User,
    opened_at: datetime,
    status: WorkOrderStatus,
    order_type: WorkOrderType,
    priority: WorkOrderPriority,
    origin: WorkOrderOrigin,
    description: str,
    estimated_duration_hours: int,
    note_prefix: str,
    transition_hour_offsets: tuple[int, int] | None = None,
) -> WorkOrder:
    work_order = WorkOrder(
        equipment_id=equipment.id,
        team_id=team.id,
        created_by_id=created_by.id,
        type=order_type,
        priority=priority,
        status=status,
        origin=origin,
        description=description,
        planned_start_at=opened_at + timedelta(hours=4),
        estimated_duration_hours=estimated_duration_hours,
        created_at=opened_at,
        updated_at=opened_at,
    )
    db.add(work_order)
    db.flush()

    open_event = WorkOrderStatusHistory(
        work_order_id=work_order.id,
        author_id=created_by.id,
        previous_status=None,
        new_status=WorkOrderStatus.ABERTA,
        note=f"{note_prefix} OS aberta para acompanhamento.",
        transition_at=opened_at,
        created_at=opened_at,
    )
    db.add(open_event)

    updated_at = opened_at
    if status in {WorkOrderStatus.EM_EXECUCAO, WorkOrderStatus.CONCLUIDA, WorkOrderStatus.CANCELADA} and transition_hour_offsets:
        execution_at = opened_at + timedelta(hours=transition_hour_offsets[0])
        db.add(
            WorkOrderStatusHistory(
                work_order_id=work_order.id,
                author_id=executor.id if status != WorkOrderStatus.CANCELADA else created_by.id,
                previous_status=WorkOrderStatus.ABERTA,
                new_status=WorkOrderStatus.EM_EXECUCAO if status != WorkOrderStatus.CANCELADA else WorkOrderStatus.CANCELADA,
                note=(
                    f"{note_prefix} Execucao iniciada pela equipe responsavel."
                    if status != WorkOrderStatus.CANCELADA
                    else f"{note_prefix} OS cancelada antes da execucao."
                ),
                transition_at=execution_at,
                created_at=execution_at,
            )
        )
        updated_at = execution_at

        if status == WorkOrderStatus.CONCLUIDA:
            closed_at = opened_at + timedelta(hours=transition_hour_offsets[1])
            db.add(
                WorkOrderStatusHistory(
                    work_order_id=work_order.id,
                    author_id=executor.id,
                    previous_status=WorkOrderStatus.EM_EXECUCAO,
                    new_status=WorkOrderStatus.CONCLUIDA,
                    note=f"{note_prefix} Servico concluido com retorno operacional registrado.",
                    transition_at=closed_at,
                    created_at=closed_at,
                )
            )
            updated_at = closed_at

    work_order.updated_at = updated_at
    return work_order


def build_last_week_work_orders(
    db,
    equipments_by_tag: dict[str, Equipment],
    teams_by_name: dict[str, Team],
    users_by_username: dict[str, User],
    now: datetime,
) -> list[WorkOrder]:
    manager = users_by_username["taina"]
    production_operator = users_by_username["michael"]
    utilities_operator = users_by_username["murillo"]
    expedition_operator = users_by_username["bruno"]

    recent_specs = [
        {
            "tag": "COMP-01",
            "team": "Utilidades",
            "status": WorkOrderStatus.CONCLUIDA,
            "type": WorkOrderType.CORRETIVA,
            "priority": WorkOrderPriority.CRITICA,
            "origin": WorkOrderOrigin.SUGERIDA,
            "description": "Troca de acoplamento e inspeção do compressor principal.",
            "opened_days_ago": 2,
            "hours": (3, 19),
            "operator": utilities_operator,
        },
        {
            "tag": "MAQ-04",
            "team": "Producao",
            "status": WorkOrderStatus.CONCLUIDA,
            "type": WorkOrderType.PREVENTIVA,
            "priority": WorkOrderPriority.ALTA,
            "origin": WorkOrderOrigin.MANUAL,
            "description": "Revisao preventiva do misturador com reaperto e inspeção térmica.",
            "opened_days_ago": 3,
            "hours": (4, 16),
            "operator": production_operator,
        },
        {
            "tag": "EMP-01",
            "team": "Expedicao",
            "status": WorkOrderStatus.CONCLUIDA,
            "type": WorkOrderType.CORRETIVA,
            "priority": WorkOrderPriority.MEDIA,
            "origin": WorkOrderOrigin.MANUAL,
            "description": "Correção de desalinhamento da esteira de expedição.",
            "opened_days_ago": 1,
            "hours": (2, 8),
            "operator": expedition_operator,
        },
        {
            "tag": "PLT-01",
            "team": "Expedicao",
            "status": WorkOrderStatus.EM_EXECUCAO,
            "type": WorkOrderType.CORRETIVA,
            "priority": WorkOrderPriority.ALTA,
            "origin": WorkOrderOrigin.SUGERIDA,
            "description": "Inspecao corretiva na paletizadora apos alertas recorrentes.",
            "opened_days_ago": 2,
            "hours": (5, 0),
            "operator": expedition_operator,
        },
        {
            "tag": "MAQ-01",
            "team": "Producao",
            "status": WorkOrderStatus.EM_EXECUCAO,
            "type": WorkOrderType.CORRETIVA,
            "priority": WorkOrderPriority.CRITICA,
            "origin": WorkOrderOrigin.SUGERIDA,
            "description": "Intervenção em prensa principal após parada recorrente.",
            "opened_days_ago": 1,
            "hours": (1, 0),
            "operator": production_operator,
        },
        {
            "tag": "COMP-01",
            "team": "Utilidades",
            "status": WorkOrderStatus.ABERTA,
            "type": WorkOrderType.PREVENTIVA,
            "priority": WorkOrderPriority.ALTA,
            "origin": WorkOrderOrigin.MANUAL,
            "description": "Inspecao complementar pós-correção do compressor principal.",
            "opened_days_ago": 0,
            "hours": None,
            "operator": utilities_operator,
        },
        {
            "tag": "MAQ-02",
            "team": "Producao",
            "status": WorkOrderStatus.ABERTA,
            "type": WorkOrderType.PREVENTIVA,
            "priority": WorkOrderPriority.MEDIA,
            "origin": WorkOrderOrigin.MANUAL,
            "description": "Preventiva programada da esteira principal.",
            "opened_days_ago": 5,
            "hours": None,
            "operator": production_operator,
        },
        {
            "tag": "GER-01",
            "team": "Utilidades",
            "status": WorkOrderStatus.ABERTA,
            "type": WorkOrderType.CORRETIVA,
            "priority": WorkOrderPriority.ALTA,
            "origin": WorkOrderOrigin.MANUAL,
            "description": "Verificacao de oscilacao de tensao no gerador reserva.",
            "opened_days_ago": 4,
            "hours": None,
            "operator": utilities_operator,
        },
    ]

    work_orders: list[WorkOrder] = []
    for spec in recent_specs:
        opened_at = now - timedelta(days=spec["opened_days_ago"], hours=2)
        work_order = create_work_order(
            db=db,
            equipment=equipments_by_tag[spec["tag"]],
            team=teams_by_name[spec["team"]],
            created_by=manager,
            executor=spec["operator"],
            opened_at=opened_at,
            status=spec["status"],
            order_type=spec["type"],
            priority=spec["priority"],
            origin=spec["origin"],
            description=spec["description"],
            estimated_duration_hours=8 if spec["status"] != WorkOrderStatus.ABERTA else 6,
            note_prefix=f"[Ultima semana] {equipments_by_tag[spec['tag']].tag}:",
            transition_hour_offsets=spec["hours"],
        )
        work_orders.append(work_order)
    return work_orders


def create_historical_work_orders(
    db,
    rng: Random,
    specs_by_tag: dict[str, EquipmentSeed],
    equipments_by_tag: dict[str, Equipment],
    teams_by_name: dict[str, Team],
    users_by_username: dict[str, User],
    now: datetime,
) -> list[WorkOrder]:
    manager = users_by_username["taina"]
    operators_by_team = {
        "Administracao": users_by_username["otavio"],
        "Producao": users_by_username["michael"],
        "Expedicao": users_by_username["bruno"],
        "Manutencao": users_by_username["leonardo"],
        "Utilidades": users_by_username["murillo"],
    }
    all_orders: list[WorkOrder] = []

    for tag, equipment in equipments_by_tag.items():
        spec = specs_by_tag[tag]
        base_count = PROFILE_WORK_ORDER_COUNTS[spec.profile]
        team = teams_by_name[spec.team_name]
        operator = operators_by_team[spec.team_name]
        for index in range(base_count):
            opened_at = now - timedelta(days=165 - (index * max(12, 22 - base_count)))
            opened_at += timedelta(days=rng.uniform(-3, 3))
            status = WorkOrderStatus.CONCLUIDA if index < base_count - 1 else WorkOrderStatus.CANCELADA if spec.profile == "tranquilo" and base_count > 1 else WorkOrderStatus.CONCLUIDA
            order_type = WorkOrderType.CORRETIVA if spec.profile == "problematico" and index % 3 != 0 else WorkOrderType.PREVENTIVA
            priority = {
                "tranquilo": WorkOrderPriority.BAIXA,
                "intermediario": WorkOrderPriority.MEDIA if index < base_count - 1 else WorkOrderPriority.ALTA,
                "problematico": WorkOrderPriority.ALTA if index < base_count - 2 else WorkOrderPriority.CRITICA,
            }[spec.profile]
            description_pool = WORK_ORDER_DESCRIPTIONS[spec.profile]
            description = f"{description_pool[index % len(description_pool)]} Equipamento {tag}."
            transition_offsets = (rng.randint(3, 18), rng.randint(24, 72))

            work_order = create_work_order(
                db=db,
                equipment=equipment,
                team=team,
                created_by=manager,
                executor=operator,
                opened_at=opened_at,
                status=status,
                order_type=order_type,
                priority=priority,
                origin=WorkOrderOrigin.MANUAL if index % 2 == 0 else WorkOrderOrigin.SUGERIDA,
                description=description,
                estimated_duration_hours=rng.randint(4, 24),
                note_prefix=f"[Historico] {tag}:",
                transition_hour_offsets=transition_offsets,
            )
            all_orders.append(work_order)

    all_orders.extend(build_last_week_work_orders(db, equipments_by_tag, teams_by_name, users_by_username, now))
    db.flush()
    return all_orders


def seed_operational_history(
    db,
    teams_by_name: dict[str, Team],
    users_by_username: dict[str, User],
    equipments_by_tag: dict[str, Equipment],
) -> dict[str, int]:
    rng = Random(20260425)
    now = utc_now()
    specs_by_tag = {spec.tag: spec for spec in EQUIPMENT_SEEDS}
    team_authors = {
        "Administracao": users_by_username["otavio"],
        "Producao": users_by_username["michael"],
        "Expedicao": users_by_username["bruno"],
        "Manutencao": users_by_username["leonardo"],
        "Utilidades": users_by_username["murillo"],
    }

    counts = defaultdict(int)

    for tag, equipment in equipments_by_tag.items():
        spec = specs_by_tag[tag]
        author = team_authors[spec.team_name]

        measurements = create_measurement_events(db, rng, equipment, author, spec, now)
        counts["measurements"] += len(measurements)
        for measurement in measurements:
            if measurement_severity(equipment, measurement.value) in {AlertSeverity.MEDIA, AlertSeverity.ALTA, AlertSeverity.CRITICA}:
                if create_alert_for_measurement(db, equipment, measurement) is not None:
                    counts["alerts"] += 1

        occurrences = create_occurrence_events(db, rng, equipment, author, spec, now)
        counts["occurrences"] += len(occurrences)
        for occurrence in occurrences:
            if create_alert_for_occurrence(db, equipment, occurrence) is not None:
                counts["alerts"] += 1

    work_orders = create_historical_work_orders(db, rng, specs_by_tag, equipments_by_tag, teams_by_name, users_by_username, now)
    counts["work_orders"] += len(work_orders)
    counts["work_order_status_history"] = db.scalar(select(func.count(WorkOrderStatusHistory.id))) or 0

    return counts


def run(reset_operational: bool = False) -> None:
    init_db()
    db = SessionLocal()
    try:
        teams_by_name = ensure_teams(db)
        users_by_username = ensure_users(db, teams_by_name)
        equipments_by_tag = ensure_equipments(db, teams_by_name)
        db.commit()

        existing_history = db.scalar(select(func.count(Occurrence.id))) or 0
        if existing_history and not reset_operational:
            print("Seed base atualizado. Historico operacional ja existe; use --reset-operational para regenerar a massa de 6 meses.")
            print(f"Senha padrao dos usuarios: {DEFAULT_PASSWORD}")
            return

        if reset_operational:
            reset_operational_data(db)

        counts = seed_operational_history(db, teams_by_name, users_by_username, equipments_by_tag)
        db.commit()
        print("Seed operacional de 6 meses concluido com sucesso.")
        print(
            "Resumo: "
            f"{len(teams_by_name)} equipes, "
            f"{len(users_by_username)} usuarios, "
            f"{len(equipments_by_tag)} equipamentos, "
            f"{counts['occurrences']} ocorrencias, "
            f"{counts['measurements']} medicoes, "
            f"{counts['alerts']} alertas, "
            f"{counts['work_orders']} OS."
        )
        print(f"Senha padrao dos usuarios: {DEFAULT_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    args = parse_args()
    run(reset_operational=args.reset_operational)
