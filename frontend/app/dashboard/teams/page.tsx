"use client";

import { FormEvent, useEffect, useState } from "react";

import { AdminGuard } from "@/components/admin-guard";
import { fetchApi } from "@/lib/api";

type TeamRecord = {
  id: number;
  name: string;
  sector: string;
  description: string | null;
  active: boolean;
  users_count: number;
  equipments_count: number;
  created_at: string;
  updated_at: string;
};

const initialForm = {
  name: "",
  sector: "",
  description: "",
  active: true,
};

export default function TeamsPage() {
  const [teams, setTeams] = useState<TeamRecord[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [form, setForm] = useState(initialForm);

  async function loadTeams(query = "") {
    setLoading(true);
    setError("");
    try {
      const suffix = query.trim() ? `?q=${encodeURIComponent(query.trim())}` : "";
      const data = await fetchApi<TeamRecord[]>(`/teams${suffix}`);
      setTeams(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar equipes.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadTeams();
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

    try {
      if (editingId) {
        await fetchApi<TeamRecord>(`/teams/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(form),
        });
        setMessage("Equipe atualizada com sucesso.");
      } else {
        await fetchApi<TeamRecord>("/teams", {
          method: "POST",
          body: JSON.stringify(form),
        });
        setMessage("Equipe criada com sucesso.");
      }

      resetForm();
      await loadTeams(search);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao salvar equipe.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeactivate(teamId: number) {
    setError("");
    setMessage("");
    try {
      await fetchApi<TeamRecord>(`/teams/${teamId}/inactive`, { method: "PATCH" });
      if (editingId === teamId) {
        resetForm();
      }
      setMessage("Equipe inativada com sucesso.");
      await loadTeams(search);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao inativar equipe.");
    }
  }

  return (
    <AdminGuard>
      <section className="stack-lg">
        <header className="panel stack">
          <p className="helper-text">Cadastro administrativo</p>
          <h2 className="section-title">Equipes</h2>
          <p className="helper-text">Nome unico, edicao simples e inativacao logica.</p>
        </header>

        <section className="module-grid">
          <article className="panel stack">
            <div className="toolbar-inline">
              <input
                className="input"
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Buscar por nome ou setor"
                value={search}
              />
              <button className="secondary-button" onClick={() => void loadTeams(search)} type="button">
                Buscar
              </button>
            </div>

            {loading ? <p className="helper-text">Carregando equipes...</p> : null}
            {error ? <div className="error-box">{error}</div> : null}
            {message ? <div className="success-box">{message}</div> : null}

            <div className="table-list">
              {teams.map((team) => (
                <div className="table-row" key={team.id}>
                  <div>
                    <strong>{team.name}</strong>
                    <p className="helper-text">
                      {team.sector} · {team.active ? "Ativa" : "Inativa"}
                    </p>
                    <p className="helper-text">
                      {team.users_count} usuario(s) · {team.equipments_count} equipamento(s)
                    </p>
                  </div>
                  <div className="row-actions">
                    <button
                      className="secondary-button inline-button"
                      onClick={() => {
                        setEditingId(team.id);
                        setForm({
                          name: team.name,
                          sector: team.sector,
                          description: team.description ?? "",
                          active: team.active,
                        });
                      }}
                      type="button"
                    >
                      Editar
                    </button>
                    {team.active ? (
                      <button
                        className="secondary-button inline-button"
                        onClick={() => void handleDeactivate(team.id)}
                        type="button"
                      >
                        Inativar
                      </button>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="panel stack">
            <div className="stack-sm">
              <h3 className="section-title">{editingId ? "Editar equipe" : "Nova equipe"}</h3>
              <p className="helper-text">Equipes inativas deixam de aceitar novos vinculos.</p>
            </div>

            <form className="stack" onSubmit={handleSubmit}>
              <label className="label" htmlFor="team-name">
                Nome
                <input
                  className="input"
                  id="team-name"
                  onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                  required
                  value={form.name}
                />
              </label>

              <label className="label" htmlFor="team-sector">
                Setor
                <input
                  className="input"
                  id="team-sector"
                  onChange={(event) => setForm((current) => ({ ...current, sector: event.target.value }))}
                  required
                  value={form.sector}
                />
              </label>

              <label className="label" htmlFor="team-description">
                Descricao
                <input
                  className="input"
                  id="team-description"
                  onChange={(event) =>
                    setForm((current) => ({ ...current, description: event.target.value }))
                  }
                  value={form.description}
                />
              </label>

              {editingId ? (
                <label className="checkbox">
                  <input
                    checked={form.active}
                    onChange={(event) => setForm((current) => ({ ...current, active: event.target.checked }))}
                    type="checkbox"
                  />
                  Equipe ativa
                </label>
              ) : null}

              <div className="toolbar-inline">
                <button className="primary-button" disabled={submitting} type="submit">
                  {submitting ? "Salvando..." : editingId ? "Salvar alteracoes" : "Criar equipe"}
                </button>
                {editingId ? (
                  <button className="secondary-button" onClick={resetForm} type="button">
                    Cancelar edicao
                  </button>
                ) : null}
              </div>
            </form>
          </article>
        </section>
      </section>
    </AdminGuard>
  );
}
