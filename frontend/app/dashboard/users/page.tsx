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

type UserRecord = {
  id: number;
  name: string;
  username: string;
  email: string;
  role: "admin" | "gerente" | "operador";
  active: boolean;
  team_id: number | null;
  team: TeamOption | null;
  created_at: string;
  updated_at: string;
};

const initialForm = {
  name: "",
  username: "",
  email: "",
  role: "operador" as UserRecord["role"],
  team_id: "",
  password: "",
  active: true,
};

export default function UsersPage() {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [teams, setTeams] = useState<TeamOption[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [form, setForm] = useState(initialForm);

  async function loadTeams() {
    const data = await fetchApi<TeamOption[]>("/teams?active=true");
    setTeams(data);
  }

  async function loadUsers(query = "") {
    setLoading(true);
    setError("");
    try {
      const suffix = query.trim() ? `?q=${encodeURIComponent(query.trim())}` : "";
      const data = await fetchApi<UserRecord[]>(`/users${suffix}`);
      setUsers(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao carregar usuarios.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        await Promise.all([loadTeams(), loadUsers()]);
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

    try {
      if (editingId) {
        await fetchApi<UserRecord>(`/users/${editingId}`, {
          method: "PUT",
          body: JSON.stringify({
            name: form.name,
            username: form.username,
            email: form.email,
            role: form.role,
            team_id: Number(form.team_id),
            active: form.active,
          }),
        });
        setMessage("Usuario atualizado com sucesso.");
      } else {
        await fetchApi<UserRecord>("/users", {
          method: "POST",
          body: JSON.stringify({
            name: form.name,
            username: form.username,
            email: form.email,
            role: form.role,
            team_id: Number(form.team_id),
            password: form.password,
          }),
        });
        setMessage("Usuario criado com sucesso.");
      }

      resetForm();
      await loadUsers(search);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao salvar usuario.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeactivate(userId: number) {
    setError("");
    setMessage("");
    try {
      await fetchApi<UserRecord>(`/users/${userId}/inactive`, { method: "PATCH" });
      if (editingId === userId) {
        resetForm();
      }
      setMessage("Usuario desativado com sucesso.");
      await loadUsers(search);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Falha ao desativar usuario.");
    }
  }

  return (
    <AdminGuard>
      <section className="stack-lg">
        <header className="panel stack">
          <p className="helper-text">Cadastro administrativo</p>
          <h2 className="section-title">Usuarios</h2>
          <p className="helper-text">Email unico, senha apenas na criacao e desativacao logica.</p>
        </header>

        <section className="module-grid">
          <article className="panel stack">
            <div className="toolbar-inline">
              <input
                className="input"
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Buscar por nome, usuario ou email"
                value={search}
              />
              <button className="secondary-button" onClick={() => void loadUsers(search)} type="button">
                Buscar
              </button>
            </div>

            {loading ? <p className="helper-text">Carregando usuarios...</p> : null}
            {error ? <div className="error-box">{error}</div> : null}
            {message ? <div className="success-box">{message}</div> : null}

            <div className="table-list">
              {users.map((user) => (
                <div className="table-row" key={user.id}>
                  <div>
                    <strong>{user.name}</strong>
                    <p className="helper-text">
                      {user.username} · {user.email}
                    </p>
                    <p className="helper-text">
                      {user.role} · {user.team ? user.team.name : "Sem equipe"} ·{" "}
                      {user.active ? "Ativo" : "Inativo"}
                    </p>
                  </div>
                  <div className="row-actions">
                    <button
                      className="secondary-button inline-button"
                      onClick={() => {
                        setEditingId(user.id);
                        setForm({
                          name: user.name,
                          username: user.username,
                          email: user.email,
                          role: user.role,
                          team_id: user.team_id ? String(user.team_id) : "",
                          password: "",
                          active: user.active,
                        });
                      }}
                      type="button"
                    >
                      Editar
                    </button>
                    {user.active ? (
                      <button
                        className="secondary-button inline-button"
                        onClick={() => void handleDeactivate(user.id)}
                        type="button"
                      >
                        Desativar
                      </button>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="panel stack">
            <div className="stack-sm">
              <h3 className="section-title">{editingId ? "Editar usuario" : "Novo usuario"}</h3>
              <p className="helper-text">Todo usuario novo precisa nascer vinculado a equipe ativa.</p>
            </div>

            <form className="stack" onSubmit={handleSubmit}>
              <label className="label" htmlFor="user-name">
                Nome
                <input
                  className="input"
                  id="user-name"
                  onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                  required
                  value={form.name}
                />
              </label>

              <label className="label" htmlFor="user-username">
                Usuario
                <input
                  className="input"
                  id="user-username"
                  onChange={(event) =>
                    setForm((current) => ({ ...current, username: event.target.value }))
                  }
                  required
                  value={form.username}
                />
              </label>

              <label className="label" htmlFor="user-email">
                Email
                <input
                  className="input"
                  id="user-email"
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                  required
                  type="email"
                  value={form.email}
                />
              </label>

              <label className="label" htmlFor="user-role">
                Perfil
                <select
                  className="input"
                  id="user-role"
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      role: event.target.value as UserRecord["role"],
                    }))
                  }
                  value={form.role}
                >
                  <option value="admin">admin</option>
                  <option value="gerente">gerente</option>
                  <option value="operador">operador</option>
                </select>
              </label>

              <label className="label" htmlFor="user-team">
                Equipe
                <select
                  className="input"
                  id="user-team"
                  onChange={(event) => setForm((current) => ({ ...current, team_id: event.target.value }))}
                  required
                  value={form.team_id}
                >
                  <option value="">Selecione uma equipe ativa</option>
                  {teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name} ({team.sector})
                    </option>
                  ))}
                </select>
              </label>

              {!editingId ? (
                <label className="label" htmlFor="user-password">
                  Senha inicial
                  <input
                    className="input"
                    id="user-password"
                    minLength={6}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, password: event.target.value }))
                    }
                    required
                    type="password"
                    value={form.password}
                  />
                </label>
              ) : (
                <label className="checkbox">
                  <input
                    checked={form.active}
                    onChange={(event) => setForm((current) => ({ ...current, active: event.target.checked }))}
                    type="checkbox"
                  />
                  Usuario ativo
                </label>
              )}

              <div className="toolbar-inline">
                <button className="primary-button" disabled={submitting} type="submit">
                  {submitting ? "Salvando..." : editingId ? "Salvar alteracoes" : "Criar usuario"}
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
