import { cn } from '@/lib/utils';

function getRecipeInitials(title?: string | null) {
  if (!title) {
    return 'RC';
  }

  return title
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
    .slice(0, 2) || 'RC';
}

export function RecipeImagePlaceholder({
  title,
  className,
}: {
  title?: string | null;
  className?: string;
}) {
  const initials = getRecipeInitials(title);

  return (
    <div
      className={cn(
        'relative isolate overflow-hidden rounded-xl border bg-[linear-gradient(135deg,oklch(96%_0.02_110)_0%,oklch(92%_0.03_150)_42%,oklch(88%_0.04_170)_100%)] text-foreground',
        className,
      )}
      aria-hidden="true"
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,oklch(100%_0_0_/_0.45),transparent_42%),radial-gradient(circle_at_bottom_left,oklch(100%_0_0_/_0.35),transparent_38%)]" />
      <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full border border-foreground/10 bg-white/30 blur-2xl" />
      <div className="absolute -left-8 bottom-0 h-24 w-24 rounded-full bg-foreground/10 blur-2xl" />
      <div className="absolute inset-0 flex items-center justify-center p-6" />
      </div>
  );
}