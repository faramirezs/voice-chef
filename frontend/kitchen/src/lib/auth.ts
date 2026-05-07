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
  const officeUrl = import.meta.env.VITE_OFFICE_URL;
  if (officeUrl) {
    // Dev: kitchen and office on different origins
    window.location.href = officeUrl + "/login";
  } else {
    // Prod: behind shared proxy, same origin
    window.location.href = "/login";
  }
}

export async function logout(): Promise<void> {
  await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
  redirectToOfficeLogin();
}
