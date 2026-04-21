import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type KInputProps = InputHTMLAttributes<HTMLInputElement>;

export const KInput = forwardRef<HTMLInputElement, KInputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "h-14 w-full min-w-0 px-5 text-lg rounded-2xl bg-surface/90 border border-border text-text placeholder:text-text-muted",
          "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/60",
          "disabled:opacity-50",
          className,
        )}
        {...props}
      />
    );
  },
);

KInput.displayName = "KInput";
