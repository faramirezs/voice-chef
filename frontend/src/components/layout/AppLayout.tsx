import { Outlet } from 'react-router-dom';
import { TooltipProvider } from '@/components/ui/tooltip';

export function AppLayout() {
  return (
    <TooltipProvider>
          <main className="flex-1 p-8">
            <Outlet />
          </main>
    </TooltipProvider>
  );
}