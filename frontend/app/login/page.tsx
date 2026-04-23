"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { AuthGuard } from "@/components/auth-guard";
import { getApiBaseUrl, saveSession } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

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
        throw new Error(data.detail ?? "Nao foi possivel entrar.");
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

  return (
    <AuthGuard>
      <main className="page-shell">
        <section className="card stack-lg">
          <div className="stack">
            <p className="helper-text">Rede local de manutencao industrial</p>
            <h1 className="hero-title">Entrar no Manimaq</h1>
            <p className="hero-copy">
              Use seu usuario ou email para acessar o ambiente operacional.
            </p>
          </div>

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
        </section>
      </main>
    </AuthGuard>
  );
}
