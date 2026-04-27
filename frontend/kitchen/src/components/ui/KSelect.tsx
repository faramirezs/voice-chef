import { forwardRef, type SelectHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface SelectOption {
  value: string;
  label: string;
}

type KSelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  options: SelectOption[];
};

export const KSelect = forwardRef<HTMLSelectElement, KSelectProps>(
  ({ className, options, ...props }, ref) => {
    return (
      <div className="relative w-full">
        <select
          ref={ref}
          className={cn(
            "h-14 w-full min-w-0 px-5 pr-12 text-lg rounded-2xl bg-surface/90 border border-border text-text appearance-none",
            "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/60",
            "disabled:opacity-50",
            className
          )}
          {...props}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <svg
          className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-text-muted"
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="4 6 8 10 12 6" />
        </svg>
      </div>
    );
  }
);

KSelect.displayName = "KSelect";
