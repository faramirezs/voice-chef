import { Suspense } from "react";
import type { SlotId } from "@/agent-ui/types";
import { getRegisteredComponent } from "@/agent-ui/registry";
import { useAgentSlots } from "./AgentSlotProvider";

function SlotSkeleton() {
  return (
    <div className="animate-pulse rounded-2xl bg-surface-alt/50 p-4">
      <div className="h-4 w-2/3 rounded bg-border/30" />
      <div className="mt-3 h-3 w-1/2 rounded bg-border/20" />
    </div>
  );
}

export function SlotOutlet({ slot }: { slot: SlotId }) {
  const { slots, clear } = useAgentSlots();
  const state = slots[slot];

  if (!state) return null;

  const entry = getRegisteredComponent(state.component);
  if (!entry) {
    return (
      <div className="rounded-2xl border border-error/30 bg-error/10 p-3 text-sm text-error">
        Unknown component: {state.component}
      </div>
    );
  }

  const Component = entry.component;

  // Notifications auto-dismiss; chips dismiss on action click. No X button.
  const hideClose = slot === "notifications" || slot === "chips";

  return (
    <Suspense fallback={<SlotSkeleton />}>
      <div data-slot={slot} className="relative">
        <Component {...state.props} slot={slot} />
        {!hideClose && (
          <button
            type="button"
            onClick={() => clear(slot)}
            className="absolute top-2 right-2 h-6 w-6 rounded-full bg-surface/80 border border-border/50 text-text-muted text-xs flex items-center justify-center hover:bg-error/20 hover:text-error transition-colors"
            aria-label={`Close ${slot} slot`}
          >
            \u00d7
          </button>
        )}
      </div>
    </Suspense>
  );
}
