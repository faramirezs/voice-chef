import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type KButtonVariant = "default" | "ghost";
type KButtonSize = "default" | "icon";

interface KButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: KButtonVariant;
  size?: KButtonSize;
}

export function KButton({
  className,
  variant = "default",
  size = "default",
  ...props
}: KButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-2xl transition-colors outline-none disabled:opacity-40 disabled:cursor-not-allowed",
        variant === "default" &&
          "bg-primary text-[#16270f] font-semibold hover:bg-primary-hover shadow-[0_10px_26px_rgba(87,128,50,0.35)]",
        variant === "ghost" &&
          "bg-surface-alt text-text-muted ring-1 ring-border/70 hover:text-text hover:bg-border/35",
        size === "default" && "h-14 px-6 text-lg",
        size === "icon" && "h-14 w-14",
        className,
      )}
      {...props}
    />
  );
}
