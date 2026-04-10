import { Outlet } from 'react-router-dom';

export function AppLayout() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <Outlet />
    </div>
  );
}
