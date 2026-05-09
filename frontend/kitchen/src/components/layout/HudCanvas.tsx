import { AgentSlotProvider } from "./AgentSlotProvider";
import { SlotOutlet } from "./SlotOutlet";
import { useAgent } from "@/hooks/useAgent";
import { useAgentSlots } from "./AgentSlotProvider";
import { HudStatusIndicator } from "./HudStatusIndicator";
import { HudVoiceBar } from "./HudVoiceBar";
import { CommandPalette } from "@/components/overlay/CommandPalette";
import { useEffect } from "react";
import { usePaletteOpen, togglePalette } from "@/lib/palette-state";

export function HudCanvas() {
  return (
    <AgentSlotProvider>
      <HudCanvasInner />
    </AgentSlotProvider>
  );
}

function EmptyCanvas() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
      <img
        src="/voice-chef-logo.svg"
        alt="Voice Chef"
        className="w-64 h-auto max-w-md opacity-80"
      />
      <div className="w-full max-w-lg px-4 flex items-center gap-2">
        <p className="flex-1 text-sm text-text-secondary">Use Cmd + K to open command palette.</p>
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
  const isPaletteOpen = usePaletteOpen();

  const hasCanvas = slots.canvas !== undefined;
  const hasOverlay = slots.overlay !== undefined;
  const hasChips = slots.chips !== undefined;

  // Cmd+K toggles the command palette.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        togglePalette();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-surface/85 backdrop-blur-sm">
      {/* Sticky slot -- pinned top bar */}
      <div className="flex-shrink-0">
        <SlotOutlet slot="sticky" />
      </div>

      {/* Canvas -- primary content area */}
      <div className="flex-1 min-h-0 overflow-hidden flex flex-col relative">
        {hasCanvas ? (
          <SlotOutlet slot="canvas" />
        ) : (
          <EmptyCanvas />
        )}

        {/* Chips -- floating panel overlay at bottom of canvas */}
        {hasChips && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 transition-all duration-200 ease-out">
            <div className="bg-surface/80 backdrop-blur-md border border-border/30 rounded-2xl shadow-lg px-4 py-3">
              <SlotOutlet slot="chips" />
            </div>
          </div>
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

      {/* Notifications -- top-right corner, above overlays */}
      <div className="absolute top-4 right-4 z-50">
        <SlotOutlet slot="notifications" />
      </div>

      {/* Overlay -- fullscreen modal (command palette or agent overlay) */}
      {isPaletteOpen ? (
        <div className="absolute inset-0 z-40 bg-black/50 flex items-start justify-center pt-[15vh]">
          <CommandPalette />
        </div>
      ) : hasOverlay ? (
        <div className="absolute inset-0 z-40 bg-black/50 flex items-center justify-center">
          <SlotOutlet slot="overlay" />
        </div>
      ) : null}
    </div>
  );
}
