type MeResponse = {
  id: string;
  email: string;
  tenant_id: string;
  role: string;
  is_active: boolean;
};

const DUMMY_ME: MeResponse = {
  id: '2e3fca16-4f5a-4af7-9739-df2b6fa8baf4',
  email: 'chef-admin@voicechef.local',
  tenant_id: '0b796544-6414-4d62-8f1f-cd2f9f0ac0a0',
  role: 'editor',
  is_active: true,
};

export function ProfilePage() {
  const me = DUMMY_ME;

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Profile settings</h1>
        <p className="text-muted-foreground">Manage your profile information and settings.</p>
      </div>
      <div className="rounded-lg border p-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <p className="text-xs uppercase tracking-wide text-muted-foreground">User ID</p>
            <p className="text-sm font-medium break-all">{me.id}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Email</p>
            <p className="text-sm font-medium break-all">{me.email}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Tenant ID</p>
            <p className="text-sm font-medium break-all">{me.tenant_id}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Role</p>
            <p className="text-sm font-medium">{me.role}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Active</p>
            <p className="text-sm font-medium">{me.is_active ? 'Yes' : 'No'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
