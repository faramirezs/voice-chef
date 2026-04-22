import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useEnvelope } from "@/hooks/useAgent";
import { isRenderInstruction, type SlotId, type SlotState } from "@/agent-ui/types";


interface SlotContextValue {
  /** Current state of each slot. undefined = empty. */
  slots: Record<SlotId, SlotState | undefined>;
  /** Dispatch a component into a slot. */
  dispatch: (slot: SlotId, component: string, props?: Record<string, unknown>) => void;
  /** Clear a slot (e.g. user closes an overlay). */
  clear: (slot: SlotId) => void;
}

const SlotContext = createContext<SlotContextValue | null>(null);

const EMPTY_SLOTS: Record<SlotId, SlotState | undefined> = {
  canvas: undefined,
  sticky: undefined,
  chips: undefined,
  notifications: undefined,
  overlay: undefined,
};

export function AgentSlotProvider({ children }: { children: ReactNode }) {
  const [slots, setSlots] = useState(EMPTY_SLOTS);

  const dispatch = useCallback(
    (slot: SlotId, component: string, props: Record<string, unknown> = {}) => {
      setSlots((prev) => ({
        ...prev,
        [slot]: { component, props },
      }));
    },
    []
  );

  const clear = useCallback((slot: SlotId) => {
    setSlots((prev) => ({
      ...prev,
      [slot]: undefined,
    }));
  }, []);

  // Subscribe to ui.render envelopes from the agent.
  useEnvelope("ui.render", (envelope) => {
    if (!isRenderInstruction(envelope)) return;
    const { slot, component, ...rest } = envelope;
    dispatch(slot, component, rest);
  });

  const value = useMemo(
    () => ({ slots, dispatch, clear }),
    [slots, dispatch, clear]
  );

  return (
    <SlotContext.Provider value={value}>{children}</SlotContext.Provider>
  );
}

export function useAgentSlots(): SlotContextValue {
  const ctx = useContext(SlotContext);
  if (!ctx) {
    throw new Error("useAgentSlots must be used within AgentSlotProvider");
  }
  return ctx;
}
