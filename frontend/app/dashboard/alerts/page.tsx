"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { fetchApi } from "@/lib/api";
import { canAccessAdminModules, getStoredSession } from "@/lib/auth";

type EquipmentSummary = {
  id: number;
  tag: string;
  name: string;
  sector: string;
  active: boolean;
  team_id: number | null;
};

type AlertRecord = {
  id: number;
  equipment_id: number;
  origin_type: "occurrence" | "measurement" | "system";
  origin_id: number | null;
  source: "rule" | "ai" | "hybrid";
  severity: "baixa" | "media" | "alta" | "critica";
  status: "aberto" | "revisado";
  title: string;
  message: string;
  recommendation: string | null;
  possible_cause: string | null;
  suggested_work_order: {
    suggested: boolean;
    type: "corretiva" | "preventiva" | null;
    priority: "baixa" | "media" | "alta" | "critica" | null;
  };
  event_at: string;
  created_at: string;
  updated_at: string;
  equipment: EquipmentSummary;
};

const severityLabels = {
  baixa: "Baixa",
  media: "Media",
  alta: "Alta",
  critica: "Critica",
} as const;

const sourceLabels = {
  rule: "Regra",
  ai: "IA",
  hybrid: "Hibrido",
} as const;

const statusLabels = {
  aberto: "Aberto",
  revisado: "Revisado",
} as const;

export default function AlertsPage() {
  const session = getStoredSession();
  const canManage = canAccessAdminModules(session?.user.role);

  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<AlertRecord | null>(null);
  const [severityFilter, setSeverityFilter] = useState("");
  const [sourceFilter, setSourceFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadAlerts() {
    setLoading(true);
    setError("");

    try {
      const query = new URLSearchParams();
      if (severityFilter) {
        query.set("severity", severityFilter);
      }
      if (sourceFilter) {
        query.set("source", sourceFilter);
      }
      if (statusFilter) {
        query.set("status_filter", statusFilter);
      }

      const suffix = query.size > 0 ? `?${query.toString()}` : "";
      const data = await fetchApi<AlertRecord[]>(`/alerts${suffix}`);
      setAlerts(data);
      setSelectedAlert((current) => data.find((item) => item.id === current?.id) ?? data[0] ?? null);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar alertas.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAlerts();
  }, []);

  const criticalSummary = useMemo(
    () => alerts.filter((alert) => alert.severity === "critica" && alert.status === "aberto").length,
    [alerts],
  );

  async function markAsReviewed() {
    if (!selectedAlert || !canManage) {
      return;
    }

    setReviewing(true);
    setError("");
    setMessage("");
    try {
      const reviewed = await fetchApi<AlertRecord>(`/alerts/${selectedAlert.id}/review`, { method: "POST" });
      setSelectedAlert(reviewed);
      setMessage("Alerta marcado como revisado.");
      await loadAlerts();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao revisar alerta.");
    } finally {
      setReviewing(false);
    }
  }

  return (
    <section className="stack-lg">
      <header className="panel stack">
        <p className="helper-text">Sprint 5.5</p>
        <h2 className="section-title">Alertas operacionais</h2>
        <p className="helper-text">
          Alertas por regra e IA ficam centralizados aqui para apoiar a avaliacao do risco e a decisao gerencial sobre
          abertura de OS.
        </p>
      </header>

      <section className="grid-layout">
        <article className="grid-card">
          <h2>Alertas ativos</h2>
          <p className="metric">{alerts.filter((alert) => alert.status === "aberto").length}</p>
          <p className="helper-text">Total de alertas ainda nao revisados na lista atual.</p>
        </article>
        <article className="grid-card">
          <h2>Criticos</h2>
          <p className="metric">{criticalSummary}</p>
          <p className="helper-text">Alertas criticos abertos merecem avaliacao prioritaria.</p>
        </article>
        <article className="grid-card">
          <h2>OS sugerida</h2>
          <p className="metric">{alerts.filter((alert) => alert.suggested_work_order.suggested).length}</p>
          <p className="helper-text">A abertura continua manual, mas agora pode partir direto do alerta.</p>
        </article>
      </section>

      <section className="module-grid">
        <article className="panel stack">
          <div className="toolbar-inline">
            <select className="input" onChange={(event) => setSeverityFilter(event.target.value)} value={severityFilter}>
              <option value="">Todas as severidades</option>
              <option value="baixa">Baixa</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
              <option value="critica">Critica</option>
            </select>

            <select className="input" onChange={(event) => setSourceFilter(event.target.value)} value={sourceFilter}>
              <option value="">Todas as origens</option>
              <option value="rule">Regra</option>
              <option value="hybrid">Hibrido</option>
              <option value="ai">IA</option>
            </select>

            <select className="input" onChange={(event) => setStatusFilter(event.target.value)} value={statusFilter}>
              <option value="">Todos os status</option>
              <option value="aberto">Aberto</option>
              <option value="revisado">Revisado</option>
            </select>

            <button className="secondary-button" onClick={() => void loadAlerts()} type="button">
              Filtrar
            </button>
          </div>

          {loading ? <p className="helper-text">Carregando alertas...</p> : null}
          {error ? <div className="error-box">{error}</div> : null}
          {message ? <div className="success-box">{message}</div> : null}

          <div className="table-list">
            {alerts.map((alert) => (
              <div
                className={`table-row ${alert.severity === "critica" ? "table-row-danger" : ""}`}
                key={alert.id}
              >
                <div className="stack-sm">
                  <div className="toolbar-inline">
                    <span className={`status-pill severity-${alert.severity}`}>{severityLabels[alert.severity]}</span>
                    <span className="status-pill">{sourceLabels[alert.source]}</span>
                    <span className={`status-pill alert-status-${alert.status}`}>{statusLabels[alert.status]}</span>
                  </div>
                  <strong>{alert.title}</strong>
                  <p className="helper-text">
                    {alert.equipment.tag} | evento em {new Date(alert.event_at).toLocaleString("pt-BR")}
                  </p>
                  <p>{alert.message}</p>
                </div>
                <div className="row-actions">
                  <button className="secondary-button inline-button" onClick={() => setSelectedAlert(alert)} type="button">
                    Detalhar
                  </button>
                </div>
              </div>
            ))}

            {!loading && alerts.length === 0 ? (
              <div className="detail-box">
                <p className="helper-text">Nenhum alerta encontrado com os filtros atuais.</p>
              </div>
            ) : null}
          </div>
        </article>

        <article className="panel stack measurements-form-panel">
          {selectedAlert ? (
            <>
              <div className="stack-sm">
                <h3 className="section-title">Alerta #{selectedAlert.id}</h3>
                <p className="helper-text">
                  {selectedAlert.equipment.tag} - {selectedAlert.equipment.name}
                </p>
                <div className="toolbar-inline">
                  <span className={`status-pill severity-${selectedAlert.severity}`}>
                    {severityLabels[selectedAlert.severity]}
                  </span>
                  <span className="status-pill">{sourceLabels[selectedAlert.source]}</span>
                  <span className={`status-pill alert-status-${selectedAlert.status}`}>
                    {statusLabels[selectedAlert.status]}
                  </span>
                </div>
              </div>

              <div className="detail-box stack">
                <p>{selectedAlert.message}</p>
                <p className="helper-text">
                  Origem: {selectedAlert.origin_type}
                  {selectedAlert.origin_id ? ` #${selectedAlert.origin_id}` : ""}
                </p>
                {selectedAlert.possible_cause ? (
                  <p>
                    <strong>Possivel causa:</strong> {selectedAlert.possible_cause}
                  </p>
                ) : null}
                {selectedAlert.recommendation ? (
                  <p>
                    <strong>Recomendacao:</strong> {selectedAlert.recommendation}
                  </p>
                ) : null}
                {selectedAlert.suggested_work_order.suggested ? (
                  <p>
                    <strong>Sugestao de OS:</strong> {selectedAlert.suggested_work_order.type ?? "corretiva"} com
                    prioridade {selectedAlert.suggested_work_order.priority ?? "alta"}.
                  </p>
                ) : (
                  <p className="helper-text">Este alerta nao trouxe sugestao de abertura de OS.</p>
                )}
              </div>

              {canManage && selectedAlert.status === "aberto" ? (
                <div className="row-actions">
                  <button className="primary-button" disabled={reviewing} onClick={() => void markAsReviewed()} type="button">
                    {reviewing ? "Revisando..." : "Marcar como revisado"}
                  </button>
                  {selectedAlert.suggested_work_order.suggested && selectedAlert.equipment.team_id ? (
                    <Link className="secondary-button inline-button" href={`/dashboard/work-orders?alert_id=${selectedAlert.id}`}>
                      Abrir OS manualmente
                    </Link>
                  ) : null}
                </div>
              ) : null}
            </>
          ) : (
            <div className="detail-box">
              <p className="helper-text">Selecione um alerta para ver detalhes e recomendacoes.</p>
            </div>
          )}
        </article>
      </section>
    </section>
  );
}
