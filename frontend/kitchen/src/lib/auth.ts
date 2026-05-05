export interface CurrentUser {
  id: string;
  email: string;
  role: string;
}

export async function getCurrentUser(): Promise<CurrentUser | null> {
  try {
    const resp = await fetch("/api/auth/me", { credentials: "same-origin" });
    if (!resp.ok) {
      if (resp.status === 401) return null;
      throw new Error(`Auth check failed (${resp.status})`);
    }
    return (await resp.json()) as CurrentUser;
  } catch {
    return null;
  }
}

export function redirectToOfficeLogin(): void {
  // Runtime > build-time > dev default. Runtime wins so the same image
  // can target different office hosts (Pi → Tailscale, server → localhost, etc.).
  const officeUrl =
    window.__APP_CONFIG__?.officeUrl ||
    import.meta.env.VITE_OFFICE_URL ||
    "http://localhost:8080";
  window.location.href = officeUrl + "/login";
}

export async function logout(): Promise<void> {
  await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
  redirectToOfficeLogin();
}
