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
          <p className="helper-text">TAG unica, detalhamento simples e vinculo opcional com equipe ativa.</p>
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
                      {equipment.name} · {equipment.sector}
                    </p>
                    <p className="helper-text">
                      {equipment.criticality} · {equipment.status} · {equipment.active ? "Ativo" : "Inativo"}
                    </p>
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
                  onChange={(event) =>
                    setForm((current) => ({ ...current, criticality: event.target.value }))
                  }
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
              </div>
            ) : null}
          </article>
        </section>
      </section>
    </AdminGuard>
  );
}
