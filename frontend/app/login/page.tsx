"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AuthGuard } from "@/components/auth-guard";
import { extractErrorMessage } from "@/lib/api";
import { getApiBaseUrl, saveSession } from "@/lib/auth";

type BootstrapStatus = {
  bootstrap_required: boolean;
  users_count: number;
};

export default function LoginPage() {
  const router = useRouter();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [bootstrapName, setBootstrapName] = useState("");
  const [bootstrapUsername, setBootstrapUsername] = useState("");
  const [bootstrapEmail, setBootstrapEmail] = useState("");
  const [bootstrapPassword, setBootstrapPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [bootstrapStatus, setBootstrapStatus] = useState<BootstrapStatus | null>(null);
  const [isLoadingBootstrapStatus, setIsLoadingBootstrapStatus] = useState(true);

  useEffect(() => {
    let isActive = true;

    async function loadBootstrapStatus() {
      try {
        const response = await fetch(`${getApiBaseUrl()}/auth/bootstrap-status`);
        const data = (await response.json()) as BootstrapStatus;
        if (isActive) {
          setBootstrapStatus(data);
        }
      } catch {
        if (isActive) {
          setBootstrapStatus({ bootstrap_required: false, users_count: 0 });
        }
      } finally {
        if (isActive) {
          setIsLoadingBootstrapStatus(false);
        }
      }
    }

    loadBootstrapStatus();
    return () => {
      isActive = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ login, password }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(extractErrorMessage(data) || "Nao foi possivel entrar.");
      }

      saveSession(data);
      router.replace("/dashboard");
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Falha inesperada ao autenticar.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleBootstrapSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/bootstrap-admin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: bootstrapName,
          username: bootstrapUsername,
          email: bootstrapEmail,
          password: bootstrapPassword,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(extractErrorMessage(data) || "Nao foi possivel criar o primeiro administrador.");
      }

      saveSession(data);
      router.replace("/dashboard");
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Falha inesperada ao criar o primeiro administrador.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthGuard>
      <main className="page-shell">
        <section className="card stack-lg">
          <div className="stack">
            <p className="helper-text">Rede local de manutencao industrial</p>
            <h1 className="hero-title">
              {bootstrapStatus?.bootstrap_required ? "Configurar o Manimaq" : "Entrar no Manimaq"}
            </h1>
            <p className="hero-copy">
              {bootstrapStatus?.bootstrap_required
                ? "Nenhum usuario foi encontrado. Crie o primeiro administrador para iniciar o ambiente."
                : "Use seu usuario ou email para acessar o ambiente operacional."}
            </p>
          </div>

          {isLoadingBootstrapStatus ? (
            <div className="detail-box">
              <p className="helper-text">Verificando estado inicial do ambiente...</p>
            </div>
          ) : bootstrapStatus?.bootstrap_required ? (
            <form className="stack-lg" onSubmit={handleBootstrapSubmit}>
              <div className="stack">
                <label className="label" htmlFor="bootstrap-name">
                  Nome completo
                  <input
                    autoComplete="name"
                    className="input"
                    id="bootstrap-name"
                    onChange={(event) => setBootstrapName(event.target.value)}
                    required
                    value={bootstrapName}
                  />
                </label>

                <label className="label" htmlFor="bootstrap-username">
                  Usuario
                  <input
                    autoComplete="username"
                    className="input"
                    id="bootstrap-username"
                    onChange={(event) => setBootstrapUsername(event.target.value)}
                    required
                    value={bootstrapUsername}
                  />
                </label>

                <label className="label" htmlFor="bootstrap-email">
                  Email
                  <input
                    autoComplete="email"
                    className="input"
                    id="bootstrap-email"
                    onChange={(event) => setBootstrapEmail(event.target.value)}
                    required
                    type="email"
                    value={bootstrapEmail}
                  />
                </label>

                <label className="label" htmlFor="bootstrap-password">
                  Senha
                  <input
                    autoComplete="new-password"
                    className="input"
                    id="bootstrap-password"
                    onChange={(event) => setBootstrapPassword(event.target.value)}
                    required
                    type="password"
                    value={bootstrapPassword}
                  />
                </label>
              </div>

              {error ? <div className="error-box">{error}</div> : null}

              <button
                className="primary-button"
                disabled={
                  isSubmitting ||
                  !bootstrapName.trim() ||
                  !bootstrapUsername.trim() ||
                  !bootstrapEmail.trim() ||
                  !bootstrapPassword.trim()
                }
                type="submit"
              >
                {isSubmitting ? "Criando ambiente..." : "Criar primeiro administrador"}
              </button>
            </form>
          ) : (
            <form className="stack-lg" onSubmit={handleSubmit}>
              <div className="stack">
                <label className="label" htmlFor="login">
                  Usuario ou email
                  <input
                    autoComplete="username"
                    className="input"
                    id="login"
                    onChange={(event) => setLogin(event.target.value)}
                    required
                    value={login}
                  />
                </label>

                <label className="label" htmlFor="password">
                  Senha
                  <input
                    autoComplete="current-password"
                    className="input"
                    id="password"
                    onChange={(event) => setPassword(event.target.value)}
                    required
                    type="password"
                    value={password}
                  />
                </label>
              </div>

              {error ? <div className="error-box">{error}</div> : null}

              <button
                className="primary-button"
                disabled={isSubmitting || !login.trim() || !password.trim()}
                type="submit"
              >
                {isSubmitting ? "Entrando..." : "Entrar"}
              </button>
            </form>
          )}
        </section>
      </main>
    </AuthGuard>
  );
}
