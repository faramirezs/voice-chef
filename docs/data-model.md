# Data Model (Schema 011)

Source of truth: Alembic migration chain ending at revision `011_drop_selected_legacy_fields`.

## Schema 011 Delta

Revision 011 is a cleanup migration.

Dropped from `recipes`:
- `branch_ids`
- `preference_price`
- `ingredient_list_product_pass`
- `preference_allergens`
- `layout_id`
- `row_height`
- `rezeptblatt_image_width`
- `vat_rate`
- `sales_price_points`
- `bio_label_eu`

Dropped object:
- `ingredient_merge_audit`

No new tables were introduced in 011.

## Current Database Objects (Schema 011)

### Tables

- `tenants`
- `users`
- `agents`
- `ingredients`
- `ingredient_nutrition`
- `recipes`
- `recipe_ingredients`
- `allergens`
- `additives`
- `ingredient_allergens`
- `ingredient_additives`
- `ingredient_prices`
- `categories`
- `tags`
- `recipe_categories`
- `recipe_tags`
- `recipe_nutrition_cache`
- `recipe_versions`
- `agent_interactions`
- `audit_logs`
- `shopping_lists`
- `shopping_list_items`
- `task_lists`
- `task_items`
- `units`
- `ingredient_units`
- `alembic_version`

### Views

- `ingredient_prices_latest`

## Key Model Notes

### 1. Canonical unit system

- `units` stores global unit definitions and optional gram conversion.
- `ingredient_units` stores ingredient-specific conversion overrides.
- `recipe_ingredients.quantity_grams` is canonical for deterministic math.

### 2. Canonical pricing

- `ingredient_prices.price_per_gram` enables direct cost math from canonical grams.
- `ingredient_prices_latest` is the latest-price read model per `(ingredient_id, unit)`.

### 3. Yield and scaling model

- `recipes.yield_mode` supports `count` and `weight` authoring modes.
- `recipes.portion_size_grams`, `total_raw_weight_grams`, `total_cooked_weight_grams`, and `portions_count_resolved` support deterministic scaling output.
- `weight_mode_requires_portion_size_when_active` constrains active weight-mode recipes.

### 4. Taxonomy structure in schema 011

- `allergens` and `additives` use `code` with multilingual columns `name_de` and `name_en`.

## Schema Presence vs MVP Runtime Scope

| Entity group | Exists in schema 011 | Included in MVP runtime scope |
|---|---|---|
| Tenants and users | Yes | Yes |
| Recipes and recipe_ingredients | Yes | Yes |
| Ingredients | Yes | Yes |
| Units and ingredient_units | Yes | Yes |
| Agent chat endpoint support (`agents`) | Yes | Yes (limited usage) |
| Agent interaction history (`agent_interactions`) | Yes | No (later) |
| Nutrition tables (`ingredient_nutrition`, `recipe_nutrition_cache`) | Yes | No (later) |
| Allergen/additive tables | Yes | No (later) |
| Categories/tags tables | Yes | No (later) |
| Shopping/task tables | Yes | No (later) |
| Export persistence model | No dedicated model | No (later) |

## MVP Data Layer Boundary

### Included now

- User records for signup/login (`users`)
- Recipe CRUD entities (`recipes`, `recipe_ingredients`)
- Ingredient CRUD entities (`ingredients`)
- Canonical conversion tables used by scaling logic (`units`, `ingredient_units`)
- Canonical quantity/pricing fields (`quantity_grams`, `price_per_gram`)

### Deferred to later

- Nutrition-facing API usage
- Allergen/additive-facing API usage
- Agent interaction history API exposure
- Shopping/task data workflows
- Export persistence workflows
