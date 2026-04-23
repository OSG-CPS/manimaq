"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { LogoutButton } from "@/components/logout-button";
import { fetchApi } from "@/lib/api";
import { AuthSession, AuthUser, canAccessAdminModules, getStoredSession, saveSession } from "@/lib/auth";

const navigationItems = [
  { href: "/dashboard", label: "Resumo" },
  { href: "/dashboard/teams", label: "Equipes" },
  { href: "/dashboard/equipments", label: "Equipamentos" },
  { href: "/dashboard/users", label: "Usuarios" },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [session, setSession] = useState<AuthSession | null>(null);

  useEffect(() => {
    const storedSession = getStoredSession();
    if (!storedSession) {
      router.replace("/login");
      return;
    }

    const activeSession: AuthSession = storedSession;
    setSession(activeSession);

    async function refreshSession() {
      try {
        const user = await fetchApi<AuthUser>("/session");
        const nextSession: AuthSession = {
          access_token: activeSession.access_token,
          token_type: activeSession.token_type,
          user,
        };
        saveSession(nextSession);
        setSession(nextSession);
      } catch {
        // A funcao fetchApi ja trata expiracao da sessao.
      }
    }

    void refreshSession();
  }, [router]);

  const canManage = canAccessAdminModules(session?.user.role);

  return (
    <AuthGuard>
      <main className="dashboard-shell">
        <section className="dashboard-frame dashboard-grid">
          <aside className="sidebar-panel stack">
            <div className="stack">
              <p className="helper-text">Sprint 2 em execucao</p>
              <h1 className="sidebar-title">Manimaq</h1>
              <p className="helper-text">
                {session ? `${session.user.name} (${session.user.role})` : "Carregando sessao..."}
              </p>
              <p className="helper-text">
                {session?.user.team ? `${session.user.team.name} · ${session.user.team.sector}` : "Sem equipe"}
              </p>
            </div>

            <nav className="stack-sm">
              {navigationItems.map((item) => {
                if (!canManage && item.href !== "/dashboard") {
                  return null;
                }

                const isActive = pathname === item.href;
                return (
                  <Link
                    className={`nav-link ${isActive ? "nav-link-active" : ""}`}
                    href={item.href}
                    key={item.href}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <div className="sidebar-footer stack">
              <p className="helper-text">
                {canManage
                  ? "Area administrativa habilitada para cadastros da Sprint 2."
                  : "Seu perfil pode consultar o resumo, mas nao acessa os cadastros administrativos."}
              </p>
              <LogoutButton />
            </div>
          </aside>

          <section className="content-panel">{children}</section>
        </section>
      </main>
    </AuthGuard>
  );
}
