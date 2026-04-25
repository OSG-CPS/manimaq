import { clearSession, getApiBaseUrl, getStoredSession } from "@/lib/auth";

type RequestOptions = RequestInit & {
  skipJsonBody?: boolean;
};

export function extractErrorMessage(data: unknown): string {
  if (!data || typeof data !== "object") {
    return "Falha na requisicao.";
  }

  const detail = (data as { detail?: unknown }).detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const firstItem = detail[0];
    if (typeof firstItem === "string" && firstItem.trim()) {
      return firstItem;
    }
    if (firstItem && typeof firstItem === "object") {
      const message = (firstItem as { msg?: unknown }).msg;
      if (typeof message === "string" && message.trim()) {
        return message;
      }
    }
  }

  if (detail && typeof detail === "object") {
    const message = (detail as { msg?: unknown }).msg;
    if (typeof message === "string" && message.trim()) {
      return message;
    }
  }

  return "Falha na requisicao.";
}

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
    throw new Error(extractErrorMessage(data));
  }

  return data as T;
}
