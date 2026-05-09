import { AgentSlotProvider } from "./AgentSlotProvider";
import { SlotOutlet } from "./SlotOutlet";
import {
  useAgent,
  useIsStreaming,
  useLastUserQuery,
  abortAgentRun,
} from "@/hooks/useAgent";
import { useAgentSlots } from "./AgentSlotProvider";
import { HudStatusIndicator } from "./HudStatusIndicator";
import { HudVoiceBar } from "./HudVoiceBar";

import { CommandPalette } from "@/components/overlay/CommandPalette";
import { useEffect, useState } from "react";
export function HudCanvas() {
  return (
    <AgentSlotProvider>
      <HudCanvasInner />
    </AgentSlotProvider>
  );
}

const IDLE_LABEL = "Tap or press Cmd + K / Ctrl + K to open command palette.";

function EmptyCanvas({
  onOpen,
  onAbort,
  currentQuery,
  isStreaming,
}: {
  onOpen: () => void;
  onAbort: () => void;
  currentQuery: string | null;
  isStreaming: boolean;
}) {
  const showingQuery = currentQuery !== null;
  const onClick = isStreaming ? onAbort : onOpen;
  const label = isStreaming
    ? `Cancel · ${currentQuery ?? ""}`
    : showingQuery
      ? (currentQuery as string)
      : IDLE_LABEL;
  const intentClass = isStreaming
    ? "border-text-secondary/40 text-text"
    : showingQuery
      ? "border-text-secondary/15 text-text-secondary/70"
      : "border-text-secondary/20 text-text-secondary";

  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
      <p className="text-2xl text-text">Voice Chef</p>
      <div className="w-full max-w-lg px-4 flex items-center justify-center gap-2">
        <button
          type="button"
          onClick={onClick}
          aria-label={isStreaming ? "Cancel current query" : "Open command palette"}
          className={`min-h-11 px-4 py-3 rounded-lg text-sm border ${intentClass} hover:bg-text-secondary/10 active:bg-text-secondary/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-text-secondary/40 transition-colors flex items-center gap-2 max-w-full`}
        >
          {isStreaming && (
            <span className="inline-block w-2 h-2 rounded-full bg-text animate-pulse flex-shrink-0" />
          )}
          <span className="line-clamp-2 text-left">{label}</span>
        </button>
      </div>
    </div>
  );
}


function HudCanvasInner() {
  // Single source of the AG-UI stream lifecycle.
  // Return values intentionally unused -- state flows through
  // useAgentState(), useIsStreaming(), useToolActivity().
  useAgent();

  const { slots } = useAgentSlots();
  const [paletteOpen, setPaletteOpen] = useState(false);
  const isStreaming = useIsStreaming();
  const lastUserQuery = useLastUserQuery();

  const hasCanvas = slots.canvas !== undefined;
  const hasOverlay = slots.overlay !== undefined;

  // Auto-close palette when canvas content arrives so user can see the card.
  useEffect(() => {
    if (hasCanvas && paletteOpen) {
      setPaletteOpen(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasCanvas]);

  // Cmd+K toggles the command palette.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // ESC aborts the in-flight agent run when the palette is closed.
  // CommandPalette owns its own ESC behaviour while open, so we gate on
  // !paletteOpen to avoid stealing that input.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !paletteOpen && isStreaming) {
        e.preventDefault();
        abortAgentRun();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [paletteOpen, isStreaming]);

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-surface/85 backdrop-blur-sm">
      {/* Sticky slot -- pinned top bar */}
      <div className="flex-shrink-0">
        <SlotOutlet slot="sticky" />
      </div>

      {/* Canvas -- primary content area */}
      <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
        {hasCanvas ? (
          <SlotOutlet slot="canvas" />
        ) : (
          <EmptyCanvas
            onOpen={() => setPaletteOpen(true)}
            onAbort={abortAgentRun}
            currentQuery={lastUserQuery}
            isStreaming={isStreaming}
          />
        )}
      </div>

      {/* Status indicator -- bottom center */}
      <div className="flex-shrink-0">
        <HudStatusIndicator />
      </div>


      {/* Voice bar -- bottom center, above status */}
      <div className="flex-shrink-0 flex justify-center">
        <HudVoiceBar />
      </div>

      {/* Chips -- bottom bar for action confirmations */}
      <div className="flex-shrink-0">
        <SlotOutlet slot="chips" />
      </div>

      {/* Notifications -- top-right corner */}
      {/* Notifications -- top-right corner, above overlays */}
      <div className="absolute top-4 right-4 z-50">
        <SlotOutlet slot="notifications" />
      </div>

      {/* Overlay -- fullscreen modal (command palette or agent overlay) */}
      {paletteOpen ? (
        <div className="absolute inset-0 z-40 bg-black/50 flex items-start justify-center pt-[15vh]">
          <CommandPalette onClose={() => setPaletteOpen(false)} />
        </div>
      ) : hasOverlay ? (
        <div className="absolute inset-0 z-40 bg-black/50 flex items-center justify-center">
          <SlotOutlet slot="overlay" />
        </div>
      ) : null}
    </div>
  );
}
