***

# Design System Strategy: Voice Chef

## 1. Overview & Creative North Star

This design system is anchored by a Creative North Star we define as **"The Digital Sous Chef."**

A sous chef doesn't show off — they make the head chef look good and keep the kitchen running without friction. Every screen in Voice Chef should operate by the same principle: **get out of the way and serve the cook.** We reject both the sterile utility-app aesthetic and the editorial lifestyle aesthetic in equal measure. This is not a magazine, and it is not a spreadsheet. It is a professional tool built for a 40°C prep station, greasy hands, and a 45-second lunch rush window.

We achieve this **operational clarity** through:
* **Information Hierarchy:** Scaled ingredient quantities are the hero of every recipe screen — not photography.
* **Tonal Depth:** Color shifts rather than lines to define structure, keeping the UI calm and non-distracting.
* **Functional Warmth:** The palette feels organic and approachable, but every decision is earned by legibility and speed-of-use.

***

## 2. Colors & Surface Architecture

The palette is a sophisticated interplay of organic greens and baked earth tones, grounded by a warm, paper-like foundation. Colors must remain readable under bright overhead kitchen lighting and on screens mounted at counter distance.

### The "No-Line" Rule
**Strict Mandate:** Designers are prohibited from using 1px solid borders to section content. Structure must be defined through background color shifts. A recipe category section should use `surface_container_low` (#f5f3ee) against the main `background` (#fbf9f4). Lines create visual noise in an already noisy kitchen environment.

### Surface Hierarchy & Nesting

Treat the UI as a series of physical layers — like a clean marble prep surface with items placed deliberately on top.

* **Level 1 (Base):** `surface` (#fbf9f4) — The worktop itself.
* **Level 2 (Sectioning):** `surface_container_low` (#f5f3ee) — Subtle grouping for secondary content and ingredient blocks.
* **Level 3 (Interactive Elements):** `surface_container_highest` (#e4e2dd) — High-priority interactive areas, scaling controls, and voice state indicators.

### The "Glass & Gradient" Rule

Use Glassmorphism sparingly for floating overlays — a voice feedback indicator, a scaling control pinned to the bottom of a recipe. Kitchen screens are frequently glanced at, not read; overlays must never obscure ingredient data.
* **Spec:** Use `surface` with 70% opacity and a `20px` backdrop-blur.
* **Gradients:** For primary CTAs, use a subtle linear gradient from `primary` (#154212) to `primary_container` (#2d5a27) at 135°. Adds finish without compromising legibility.

***

## 3. Typography: The Operational Voice

We use a dual-typeface system that balances character with **extreme legibility at distance.** The spec for kitchen use requires that recipe steps are readable from 60cm away on a counter-mounted tablet or phone.

* **The Display Voice (Epilogue):** Used for `display` and `headline` scales — recipe names, section titles. Geometric warmth that reads confidently on large kitchen screens.
  * *Kitchen Note:* Use `display-lg` for recipe titles. Keep letter-spacing at **default or +1%** — tight fashion-style spacing sacrifices distance legibility in bright environments.

* **The Functional Voice (Plus Jakarta Sans):** Used for `title`, `body`, and `label` scales. The workhorse of the system.
  * Use `body-lg` (18px minimum) for **all ingredient quantities and recipe instructions.** A cook should never need to squint, lean in, or touch the screen to read a measurement.
  * Ingredient quantities (`150g`, `3 portions`) should be displayed in `title-md` or larger — they are the most safety-critical data on screen.

***

## 4. Elevation & Depth

Elevation signals what needs attention now. In a kitchen context, a floating element is almost always time-sensitive — a voice state indicator, a scaling result, a timer.

### The Layering Principle

Achieve depth by stacking tiers. A recipe card (`surface_container_lowest`) on a `surface_container` background creates a "soft lift" that feels natural. Never use depth decoratively — every layer must have a functional reason to exist.

### Ambient Shadows

Shadows are a last resort. When a floating effect is required (voice status pill, modal, FAB):
* **Color:** Use a tinted version of `on_surface` (#1b1c19) at 5–8% opacity.
* **Blur:** Minimum `32px` blur with `4px` Y-offset. Mimics soft overhead kitchen lighting.

### The "Ghost Border" Fallback

If accessibility requirements demand a container boundary, use a **Ghost Border:**
* **Token:** `outline_variant` (#c2c9bb) at 20% opacity. It should be felt, not seen.

***

## 5. Components

### Buttons & Interaction

* **Primary CTA:** Roundedness `full` (9999px). Uses the satin gradient (Primary → Primary-Container). Text is `on_primary`. Minimum touch target: **48×48px** — non-negotiable for wet or gloved hands.
* **Secondary:** Roundedness `lg` (1rem). Background is `secondary_container` (#fc845e), text is `on_secondary_container`.
* **Tertiary:** No container. Uses `primary` text with an icon. Used for low-priority actions only.

### Voice State Indicator

The most important kitchen-specific component. A persistent, unobtrusive pill (bottom of screen or top-right corner) that communicates the voice pipeline state:

* **Idle:** `surface_container_high` background, muted mic icon.
* **Listening:** Animated `primary` (#154212) pulse ring. Label: *"Listening…"*
* **Processing:** Spinner in `secondary` (#a13f1f). Label: *"Thinking…"*
* **Result Ready:** Brief `primary_container` flash, then auto-dismiss. The result is on screen — the indicator steps back.

Never use a full-screen overlay for voice states. The cook needs to keep eyes on their work.

### Cards & Recipe Feeds

* **Mandate:** Zero borders. Zero divider lines.
* **Layout:** Use `spacing-6` (2rem) between cards.
* **Image Handling:** Food photography is **supporting context,** not the architectural element. Thumbnail images are welcome; full-bleed hero images on list views waste vertical space a cook needs for ingredients. Reserve large imagery for the Recipe Detail view header only.
* **Corners:** Use `xl` (1.5rem) for main recipe cards.

### Recipe Detail — Ingredients-First Layout

Per product spec: **the scaled ingredient list is the primary view.** When a recipe is opened, the ingredients tab is the default. This is the one screen where the cook's eyes will return to most often mid-prep.

* Ingredient rows: `body-lg` quantity + unit (left-aligned, bold), ingredient name (right or below). High contrast.
* Scaling controls are pinned or immediately accessible — never buried.
* The Instructions tab is secondary. Nutrition, Cost, Allergens are tertiary tabs.

### Inputs & Search

* **Search Bar:** `surface_container_high` (#eae8e3) with `full` roundedness. No border. Large enough to tap with a thumb from the side of a hand.
* **Input Fields:** "Bottom-heavy" design — only a `2px outline` on the bottom edge when focused, using `secondary` (#a13f1f) terracotta. Avoid full input borders; they add visual weight without utility.
* **Scaling Input:** Treat as a first-class component. The portion/weight input on a recipe screen should be `title-lg` sized with large `+` / `−` steppers. A cook adjusting from 10 to 100 portions should never misfire a tap.

### Culinary-Specific Components

* **The Ingredient Chip:** `tertiary_fixed` (#f0e0cc) background, `title-sm` typography. Feels like a pantry label. Used for allergen tags, dietary flags.
* **Progressive Step Indicator:** Vertical line using `outline_variant` at 30% opacity, active steps highlighted in `secondary` terracotta. Used in prep instructions.
* **Multilingual Badge:** Small `surface_container_highest` chip indicating detected language (DE, EN, ES…). Appears in the AI chat thread next to voice transcript messages.

***

## 6. Do's and Don'ts

### Do:
* **Do** make ingredient quantities and scaled amounts the most visually dominant element on recipe screens.
* **Do** use `spacing-12` and `spacing-16` for top-level padding. Breathing room reduces cognitive load in a high-stress kitchen.
* **Do** use `tertiary` (#41382a) for captions and secondary metadata. The brown-grey tint reads as calm context, not noise.
* **Do** design every interactive element for a **48×48px minimum touch target.** Assume the user's hands are wet, gloved, or occupied.
* **Do** use high-contrast text on all critical data (quantities, temperatures, times). Test under simulated bright overhead lighting.

### Don't:
* **Don't** use 1px dividers between list items. Use `spacing-3` (1rem) of white space instead.
* **Don't** use "pure black" (#000000) or "pure white" (#FFFFFF). Stick to `on_surface` and `surface` tokens to maintain warmth.
* **Don't** use "Hard" corners (`none`). Even small utility components need at least `sm` (0.25rem) rounding.
* **Don't** treat food photography as the primary layout driver. A screen with a full-bleed hero image and no visible ingredient data has failed its user.
* **Don't** build screens that require a cook to scroll to find quantities. If scaling controls and ingredient data don't both fit above the fold, redesign the layout.
* **Don't** add decorative layers, overlapping text, or asymmetric grid layouts to recipe screens. Clarity over artfulness — always.

***

**Director's Final Note:** We are not building an inspiration engine. We are building a tool a cook trusts with their livelihood — their margins, their consistency, their reputation. If a screen feels crowded, remove a decorative element before removing data. The ingredient list is never optional. The beautiful photograph is. When in doubt: serve the cook, not the camera.
