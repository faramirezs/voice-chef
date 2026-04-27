# RecipeDetailCard — Design Specification

## 1. Overview

A unified card component that lives in the **canvas slot** of the voice-first kitchen HUD. It merges the read-only recipe detail view and the editable scaling interface into a single, mode-aware component.

**Data sources**
- `recipe.detail` envelope — read-only recipe data from `GET /api/recipes/:id`
- `STATE_SNAPSHOT` with `widget: "recipe.scaling"` — editable scaling state

**Modes**
- **Detail mode** — read-only display of recipe metadata, yield, ingredients, instructions
- **Scaling mode** — yield fields become editable inputs; ingredient quantities show scaled values; dirty indicator and apply action surface

---

## 2. Visual Design System

### 2.1 Tokens (inherited from kitchen HUD)

| Token | Value | Usage |
|-------|-------|-------|
| `surface` | `#101a1a` | Page background |
| `surface-alt` | `#173232` | Card background (`KCard`) |
| `primary` | `#95cc62` | CTA buttons, accent highlights, focus rings |
| `primary-hover` | `#a9dc7a` | Button hover |
| `text` | `#b4c3a6` | Primary body text |
| `text-muted` | `#b4c3a6` | Labels, secondary text (opacity + context distinguishes) |
| `border` | `#355f4d` | Dividers, input borders |
| `success` | `#4ade80` | Status: active |
| `warning` | `#facc15` | Status: draft, dirty indicator |
| `error` | `#f87171` | Errors, destructive actions |

### 2.2 Typography (kitchen HUD scale)

| Element | Size | Weight | Line-height |
|---------|------|--------|-------------|
| Recipe name | `text-2xl` (24px) | `font-semibold` | 1.2 |
| Section heading | `text-sm` (14px) | `font-medium` | 1.4 |
| Body / table | `text-base` (16px) | `font-normal` | 1.5 |
| Label / caption | `text-xs` (12px) | `font-medium` | 1.4 |
| Mono (quantities) | `text-base` | `font-mono` | 1.2 |

HUD constraint: minimum readable size at arm's length is 16px body, 14px labels.

### 2.3 Spacing

- Card padding: `p-5` (20px)
- Section gap inside card: `gap-5` (20px)
- Inner section gap: `gap-3` (12px)
- Table row vertical padding: `py-2.5` (10px)
- Yield field gap: `gap-3` (12px)

---

## 3. Card Layout — Section by Section

### 3.1 Header

```
┌─────────────────────────────────────────────┐
│ [Recipe Name]                    [status] ✕ │
│ Description line...                         │
└─────────────────────────────────────────────┘
```

**Elements**
- **Recipe name** (`text-2xl font-semibold text-text`) — left-aligned, truncates with `truncate`
- **Status badge** — inline-flex pill, right of name
  - `draft`: `bg-warning/15 text-warning` + border `border-warning/30`
  - `active`: `bg-success/15 text-success` + border `border-success/30`
  - `archived`: `bg-border/30 text-text-muted` + border `border-border/50`
- **Close button** — absolute top-right, `h-8 w-8 rounded-full bg-surface/80 border border-border/50 text-text-muted`. Only shown when card is dispatched into canvas (not for permanent routes). Clears the canvas slot on click.

**States**
- Detail mode: badge shows recipe status from backend
- Scaling mode: in addition to status badge, a **dirty indicator** pill appears: `bg-warning/15 text-warning border-warning/30` with text "Unsaved changes"

### 3.2 Yield Bar

```
┌─────────────────────────────────────────────┐
│ Portions      Raw weight    Cooked weight   │
│ ┌─────────┐  ┌─────────┐   ┌─────────┐     │
│ │ 35      │  │ 1237g   │   │ 1237g   │     │
│ └─────────┘  └─────────┘   └─────────┘     │
│          [drive]                            │
└─────────────────────────────────────────────┘
```

**Detail mode** — three read-only display chips:
- Container: `rounded-2xl bg-surface/60 border border-border/40 px-4 py-3`
- Label above chip: `text-xs text-text-muted uppercase tracking-wide`
- Value inside chip: `text-lg font-mono font-medium text-text`
- The **drive field** (the field that drives scaling based on `yieldMode`) gets a `primary` accent: left border `border-l-2 border-l-primary` or a small `primary` badge inside the chip reading "drive"

**Scaling mode** — three editable inputs using `KInput` styling:
- `KInput` (`h-14 rounded-2xl bg-surface/90 border border-border text-text`)
- `type="number" step="any"`
- Drive field gets a `primary` focus ring by default and a "drive" micro-badge on the label
- When a value differs from original, show a small delta indicator: e.g. original `35` → current `42`, show `+7` in `text-xs text-primary` beside the input

**Layout**: `grid grid-cols-3 gap-3` on desktop, `grid-cols-1` on very narrow canvas (< 480px).

### 3.3 Ingredients Table

```
┌─────────────────────────────────────────────┐
│ INGREDIENTS                                 │
├──────────────┬──────────┬──────────┬────────┤
│ Ingredient   │ Prep     │ Quantity │ Unit   │
├──────────────┼──────────┼──────────┼────────┤
│ olivenöl     │ —        │ 405      │ g      │
│ ...          │ ...      │ ...      │ ...    │
└──────────────┴──────────┴──────────┴────────┘
```

**Detail mode columns**
1. **Ingredient** — `ingredient_name`
2. **Preparation** — `preparation` or em-dash
3. **Quantity** — `quantity` (original), right-aligned, `font-mono`
4. **Unit** — `unit`

**Scaling mode columns**
1. **Ingredient** — `name`
2. **Preparation** — `preparation` or em-dash
3. **Original** — `originalQuantity`, `text-text-muted` (smaller, `text-sm`)
4. **Scaled** — computed scaled quantity, right-aligned, `font-mono text-base`, highlighted with `text-primary` if ratio ≠ 1
5. **Unit** — `unit`

**Table styling**
- Header row: `border-b border-border/50 text-text-muted text-left text-xs uppercase tracking-wide`
- Data rows: `border-b border-border/20`
- Row hover: `hover:bg-surface/40` (subtle, for readability feedback)
- Last row: no bottom border
- Empty state: centered text "No ingredients listed" in `text-text-muted italic text-sm`

**Scroll behavior**: table body scrolls if ingredients exceed ~8 rows (`max-h-[320px] overflow-y-auto` with custom thin scrollbar `scrollbar-thin scrollbar-thumb-border/50 scrollbar-track-transparent`).

### 3.4 Instructions Section

```
┌─────────────────────────────────────────────┐
│ INSTRUCTIONS                                │
│                                             │
│ 1. Finely chop...                           │
│ 2. In a medium...                           │
│                                             │
└─────────────────────────────────────────────┘
```

- Section heading: `text-sm font-medium text-text-muted uppercase tracking-wide`
- Body: `text-base text-text whitespace-pre-line leading-relaxed`
- Container: no card nesting — flat within the main card. A subtle top border `border-t border-border/30 pt-4` separates it from the ingredients table.
- **Collapsible**: default collapsed in scaling mode (to keep yield fields and ingredients above the fold), default expanded in detail mode. Use a `KButton variant="ghost" size="icon"` chevron toggle.

### 3.5 Description Section

- Same styling as instructions
- **Detail mode**: visible if present
- **Scaling mode**: collapsed by default behind the same chevron pattern, or hidden entirely if viewport is tight. Priority: yield > ingredients > instructions > description.

### 3.6 Footer Actions (Scaling Mode Only)

```
┌─────────────────────────────────────────────┐
│                           [Cancel] [Apply]  │
└─────────────────────────────────────────────┘
```

- Only rendered in scaling mode AND when `dirty === true`
- **Apply**: `KButton` default variant. Text: "Apply to database". Disabled while `applying`. Shows spinner state.
- **Cancel**: `KButton` ghost variant. Text: "Reset". Reverts local state to `state.current` (not original — cancels local edits since last apply).
- Layout: `flex justify-end gap-3 pt-2`

### 3.7 Error State

If `state.error` is present in scaling mode, render above the yield bar:
```
┌─────────────────────────────────────────────┐
│ ⚠ Error loading recipe                      │
│ [error message]                             │
└─────────────────────────────────────────────┘
```
- Container: `bg-error/10 border border-error/30 rounded-2xl p-4`
- Text: `text-error font-semibold` for title, `text-sm` for detail

---

## 4. Mode Transitions

### 4.1 Mode Detection

The component derives its mode from the presence of scaling state:

```ts
const scalingState = isRecipeScalingState(agentState) ? agentState : null;
const mode = scalingState?.recipeId === recipe.id ? "scaling" : "detail";
```

- If no scaling state matches the displayed recipe → **Detail mode**
- If scaling state arrives for this recipe → **Scaling mode**

### 4.2 Transition: Detail → Scaling

**Trigger**: `STATE_SNAPSHOT` with `widget: "recipe.scaling"` and matching `recipeId` arrives.

**Visual changes** (immediate, no animation required for HUD clarity):
1. Yield chips morph into `KInput` fields
2. Ingredient table gains "Original" column, "Quantity" becomes "Scaled"
3. Dirty indicator badge fades in (if `isDirty` or local edits exist)
4. Footer actions appear when dirty
5. Instructions section auto-collapses to prioritize editing surface

### 4.3 Transition: Scaling → Detail

**Trigger**: User clicks "Apply" successfully, or canvas slot is cleared, or `ui.clear` envelope arrives.

**Visual changes**:
1. Inputs revert to read-only chips showing the newly applied values
2. Extra "Original" column disappears
3. Dirty indicator and footer actions removed
4. Instructions section expands

---

## 5. Component Props Interface

```ts
interface RecipeDetailCardProps {
  /** Populated by recipe.detail envelope via ui.render props */
  recipe?: {
    id: string;
    name: string;
    description: string | null;
    instructions: string | null;
    status: string;
    yield_mode: "count" | "weight";
    portion_size_grams: string | null;
    total_raw_weight_grams: string | null;
    total_cooked_weight_grams: string | null;
    portions_count_resolved: string | null;
    ingredients: Array<{
      id: string;
      ingredient_name: string;
      quantity: string;
      unit: string;
      quantity_grams: string | null;
      preparation: string | null;
      sort_order: number;
    }>;
  };
  /** Injected by SlotOutlet */
  slot?: string;
}
```

The component reads scaling state internally via `useAgentState()` — it is **not** passed as a prop.

---

## 6. Responsive Behavior

The canvas slot is centered and can vary in width depending on HUD layout.

| Canvas width | Behavior |
|-------------|----------|
| `>= 640px` | Full 3-column yield grid, 4–5 column ingredient table, side-by-side footer buttons |
| `480px – 639px` | 3-column yield grid (smaller inputs), ingredient table scrolls horizontally if needed |
| `< 480px` | Yield grid stacks to 1 column, ingredient table shows only Ingredient + Scaled + Unit (hide Prep and Original in scaling mode, hide Prep in detail mode) |

**HUD-specific**: The card should never exceed `max-w-2xl` (672px) in the canvas to maintain readability at arm's length. If the canvas is wider, the card centers with generous padding.

---

## 7. Interaction Patterns

### 7.1 Editing Yield Values
- Input `type="number" step="any"`
- On change: update local state, recompute ingredient ratios immediately
- Empty input = `null` (clears scaling for that field)
- Invalid (NaN) input: ignore, keep previous valid value
- **Drive field**: the field matching `yieldMode` is the scaling driver. Changing it recomputes all ingredient quantities. Changing non-drive fields does NOT back-compute the driver — they are display-only derivations.

### 7.2 Apply Flow
1. User edits fields → `dirty = true`
2. Footer shows Apply + Cancel
3. Click Apply → `sendMessage` with formatted scaling payload
4. Button enters loading state: disabled, text "Applying..."
5. On success (next STATE_SNAPSHOT with `isDirty: false`), revert to detail mode display with updated values
6. On error (next STATE_SNAPSHOT with `error`), show error banner and keep scaling mode active

### 7.3 Cancel / Reset
- Reverts local edits to the last received `state.current` values
- Does NOT clear the canvas slot
- If already matching `state.current`, button is effectively a no-op

### 7.4 Keyboard
- `Enter` inside yield input: moves focus to next input, does not submit
- `Escape`: cancels local edits (same as Reset button)
- Tab order: portions → raw weight → cooked weight → Apply → Cancel

---

## 8. Accessibility

- **Color contrast**: All text on `surface-alt` passes WCAG AA. Primary green `#95cc62` on `#173232` has ratio 5.8:1.
- **Focus rings**: `focus:ring-2 focus:ring-primary/50` on all interactive elements
- **Semantic HTML**: use `<table>` for ingredients, `<section>` with `aria-labelledby` for collapsible regions
- **Screen reader**: announce mode changes with `aria-live="polite"` on the card root. Badge text reads "Unsaved changes" when dirty.
- **Touch targets**: all buttons and inputs minimum 44px (KButton is 56px, KInput is 56px)

---

## 9. File Structure

```
frontend/kitchen/src/components/recipe/
├── RecipeDetailCard.tsx      # Main unified card
├── RecipeYieldBar.tsx        # Yield chips/inputs (mode-aware)
├── RecipeIngredientTable.tsx # Table with mode-aware columns
├── RecipeSection.tsx         # Reusable collapsible section wrapper
└── index.ts                  # Re-exports
```

**Registry entry** (in `agent-ui/registry.ts`):
```ts
const RecipeDetailCard = lazy(() =>
  import("@/components/recipe/RecipeDetailCard").then((m) => ({
    default: m.RecipeDetailCard,
  }))
);

registry.set("recipe_detail", {
  component: RecipeDetailCard as ComponentType<Record<string, unknown>>,
  defaultSlot: "canvas",
});
```

**Deprecate**: `RecipeScalingCard` in sticky slot. The unified card replaces it. Remove or repurpose `recipe_scaling` registry entry to dispatch `recipe_detail` with scaling state into canvas instead.

---

## 10. Edge Cases

| Scenario | Behavior |
|----------|----------|
| Recipe has no ingredients | Show empty state row in table |
| Recipe has no instructions | Collapse instructions section, heading hidden |
| Scaling state arrives for different recipe | Stay in detail mode for current recipe; ignore mismatched scaling state |
| Scaling state has `error` | Show error banner, keep yield fields editable, disable Apply |
| User clears canvas slot while in scaling mode | Component unmounts; local state lost (acceptable — state is canonical in agent) |
| `yieldMode === "weight"` | Raw weight is drive field; portions is derived display |
| `yieldMode === "count"` | Portions is drive field; weights are derived display |
| All yield values null | Show placeholder "—" in chips; empty inputs in scaling mode |
