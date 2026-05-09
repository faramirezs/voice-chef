/**
 * Full-canvas loading skeleton shown while the agent is processing a request.
 * Dispatched into the canvas slot synthetically by useAgent.sendMessage().
 */
export function CanvasLoadingState() {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full p-6 animate-pulse">
      {/* Title skeleton */}
      <div className="w-2/3 h-8 rounded-lg bg-surface-alt/60 mb-6" />
      {/* Meta row skeleton */}
      <div className="w-1/3 h-4 rounded bg-surface-alt/40 mb-8" />
      {/* Content block skeleton */}
      <div className="w-full max-w-lg space-y-4">
        <div className="h-4 rounded bg-surface-alt/40 w-full" />
        <div className="h-4 rounded bg-surface-alt/30 w-5/6" />
        <div className="h-4 rounded bg-surface-alt/20 w-4/6" />
      </div>
      {/* Table skeleton */}
      <div className="w-full max-w-lg mt-8 space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="h-4 rounded bg-surface-alt/30 flex-[3]" />
            <div className="h-4 rounded bg-surface-alt/20 flex-[1]" />
            <div className="h-4 rounded bg-surface-alt/20 flex-[1]" />
          </div>
        ))}
      </div>
    </div>
  );
}
