import { useEffect, useRef } from "react";
import { KCard } from "@/components/ui/KCard";
import { useAgentSlots } from "@/components/layout/AgentSlotProvider";


const LEVEL_STYLES: Record<string, string> = {
  info: "border-primary/30 bg-primary/10 text-primary",
  success: "border-green-500/30 bg-green-500/10 text-green-400",
  warning: "border-warning/30 bg-warning/10 text-warning",
  error: "border-error/30 bg-error/10 text-error",
};

const LEVEL_ICONS: Record<string, string> = {
  info: "\u2139",       // ℹ
  success: "\u2713",   // ✓
  warning: "\u26A0",   // ⚠
  error: "\u2717",     // ✗
};

export function NotificationToast(props: Record<string, unknown>) {
  const { clear } = useAgentSlots();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const message = typeof props.message === "string" ? props.message : "";
  const rawLevel = typeof props.level === "string" ? props.level : "info";
  const level = LEVEL_STYLES[rawLevel] ? rawLevel : "info";
  const rawDuration = typeof props.duration === "number" ? props.duration : 5000;
  const duration = rawDuration > 0 ? rawDuration : 5000;

  useEffect(() => {
    timerRef.current = setTimeout(() => {
      clear("notifications");
    }, duration);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [clear, duration]);

  return (
    <KCard
      className={`flex items-center gap-3 px-4 py-3 border ${LEVEL_STYLES[level]}`}
    >
      <span className="text-lg select-none" aria-hidden="true">
        {LEVEL_ICONS[level]}
      </span>
      <span className="text-sm font-medium">{message}</span>
    </KCard>
  );
}
