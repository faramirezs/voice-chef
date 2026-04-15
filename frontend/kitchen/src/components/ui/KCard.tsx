import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type KCardProps = HTMLAttributes<HTMLDivElement>;

export function KCard({ className, ...props }: KCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-border/70 bg-surface-alt/90 shadow-[0_8px_22px_rgba(0,0,0,0.18)]",
        className,
      )}
      {...props}
    />
  );
}
