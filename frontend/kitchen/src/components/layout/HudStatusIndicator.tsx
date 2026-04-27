import { useIsStreaming, useToolActivity } from "@/hooks/useAgent";

export function HudStatusIndicator() {
  const isStreaming = useIsStreaming();
  const toolActivity = useToolActivity();

  if (!isStreaming) return null;

  const running = toolActivity.filter((a) => a.status === "running");
  const label = running.length > 0
    ? running[running.length - 1].toolName
    : "Thinking";

  return (
    <div className="flex items-center justify-center gap-2 pb-2">
      <span className="inline-block h-2 w-2 rounded-full bg-primary animate-pulse" />
      <span className="text-sm text-text-muted">{label}</span>
    </div>
  );
}
