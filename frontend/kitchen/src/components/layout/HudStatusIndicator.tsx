import { useIsStreaming, useToolActivity, getAbortAgent } from "@/hooks/useAgent";

export function HudStatusIndicator() {
  const isStreaming = useIsStreaming();
  const toolActivity = useToolActivity();

  if (!isStreaming) return null;

  const running = toolActivity.filter((a) => a.status === "running");
  const label = running.length > 0
    ? running[running.length - 1].toolName
    : "Thinking";

  const handleStop = () => {
    getAbortAgent()();
  };

  return (
    <div className="flex items-center justify-center gap-2 py-2 px-4">
      <div className="flex items-center gap-2 bg-surface-alt/80 backdrop-blur-md border border-border/30 rounded-full px-4 py-2 shadow-lg">
        {/* Animated spinner */}
        <svg
          className="animate-spin h-5 w-5 text-primary"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="3"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
        <span className="text-sm font-semibold text-text">{label}</span>
        {/* Stop button */}
        <button
          type="button"
          onClick={handleStop}
          className="ml-1 flex items-center justify-center h-6 w-6 rounded-full bg-error/20 hover:bg-error/40 text-error transition-colors"
          aria-label="Stop agent"
          title="Stop"
        >
          <svg
            className="h-3 w-3"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <rect x="6" y="6" width="12" height="12" rx="1" />
          </svg>
        </button>
      </div>
    </div>
  );
}
