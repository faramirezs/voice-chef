import { useCallback, useRef, useEffect, useState } from "react";
import { KButton } from "@/components/ui/KButton";
import { getSendMessage } from "@/hooks/useAgent";
import { useAgentSlots } from "@/components/layout/AgentSlotProvider";
import { cn } from "@/lib/utils";

// --- Legacy chip action (backward-compatible) ---
interface ChipAction {
  label: string;
  message: string;
  variant?: string;
}

// --- Rich chip item (new) ---
interface ChipItem {
  id: string;
  label: string;
  message: string;
  image_url?: string | null;
  description?: string | null;
  variant?: "default" | "ghost" | "destructive";
  action_type?: "agent" | "dispatch" | "navigate";
  action_payload?: Record<string, unknown> | null;
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

function isChipItems(value: unknown): value is ChipItem[] {
  if (!Array.isArray(value)) return false;
  return value.every(
    (item) =>
      typeof item === "object" &&
      item !== null &&
      typeof (item as Record<string, unknown>).id === "string" &&
      typeof (item as Record<string, unknown>).label === "string" &&
      typeof (item as Record<string, unknown>).message === "string"
  );
}

export function RecipeChips(props: Record<string, unknown>) {
  const { dispatch, clear } = useAgentSlots();
  const [focusIndex, setFocusIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Determine mode: rich items or legacy actions
  const items = isChipItems(props.items) ? (props.items as ChipItem[]) : [];
  const actions = items.length === 0 && isChipActions(props.actions) ? (props.actions as ChipAction[]) : [];
  const totalCount = typeof props.total_count === "number" ? props.total_count : 0;
  const overflow = totalCount > items.length ? totalCount - items.length : 0;

  // Keyboard navigation
  const totalCounts = items.length > 0 ? items.length : actions.length;

  useEffect(() => {
    if (focusIndex < 0) return;
    const btns = containerRef.current?.querySelectorAll<HTMLButtonElement>("[data-chip-index]");
    btns?.[focusIndex]?.focus();
  }, [focusIndex]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowRight") {
        e.preventDefault();
        setFocusIndex((prev) => (prev + 1) % totalCounts);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        setFocusIndex((prev) => (prev - 1 + totalCounts) % totalCounts);
      }
    },
    [totalCounts]
  );

  const handleAgentAction = useCallback(
    (message: string) => {
      try {
        getSendMessage()(message);
      } catch {
        // Agent not initialized
      }
      clear("chips");
    },
    [clear]
  );

  const handleDispatchAction = useCallback(
    (payload: Record<string, unknown>) => {
      const slot = (payload.slot as string) || "canvas";
      const component = (payload.component as string) || "";
      const componentProps = (payload.props as Record<string, unknown>) || {};
      if (component) {
        dispatch(slot, component, componentProps);
      }
      clear("chips");
    },
    [dispatch, clear]
  );

  const handleItemClick = useCallback(
    (item: ChipItem) => {
      const actionType = item.action_type || "agent";
      if (actionType === "dispatch" && item.action_payload) {
        handleDispatchAction(item.action_payload);
      } else {
        handleAgentAction(item.message);
      }
    },
    [handleAgentAction, handleDispatchAction]
  );

  // --- Rich items mode ---
  if (items.length > 0) {
    return (
      <div
        ref={containerRef}
        className="flex items-center gap-3 overflow-x-auto"
        onKeyDown={handleKeyDown}
        role="listbox"
        aria-label="Recipe options"
      >
        {items.map((item, index) => (
          <button
            key={item.id}
            data-chip-index={index}
            type="button"
            role="option"
            className={cn(
              "flex-shrink-0 flex items-center gap-3 rounded-xl p-2 pr-4 transition-all",
              "bg-surface-alt/60 hover:bg-surface-alt border border-border/30 hover:border-border/60",
              "focus:outline-none focus:ring-2 focus:ring-primary/50",
              item.variant === "destructive" && "border-error/30 hover:border-error/60 hover:bg-error/10",
            )}
            onClick={() => handleItemClick(item)}
          >
            {item.image_url && (
              <img
                src={item.image_url}
                alt={item.label}
                className="h-12 w-12 rounded-lg object-cover flex-shrink-0"
              />
            )}
            <div className="flex flex-col items-start text-left min-w-0">
              <span className="text-sm font-medium text-text truncate max-w-[140px]">
                {item.label}
              </span>
              {item.description && (
                <span className="text-xs text-text-muted truncate max-w-[140px]">
                  {item.description}
                </span>
              )}
            </div>
          </button>
        ))}
        {overflow > 0 && (
          <span className="flex-shrink-0 text-sm text-text-muted px-2">
            +{overflow} more
          </span>
        )}
      </div>
    );
  }

  // --- Legacy actions mode ---
  if (actions.length === 0) {
    return null;
  }

  return (
    <div
      ref={containerRef}
      className="flex flex-row gap-2"
      onKeyDown={handleKeyDown}
    >
      {actions.map((action, index) => {
        const isGhost = action.variant === "ghost";
        const isDestructive = action.variant === "destructive";

        return (
          <KButton
            key={index}
            data-chip-index={index}
            variant={isGhost ? "ghost" : undefined}
            className={isDestructive ? "bg-error/80 text-white hover:bg-error" : undefined}
            onClick={() => handleAgentAction(action.message)}
          >
            {action.label}
          </KButton>
        );
      })}
    </div>
  );
}
