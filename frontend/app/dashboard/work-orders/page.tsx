"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { fetchApi } from "@/lib/api";
import { canAccessAdminModules, getStoredSession } from "@/lib/auth";

type EquipmentOption = {
  id: number;
  tag: string;
  name: string;
  sector: string;
  active: boolean;
};

type TeamOption = {
  id: number;
  name: string;
  sector: string;
  active: boolean;
};

type UserSummary = {
  id: number;
  name: string;
  username: string;
  role: "admin" | "gerente" | "operador";
  active: boolean;
};

type WorkOrderStatus = "aberta" | "em_execucao" | "concluida" | "cancelada";

type WorkOrderHistoryEntry = {
  id: number;
  previous_status: WorkOrderStatus | null;
  new_status: WorkOrderStatus;
  note: string | null;
  transition_at: string;
  created_at: string;
  author: UserSummary;
};

type WorkOrderRecord = {
  id: number;
  equipment_id: number;
  team_id: number;
  type: "corretiva" | "preventiva";
  priority: "baixa" | "media" | "alta" | "critica";
  status: WorkOrderStatus;
  description: string;
  origin: "manual" | "sugerida";
  planned_start_at: string | null;
  estimated_duration_hours: number | null;
  equipment: EquipmentOption;
  team: TeamOption;
  created_by: UserSummary;
  status_history: WorkOrderHistoryEntry[];
  created_at: string;
  updated_at: string;
};

function getDefaultDateTimeLocal() {
  const now = new Date();
  const adjusted = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return adjusted.toISOString().slice(0, 16);
}

function toApiDateTime(value: string) {
  return value ? new Date(value).toISOString() : null;
}

const initialForm = {
  equipment_id: "",
  team_id: "",
  type: "corretiva",
  priority: "media",
  description: "",
  planned_start_at: getDefaultDateTimeLocal(),
  estimated_duration_hours: "2",
  initial_note: "",
};

const statusLabels: Record<WorkOrderStatus, string> = {
  aberta: "Aberta",
  em_execucao: "Em execucao",
  concluida: "Concluida",
  cancelada: "Cancelada",
};

export default function WorkOrdersPage() {
  const session = getStoredSession();
  const canManage = canAccessAdminModules(session?.user.role);
  const currentTeamId = session?.user.team_id ?? null;

  const [equipments, setEquipments] = useState<EquipmentOption[]>([]);
  const [teams, setTeams] = useState<TeamOption[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrderRecord[]>([]);
  const [selectedWorkOrder, setSelectedWorkOrder] = useState<WorkOrderRecord | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [statusNote, setStatusNote] = useState("");
  const [statusTransitionAt, setStatusTransitionAt] = useState(getDefaultDateTimeLocal());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [form, setForm] = useState(initialForm);

  async function loadWorkOrders(filter = statusFilter) {
    setLoading(true);
    setError("");
    try {
      const suffix = filter ? `?status_filter=${encodeURIComponent(filter)}` : "";
      const data = await fetchApi<WorkOrderRecord[]>(`/work-orders${suffix}`);
      setWorkOrders(data);
      if (selectedWorkOrder) {
        const refreshed = data.find((item) => item.id === selectedWorkOrder.id) ?? null;
        setSelectedWorkOrder(refreshed);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar OS.");
    } finally {
      setLoading(false);
    }
  }

  async function loadCreationCatalogs() {
    const [equipmentData, teamData] = await Promise.all([
      fetchApi<EquipmentOption[]>("/equipment-history/catalog"),
      canManage ? fetchApi<TeamOption[]>("/teams") : Promise.resolve([]),
    ]);
    const activeTeams = teamData.filter((team) => team.active);

    setEquipments(equipmentData);
    setTeams(activeTeams);

    setForm((current) => ({
      ...current,
      equipment_id: current.equipment_id || (equipmentData[0] ? String(equipmentData[0].id) : ""),
      team_id: current.team_id || (activeTeams[0] ? String(activeTeams[0].id) : ""),
    }));
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        await Promise.all([loadCreationCatalogs(), loadWorkOrders("")]);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao preparar pagina.");
        setLoading(false);
      }
    }

    void bootstrap();
  }, []);

  function resetForm() {
    setForm({
      ...initialForm,
      equipment_id: equipments[0] ? String(equipments[0].id) : "",
      team_id: teams[0] ? String(teams[0].id) : "",
      planned_start_at: getDefaultDateTimeLocal(),
    });
  }

  function selectWorkOrder(workOrder: WorkOrderRecord) {
    setSelectedWorkOrder(workOrder);
    setStatusNote("");
    setStatusTransitionAt(getDefaultDateTimeLocal());
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await fetchApi<WorkOrderRecord>("/work-orders", {
        method: "POST",
        body: JSON.stringify({
          equipment_id: Number(form.equipment_id),
          team_id: Number(form.team_id),
          type: form.type,
          priority: form.priority,
          description: form.description,
          origin: "manual",
          planned_start_at: toApiDateTime(form.planned_start_at),
          estimated_duration_hours: form.estimated_duration_hours ? Number(form.estimated_duration_hours) : null,
          initial_note: form.initial_note || null,
        }),
      });
      setMessage("OS criada com sucesso.");
      resetForm();
      await loadWorkOrders();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao criar OS.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(nextStatus: WorkOrderStatus) {
    if (!selectedWorkOrder) {
      return;
    }

    setUpdatingStatus(true);
    setError("");
    setMessage("");
    try {
      const updated = await fetchApi<WorkOrderRecord>(`/work-orders/${selectedWorkOrder.id}/status`, {
        method: "POST",
        body: JSON.stringify({
          status: nextStatus,
          note: statusNote || null,
          transition_at: toApiDateTime(statusTransitionAt),
        }),
      });
      setSelectedWorkOrder(updated);
      setStatusNote("");
      setStatusTransitionAt(getDefaultDateTimeLocal());
      setMessage(`OS atualizada para ${statusLabels[nextStatus].toLowerCase()}.`);
      await loadWorkOrders(statusFilter);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao atualizar status da OS.");
    } finally {
      setUpdatingStatus(false);
    }
  }

  const availableActions = useMemo(() => {
    if (!selectedWorkOrder) {
      return [] as WorkOrderStatus[];
    }

    if (selectedWorkOrder.status === "aberta") {
      return canManage ? ["em_execucao", "cancelada"] : ["em_execucao"];
    }
    if (selectedWorkOrder.status === "em_execucao") {
      return canManage ? ["concluida", "cancelada"] : ["concluida"];
    }
    return [] as WorkOrderStatus[];
  }, [canManage, selectedWorkOrder]);

  const operatorCanSeeSelected =
    !selectedWorkOrder || canManage || (currentTeamId !== null && selectedWorkOrder.team_id === currentTeamId);

  return (
    <section className="stack-lg">
      <header className="panel stack">
        <p className="helper-text">Fluxo de manutencao</p>
        <h2 className="section-title">Ordens de servico</h2>
        <p className="helper-text">
          Gerentes e admins abrem OS. Operadores da equipe executam, atualizam andamento e concluem com rastreabilidade.
        </p>
      </header>

      <section className="module-grid">
        <section className="stack-lg">
          <article className="panel stack">
            <div className="toolbar-inline">
              <select className="input" onChange={(event) => setStatusFilter(event.target.value)} value={statusFilter}>
                <option value="">Todos os status</option>
                <option value="aberta">Abertas</option>
                <option value="em_execucao">Em execucao</option>
                <option value="concluida">Concluidas</option>
                <option value="cancelada">Canceladas</option>
              </select>
              <button className="secondary-button" onClick={() => void loadWorkOrders()} type="button">
                Filtrar
              </button>
            </div>

            {loading ? <p className="helper-text">Carregando OS...</p> : null}
            {error ? <div className="error-box">{error}</div> : null}
            {message ? <div className="success-box">{message}</div> : null}

            <div className="table-list">
              {workOrders.map((workOrder) => (
                <div className="table-row" key={workOrder.id}>
                  <div className="stack-sm">
                    <div className="toolbar-inline">
                      <strong>OS #{workOrder.id}</strong>
                      <span className={`status-pill work-order-status-${workOrder.status}`}>
                        {statusLabels[workOrder.status]}
                      </span>
                      <span className={`status-pill priority-${workOrder.priority}`}>{workOrder.priority}</span>
                    </div>
                    <p className="helper-text">
                      {workOrder.equipment.tag} | {workOrder.team.name} | aberta por {workOrder.created_by.name}
                    </p>
                    <p>{workOrder.description}</p>
                  </div>
                  <div className="row-actions">
                    <button
                      className="secondary-button inline-button"
                      onClick={() => selectWorkOrder(workOrder)}
                      type="button"
                    >
                      Detalhar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </article>

          {selectedWorkOrder && operatorCanSeeSelected ? (
            <article className="panel stack">
              <div className="stack-sm">
                <h3 className="section-title">Detalhe da OS #{selectedWorkOrder.id}</h3>
                <p className="helper-text">
                  {selectedWorkOrder.equipment.tag} - {selectedWorkOrder.equipment.name}
                </p>
                <p className="helper-text">Equipe: {selectedWorkOrder.team.name}</p>
                <p className="helper-text">Status atual: {statusLabels[selectedWorkOrder.status]}</p>
                <p className="helper-text">
                  Inicio previsto:{" "}
                  {selectedWorkOrder.planned_start_at
                    ? new Date(selectedWorkOrder.planned_start_at).toLocaleString("pt-BR")
                    : "Nao informado"}
                </p>
                <p className="helper-text">
                  Duracao estimada: {selectedWorkOrder.estimated_duration_hours ?? "--"} hora(s)
                </p>
                <p>{selectedWorkOrder.description}</p>
              </div>

              {availableActions.length > 0 ? (
                <div className="detail-box stack">
                  <h4 className="section-title">Atualizar andamento</h4>
                  <label className="label" htmlFor="work-order-status-transition-at">
                    Data e hora da atualizacao
                    <input
                      className="input"
                      id="work-order-status-transition-at"
                      onChange={(event) => setStatusTransitionAt(event.target.value)}
                      type="datetime-local"
                      value={statusTransitionAt}
                    />
                  </label>

                  <label className="label" htmlFor="work-order-status-note">
                    Observacao da transicao
                    <textarea
                      className="input"
                      id="work-order-status-note"
                      onChange={(event) => setStatusNote(event.target.value)}
                      placeholder="Ex.: maquina liberada para teste, pecas substituidas, servico concluido"
                      value={statusNote}
                    />
                  </label>

                  <div className="row-actions">
                    {availableActions.map((nextStatus) => (
                      <button
                        className="primary-button inline-button"
                        disabled={updatingStatus}
                        key={nextStatus}
                        onClick={() => void handleStatusUpdate(nextStatus)}
                        type="button"
                      >
                        {updatingStatus ? "Atualizando..." : `Marcar como ${statusLabels[nextStatus]}`}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="helper-text">Esta OS nao possui novas transicoes disponiveis no estado atual.</p>
              )}

              <div className="stack-sm">
                <h4 className="section-title">Historico de status</h4>
                <div className="table-list">
                  {selectedWorkOrder.status_history.map((entry) => (
                    <div className="table-row" key={entry.id}>
                      <div className="stack-sm">
                        <div className="toolbar-inline">
                          <span className="status-pill">
                            {entry.previous_status ? statusLabels[entry.previous_status] : "Abertura"}
                          </span>
                          <span className="helper-text">para</span>
                          <span className={`status-pill work-order-status-${entry.new_status}`}>
                            {statusLabels[entry.new_status]}
                          </span>
                        </div>
                        <p className="helper-text">
                          {entry.author.name} | evento em {new Date(entry.transition_at).toLocaleString("pt-BR")}
                        </p>
                        <p className="helper-text">
                          Registro no sistema em {new Date(entry.created_at).toLocaleString("pt-BR")}
                        </p>
                        {entry.note ? <p>{entry.note}</p> : null}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </article>
          ) : null}
        </section>

        <article className="panel stack measurements-form-panel">
          {canManage ? (
            <>
              <div className="stack-sm">
                <h3 className="section-title">Nova OS</h3>
                <p className="helper-text">Use este bloco para abrir e encaminhar uma OS para a equipe responsavel.</p>
              </div>

              <form className="stack" onSubmit={handleSubmit}>
                <label className="label" htmlFor="work-order-equipment">
                  Equipamento
                  <select
                    className="input"
                    id="work-order-equipment"
                    onChange={(event) => setForm((current) => ({ ...current, equipment_id: event.target.value }))}
                    required
                    value={form.equipment_id}
                  >
                    <option value="">Selecione</option>
                    {equipments.map((equipment) => (
                      <option key={equipment.id} value={equipment.id}>
                        {equipment.tag} - {equipment.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="label" htmlFor="work-order-team">
                  Equipe responsavel
                  <select
                    className="input"
                    id="work-order-team"
                    onChange={(event) => setForm((current) => ({ ...current, team_id: event.target.value }))}
                    required
                    value={form.team_id}
                  >
                    <option value="">Selecione</option>
                    {teams.map((team) => (
                      <option key={team.id} value={team.id}>
                        {team.name} - {team.sector}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="label" htmlFor="work-order-type">
                  Tipo
                  <select
                    className="input"
                    id="work-order-type"
                    onChange={(event) => setForm((current) => ({ ...current, type: event.target.value }))}
                    value={form.type}
                  >
                    <option value="corretiva">Corretiva</option>
                    <option value="preventiva">Preventiva</option>
                  </select>
                </label>

                <label className="label" htmlFor="work-order-priority">
                  Prioridade
                  <select
                    className="input"
                    id="work-order-priority"
                    onChange={(event) => setForm((current) => ({ ...current, priority: event.target.value }))}
                    value={form.priority}
                  >
                    <option value="baixa">Baixa</option>
                    <option value="media">Media</option>
                    <option value="alta">Alta</option>
                    <option value="critica">Critica</option>
                  </select>
                </label>

                <label className="label" htmlFor="work-order-planned-start">
                  Inicio previsto
                  <input
                    className="input"
                    id="work-order-planned-start"
                    onChange={(event) => setForm((current) => ({ ...current, planned_start_at: event.target.value }))}
                    type="datetime-local"
                    value={form.planned_start_at}
                  />
                </label>

                <label className="label" htmlFor="work-order-estimated-duration">
                  Duracao estimada (horas)
                  <input
                    className="input"
                    id="work-order-estimated-duration"
                    min="1"
                    onChange={(event) =>
                      setForm((current) => ({ ...current, estimated_duration_hours: event.target.value }))
                    }
                    type="number"
                    value={form.estimated_duration_hours}
                  />
                </label>

                <label className="label" htmlFor="work-order-description">
                  Descricao
                  <textarea
                    className="input textarea"
                    id="work-order-description"
                    onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
                    required
                    value={form.description}
                  />
                </label>

                <label className="label" htmlFor="work-order-initial-note">
                  Observacao inicial
                  <textarea
                    className="input"
                    id="work-order-initial-note"
                    onChange={(event) => setForm((current) => ({ ...current, initial_note: event.target.value }))}
                    value={form.initial_note}
                  />
                </label>

                <button className="primary-button" disabled={submitting} type="submit">
                  {submitting ? "Salvando..." : "Abrir OS"}
                </button>
              </form>
            </>
          ) : (
            <div className="detail-box stack">
              <h3 className="section-title">Execucao da equipe</h3>
              <p className="helper-text">
                Seu perfil visualiza as OS da propria equipe e pode iniciar ou concluir a execucao com data/hora editavel.
              </p>
            </div>
          )}
        </article>
      </section>
    </section>
  );
}
