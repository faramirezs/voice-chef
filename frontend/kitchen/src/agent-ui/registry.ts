import { lazy, type ComponentType } from "react";

/**
 * Component registry: maps component keys (from render_component tool)
 * to lazy-loaded React components.
 *
 * Each component receives its own props derived from the render instruction.
 * Lazy loading keeps the initial bundle small and provides Suspense boundaries.
 */

// Lazy-loaded placeholder for testing slot wiring.
const PlaceholderCard = lazy(() =>
  import("@/components/layout/PlaceholderCard").then((m) => ({
    default: m.PlaceholderCard,
  }))
);

// Recipe scaling widget for the sticky slot.
const RecipeScalingCard = lazy(() =>
  import("@/components/chat/RecipeScalingCard").then((m) => ({
    default: m.RecipeScalingCard,
  }))
);

export interface RegisteredComponent {
  component: ComponentType<Record<string, unknown>>;
  /** Default slot if the agent omits one. */
  defaultSlot: string;
}

const registry = new Map<string, RegisteredComponent>();

registry.set("placeholder", {
  component: PlaceholderCard as ComponentType<Record<string, unknown>>,
  defaultSlot: "main",
});

registry.set("recipe_scaling", {
  component: RecipeScalingCard as ComponentType<Record<string, unknown>>,
  defaultSlot: "sticky",
});

export function getRegisteredComponent(
  key: string
): RegisteredComponent | undefined {
  return registry.get(key);
}

export function registerComponent(
  key: string,
  entry: RegisteredComponent
): void {
  registry.set(key, entry);
}
