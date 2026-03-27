# API Specification (Schema 011 Aligned)

This document defines:
- MVP API contract: what is in scope now
- Later API contract: explicitly deferred endpoints

Source of truth for schema alignment: Alembic migration chain ending at revision 011.

## Scope Note

This is a target contract document for MVP product scope.
It is not a statement that every endpoint is already implemented in FastAPI today.

## MVP API Contract

### Authentication and User Management

- POST `/auth/signup`
- POST `/auth/login`

MVP auth scope:
- Email/password signup for office/admin users
- Email/password login
- Tenant-bound user records

Not in MVP auth scope:
- refresh token flow
- social login
- SSO

### Recipes (CRUD)

- GET `/recipes`
- POST `/recipes`
- GET `/recipes/{id}`
- PUT `/recipes/{id}`
- DELETE `/recipes/{id}`

Schema-backed recipe fields used in MVP:
- `name`
- `description`
- `instructions`
- `status`
- `yield_amount`
- `yield_unit`
- `yield_mode` (`count` | `weight`)
- `reduction_factor`
- `portion_size_grams`
- `total_raw_weight_grams`
- `total_cooked_weight_grams`
- `portions_count_resolved`

Constraint relevant to MVP:
- active weight-mode recipes require `portion_size_grams > 0`

### Ingredients (CRUD)

- GET `/ingredients`
- POST `/ingredients`
- GET `/ingredients/{id}`
- PUT `/ingredients/{id}`
- DELETE `/ingredients/{id}`

Schema-backed ingredient fields used in MVP:
- `name`
- `name_english`
- `default_unit`
- `source`
- `bls_key`
- `is_custom`
- `parent_id`

### Agent and Voice Intent (HTTP-First MVP)

- POST `/agent/chat`

MVP behavior for agent command execution:
- Accept text or voice transcript payload
- Parse user intent with AI
- Execute backend query/tool
- Return render-ready screen response

MVP user flows supported via agent intent:
- Ask for a recipe
- Scale recipe by target portions
- Scale recipe by ingredient constraint

Example intent request:

```json
{
  "source": "voice",
  "text": "Scale Kartoffelsalat to 100 portions",
  "language": "en"
}
```

Example intent response:

```json
{
  "intent": "scale_recipe_by_portions",
  "status": "success",
  "result": {
    "recipe_id": "...",
    "recipe_name": "Kartoffelsalat",
    "target_portions": 100,
    "ui_action": "render_recipe_detail"
  }
}
```

## Later API Contract (Explicitly Deferred)

### Nutrition and Allergens

Deferred for later milestone:
- GET `/recipes/{id}/nutrition`
- GET `/allergens`
- GET `/additives`
- GET `/recipes/{id}/allergens`

### Voice Transport (Realtime)

Deferred for later milestone:
- WS `/agent/voice`
- GET `/agent/interactions`

MVP uses HTTP-first command execution via `/agent/chat`.

### Shopping, Tasks, Planning, Export

Deferred for later milestone:
- POST `/recipes/{id}/plan`
- GET `/shopping-lists`
- POST `/shopping-lists/items`
- PATCH `/shopping-lists/items/{id}`
- DELETE `/shopping-lists/items/{id}`
- GET `/tasks`
- POST `/tasks`
- PATCH `/tasks/{id}`
- DELETE `/tasks/{id}`
- POST `/recipes/{id}/exports`
- GET `/exports/{id}`
- GET `/recipes/{id}/exports`

## MVP vs Later Summary

### Included in MVP

- User signup and login
- Recipe CRUD
- Ingredient CRUD
- AI intent processing with voice/text input via `/agent/chat`
- Recipe lookup and scaling workflows rendered on screen

### Not Included in MVP

- Nutrition endpoints
- Allergen/additive endpoints
- WebSocket voice channel
- Agent interaction history API
- Shopping/task/planning/export APIs
