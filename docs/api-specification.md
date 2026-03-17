# API Specification (Schema 010 Aligned)

This document distinguishes:
- Current API contract: endpoints that map directly to tables/views in `db/schema_alembic_010.sql`
- Planned API contract: post-MVP endpoints that require tables not present in schema 010

## Current API Contract (Schema-Backed)

### Authentication
- POST `/auth/login`
- POST `/auth/refresh`

### Recipes
- GET `/recipes`
- POST `/recipes`
- GET `/recipes/{id}`
- PUT `/recipes/{id}`
- DELETE `/recipes/{id}`
- POST `/recipes/{id}/scale`

Recipe fields that are schema-backed in `recipes`:
- `yield_amount`
- `yield_unit`
- `yield_mode` (`count` | `weight`)
- `reduction_factor`
- `portion_size_grams`
- `total_raw_weight_grams`
- `total_cooked_weight_grams`
- `portions_count_resolved`

Validation rule backed by DB constraint:
- active weight-mode recipes require `portion_size_grams > 0`

### Recipe Versions
- GET `/recipes/{id}/versions`
- GET `/recipes/{id}/versions/{version}`
- POST `/recipes/{id}/versions`

Backed by:
- `recipe_versions`

### Ingredients
- GET `/ingredients`
- POST `/ingredients`
- GET `/ingredients/{id}`
- PUT `/ingredients/{id}`
- DELETE `/ingredients/{id}`

Backed by:
- `ingredients`
- `ingredient_nutrition`
- `ingredient_prices`
- `ingredient_units`

### Units and Conversions
- GET `/units`
- GET `/ingredients/{id}/units`
- POST `/ingredients/{id}/units`
- PUT `/ingredients/{id}/units/{unit_code}`
- DELETE `/ingredients/{id}/units/{unit_code}`

Backed by:
- `units`
- `ingredient_units`

### Allergens and Additives
- GET `/allergens`
- GET `/additives`
- GET `/recipes/{id}/allergens`

Backed by:
- `allergens`
- `additives`
- `ingredient_allergens`
- `ingredient_additives`

### Categories and Tags
- GET `/categories`
- POST `/categories`
- GET `/tags`
- POST `/tags`

Backed by:
- `categories`
- `tags`
- `recipe_categories`
- `recipe_tags`

### Recipe Media and Files
- GET `/recipes/{id}/photos`
- POST `/recipes/{id}/photos`
- GET `/recipes/{id}/files`
- POST `/recipes/{id}/files`

Backed by:
- `recipe_photos`
- `files`

### Nutrition and Cost Read Models
- GET `/recipes/{id}/nutrition`
- GET `/recipes/{id}/cost`

Backed by:
- `recipe_nutrition`
- `nutrition_facts`
- `recipe_ingredients`
- `ingredient_prices` / `ingredient_prices_latest`

## Planned API Contract (Post-MVP, Not in Schema 010)

The following endpoints are intentionally planned and require new tables/migrations:

### Agent runtime persistence
- POST `/agent/chat`
- WS `/agent/voice`
- GET `/agent/interactions`

Required future tables:
- `agents`
- `agent_interactions`

### Service planning and operations lists
- POST `/recipes/{id}/plan`
- GET `/shopping-lists`
- POST `/shopping-lists/items`
- PATCH `/shopping-lists/items/{id}`
- DELETE `/shopping-lists/items/{id}`
- GET `/tasks`
- POST `/tasks`
- PATCH `/tasks/{id}`
- DELETE `/tasks/{id}`

Required future tables:
- `shopping_lists`
- `shopping_list_items`
- `task_lists`
- `task_items`

### Export workflow
- POST `/recipes/{id}/exports`
- GET `/exports/{id}`
- GET `/recipes/{id}/exports`

Required future tables or storage model:
- export job/result persistence not present in schema 010

## MVP vs Full Project Boundary

### MVP (schema-backed)
- Authentication
- Recipe CRUD + scaling
- Ingredients + nutrition + pricing
- Units and conversion APIs
- Allergens/additives read models
- Categories/tags

### Whole project (post-MVP)
- Agent interaction persistence in DB
- Shopping and task APIs
- Recipe planning endpoint tied to shopping/task persistence
- Export pipeline endpoints
