import { AgentSlotProvider } from "./AgentSlotProvider";
import { SlotOutlet } from "./SlotOutlet";
import { useAgent } from "@/hooks/useAgent";
import { useAgentSlots } from "./AgentSlotProvider";
import { HudVoiceBar } from "./HudVoiceBar";
import { HudStatusIndicator } from "./HudStatusIndicator";
import { CommandPalette } from "@/components/overlay/CommandPalette";
import { useEffect, useState } from "react";

export function HudCanvas() {
  return (
    <AgentSlotProvider>
      <HudCanvasInner />
    </AgentSlotProvider>
  );
}

function EmptyCanvas() {
  return (
    <div className="flex items-center justify-center h-full text-center">
      <div>
        <p className="text-2xl text-text">Tap the mic to start</p>
        <p className="text-base text-text-muted mt-2">
          Say a recipe name or ask a question
        </p>
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

  const hasCanvas = slots.canvas !== undefined;
  const hasOverlay = slots.overlay !== undefined;

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

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-surface/85 backdrop-blur-sm">
      {/* Sticky slot -- pinned top bar */}
      <div className="flex-shrink-0">
        <SlotOutlet slot="sticky" />
      </div>

      {/* Canvas -- primary content, centered */}
      <div className="flex-1 min-h-0 overflow-hidden flex items-center justify-center">
        {hasCanvas ? (
          <SlotOutlet slot="canvas" />
        ) : (
          <EmptyCanvas />
        )}
      </div>

      {/* Voice input + status indicator -- bottom center */}
      <div className="flex-shrink-0">
        <HudStatusIndicator />
        <HudVoiceBar />
      </div>

      {/* Chips -- bottom bar for action confirmations */}
      <div className="flex-shrink-0">
        <SlotOutlet slot="chips" />
      </div>

      {/* Notifications -- top-right corner */}
      <div className="absolute top-4 right-4 z-30">
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
