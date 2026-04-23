"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AuthGuard } from "@/components/auth-guard";
import { LogoutButton } from "@/components/logout-button";
import { AuthSession, getApiBaseUrl, getStoredSession } from "@/lib/auth";

type DashboardSummary = {
  message: string;
  role: string;
  team: string | null;
};

export default function DashboardPage() {
  const router = useRouter();
  const [session, setSession] = useState<AuthSession | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const activeSession = getStoredSession();
    if (!activeSession) {
      router.replace("/login");
      return;
    }

    setSession(activeSession);
    const token = activeSession.access_token;

    async function loadSummary() {
      const response = await fetch(`${getApiBaseUrl()}/dashboard-summary`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        router.replace("/login");
        return;
      }

      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Falha ao carregar a area autenticada.");
        return;
      }

      setSummary(data);
    }

    void loadSummary();
  }, [router]);

  return (
    <AuthGuard>
      <main className="dashboard-shell">
        <section className="dashboard-frame">
          <header className="toolbar">
            <div className="stack">
              <p className="helper-text">Sprint 1 pronta para evolucao</p>
              <h1>Painel autenticado</h1>
              <p className="helper-text">
                {session ? `${session.user.name} (${session.user.role})` : "Carregando usuario..."}
              </p>
            </div>
            <LogoutButton />
          </header>

          {error ? <div className="error-box">{error}</div> : null}

          <section className="grid-layout">
            <article className="grid-card">
              <h2>Autenticacao</h2>
              <p className="metric">{summary ? "OK" : "..."}</p>
              <p className="helper-text">JWT emitido e rota privada validada pelo backend.</p>
            </article>

            <article className="grid-card">
              <h2>Perfil</h2>
              <p className="metric">{session?.user.role ?? "--"}</p>
              <p className="helper-text">Perfis basicos seedados: admin, gerente e operador.</p>
            </article>

            <article className="grid-card">
              <h2>Equipe</h2>
              <p className="metric">{summary?.team ?? "--"}</p>
              <p className="helper-text">Usuario vinculado a equipe ativa para a proxima sprint.</p>
            </article>
          </section>

          <section className="grid-card stack">
            <h3>Base pronta para Sprint 2</h3>
            <ul className="list">
              <li>Backend organizado em modulos para auth, models, schemas e rotas.</li>
              <li>Frontend com login, sessao local, guarda de rotas e logout.</li>
              <li>Seeds iniciais para usuarios, equipes e equipamentos de teste.</li>
            </ul>
          </section>
        </section>
      </main>
    </AuthGuard>
  );
}
