import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  {
    to: '/',
    label: 'Recipes',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 shrink-0">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        <line x1="9" y1="7" x2="15" y2="7" />
        <line x1="9" y1="11" x2="15" y2="11" />
      </svg>
    ),
  },
  {
    to: '/planner',
    label: 'Planner',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 shrink-0">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </svg>
    ),
  },
  {
    to: '/notes',
    label: 'Notes',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 shrink-0">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="9" y1="13" x2="15" y2="13" />
        <line x1="9" y1="17" x2="13" y2="17" />
      </svg>
    ),
  },
];

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 h-screen flex flex-col bg-sidebar border-r border-sidebar-border">
      {/* Logo / app name */}
      <div className="h-14 flex items-center gap-2.5 px-4 border-b border-sidebar-border">
        <div className="w-7 h-7 rounded-lg bg-sidebar-primary flex items-center justify-center">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-sidebar-primary-foreground">
            <path d="M3 11l19-9-9 19-2-8-8-2z" />
          </svg>
        </div>
        <span className="font-semibold text-sidebar-foreground text-sm tracking-tight">
          Voice Chef
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {NAV_ITEMS.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-accent text-white'
                  : 'text-white hover:bg-sidebar-accent/50',
              )
            }
          >
            {icon}
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
