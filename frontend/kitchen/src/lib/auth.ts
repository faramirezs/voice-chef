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

/**
 * Handle a 401 from any kitchen API call. Tries kitchen-device silent login
 * first; if that succeeds the page is reloaded so the next render sees a
 * fresh session. Falls back to the office redirect when no kitchen creds
 * are configured or silent login fails.
 *
 * A simple sessionStorage timestamp guards against reload loops if the
 * cookie keeps being rejected after a "successful" login.
 */
export async function handleAuthFailure(): Promise<void> {
  const LOOP_GUARD_KEY = "kitchen-auth-loop-guard";
  const last = Number(sessionStorage.getItem(LOOP_GUARD_KEY) || "0");
  if (Date.now() - last < 5000) {
    sessionStorage.removeItem(LOOP_GUARD_KEY);
    redirectToOfficeLogin();
    return;
  }

  if (await tryKitchenLogin()) {
    sessionStorage.setItem(LOOP_GUARD_KEY, String(Date.now()));
    window.location.reload();
    return;
  }

  redirectToOfficeLogin();
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
