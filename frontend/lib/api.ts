import { clearSession, getApiBaseUrl, getStoredSession } from "@/lib/auth";

type RequestOptions = RequestInit & {
  skipJsonBody?: boolean;
};

export async function fetchApi<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const session = getStoredSession();
  const headers = new Headers(options.headers);

  if (!headers.has("Content-Type") && options.body && !options.skipJsonBody) {
    headers.set("Content-Type", "application/json");
  }

  if (session?.access_token) {
    headers.set("Authorization", `Bearer ${session.access_token}`);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearSession();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Sessao expirada. Faca login novamente.");
  }

  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    throw new Error((data as { detail?: string } | null)?.detail ?? "Falha na requisicao.");
  }

  return data as T;
}
