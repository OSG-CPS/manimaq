"use client";

import { FormEvent, useEffect, useState } from "react";

import { AdminGuard } from "@/components/admin-guard";
import { fetchApi } from "@/lib/api";

type TeamOption = {
  id: number;
  name: string;
  sector: string;
  active: boolean;
};

type EquipmentRecord = {
  id: number;
  tag: string;
  name: string;
  sector: string;
  criticality: string;
  status: string;
  active: boolean;
  team_id: number | null;
  alert_measurement_type: "vibracao" | "temperatura" | "tensao" | "corrente" | null;
  measurement_unit: string | null;
  alert_threshold_low: number | null;
  alert_threshold_medium: number | null;
  alert_threshold_high: number | null;
  alert_threshold_critical: number | null;
  team: TeamOption | null;
  created_at: string;
  updated_at: string;
};

const initialForm = {
  tag: "",
  name: "",
  sector: "",
  criticality: "media",
  status: "ativo",
  team_id: "",
  alert_measurement_type: "",
  measurement_unit: "",
  alert_threshold_low: "",
  alert_threshold_medium: "",
  alert_threshold_high: "",
  alert_threshold_critical: "",
  active: true,
};

export default function EquipmentsPage() {
  const [equipments, setEquipments] = useState<EquipmentRecord[]>([]);
  const [teams, setTeams] = useState<TeamOption[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<EquipmentRecord | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [form, setForm] = useState(initialForm);

  async function loadTeams() {
    const data = await fetchApi<TeamOption[]>("/teams?active=true");
    setTeams(data);
  }

  async function loadEquipments(query = "") {
    setLoading(true);
    setError("");
    try {
      const suffix = query.trim() ? `?q=${encodeURIComponent(query.trim())}` : "";
      const data = await fetchApi<EquipmentRecord[]>(`/equipments${suffix}`);
      setEquipments(data);
      if (selectedEquipment) {
        const refreshed = data.find((item) => item.id === selectedEquipment.id) ?? null;
        setSelectedEquipment(refreshed);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar equipamentos.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        await Promise.all([loadTeams(), loadEquipments()]);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao preparar pagina.");
        setLoading(false);
      }
    }

    void bootstrap();
  }, []);

  function resetForm() {
    setEditingId(null);
    setForm(initialForm);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    const payload = {
      tag: form.tag,
      name: form.name,
      sector: form.sector,
      criticality: form.criticality,
      status: form.status,
      team_id: form.team_id ? Number(form.team_id) : null,
      alert_measurement_type: form.alert_measurement_type || null,
      measurement_unit: form.measurement_unit || null,
      alert_threshold_low: form.alert_threshold_low ? Number(form.alert_threshold_low) : null,
      alert_threshold_medium: form.alert_threshold_medium ? Number(form.alert_threshold_medium) : null,
      alert_threshold_high: form.alert_threshold_high ? Number(form.alert_threshold_high) : null,
      alert_threshold_critical: form.alert_threshold_critical ? Number(form.alert_threshold_critical) : null,
      active: form.active,
    };

    try {
      if (editingId) {
        await fetchApi<EquipmentRecord>(`/equipments/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        setMessage("Equipamento atualizado com sucesso.");
      } else {
        await fetchApi<EquipmentRecord>("/equipments", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setMessage("Equipamento criado com sucesso.");
      }

      resetForm();
      await loadEquipments(search);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao salvar equipamento.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AdminGuard>
      <section className="stack-lg">
        <header className="panel stack">
          <p className="helper-text">Cadastro administrativo</p>
          <h2 className="section-title">Equipamentos</h2>
          <p className="helper-text">
            TAG unica, detalhamento simples, vinculo opcional com equipe ativa e thresholds de alerta por equipamento.
          </p>
        </header>

        <section className="module-grid">
          <article className="panel stack">
            <div className="toolbar-inline">
              <input
                className="input"
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Buscar por TAG, nome ou setor"
                value={search}
              />
              <button className="secondary-button" onClick={() => void loadEquipments(search)} type="button">
                Buscar
              </button>
            </div>

            {loading ? <p className="helper-text">Carregando equipamentos...</p> : null}
            {error ? <div className="error-box">{error}</div> : null}
            {message ? <div className="success-box">{message}</div> : null}

            <div className="table-list">
              {equipments.map((equipment) => (
                <div className="table-row" key={equipment.id}>
                  <div>
                    <strong>{equipment.tag}</strong>
                    <p className="helper-text">
                      {equipment.name} - {equipment.sector}
                    </p>
                    <p className="helper-text">
                      {equipment.criticality} - {equipment.status} - {equipment.active ? "Ativo" : "Inativo"}
                    </p>
                    {equipment.alert_measurement_type && equipment.measurement_unit ? (
                      <p className="helper-text">
                        alerta por {equipment.alert_measurement_type} em {equipment.measurement_unit}
                      </p>
                    ) : null}
                  </div>
                  <div className="row-actions">
                    <button
                      className="secondary-button inline-button"
                      onClick={() => setSelectedEquipment(equipment)}
                      type="button"
                    >
                      Detalhar
                    </button>
                    <button
                      className="secondary-button inline-button"
                      onClick={() => {
                        setEditingId(equipment.id);
                        setForm({
                          tag: equipment.tag,
                          name: equipment.name,
                          sector: equipment.sector,
                          criticality: equipment.criticality,
                          status: equipment.status,
                          team_id: equipment.team_id ? String(equipment.team_id) : "",
                          alert_measurement_type: equipment.alert_measurement_type ?? "",
                          measurement_unit: equipment.measurement_unit ?? "",
                          alert_threshold_low:
                            equipment.alert_threshold_low !== null ? String(equipment.alert_threshold_low) : "",
                          alert_threshold_medium:
                            equipment.alert_threshold_medium !== null ? String(equipment.alert_threshold_medium) : "",
                          alert_threshold_high:
                            equipment.alert_threshold_high !== null ? String(equipment.alert_threshold_high) : "",
                          alert_threshold_critical:
                            equipment.alert_threshold_critical !== null ? String(equipment.alert_threshold_critical) : "",
                          active: equipment.active,
                        });
                      }}
                      type="button"
                    >
                      Editar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="panel stack">
            <div className="stack-sm">
              <h3 className="section-title">{editingId ? "Editar equipamento" : "Novo equipamento"}</h3>
              <p className="helper-text">A equipe vinculada precisa estar ativa para novos cadastros.</p>
            </div>

            <form className="stack" onSubmit={handleSubmit}>
              <label className="label" htmlFor="equipment-tag">
                TAG
                <input
                  className="input"
                  id="equipment-tag"
                  onChange={(event) => setForm((current) => ({ ...current, tag: event.target.value }))}
                  required
                  value={form.tag}
                />
              </label>

              <label className="label" htmlFor="equipment-name">
                Nome
                <input
                  className="input"
                  id="equipment-name"
                  onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                  required
                  value={form.name}
                />
              </label>

              <label className="label" htmlFor="equipment-sector">
                Setor
                <input
                  className="input"
                  id="equipment-sector"
                  onChange={(event) => setForm((current) => ({ ...current, sector: event.target.value }))}
                  required
                  value={form.sector}
                />
              </label>

              <label className="label" htmlFor="equipment-criticality">
                Criticidade
                <input
                  className="input"
                  id="equipment-criticality"
                  onChange={(event) => setForm((current) => ({ ...current, criticality: event.target.value }))}
                  required
                  value={form.criticality}
                />
              </label>

              <label className="label" htmlFor="equipment-status">
                Status
                <input
                  className="input"
                  id="equipment-status"
                  onChange={(event) => setForm((current) => ({ ...current, status: event.target.value }))}
                  required
                  value={form.status}
                />
              </label>

              <label className="label" htmlFor="equipment-team">
                Equipe responsavel
                <select
                  className="input"
                  id="equipment-team"
                  onChange={(event) => setForm((current) => ({ ...current, team_id: event.target.value }))}
                  value={form.team_id}
                >
                  <option value="">Sem equipe vinculada</option>
                  {teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name} ({team.sector})
                    </option>
                  ))}
                </select>
              </label>

              <label className="label" htmlFor="equipment-alert-measurement-type">
                Tipo principal de medicao para alerta
                <select
                  className="input"
                  id="equipment-alert-measurement-type"
                  onChange={(event) =>
                    setForm((current) => ({ ...current, alert_measurement_type: event.target.value }))
                  }
                  value={form.alert_measurement_type}
                >
                  <option value="">Sem configuracao</option>
                  <option value="vibracao">Vibracao</option>
                  <option value="temperatura">Temperatura</option>
                  <option value="tensao">Tensao</option>
                  <option value="corrente">Corrente</option>
                </select>
              </label>

              <label className="label" htmlFor="equipment-measurement-unit">
                Unidade de medida
                <input
                  className="input"
                  id="equipment-measurement-unit"
                  onChange={(event) => setForm((current) => ({ ...current, measurement_unit: event.target.value }))}
                  placeholder="Ex.: C, mm/s, V, A"
                  value={form.measurement_unit}
                />
              </label>

              <label className="label" htmlFor="equipment-alert-threshold-low">
                Limiar baixo
                <input
                  className="input"
                  id="equipment-alert-threshold-low"
                  min="0"
                  onChange={(event) => setForm((current) => ({ ...current, alert_threshold_low: event.target.value }))}
                  step="0.01"
                  type="number"
                  value={form.alert_threshold_low}
                />
              </label>

              <label className="label" htmlFor="equipment-alert-threshold-medium">
                Limiar medio
                <input
                  className="input"
                  id="equipment-alert-threshold-medium"
                  min="0"
                  onChange={(event) =>
                    setForm((current) => ({ ...current, alert_threshold_medium: event.target.value }))
                  }
                  step="0.01"
                  type="number"
                  value={form.alert_threshold_medium}
                />
              </label>

              <label className="label" htmlFor="equipment-alert-threshold-high">
                Limiar alto
                <input
                  className="input"
                  id="equipment-alert-threshold-high"
                  min="0"
                  onChange={(event) => setForm((current) => ({ ...current, alert_threshold_high: event.target.value }))}
                  step="0.01"
                  type="number"
                  value={form.alert_threshold_high}
                />
              </label>

              <label className="label" htmlFor="equipment-alert-threshold-critical">
                Limiar critico
                <input
                  className="input"
                  id="equipment-alert-threshold-critical"
                  min="0"
                  onChange={(event) =>
                    setForm((current) => ({ ...current, alert_threshold_critical: event.target.value }))
                  }
                  step="0.01"
                  type="number"
                  value={form.alert_threshold_critical}
                />
              </label>

              {editingId ? (
                <label className="checkbox">
                  <input
                    checked={form.active}
                    onChange={(event) => setForm((current) => ({ ...current, active: event.target.checked }))}
                    type="checkbox"
                  />
                  Equipamento ativo
                </label>
              ) : null}

              <div className="toolbar-inline">
                <button className="primary-button" disabled={submitting} type="submit">
                  {submitting ? "Salvando..." : editingId ? "Salvar alteracoes" : "Criar equipamento"}
                </button>
                {editingId ? (
                  <button className="secondary-button" onClick={resetForm} type="button">
                    Cancelar edicao
                  </button>
                ) : null}
              </div>
            </form>

            {selectedEquipment ? (
              <div className="detail-box stack">
                <h4 className="section-title">Detalhe rapido</h4>
                <p className="helper-text">TAG: {selectedEquipment.tag}</p>
                <p className="helper-text">Nome: {selectedEquipment.name}</p>
                <p className="helper-text">Setor: {selectedEquipment.sector}</p>
                <p className="helper-text">Criticidade: {selectedEquipment.criticality}</p>
                <p className="helper-text">Status: {selectedEquipment.status}</p>
                <p className="helper-text">
                  Equipe: {selectedEquipment.team ? selectedEquipment.team.name : "Sem vinculacao"}
                </p>
                <p className="helper-text">
                  Medicao de alerta: {selectedEquipment.alert_measurement_type ?? "Nao configurada"}
                </p>
                <p className="helper-text">Unidade: {selectedEquipment.measurement_unit ?? "Nao configurada"}</p>
                <p className="helper-text">
                  Limiares: baixo {selectedEquipment.alert_threshold_low ?? "--"} | medio{" "}
                  {selectedEquipment.alert_threshold_medium ?? "--"} | alto {selectedEquipment.alert_threshold_high ?? "--"} |
                  critico {selectedEquipment.alert_threshold_critical ?? "--"}
                </p>
              </div>
            ) : null}
          </article>
        </section>
      </section>
    </AdminGuard>
  );
}
