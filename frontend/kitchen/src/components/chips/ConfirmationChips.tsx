import { useCallback } from "react";
import { KButton } from "@/components/ui/KButton";
import { getSendMessage } from "@/hooks/useAgent";
import { useAgentSlots } from "@/components/layout/AgentSlotProvider";

interface ChipAction {
  label: string;
  message: string;
  variant?: string; // "default" | "ghost" | "destructive"
}

function isChipActions(value: unknown): value is ChipAction[] {
  if (!Array.isArray(value)) return false;
  return value.every(
    (item) =>
      typeof item === "object" &&
      item !== null &&
      typeof (item as Record<string, unknown>).label === "string" &&
      typeof (item as Record<string, unknown>).message === "string"
  );
}

export function ConfirmationChips(props: Record<string, unknown>) {
  const { clear } = useAgentSlots();
  const actions = isChipActions(props.actions) ? props.actions : [];

  if (actions.length === 0) {
    return null;
  }

  const handleClick = useCallback(
    (message: string) => {
      try {
        getSendMessage()(message);
      } catch {
        // Agent not initialized -- silently ignore
      }
      clear("chips");
    },
    [clear],
  );

  return (
    <div className="flex flex-row gap-2">
      {actions.map((action, index) => {
        const isGhost = action.variant === "ghost";
        const isDestructive = action.variant === "destructive";

        return (
          <KButton
            key={index}
            variant={isGhost ? "ghost" : undefined}
            className={isDestructive ? "bg-error/80 text-white hover:bg-error" : undefined}
            onClick={() => handleClick(action.message)}
          >
            {action.label}
          </KButton>
        );
      })}
    </div>
  );
}