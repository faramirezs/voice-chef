import {
  createContext,
  useCallback,
  useContext,
  useEffect,
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
  /** ID of the recipe currently shown in canvas, if any. */
  selectedRecipeId: string | null;
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
  const [selectedRecipeId, setSelectedRecipeId] = useState<string | null>(null);


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

  // Derive selected recipe from canvas slot props.
  useEffect(() => {
    const canvas = slots.canvas;
    if (canvas?.component === "recipe_detail") {
      const recipe = canvas.props.recipe as Record<string, unknown> | undefined;
      if (recipe && typeof recipe.id === "string") {
        setSelectedRecipeId(recipe.id);
        return;
      }
    }
    setSelectedRecipeId(null);
  }, [slots.canvas]);

  // Subscribe to ui.render envelopes from the agent.
  useEnvelope("ui.render", (envelope) => {
    if (!isRenderInstruction(envelope)) return;
    const { slot, component, ...rest } = envelope;
    dispatch(slot, component, rest);
  });

  // Subscribe to ui.clear envelopes from the agent.
  useEnvelope("ui.clear", (envelope) => {
    const slot = envelope.slot as SlotId;
    if (slot) clear(slot);
  });

  const value = useMemo(
    () => ({ slots, dispatch, clear, selectedRecipeId }),
    [slots, dispatch, clear, selectedRecipeId]
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
