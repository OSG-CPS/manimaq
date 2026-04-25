"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchApi } from "@/lib/api";
import { canAccessAdminModules, getStoredSession } from "@/lib/auth";

type DashboardSummary = {
  message: string;
  role: string;
  team: string | null;
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState("");
  const session = getStoredSession();
  const canManage = canAccessAdminModules(session?.user.role);

  useEffect(() => {
    async function loadSummary() {
      try {
        const data = await fetchApi<DashboardSummary>("/dashboard-summary");
        setSummary(data);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao carregar a area autenticada.");
      }
    }

    void loadSummary();
  }, []);

  return (
    <section className="stack-lg">
      <header className="panel stack">
        <div className="stack">
          <p className="helper-text">Painel autenticado do MVP</p>
          <h2 className="section-title">Resumo operacional</h2>
          <p className="helper-text">{summary?.message ?? "Carregando dados da sessao..."}</p>
        </div>
        {error ? <div className="error-box">{error}</div> : null}
      </header>

      <section className="grid-layout">
        <article className="grid-card">
          <h2>Autenticacao</h2>
          <p className="metric">{summary ? "OK" : "..."}</p>
          <p className="helper-text">JWT emitido, sessao persistida e rotas privadas protegidas.</p>
        </article>

        <article className="grid-card">
          <h2>Perfil</h2>
          <p className="metric">{session?.user.role ?? "--"}</p>
          <p className="helper-text">Perfis basicos: admin, gerente e operador.</p>
        </article>

        <article className="grid-card">
          <h2>Equipe</h2>
          <p className="metric">{summary?.team ?? "--"}</p>
          <p className="helper-text">Novo vinculo exige equipe ativa no backend.</p>
        </article>

        <article className="grid-card">
          <h2>Sprint</h2>
          <p className="metric">SPT5</p>
          <p className="helper-text">Alertas por regra e IA agora entram no fluxo operacional do MVP.</p>
        </article>
      </section>

      <section className="panel stack">
        <h3 className="section-title">Base atual do MVP</h3>
        <ul className="list">
          <li>Autorizacao por perfil aplicada no backend para os modulos administrativos.</li>
          <li>Cadastros de equipes, equipamentos e usuarios com persistencia em SQLite.</li>
          <li>Validacoes de email unico, TAG unica e bloqueio de equipe inativa.</li>
          <li>Fluxos operacionais prontos para registrar ocorrencias e medicoes com autor e data/hora.</li>
          <li>Ordens de servico podem ser abertas por gestao e executadas pela equipe responsavel com rastreabilidade.</li>
          <li>Alertas podem ser gerados a partir de ocorrencias e medicoes com sugestao de OS para analise gerencial.</li>
        </ul>
      </section>

      <section className="grid-layout">
        <Link className="grid-card card-link" href="/dashboard/alerts">
          <h2>Alertas</h2>
          <p className="helper-text">Consultar alertas por regra e enriquecimento de IA com sugestao de OS.</p>
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
