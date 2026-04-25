from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from urllib import error, request

from app.core.config import settings
from app.schemas.dashboard import (
    DashboardAnalyticalReading,
    DashboardKpis,
    DashboardTrendHotSpotItem,
    DashboardTrendReading,
    EquipmentRankingItem,
    MaintenanceTypeReportItem,
    TeamReportItem,
)

ANALYTICS_MODEL = "gpt-5.4-mini"
ANALYTICS_DISCLAIMER = (
    "Leitura analitica assistida por IA para apoio gerencial. Nao substitui decisao humana nem aciona manutencao automaticamente."
)
TREND_DISCLAIMER = (
    "Analise de tendencias assistida por IA com carater consultivo. Indica sinais de monitoramento e priorizacao, sem prever falha de forma deterministica."
)


def build_dashboard_analytical_reading(
    *,
    scope: str,
    team_name: str | None,
    period_days: int,
    filters: dict[str, int | str | None],
    kpis: DashboardKpis,
    occurrences_by_equipment: list[EquipmentRankingItem],
    work_orders_by_team: list[TeamReportItem],
    work_orders_by_type: list[MaintenanceTypeReportItem],
) -> DashboardAnalyticalReading:
    payload = _build_analytics_payload(
        scope=scope,
        team_name=team_name,
        period_days=period_days,
        filters=filters,
        kpis=kpis,
        occurrences_by_equipment=occurrences_by_equipment,
        work_orders_by_team=work_orders_by_team,
        work_orders_by_type=work_orders_by_type,
    )
    ai_reading = _get_ai_reading(payload)
    if ai_reading is not None:
        return DashboardAnalyticalReading(
            source="ai",
            model=ANALYTICS_MODEL,
            generated_at=datetime.now(timezone.utc),
            disclaimer=ANALYTICS_DISCLAIMER,
            summary=ai_reading["summary"],
            attention_points=ai_reading["attention_points"],
            patterns=ai_reading["patterns"],
            recommendations=ai_reading["recommendations"],
            based_on=payload["meta"],
        )

    fallback = _build_fallback_reading(payload)
    return DashboardAnalyticalReading(
        source="fallback",
        model=None,
        generated_at=datetime.now(timezone.utc),
        disclaimer=ANALYTICS_DISCLAIMER,
        summary=fallback["summary"],
        attention_points=fallback["attention_points"],
        patterns=fallback["patterns"],
        recommendations=fallback["recommendations"],
        based_on=payload["meta"],
    )


def _build_analytics_payload(
    *,
    scope: str,
    team_name: str | None,
    period_days: int,
    filters: dict[str, int | str | None],
    kpis: DashboardKpis,
    occurrences_by_equipment: list[EquipmentRankingItem],
    work_orders_by_team: list[TeamReportItem],
    work_orders_by_type: list[MaintenanceTypeReportItem],
) -> dict[str, Any]:
    return {
        "meta": {
            "scope": scope,
            "team_name": team_name,
            "period_days": period_days,
            "equipment_id": filters.get("equipment_id"),
            "team_id": filters.get("team_id"),
            "maintenance_type": filters.get("maintenance_type"),
        },
        "kpis": kpis.model_dump(),
        "top_occurrences": [item.model_dump() for item in occurrences_by_equipment[:3]],
        "team_workload": [item.model_dump() for item in work_orders_by_team[:3]],
        "maintenance_mix": [item.model_dump() for item in work_orders_by_type],
    }


def _get_ai_reading(payload: dict[str, Any]) -> dict[str, Any] | None:
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "attention_points": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
            },
            "patterns": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
            },
        },
        "required": ["summary", "attention_points", "patterns", "recommendations"],
        "additionalProperties": False,
    }
    parsed = _request_openai_json(
        schema_name="dashboard_analytical_reading",
        developer_text=(
            "Voce analisa dados consolidados de manutencao industrial. "
            "Responda apenas com JSON valido, sem markdown, em portugues do Brasil, "
            "curto, objetivo e ancorado nos numeros recebidos. "
            "Nao afirme previsao deterministica nem automatize decisao critica."
        ),
        payload=payload,
        schema=schema,
    )
    if not _is_valid_ai_reading(parsed):
        return None
    return parsed


def build_dashboard_trend_reading(
    *,
    scope: str,
    team_name: str | None,
    analysis_scope: str,
    window: str,
    equipment_id: int | None,
    sector: str | None,
    maintenance_type: str | None,
    totals: dict[str, int | float | None],
    hot_spots: list[dict[str, Any]],
) -> DashboardTrendReading:
    payload = {
        "meta": {
            "scope": scope,
            "team_name": team_name,
            "analysis_scope": analysis_scope,
            "window": window,
            "equipment_id": equipment_id,
            "sector": sector,
            "maintenance_type": maintenance_type,
        },
        "totals": totals,
        "hot_spots": hot_spots[:5],
    }

    ai_reading = _get_ai_trend_reading(payload)
    if ai_reading is not None:
        return DashboardTrendReading(
            source="ai",
            model=ANALYTICS_MODEL,
            generated_at=datetime.now(timezone.utc),
            disclaimer=TREND_DISCLAIMER,
            analysis_scope=analysis_scope,
            window=window,
            classification=ai_reading["classification"],
            executive_reading=ai_reading["executive_reading"],
            technical_reading=ai_reading["technical_reading"],
            recommendations=ai_reading["recommendations"],
            based_on=payload["meta"],
            totals=totals,
            hot_spots=[DashboardTrendHotSpotItem.model_validate(item) for item in hot_spots[:5]],
        )

    fallback = _build_fallback_trend_reading(payload)
    return DashboardTrendReading(
        source="fallback",
        model=None,
        generated_at=datetime.now(timezone.utc),
        disclaimer=TREND_DISCLAIMER,
        analysis_scope=analysis_scope,
        window=window,
        classification=fallback["classification"],
        executive_reading=fallback["executive_reading"],
        technical_reading=fallback["technical_reading"],
        recommendations=fallback["recommendations"],
        based_on=payload["meta"],
        totals=totals,
        hot_spots=[DashboardTrendHotSpotItem.model_validate(item) for item in hot_spots[:5]],
    )


def _get_ai_trend_reading(payload: dict[str, Any]) -> dict[str, Any] | None:
    schema = {
        "type": "object",
        "properties": {
            "classification": {"type": "string"},
            "executive_reading": {"type": "string"},
            "technical_reading": {"type": "string"},
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
            },
        },
        "required": ["classification", "executive_reading", "technical_reading", "recommendations"],
        "additionalProperties": False,
    }
    parsed = _request_openai_json(
        schema_name="dashboard_trend_reading",
        developer_text=(
            "Voce analisa tendencias operacionais de manutencao industrial. "
            "Classifique o contexto apenas como normal, monitorar ou intervir. "
            "Responda em portugues do Brasil, sem markdown, com leitura executiva e tecnica curtas, "
            "sempre ancoradas nos numeros recebidos. "
            "Nao prometa previsao certa de falha e deixe implícito que se trata de apoio a decisao."
        ),
        payload=payload,
        schema=schema,
    )
    if not isinstance(parsed, dict):
        return None
    if parsed.get("classification") not in {"normal", "monitorar", "intervir"}:
        return None
    if not isinstance(parsed.get("executive_reading"), str) or not parsed["executive_reading"].strip():
        return None
    if not isinstance(parsed.get("technical_reading"), str) or not parsed["technical_reading"].strip():
        return None
    recommendations = parsed.get("recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        return None
    if any(not isinstance(item, str) or not item.strip() for item in recommendations):
        return None
    return parsed


def _request_openai_json(
    *,
    schema_name: str,
    developer_text: str,
    payload: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any] | None:
    if not settings.openai_api_key.strip():
        return None

    request_payload = {
        "model": ANALYTICS_MODEL,
        "input": [
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": developer_text,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(payload, ensure_ascii=True),
                    }
                ],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": schema,
            }
        },
    }

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=20) as response:
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
    return parsed


def _is_valid_ai_reading(parsed: Any) -> bool:
    if not isinstance(parsed, dict):
        return False

    for key in ("summary", "attention_points", "patterns", "recommendations"):
        if key not in parsed:
            return False

    if not isinstance(parsed["summary"], str) or not parsed["summary"].strip():
        return False

    for key in ("attention_points", "patterns", "recommendations"):
        value = parsed[key]
        if not isinstance(value, list) or not value:
            return False
        if any(not isinstance(item, str) or not item.strip() for item in value):
            return False

    return True


def _build_fallback_reading(payload: dict[str, Any]) -> dict[str, Any]:
    kpis = payload["kpis"]
    top_occurrences = payload["top_occurrences"]
    team_workload = payload["team_workload"]
    maintenance_mix = payload["maintenance_mix"]
    period_days = payload["meta"]["period_days"]

    top_equipment = top_occurrences[0] if top_occurrences else None
    busiest_team = team_workload[0] if team_workload else None
    corrective_share = next((item["percentage"] for item in maintenance_mix if item["type"] == "corretiva"), 0)
    preventive_share = next((item["percentage"] for item in maintenance_mix if item["type"] == "preventiva"), 0)

    summary_parts = [
        f"Analise consolidada dos ultimos {period_days} dias com {kpis['total_occurrences']} ocorrencia(s)",
        f"{kpis['open_work_orders']} OS em aberto e {kpis['open_alerts']} alerta(s) ainda aberto(s)",
    ]
    if top_equipment is not None:
        summary_parts.append(
            f"maior concentracao de ocorrencias no equipamento {top_equipment['equipment_tag']} - {top_equipment['equipment_name']}"
        )
    summary = ". ".join(summary_parts) + "."

    attention_points = [
        f"Backlog atual em {kpis['work_order_backlog']} OS, exigindo priorizacao operacional."
    ]
    if top_equipment is not None:
        attention_points.append(
            f"{top_equipment['equipment_tag']} soma {top_equipment['occurrences']} ocorrencia(s), {top_equipment['alerts']} alerta(s) e {top_equipment['open_work_orders']} OS aberta(s)."
        )
    else:
        attention_points.append("Nao houve recorrencia suficiente por equipamento para destacar concentracao de falhas.")
    if kpis["mean_resolution_hours"] is not None:
        attention_points.append(
            f"O tempo medio de resolucao esta em {kpis['mean_resolution_hours']}h no recorte analisado."
        )
    else:
        attention_points.append("Ainda nao ha base concluida suficiente para calcular o tempo medio de resolucao.")

    patterns = []
    if corrective_share > preventive_share:
        patterns.append(
            f"O mix esta mais reativo, com {corrective_share}% de OS corretivas contra {preventive_share}% preventivas."
        )
    else:
        patterns.append(
            f"O mix mostra maior equilibrio preventivo, com {preventive_share}% preventivas contra {corrective_share}% corretivas."
        )
    if busiest_team is not None:
        patterns.append(
            f"A maior carga de atendimento esta com a equipe {busiest_team['team_name']}, com {busiest_team['work_orders']} OS no periodo."
        )
    else:
        patterns.append("Nao houve volume suficiente para destacar concentracao de carga por equipe.")
    patterns.append(
        f"Foram revisados {kpis['reviewed_alerts']} alerta(s), mantendo o fluxo de avaliacao humana sobre os sinais operacionais."
    )

    recommendations = [
        "Priorizar verificacao dos equipamentos com maior recorrencia antes de ampliar novas intervencoes.",
        "Usar esta leitura como apoio gerencial e confirmar em campo qualquer decisao de manutencao.",
    ]
    if corrective_share >= 60:
        recommendations.append("Revisar plano preventivo dos ativos mais reincidentes para reduzir atuacao corretiva recorrente.")
    else:
        recommendations.append("Manter acompanhamento do mix preventivo para evitar retorno do backlog corretivo.")
    if kpis["open_alerts"] > 0:
        recommendations.append("Concluir a triagem dos alertas ainda abertos para evitar acumulacao de risco sem revisao.")
    else:
        recommendations.append("Preservar o ritmo de revisao gerencial, mesmo com baixo volume de alertas em aberto.")

    return {
        "summary": summary,
        "attention_points": attention_points[:3],
        "patterns": patterns[:3],
        "recommendations": recommendations[:4],
    }


def _build_fallback_trend_reading(payload: dict[str, Any]) -> dict[str, Any]:
    totals = payload["totals"]
    hot_spots = payload["hot_spots"]
    analysis_scope = payload["meta"]["analysis_scope"]
    window = payload["meta"]["window"]

    primary_hot_spot = hot_spots[0] if hot_spots else None
    score = 0
    if totals["occurrences"] >= 4:
        score += 1
    if totals["open_alerts"] > 0:
        score += 1
    if totals["open_work_orders"] >= max(2, totals["completed_work_orders"]):
        score += 1
    if totals["corrective_percentage"] is not None and totals["corrective_percentage"] >= 60:
        score += 1
    if primary_hot_spot is not None and (
        primary_hot_spot["trend_direction"] == "subindo" or primary_hot_spot["open_work_orders"] >= 2
    ):
        score += 1

    classification = "normal"
    if score >= 4:
        classification = "intervir"
    elif score >= 2:
        classification = "monitorar"

    focus_label = "equipamentos" if analysis_scope == "equipment" else "setores"
    summary = (
        f"Leitura executiva para janela {window}: o recorte de {focus_label} mostra "
        f"{totals['occurrences']} ocorrencia(s), {totals['alerts']} alerta(s) e {totals['open_work_orders']} OS em aberto, "
        f"classificando o contexto como {classification}."
    )

    technical_parts = [
        f"O mix atual de manutencao esta em {totals['corrective_percentage']}% corretiva e {totals['preventive_percentage']}% preventiva."
    ]
    if primary_hot_spot is not None:
        technical_parts.append(
            f"O principal foco do recorte e {primary_hot_spot['label']}, com {primary_hot_spot['occurrences']} ocorrencia(s), "
            f"{primary_hot_spot['alerts']} alerta(s) e tendencia {primary_hot_spot['trend_direction']}."
        )
    technical_parts.append(
        f"Alertas abertos: {totals['open_alerts']}; alertas revisados: {totals['reviewed_alerts']}; OS concluidas: {totals['completed_work_orders']}."
    )

    recommendations = [
        "Tratar esta classificacao como apoio gerencial e confirmar em campo os sinais mais concentrados.",
        "Priorizar o acompanhamento dos focos com maior recorrencia antes de ampliar novas acoes corretivas.",
    ]
    if classification == "intervir":
        recommendations.append("Planejar inspecao priorizada no foco mais recorrente e revisar backlog pendente do recorte.")
    elif classification == "monitorar":
        recommendations.append("Acompanhar a evolucao do recorte na proxima janela para confirmar se o sinal esta se consolidando.")
    else:
        recommendations.append("Manter monitoramento de rotina e preservar o equilibrio entre manutencao preventiva e corretiva.")

    return {
        "classification": classification,
        "executive_reading": summary,
        "technical_reading": " ".join(technical_parts),
        "recommendations": recommendations[:4],
    }
