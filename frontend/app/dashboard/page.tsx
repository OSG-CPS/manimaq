"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchApi } from "@/lib/api";
import { canAccessAdminModules, getStoredSession } from "@/lib/auth";

type DashboardOverview = {
  scope: "global" | "team";
  team_id: number | null;
  team_name: string | null;
  period_days: number;
  generated_at: string;
  kpis: {
    open_work_orders: number;
    completed_work_orders: number;
    work_order_backlog: number;
    corrective_work_orders: number;
    preventive_work_orders: number;
    corrective_percentage: number;
    preventive_percentage: number;
    mean_resolution_hours: number | null;
    total_occurrences: number;
    open_alerts: number;
    reviewed_alerts: number;
  };
  top_failure_equipments: Array<{
    equipment_id: number;
    equipment_tag: string;
    equipment_name: string;
    occurrences: number;
    open_work_orders: number;
    alerts: number;
  }>;
  work_orders_by_team: Array<{
    team_id: number;
    team_name: string;
    sector: string;
    work_orders: number;
    open_work_orders: number;
    completed_work_orders: number;
  }>;
  work_orders_by_type: Array<{
    type: "corretiva" | "preventiva";
    total: number;
    percentage: number;
  }>;
};

export default function DashboardPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [periodDays, setPeriodDays] = useState("30");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const session = getStoredSession();
  const canManage = canAccessAdminModules(session?.user.role);
  const meanResolutionHours = overview?.kpis.mean_resolution_hours;

  useEffect(() => {
    async function loadOverview() {
      setLoading(true);
      try {
        const data = await fetchApi<DashboardOverview>(`/dashboard/overview?period_days=${periodDays}`);
        setOverview(data);
        setError("");
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao carregar a area autenticada.");
      } finally {
        setLoading(false);
      }
    }

    void loadOverview();
  }, [periodDays]);

  return (
    <section className="stack-lg">
      <header className="panel stack">
        <div className="toolbar-inline toolbar-wrap">
          <div className="stack">
            <p className="helper-text">Sprint 6</p>
            <h2 className="section-title">Dashboard operacional</h2>
            <p className="helper-text">
              {overview
                ? `Indicadores reais dos ultimos ${overview.period_days} dia(s) para ${overview.scope === "global" ? "gestao geral" : `a equipe ${overview.team_name ?? "vinculada"}`}.`
                : "Carregando indicadores consolidados do MVP..."}
            </p>
          </div>
          <label className="label dashboard-filter">
            Periodo
            <select className="input" onChange={(event) => setPeriodDays(event.target.value)} value={periodDays}>
              <option value="7">7 dias</option>
              <option value="30">30 dias</option>
              <option value="90">90 dias</option>
              <option value="365">365 dias</option>
            </select>
          </label>
        </div>
        {error ? <div className="error-box">{error}</div> : null}
      </header>

      <section className="grid-layout">
        <article className="grid-card">
          <h2>OS abertas</h2>
          <p className="metric">{loading ? "..." : overview?.kpis.open_work_orders ?? 0}</p>
          <p className="helper-text">Inclui OS abertas e em execucao que ainda compoem o backlog operacional.</p>
        </article>

        <article className="grid-card">
          <h2>OS concluidas</h2>
          <p className="metric">{loading ? "..." : overview?.kpis.completed_work_orders ?? 0}</p>
          <p className="helper-text">Atendimentos finalizados dentro do periodo consultado.</p>
        </article>

        <article className="grid-card">
          <h2>Ocorrencias</h2>
          <p className="metric">{loading ? "..." : overview?.kpis.total_occurrences ?? 0}</p>
          <p className="helper-text">Eventos operacionais reais usados como base do ranking de recorrencia.</p>
        </article>

        <article className="grid-card">
          <h2>TMA</h2>
          <p className="metric">{loading ? "..." : meanResolutionHours !== null && meanResolutionHours !== undefined ? `${meanResolutionHours}h` : "--"}</p>
          <p className="helper-text">Tempo medio entre abertura e conclusao das OS finalizadas.</p>
        </article>
      </section>

      <section className="stats-strip">
        <article className="panel stack-sm">
          <p className="helper-text">Backlog</p>
          <p className="metric-inline">{overview?.kpis.work_order_backlog ?? 0} OS</p>
        </article>
        <article className="panel stack-sm">
          <p className="helper-text">Corretiva vs preventiva</p>
          <p className="metric-inline">
            {overview ? `${overview.kpis.corrective_percentage}% / ${overview.kpis.preventive_percentage}%` : "--"}
          </p>
        </article>
        <article className="panel stack-sm">
          <p className="helper-text">Alertas abertos vs revisados</p>
          <p className="metric-inline">
            {overview ? `${overview.kpis.open_alerts} / ${overview.kpis.reviewed_alerts}` : "--"}
          </p>
        </article>
        <article className="panel stack-sm">
          <p className="helper-text">Perfil atual</p>
          <p className="metric-inline">{session?.user.role ?? "--"}</p>
        </article>
      </section>

      <section className="report-grid">
        <article className="panel stack">
          <div className="stack-sm">
            <h3 className="section-title">Equipamentos com maior recorrencia</h3>
            <p className="helper-text">Ranking por quantidade de ocorrencias no periodo selecionado.</p>
          </div>
          <div className="table-list">
            {overview?.top_failure_equipments.length ? (
              overview.top_failure_equipments.map((item) => (
                <div className="table-row" key={item.equipment_id}>
                  <div className="stack-sm">
                    <strong>
                      {item.equipment_tag} - {item.equipment_name}
                    </strong>
                    <p className="helper-text">
                      {item.occurrences} ocorrencia(s) | {item.alerts} alerta(s) | {item.open_work_orders} OS aberta(s)
                    </p>
                  </div>
                  <Link className="secondary-button inline-button" href={`/dashboard/history?equipment_id=${item.equipment_id}`}>
                    Historico
                  </Link>
                </div>
              ))
            ) : (
              <div className="detail-box">
                <p className="helper-text">Nenhuma ocorrencia encontrada neste periodo.</p>
              </div>
            )}
          </div>
        </article>

        <article className="panel stack">
          <div className="stack-sm">
            <h3 className="section-title">Distribuicao por equipe</h3>
            <p className="helper-text">Carga total, backlog e concluido por equipe no periodo.</p>
          </div>
          <div className="table-list">
            {overview?.work_orders_by_team.length ? (
              overview.work_orders_by_team.map((item) => (
                <div className="table-row" key={item.team_id}>
                  <div className="stack-sm">
                    <strong>{item.team_name}</strong>
                    <p className="helper-text">{item.sector}</p>
                  </div>
                  <div className="stack-sm align-end">
                    <span className="metric-inline">{item.work_orders} OS</span>
                    <p className="helper-text">
                      {item.open_work_orders} abertas | {item.completed_work_orders} concluidas
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="detail-box">
                <p className="helper-text">Nenhuma OS encontrada neste periodo.</p>
              </div>
            )}
          </div>
        </article>
      </section>

      <section className="grid-layout">
        <Link className="grid-card card-link" href="/dashboard/alerts">
          <h2>Alertas</h2>
          <p className="helper-text">Consultar alertas por regra e enriquecimento de IA com sugestao de OS.</p>
        </Link>
        <Link className="grid-card card-link" href="/dashboard/reports">
          <h2>Relatorios</h2>
          <p className="helper-text">Consultar filtros por periodo, equipamento, equipe e tipo de manutencao.</p>
        </Link>
        <Link className="grid-card card-link" href="/dashboard/work-orders">
          <h2>Ordens de Servico</h2>
          <p className="helper-text">Abrir OS, acompanhar fila da equipe e registrar execucao e conclusao.</p>
        </Link>
        <Link className="grid-card card-link" href="/dashboard/occurrences">
          <h2>Ocorrencias</h2>
          <p className="helper-text">Registrar falhas, risco a seguranca e parada de producao.</p>
        </Link>
        <Link className="grid-card card-link" href="/dashboard/measurements">
          <h2>Medicoes</h2>
          <p className="helper-text">Lancar vibracao, temperatura, tensao e corrente.</p>
        </Link>
        <Link className="grid-card card-link" href="/dashboard/history">
          <h2>Historico</h2>
          <p className="helper-text">Consultar a linha do tempo operacional de cada equipamento.</p>
        </Link>
      </section>

      {canManage ? (
        <section className="grid-layout">
          <Link className="grid-card card-link" href="/dashboard/teams">
            <h2>Equipes</h2>
            <p className="helper-text">Criar, editar, listar e inativar equipes.</p>
          </Link>
          <Link className="grid-card card-link" href="/dashboard/equipments">
            <h2>Equipamentos</h2>
            <p className="helper-text">Gerenciar TAG, setor, criticidade e vinculacao.</p>
          </Link>
          <Link className="grid-card card-link" href="/dashboard/users">
            <h2>Usuarios</h2>
            <p className="helper-text">Criar, editar, listar e desativar usuarios.</p>
          </Link>
        </section>
      ) : null}
    </section>
  );
}
