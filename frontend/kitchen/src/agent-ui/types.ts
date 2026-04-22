/** Layout slot identifiers. Each slot has a distinct position and z-index. */
export type SlotId = "canvas" | "sticky" | "chips" | "notifications" | "overlay";

/** Shape emitted by the backend render_component tool. */
export interface RenderInstruction {
  type: "ui.render";
  version: "1";
  component: string;
  slot: SlotId;
  [key: string]: unknown;
}

/** State tracked per slot by AgentSlotProvider. */
export interface SlotState {
  component: string;
  props: Record<string, unknown>;
}

/** Type guard for the render instruction envelope. */
export function isRenderInstruction(value: unknown): value is RenderInstruction {
  if (typeof value !== "object" || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    obj.type === "ui.render" &&
    obj.version === "1" &&
    typeof obj.component === "string" &&
    typeof obj.slot === "string"
  );
}
