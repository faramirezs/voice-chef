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

/**
 * Silent kitchen-device login. Used on a kitchen-pi kiosk where the device
 * itself is the principal (not a specific person). Credentials live in the
 * runtime config injected by docker-entrypoint.sh from the host's env vars.
 *
 * Returns true if the cookie was set successfully, false otherwise.
 * Returns false (without attempting) if creds aren't configured — the caller
 * should then fall back to the regular office login redirect.
 */
export async function tryKitchenLogin(): Promise<boolean> {
  const email = window.__APP_CONFIG__?.kitchenEmail;
  const password = window.__APP_CONFIG__?.kitchenPassword;
  if (!email || !password) return false;

  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  try {
    const resp = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
      credentials: "same-origin",
    });
    return resp.ok;
  } catch {
    return false;
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
