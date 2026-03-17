# Data Model (Current Schema 010)

Source of truth for current state: `db/schema_alembic_010.sql`.

## Current Tables (Schema 010)

### Core
- `tenants`
- `users`
- `recipes`
- `ingredients`
- `ingredient_nutrition`
- `units`
- `ingredient_units`
- `recipe_ingredients`

### Classification and labeling
- `categories`
- `tags`
- `recipe_categories`
- `recipe_tags`
- `allergens`
- `additives`
- `ingredient_allergens`
- `ingredient_additives`

### Pricing and nutrition
- `ingredient_prices`
- `ingredient_prices_latest` (view)
- `nutrition_facts`
- `recipe_nutrition`

### Media, files, versions, audit
- `files`
- `recipe_photos`
- `recipe_versions`
- `audit_logs`
- `ingredient_merge_audit`

### Migration metadata
- `alembic_version`

## Key Model Notes (Current)

1. Canonical units and conversions
- `units` stores global unit definitions and base conversion where applicable.
- `ingredient_units` stores ingredient-specific overrides (`ingredient_id`, `unit_code`, `grams_per_unit`).
- `recipe_ingredients.quantity_grams` is stored and used as canonical weight for cost/nutrition/scaling calculations.

2. Yield model on recipes
- `recipes` includes `yield_mode`, `portion_size_grams`, `total_raw_weight_grams`, `total_cooked_weight_grams`, and `portions_count_resolved`.
- `recipes` enforces `valid_yield_mode` (`count` or `weight`).
- `recipes` enforces `weight_mode_requires_portion_size_when_active`.

3. Pricing model
- `ingredient_prices` supports multiple supplier rows.
- Unique behavior is enforced by constraint/index strategy around `(ingredient_id, supplier_id)` and helper indexes.
- `ingredient_prices_latest` provides latest-price lookup by ingredient/unit ordering.

4. Recipe and nutrition representation
- `recipe_nutrition` links `recipe_id` to `nutrition_id` in `nutrition_facts`.
- Current schema does not use a `recipe_nutrition_cache` table name.

5. Taxonomy tables
- `allergens` and `additives` currently use `code` (text) and `name` (text).
- Current schema does not expose `name_de`/`name_en` split columns in these two tables.

## MVP vs Full Project (Data Layer)

### MVP-backed in schema 010
- Recipes and recipe ingredients
- Ingredient master and nutrition tables
- Unit conversion system (`units`, `ingredient_units`, `quantity_grams`, `price_per_gram`)
- Pricing tables and latest-price view
- Categories/tags and allergen/additive mapping tables
- Audit log baseline (`audit_logs`)

### Planned / post-MVP (not present in schema 010)
- `agents` table
- `agent_interactions` table
- `shopping_lists`, `shopping_list_items`
- `task_lists`, `task_items`
- RLS policies and tenant isolation policy definitions as an enforced runtime model

## Planned Evolution Notes

The following structures are intentionally treated as planned, not current:
- richer multilingual fields for allergens/additives
- dedicated agent identity and interaction logs
- first-class shopping and task list entities

If these are introduced, they must be documented as a new schema revision after migration scripts are updated.
