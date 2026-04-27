import { useState, type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface RecipeSectionProps {
  title: string;
  defaultOpen?: boolean;
  forceOpen?: boolean;
  children: ReactNode;
}

export function RecipeSection({
  title,
  defaultOpen = true,
  forceOpen = false,
  children,
}: RecipeSectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  const isOpen = forceOpen || open;

  return (
    <div className="border-t border-border/30 pt-4">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-2 w-full text-left text-sm font-medium text-text-muted uppercase tracking-wide hover:text-text transition-colors"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={cn(
            "transition-transform shrink-0",
            isOpen && "rotate-90"
          )}
        >
          <polyline points="6 4 10 8 6 12" />
        </svg>
        {title}
      </button>
      {isOpen && <div className="mt-3">{children}</div>}
    </div>
  );
}
