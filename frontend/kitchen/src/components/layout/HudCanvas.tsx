import { AgentSlotProvider } from "./AgentSlotProvider";
import { SlotOutlet } from "./SlotOutlet";
import { useAgent } from "@/hooks/useAgent";
import { useAgentSlots } from "./AgentSlotProvider";
import { HudStatusIndicator } from "./HudStatusIndicator";

import { CommandPalette } from "@/components/overlay/CommandPalette";
import { VoiceInput } from "@/components/chat/VoiceInput";
import { getSendMessage } from "@/hooks/useAgent";
import { useEffect, useState } from "react";

export function HudCanvas() {
  return (
    <AgentSlotProvider>
      <HudCanvasInner />
    </AgentSlotProvider>
  );
}

function EmptyCanvas({ onOpenPalette }: { onOpenPalette: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
      <p className="text-2xl text-text">Voice Chef</p>
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
  const [paletteOpen, setPaletteOpen] = useState(false);

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
          <EmptyCanvas onOpenPalette={() => setPaletteOpen(true)} />
        )}
      </div>

      {/* Status indicator -- bottom center */}
      <div className="flex-shrink-0">
        <HudStatusIndicator />
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
