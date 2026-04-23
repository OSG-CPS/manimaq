export const AUTH_STORAGE_KEY = "manimaq.auth";

export type AuthUser = {
  id: number;
  name: string;
  username: string;
  email: string;
  role: "admin" | "gerente" | "operador";
  active: boolean;
  team_id: number | null;
  team?: {
    id: number;
    name: string;
    sector: string;
    active: boolean;
  } | null;
  created_at: string;
};

export type AuthSession = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
}

export function getStoredSession(): AuthSession | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
  }
}

export function saveSession(session: AuthSession): void {
  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  window.localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function canAccessAdminModules(role: AuthUser["role"] | undefined): boolean {
  return role === "admin" || role === "gerente";
}
