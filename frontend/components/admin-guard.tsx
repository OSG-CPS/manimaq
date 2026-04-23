"use client";

import Link from "next/link";

import { canAccessAdminModules, getStoredSession } from "@/lib/auth";

export function AdminGuard({ children }: { children: React.ReactNode }) {
  const session = getStoredSession();

  if (!canAccessAdminModules(session?.user.role)) {
    return (
      <section className="panel stack">
        <div className="error-box">
          Seu perfil nao tem permissao para acessar os cadastros administrativos.
        </div>
        <Link className="secondary-button inline-button" href="/dashboard">
          Voltar ao resumo
        </Link>
      </section>
    );
  }

  return <>{children}</>;
}
