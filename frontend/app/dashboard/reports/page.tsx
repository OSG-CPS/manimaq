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
};

export default function ReportsPage() {
  const session = getStoredSession();
  const canManage = canAccessAdminModules(session?.user.role);
  const [equipments, setEquipments] = useState<EquipmentOption[]>([]);
  const [teams, setTeams] = useState<TeamOption[]>([]);
  const [report, setReport] = useState<DashboardReport | null>(null);
  const [periodDays, setPeriodDays] = useState("30");
  const [equipmentId, setEquipmentId] = useState("");
  const [teamId, setTeamId] = useState("");
  const [maintenanceType, setMaintenanceType] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
      const query = new URLSearchParams();
      query.set("period_days", periodDays);
      if (equipmentId) {
        query.set("equipment_id", equipmentId);
      }
      if (teamId && canManage) {
        query.set("team_id", teamId);
      }
      if (maintenanceType) {
        query.set("maintenance_type", maintenanceType);
      }

      const data = await fetchApi<DashboardReport>(`/dashboard/reports?${query.toString()}`);
      setReport(data);
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
        <p className="helper-text">Sprint 6</p>
        <h2 className="section-title">Relatorios basicos</h2>
        <p className="helper-text">
          Consolidados simples e auditaveis por periodo, equipamento, equipe e tipo de manutencao.
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
