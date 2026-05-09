import { lazy, type ComponentType } from "react";
// Recipe list grid for browsing recipes in the canvas slot.
const RecipeListView = lazy(() =>
  import("@/components/recipe/RecipeListView").then((m) => ({
    default: m.RecipeListView,
  }))
);


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

// Unified recipe card for the canvas slot.
const RecipeDetailCard = lazy(() =>
  import("@/components/recipe/RecipeDetailCard").then((m) => ({
    default: m.RecipeDetailCard,
  }))
);

// Rich recipe chips (replaces ConfirmationChips).
const RecipeChips = lazy(() =>
  import("@/components/chips/RecipeChips").then((m) => ({
    default: m.RecipeChips,
  }))
);

// Notification toast for the notifications slot.
const NotificationToast = lazy(() =>
  import("@/components/notifications/NotificationToast").then((m) => ({
    default: m.NotificationToast,
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
  defaultSlot: "canvas",
});

registry.set("recipe_list", {
  component: RecipeListView as ComponentType<Record<string, unknown>>,
  defaultSlot: "canvas",
});


registry.set("recipe_detail", {
  component: RecipeDetailCard as ComponentType<Record<string, unknown>>,
  defaultSlot: "canvas",
});

registry.set("confirmation_chips", {
  component: RecipeChips as ComponentType<Record<string, unknown>>,
  defaultSlot: "chips",
});

registry.set("notification", {
  component: NotificationToast as ComponentType<Record<string, unknown>>,
  defaultSlot: "notifications",
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
