import { Outlet, Link } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar';
import { TooltipProvider } from '@/components/ui/tooltip';
import { AppSidebar } from '@/components/app-sidebar';

export function AppLayout() {
  const location = useLocation();

  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center gap-2 border-b bg-background px-4">
            <SidebarTrigger />
            <div className="ml-auto flex items-center gap-4 text-sm text-muted-foreground">
              <Link to="/terms" className="underline hover:text-primary">Terms</Link>
              <span>•</span>
              <Link to="/privacy" className="underline hover:text-primary">Privacy</Link>
            </div>
          </header>
          <main className="flex-1 p-8">
            <div key={location.pathname} className="page-fade-in">
              <Outlet />
            </div>
          </main>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  );
}
