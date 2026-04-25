"use client";

import { useEffect, useState } from "react";

import { fetchApi } from "@/lib/api";
import { canAccessAdminModules, getStoredSession } from "@/lib/auth";

type EquipmentOption = {
  id: number;
  tag: string;
  name: string;
  sector: string;
  active: boolean;
  team_id: number | null;
};

type TeamOption = {
  id: number;
  name: string;
  sector: string;
  active: boolean;
};

type DashboardTrend = {
  scope: "global" | "team";
  team_id: number | null;
  team_name: string | null;
  generated_at: string;
  filters: {
    analysis_scope: "equipment" | "sector";
    window: "7" | "30" | "total";
    equipment_id: number | null;
    sector: string | null;
    maintenance_type: "corretiva" | "preventiva" | null;
  };
  trend_reading: {
    source: "ai" | "fallback";
    model: string | null;
    generated_at: string;
    disclaimer: string;
    analysis_scope: "equipment" | "sector";
    window: "7" | "30" | "total";
    classification: "normal" | "monitorar" | "intervir";
    executive_reading: string;
    technical_reading: string;
    recommendations: string[];
    based_on: {
      scope: string;
      team_name: string | null;
      analysis_scope: "equipment" | "sector";
      window: "7" | "30" | "total";
      equipment_id: number | null;
      sector: string | null;
      maintenance_type: "corretiva" | "preventiva" | null;
    };
    totals: {
      occurrences: number;
      alerts: number;
      open_alerts: number;
      reviewed_alerts: number;
      open_work_orders: number;
      completed_work_orders: number;
      corrective_percentage: number;
      preventive_percentage: number;
      mean_resolution_hours: number | null;
    };
    hot_spots: Array<{
      label: string;
      scope: "equipment" | "sector";
      occurrences: number;
      alerts: number;
      open_alerts: number;
      open_work_orders: number;
      completed_work_orders: number;
      trend_direction: "subindo" | "reduzindo" | "estavel";
    }>;
  };
};

type DashboardReport = {
  scope: "global" | "team";
  team_id: number | null;
  team_name: string | null;
  period_days: number;
  generated_at: string;
  filters: {
    equipment_id: number | null;
    team_id: number | null;
    maintenance_type: "corretiva" | "preventiva" | null;
  };
  kpis: {
    open_work_orders: number;
    completed_work_orders: number;
    work_order_backlog: number;
    corrective_percentage: number;
    preventive_percentage: number;
    mean_resolution_hours: number | null;
    total_occurrences: number;
    open_alerts: number;
    reviewed_alerts: number;
  };
  occurrences_by_equipment: Array<{
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
  analytical_reading: {
    source: "ai" | "fallback";
    model: string | null;
    generated_at: string;
    disclaimer: string;
    summary: string;
    attention_points: string[];
    patterns: string[];
    recommendations: string[];
    based_on: {
      scope: string;
      team_name: string | null;
      period_days: number;
      equipment_id: number | null;
      team_id: number | null;
      maintenance_type: "corretiva" | "preventiva" | null;
    };
  };
};

export default function ReportsPage() {
  const session = getStoredSession();
  const canManage = canAccessAdminModules(session?.user.role);
  const [equipments, setEquipments] = useState<EquipmentOption[]>([]);
  const [teams, setTeams] = useState<TeamOption[]>([]);
  const [report, setReport] = useState<DashboardReport | null>(null);
  const [trend, setTrend] = useState<DashboardTrend | null>(null);
  const [periodDays, setPeriodDays] = useState("30");
  const [equipmentId, setEquipmentId] = useState("");
  const [teamId, setTeamId] = useState("");
  const [maintenanceType, setMaintenanceType] = useState("");
  const [trendScope, setTrendScope] = useState<"equipment" | "sector">("equipment");
  const [trendWindow, setTrendWindow] = useState<"7" | "30" | "total">("30");
  const [trendSector, setTrendSector] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const sectors = Array.from(new Set([...equipments.map((item) => item.sector), ...teams.map((item) => item.sector)])).filter(
    Boolean,
  );

  async function loadCatalogs() {
    const [equipmentData, teamData] = await Promise.all([
      fetchApi<EquipmentOption[]>("/equipment-history/catalog"),
      canManage ? fetchApi<TeamOption[]>("/teams") : Promise.resolve([]),
    ]);
    setEquipments(equipmentData);
    setTeams(teamData.filter((team) => team.active));
  }

  async function loadReport() {
    setLoading(true);
    setError("");
    try {
      const reportQuery = new URLSearchParams();
      reportQuery.set("period_days", periodDays);
      if (equipmentId) {
        reportQuery.set("equipment_id", equipmentId);
      }
      if (teamId && canManage) {
        reportQuery.set("team_id", teamId);
      }
      if (maintenanceType) {
        reportQuery.set("maintenance_type", maintenanceType);
      }
      const trendQuery = new URLSearchParams();
      trendQuery.set("analysis_scope", trendScope);
      trendQuery.set("window", trendWindow);
      if (maintenanceType) {
        trendQuery.set("maintenance_type", maintenanceType);
      }
      if (trendScope === "equipment" && equipmentId) {
        trendQuery.set("equipment_id", equipmentId);
      }
      if (trendScope === "sector" && trendSector) {
        trendQuery.set("sector", trendSector);
      }

      const [reportData, trendData] = await Promise.all([
        fetchApi<DashboardReport>(`/dashboard/reports?${reportQuery.toString()}`),
        fetchApi<DashboardTrend>(`/dashboard/trends?${trendQuery.toString()}`),
      ]);
      setReport(reportData);
      setTrend(trendData);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar relatorios.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        await loadCatalogs();
        await loadReport();
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao preparar a pagina de relatorios.");
        setLoading(false);
      }
    }

    void bootstrap();
  }, []);

  return (
    <section className="stack-lg">
      <header className="panel stack">
        <p className="helper-text">Sprint 7.5</p>
        <h2 className="section-title">Relatorios analiticos</h2>
        <p className="helper-text">
          Consolidados auditaveis com leitura assistida e relatorio de tendencias por equipamento ou setor.
        </p>
      </header>

      <article className="panel stack">
        <div className="filters-grid">
          <label className="label">
            Periodo
            <select className="input" onChange={(event) => setPeriodDays(event.target.value)} value={periodDays}>
              <option value="7">7 dias</option>
              <option value="30">30 dias</option>
              <option value="90">90 dias</option>
              <option value="365">365 dias</option>
            </select>
          </label>

          <label className="label">
            Equipamento
            <select className="input" onChange={(event) => setEquipmentId(event.target.value)} value={equipmentId}>
              <option value="">Todos</option>
              {equipments.map((equipment) => (
                <option key={equipment.id} value={equipment.id}>
                  {equipment.tag} - {equipment.name}
                </option>
              ))}
            </select>
          </label>

          {canManage ? (
            <label className="label">
              Equipe
              <select className="input" onChange={(event) => setTeamId(event.target.value)} value={teamId}>
                <option value="">Todas</option>
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name} - {team.sector}
                  </option>
                ))}
              </select>
            </label>
          ) : null}

          <label className="label">
            Tipo de manutencao
            <select className="input" onChange={(event) => setMaintenanceType(event.target.value)} value={maintenanceType}>
              <option value="">Todos</option>
              <option value="corretiva">Corretiva</option>
              <option value="preventiva">Preventiva</option>
            </select>
          </label>
        </div>

        <div className="toolbar-inline">
          <button className="primary-button" onClick={() => void loadReport()} type="button">
            Aplicar filtros
          </button>
          <button
            className="secondary-button"
            onClick={() => {
              setPeriodDays("30");
              setEquipmentId("");
              setTeamId("");
              setMaintenanceType("");
              setTrendScope("equipment");
              setTrendWindow("30");
              setTrendSector("");
            }}
            type="button"
          >
            Limpar selecao
          </button>
        </div>

        {error ? <div className="error-box">{error}</div> : null}
      </article>

      <section className="grid-layout">
        <article className="grid-card">
          <h2>Backlog</h2>
          <p className="metric">{loading ? "..." : report?.kpis.work_order_backlog ?? 0}</p>
          <p className="helper-text">OS ainda pendentes no recorte filtrado.</p>
        </article>
        <article className="grid-card">
          <h2>Concluidas</h2>
          <p className="metric">{loading ? "..." : report?.kpis.completed_work_orders ?? 0}</p>
          <p className="helper-text">OS finalizadas dentro do recorte atual.</p>
        </article>
        <article className="grid-card">
          <h2>Corretiva / Preventiva</h2>
          <p className="metric-inline">
            {loading ? "..." : report ? `${report.kpis.corrective_percentage}% / ${report.kpis.preventive_percentage}%` : "--"}
          </p>
          <p className="helper-text">Percentual por tipo de manutencao no periodo filtrado.</p>
        </article>
        <article className="grid-card">
          <h2>TMA</h2>
          <p className="metric">{loading ? "..." : report?.kpis.mean_resolution_hours !== null ? `${report?.kpis.mean_resolution_hours}h` : "--"}</p>
          <p className="helper-text">Media de horas entre abertura e conclusao.</p>
        </article>
      </section>

      <section className="report-grid">
        <article className="panel stack">
          <div className="stack-sm">
            <div className="toolbar-inline toolbar-wrap">
              <div className="stack-sm">
                <h3 className="section-title">Analise de tendencias</h3>
                <p className="helper-text">
                  Leitura executiva e tecnica por {trendScope === "equipment" ? "equipamento" : "setor"} na janela selecionada.
                </p>
              </div>
              <span
                className={
                  trend?.trend_reading.classification === "intervir"
                    ? "status-pill severity-critica"
                    : trend?.trend_reading.classification === "monitorar"
                      ? "status-pill severity-media"
                      : "status-pill"
                }
              >
                {loading ? "Analisando..." : trend?.trend_reading.classification ?? "--"}
              </span>
            </div>

            <div className="filters-grid">
              <label className="label">
                Recorte
                <select
                  className="input"
                  onChange={(event) => setTrendScope(event.target.value as "equipment" | "sector")}
                  value={trendScope}
                >
                  <option value="equipment">Equipamento</option>
                  <option value="sector">Setor</option>
                </select>
              </label>

              <label className="label">
                Janela
                <select
                  className="input"
                  onChange={(event) => setTrendWindow(event.target.value as "7" | "30" | "total")}
                  value={trendWindow}
                >
                  <option value="7">7 dias</option>
                  <option value="30">30 dias</option>
                  <option value="total">Total</option>
                </select>
              </label>

              {trendScope === "sector" ? (
                <label className="label">
                  Setor
                  <select className="input" onChange={(event) => setTrendSector(event.target.value)} value={trendSector}>
                    <option value="">Todos</option>
                    {sectors.map((sector) => (
                      <option key={sector} value={sector}>
                        {sector}
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
            </div>

            <p className="helper-text">
              {trend?.trend_reading.disclaimer ?? "Analise de tendencia com carater assistivo e nao deterministico."}
            </p>
          </div>

          <section className="trend-summary-grid">
            <div className="detail-box">
              <strong>Ocorrencias</strong>
              <p className="metric-inline">{loading ? "..." : trend?.trend_reading.totals.occurrences ?? 0}</p>
            </div>
            <div className="detail-box">
              <strong>Alertas abertos</strong>
              <p className="metric-inline">{loading ? "..." : trend?.trend_reading.totals.open_alerts ?? 0}</p>
            </div>
            <div className="detail-box">
              <strong>OS em aberto</strong>
              <p className="metric-inline">{loading ? "..." : trend?.trend_reading.totals.open_work_orders ?? 0}</p>
            </div>
            <div className="detail-box">
              <strong>Mix corretiva</strong>
              <p className="metric-inline">
                {loading ? "..." : trend ? `${trend.trend_reading.totals.corrective_percentage}%` : "--"}
              </p>
            </div>
          </section>

          <div className="detail-box stack-sm">
            <strong>Leitura executiva</strong>
            <p className="helper-text">{loading ? "Gerando leitura..." : trend?.trend_reading.executive_reading ?? "--"}</p>
          </div>

          <div className="detail-box stack-sm">
            <strong>Leitura tecnica</strong>
            <p className="helper-text">{loading ? "Gerando leitura..." : trend?.trend_reading.technical_reading ?? "--"}</p>
          </div>

          <div className="stack-sm">
            <div className="toolbar-inline">
              <strong>Focos do recorte</strong>
              <span className={trend?.trend_reading.source === "ai" ? "status-pill severity-media" : "status-pill"}>
                {trend?.trend_reading.source === "ai" ? "Gerado por IA" : "Fallback local"}
              </span>
            </div>
            <div className="table-list">
              {trend?.trend_reading.hot_spots.length ? (
                trend.trend_reading.hot_spots.map((item) => (
                  <div className="table-row" key={item.label}>
                    <div className="stack-sm">
                      <strong>{item.label}</strong>
                      <p className="helper-text">
                        {item.occurrences} ocorrencia(s) | {item.alerts} alerta(s) | {item.open_work_orders} OS aberta(s)
                      </p>
                    </div>
                    <span
                      className={
                        item.trend_direction === "subindo"
                          ? "status-pill severity-critica"
                          : item.trend_direction === "reduzindo"
                            ? "status-pill"
                            : "status-pill severity-media"
                      }
                    >
                      {item.trend_direction}
                    </span>
                  </div>
                ))
              ) : (
                <div className="detail-box">
                  <p className="helper-text">Sem recorrencia suficiente para destacar tendencia no recorte atual.</p>
                </div>
              )}
            </div>
          </div>

          <div className="stack-sm">
            <strong>Recomendacoes operacionais</strong>
            <div className="table-list">
              {trend?.trend_reading.recommendations.length ? (
                trend.trend_reading.recommendations.map((item) => (
                  <div className="table-row" key={item}>
                    <p className="helper-text">{item}</p>
                  </div>
                ))
              ) : (
                <div className="detail-box">
                  <p className="helper-text">Sem recomendacoes adicionais para esta tendencia.</p>
                </div>
              )}
            </div>
          </div>
        </article>

        <article className="panel stack">
          <div className="stack-sm">
            <div className="toolbar-inline">
              <h3 className="section-title">Leitura analitica</h3>
              <span className={report?.analytical_reading.source === "ai" ? "status-pill severity-media" : "status-pill"}>
                {report?.analytical_reading.source === "ai" ? "Gerado por IA" : "Fallback local"}
              </span>
            </div>
            <p className="helper-text">
              {report?.analytical_reading.disclaimer ?? "Leitura gerencial assistida para apoio a decisao."}
            </p>
          </div>

          <div className="detail-box">
            <strong>Resumo executivo</strong>
            <p className="helper-text">{loading ? "Gerando leitura..." : report?.analytical_reading.summary ?? "--"}</p>
          </div>

          <div className="stack-sm">
            <strong>Pontos de atencao</strong>
            <div className="table-list">
              {report?.analytical_reading.attention_points.length ? (
                report.analytical_reading.attention_points.map((item) => (
                  <div className="table-row" key={item}>
                    <p className="helper-text">{item}</p>
                  </div>
                ))
              ) : (
                <div className="detail-box">
                  <p className="helper-text">Sem destaques analiticos para o recorte atual.</p>
                </div>
              )}
            </div>
          </div>

          <div className="stack-sm">
            <strong>Padroes observados</strong>
            <div className="table-list">
              {report?.analytical_reading.patterns.length ? (
                report.analytical_reading.patterns.map((item) => (
                  <div className="table-row" key={item}>
                    <p className="helper-text">{item}</p>
                  </div>
                ))
              ) : (
                <div className="detail-box">
                  <p className="helper-text">Sem padroes relevantes identificados.</p>
                </div>
              )}
            </div>
          </div>

          <div className="stack-sm">
            <strong>Recomendacoes operacionais</strong>
            <div className="table-list">
              {report?.analytical_reading.recommendations.length ? (
                report.analytical_reading.recommendations.map((item) => (
                  <div className="table-row" key={item}>
                    <p className="helper-text">{item}</p>
                  </div>
                ))
              ) : (
                <div className="detail-box">
                  <p className="helper-text">Sem recomendacoes adicionais.</p>
                </div>
              )}
            </div>
          </div>

          <p className="helper-text">
            Atualizado em{" "}
            {report ? new Date(report.analytical_reading.generated_at).toLocaleString("pt-BR") : "--"}
            {report?.analytical_reading.model ? ` com ${report.analytical_reading.model}` : " sem dependencia da OpenAI"}.
          </p>
        </article>

        <article className="panel stack">
          <div className="stack-sm">
            <h3 className="section-title">Ocorrencias por equipamento</h3>
            <p className="helper-text">Equipamentos com maior recorrencia de falha no recorte atual.</p>
          </div>
          <div className="table-list">
            {report?.occurrences_by_equipment.length ? (
              report.occurrences_by_equipment.map((item) => (
                <div className="table-row" key={item.equipment_id}>
                  <div className="stack-sm">
                    <strong>
                      {item.equipment_tag} - {item.equipment_name}
                    </strong>
                    <p className="helper-text">
                      {item.occurrences} ocorrencia(s) | {item.alerts} alerta(s) | {item.open_work_orders} OS aberta(s)
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="detail-box">
                <p className="helper-text">Nenhum registro de ocorrencia encontrado.</p>
              </div>
            )}
          </div>
        </article>

        <article className="panel stack">
          <div className="stack-sm">
            <h3 className="section-title">OS por equipe</h3>
            <p className="helper-text">Visao pratica da carga de manutencao distribuida por equipe.</p>
          </div>
          <div className="table-list">
            {report?.work_orders_by_team.length ? (
              report.work_orders_by_team.map((item) => (
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
                <p className="helper-text">Nenhuma OS encontrada para os filtros atuais.</p>
              </div>
            )}
          </div>
        </article>
      </section>

      <article className="panel stack">
        <div className="stack-sm">
          <h3 className="section-title">Distribuicao por tipo de manutencao</h3>
          <p className="helper-text">
            Relatorio simples para leitura gerencial. Atualizado em{" "}
            {report ? new Date(report.generated_at).toLocaleString("pt-BR") : "--"}.
          </p>
        </div>
        <div className="table-list">
          {report?.work_orders_by_type.length ? (
            report.work_orders_by_type.map((item) => (
              <div className="table-row" key={item.type}>
                <div className="stack-sm">
                  <strong>{item.type === "corretiva" ? "Corretiva" : "Preventiva"}</strong>
                  <p className="helper-text">{item.total} OS no recorte atual.</p>
                </div>
                <span className="metric-inline">{item.percentage}%</span>
              </div>
            ))
          ) : (
            <div className="detail-box">
              <p className="helper-text">Nenhuma OS encontrada para compor a distribuicao.</p>
            </div>
          )}
        </div>
      </article>
    </section>
  );
}
