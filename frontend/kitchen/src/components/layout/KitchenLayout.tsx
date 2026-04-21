import { ChatInterface } from "@/components/chat/ChatInterface";
import { AgentSlotProvider } from "./AgentSlotProvider";
import { SlotOutlet } from "./SlotOutlet";

export function KitchenLayout() {
  return (
    <AgentSlotProvider>
      <div className="h-full flex flex-col relative">
        {/* Sticky slot -- pinned below the header */}
        <div className="flex-shrink-0 px-4 pt-2">
          <SlotOutlet slot="sticky" />
        </div>

        {/* Main area: chat + main slot */}
        <div className="flex-1 flex min-h-0">
          {/* Chat takes center stage */}
          <div className="flex-1 min-w-0">
            <ChatInterface />
          </div>

          {/* Main slot -- center canvas content */}
          <div className="flex-shrink-0 w-96 border-l border-border/40 overflow-y-auto">
            <div className="p-4">
              <SlotOutlet slot="main" />
            </div>
          </div>
        </div>

        {/* Tray slot -- slides in from right */}
        <div className="absolute top-0 right-0 bottom-0 w-96 z-10 pointer-events-none">
          <SlotOutlet slot="tray" />
        </div>

        {/* Overlay slot -- full screen with backdrop */}
        <SlotOutlet slot="overlay" />
      </div>
    </AgentSlotProvider>
  );
}
