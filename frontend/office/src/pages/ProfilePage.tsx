import { useEffect, useState } from "react";

type MeResponse = {
  id: string;
  email: string;
  tenant_id: string;
  role: string;
  is_active: boolean;
};

export function ProfilePage() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadMe() {
      try {
        const resp = await fetch("/api/auth/me", { credentials: "same-origin" });
        if (!resp.ok) {
          if (resp.status === 401) {
            if (!mounted) return;
            setError("Not authenticated");
            setLoading(false);
            return;
          }
          throw new Error(`Failed to load profile (${resp.status})`);
        }
        const data = (await resp.json()) as MeResponse;
        if (!mounted) return;
        setMe(data);
      } catch (err: any) {
        if (!mounted) return;
        setError(err?.message ?? String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadMe();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Profile settings</h1>
        <p className="text-muted-foreground">Manage your profile information and settings.</p>
      </div>

      <div className="rounded-lg border p-6">
        {loading ? (
          <p>Loading profile…</p>
        ) : error ? (
          <p className="text-destructive">Error: {error}</p>
        ) : me ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">User ID</p>
              <p className="text-sm font-medium break-all">{me.id}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Email</p>
              <p className="text-sm font-medium break-all">{me.email}</p>
            </div>
            {/* <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Tenant ID</p>
              <p className="text-sm font-medium break-all">{me.tenant_id}</p>
            </div> */}
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Role</p>
              <p className="text-sm font-medium">{me.role}</p>
            </div>
            {/* <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Active</p>
              <p className="text-sm font-medium">{me.is_active ? "Yes" : "No"}</p>
            </div> */}
          </div>
        ) : (
          <p>No profile data available.</p>
        )}
      </div>
    </div>
  );
}
