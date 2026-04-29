# API Contract Specification (Schema 011 Aligned)

This document defines:
- strict MVP API contract (route-by-route)
- request and response schemas
- status code rules per endpoint
- deferred endpoints that are explicitly out of MVP

Source of truth for schema alignment: Alembic migration chain ending at revision 011.

## Scope Note

This is the target API contract for MVP product scope.
It is not a statement that every endpoint is already implemented in FastAPI today.

## Contract Conventions

### API Base Path and Versioning

- Base path: `/api/v1`
- Paths listed below are relative to `/api/v1`
- Breaking contract changes require a new API version

### Authentication and Tenant Context

- Auth type: Bearer JWT
- Header: `Authorization: Bearer <token>`
- Tenant context is derived from JWT claim `tenant_id`
- No `X-Tenant-Id` header in MVP
- Signup does not create tenants in MVP; new users are assigned to a preconfigured default tenant

### Content and Serialization

- Content type: `application/json`
- Resource IDs: UUID strings
- Timestamps: ISO-8601 UTC (example: `2026-03-28T09:30:00Z`)
- Decimal values are serialized as strings to avoid JS precision loss

### Pagination

- Offset pagination for list endpoints
- Query params:
  - `limit` (int, default `20`, min `1`, max `100`)
  - `offset` (int, default `0`, min `0`)
- List response shape:

```json
{
  "items": [],
  "meta": {
    "limit": 20,
    "offset": 0,
    "total": 0
  }
}
```

### Error Contract (All Endpoints)

Error responses follow Problem Details style:

```json
{
  "type": "https://voice-chef.dev/errors/validation",
  "title": "Validation failed",
  "status": 400,
  "detail": "portion_size_grams is required for active weight-mode recipes",
  "code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "portion_size_grams",
      "message": "must be greater than 0",
      "rule": "weight_mode_requires_portion_size_when_active"
    }
  ]
}
```

Common error statuses:
- `400` bad request / business rule violation
- `401` unauthorized or missing/invalid token
- `403` authenticated but forbidden
- `404` resource not found
- `409` conflict
- `422` malformed payload (schema/type)
- `429` rate limited
- `503` service unavailable (for example, default tenant not configured)
- `500` internal error

### Derived Field Ownership

- Backend computes canonical derived values:
  - `recipe_ingredients[].quantity_grams`
  - `ingredient_prices.price_per_gram`
- Client sends authoring values (`quantity`, `unit`, `price_per_unit`, etc.)
- Response returns canonical values used by the system

## Schema Catalog (MVP)

### Enums

- `RecipeStatus`: string (DB default `draft`; no DB enum check in `models.py`)
- `YieldMode`: `count | weight`
- `IngredientType`: string (`ingredients.ingredient_type`)
- `UnitType`: `weight | volume | piece | custom`
- `ChatSource`: `voice | text`
- `AgentStatus`: `success | needs_clarification | error`

### Auth Schemas

`AuthSignupRequest`

```json
{
  "email": "chef-admin@kitchen.local",
  "password": "StrongPassword123!"
}
```

`AuthLoginRequest`

> The login endpoint expects `x-www-form-urlencoded` (not JSON) because it uses FastAPI's `OAuth2PasswordRequestForm`. The field is called `username` but we send the email.

*Note: `application/x-www-form-urlencoded` encodes form data as key-value pairs, separated by `&`, with `=` separating keys and values (e.g., `name=John+Doe&age=25`). Non-alphanumeric characters are percent-encoded (e.g., spaces become `+` or `%20`).*

**Request Body:**

The body must be sent as `x-www-form-urlencoded` data (like a standard HTML form submission), not as JSON.

- `username`: The user's email address. (string, **required**)
- `password`: The user's password. (string, **required**)

**Example of raw request body:**

```
username=user%40example.com&password=strongpassword123
```

<!-- ```json
{
  "email": "chef-admin@kitchen.local",
  "password": "StrongPassword123!"
}
``` -->

`AuthTokenResponse`

Note: `expires_in` is measured in seconds

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "b4cce9a0-7a56-4687-9aab-16cdf55f6961",
    "tenant_id": "98aa2780-6ad4-4de0-8908-3fa799eb67db",
    "email": "chef-admin@kitchen.local",
    "role": "admin",
    "is_active": true
  }
}
```

### Recipe Schemas

`RecipeIngredientWrite`

```json
{
  "ingredient_id": "1a6f300b-df96-49b7-a72d-f3004ce6dbf3",
  "quantity": "2.500",
  "unit": "kg",
  "preparation": "peeled",
  "sort_order": 1
}
```

`RecipeWrite`

```json
{
  "name": "Kartoffelsalat",
  "description": "Classic potato salad",
  "instructions": "Cook, cool, mix.",
  "status": "draft",
  "yield_mode": "count",
  "portion_size_grams": null,
  "total_raw_weight_grams": "8500.000",
  "total_cooked_weight_grams": "7900.000",
  "portions_count_resolved": "100",
  "ingredients": []
}
```

`RecipeIngredientResponse`

```json
{
  "id": "ac85a727-bcc5-4623-a176-0f0f064f7691",
  "ingredient_id": "1a6f300b-df96-49b7-a72d-f3004ce6dbf3",
  "ingredient_name": "Potato",
  "ingredient_default_unit": "kg",
  "quantity": "2.500",
  "unit": "kg",
  "quantity_grams": "2500.000",
  "preparation": "peeled",
  "sort_order": 1
}
```

`RecipeSummaryResponse`

```json
{
  "id": "272e1fc7-b6dc-4e29-95be-548ca138a52b",
  "name": "Kartoffelsalat",
  "description": "Classic potato salad",
  "instructions": "Cook, cool, mix.",
  "status": "active",
  "yield_mode": "weight",
  "portion_size_grams": "250.000",
  "total_raw_weight_grams": "8500.000",
  "total_cooked_weight_grams": "7900.000",
  "portions_count_resolved": "31.6",
  "photo_url": "https://example.com/recipes/kartoffelsalat.jpg",
  "created_at": "2026-03-28T09:30:00Z",
  "updated_at": "2026-03-28T09:40:00Z"
}
```

`RecipeDetailResponse`

```json
{
  "id": "272e1fc7-b6dc-4e29-95be-548ca138a52b",
  "name": "Kartoffelsalat",
  "description": "Classic potato salad",
  "instructions": "Cook, cool, mix.",
  "status": "active",
  "yield_mode": "weight",
  "portion_size_grams": "250.000",
  "total_raw_weight_grams": "8500.000",
  "total_cooked_weight_grams": "7900.000",
  "portions_count_resolved": "31.6",
  "photo_url": "https://example.com/recipes/kartoffelsalat.jpg",
  "preparation_time_minutes": 15,
  "cooking_time_minutes": 30,
  "is_component": false,
  "ingredients": [
    {
      "id": "ac85a727-bcc5-4623-a176-0f0f064f7691",
      "ingredient_id": "1a6f300b-df96-49b7-a72d-f3004ce6dbf3",
      "ingredient_name": "Potato",
      "ingredient_default_unit": "kg",
      "quantity": "2.500",
      "unit": "kg",
      "quantity_grams": "2500.000",
      "preparation": "peeled",
      "sort_order": 1
    }
  ],
  "created_at": "2026-03-28T09:30:00Z",
  "updated_at": "2026-03-28T09:40:00Z"
}
```

Validation rules (from schema):
- `status` is required string (DB default is `draft`)
- `yield_mode` must be one of `count|weight`
- if `status=active` and `yield_mode=weight`, then `portion_size_grams > 0`
- `total_raw_weight_grams >= 0` when present
- `total_cooked_weight_grams >= 0` when present
- `portions_count_resolved > 0` when present
- `recipe_ingredients.quantity_grams >= 0` when present
- `recipe_ingredients` line uniqueness: (`recipe_id`, `ingredient_id`, `sort_order`)

### Ingredient Schemas

`IngredientWrite`

```json
{
  "name": "Potato",
  "default_unit": "kg",
  "ingredient_type": "canonical",
  "bls_key": "BLS-1234",
  "is_custom": false,
  "parent_id": null
}
```

`IngredientResponse`

```json
{
  "id": "1a6f300b-df96-49b7-a72d-f3004ce6dbf3",
  "name": "Potato",
  "default_unit": "kg",
  "ingredient_type": "canonical",
  "bls_key": "BLS-1234",
  "is_custom": false,
  "has_parent": false,
  "parent_id": null,
  "created_at": "2026-03-28T09:30:00Z",
  "updated_at": "2026-03-28T09:30:00Z"
}
```

### Unit and Pricing Schemas

`UnitResponse`

```json
{
  "id": "5ac7f383-8fd7-478b-ab13-41a672758f40",
  "code": "kg",
  "name_de": "Kilogramm",
  "name_en": "kilogram",
  "grams_per_unit": "1000.000",
  "unit_type": "weight",
  "is_base": false
}
```

`IngredientLatestPriceResponse`

```json
{
  "ingredient_id": "1a6f300b-df96-49b7-a72d-f3004ce6dbf3",
  "latest_price": {
    "id": "66cd77b5-aa6c-4f6d-ad2e-3db5ca7ac86e",
    "unit": "kg",
    "currency": "EUR",
    "price_per_unit": "2.9900",
    "price_per_gram": "0.00299000",
    "supplier_id": "metro-001",
    "supplier_name": "Metro",
    "article_number": "A-123",
    "created_at": "2026-03-28T09:20:00Z",
    "updated_at": "2026-03-28T09:30:00Z"
  }
}
```

If no price exists for a valid ingredient:

```json
{
  "ingredient_id": "1a6f300b-df96-49b7-a72d-f3004ce6dbf3",
  "latest_price": null
}
```

### Agent Schemas

`AgentChatRequest`

```json
{
  "source": "voice",
  "text": "Scale Kartoffelsalat to 100 portions",
  "language": "en"
}
```

`AgentChatResponse`

```json
{
  "interaction_id": "0d7260fa-a486-4ef8-abda-1a572962e907",
  "intent": "scale_recipe_by_portions",
  "status": "success",
  "result": {
    "recipe_id": "272e1fc7-b6dc-4e29-95be-548ca138a52b",
    "recipe_name": "Kartoffelsalat",
    "target_portions": 100,
    "ui_action": "render_recipe_detail"
  }
}
```

MVP intents:
- `find_recipe`
- `scale_recipe_by_portions`
- `scale_recipe_by_ingredient_constraint`

## Endpoint Matrix (Strict MVP)

### Matrix Overview

| Method | Path | Auth | Request Schema | Success Response | Success Status | Error Statuses |
|---|---|---|---|---|---|---|
| POST | `/auth/signup` | Public | `UserSignupLogin` | `UserSignupResponse` | `201` | `400, 409, 422, 503, 500` |
| POST | `/auth/login` | Public | `UserSignupLogin` | `AuthTokenResponse` | `200` | `400, 401, 403, 422, 500` |
| GET | `/recipes` | Bearer | Query: `limit`, `offset`, `status`, `search` | `{ items: RecipeSummaryResponse[], meta }` | `200` | `401, 422, 500` |
| POST | `/recipes` | Bearer | `RecipeWrite` | `RecipeDetailResponse` | `201` | `400, 401, 404, 409, 422, 500` |
| GET | `/recipes/{id}` | Bearer | Path: `id` UUID | `RecipeDetailResponse` | `200` | `401, 404, 422, 500` |
| PATCH | `/recipes/{id}` | Bearer | Path: `id` UUID, Body: `RecipeUpdate` (partial merge) | `RecipeDetailResponse` | `200` | `400, 401, 404, 409, 422, 500` |
| DELETE | `/recipes/{id}` | Bearer | Path: `id` UUID | none | `204` | `401, 404, 422, 500` |
| GET | `/ingredients` | Bearer | Query: `limit`, `offset`, `ingredient_type`, `search`, `is_custom` | `{ items: IngredientResponse[], meta }` | `200` | `401, 422, 500` |
| POST | `/ingredients` | Bearer | `IngredientWrite` | `IngredientResponse` | `201` | `400, 401, 409, 422, 500` |
| GET | `/ingredients/{id}` | Bearer | Path: `id` UUID | `IngredientResponse` | `200` | `401, 404, 422, 500` |
| PATCH | `/ingredients/{id}` | Bearer | Path: `id` UUID, Body: `IngredientUpdate` (partial merge) | `IngredientResponse` | `200` | `400, 401, 404, 409, 422, 500` |
| DELETE | `/ingredients/{id}` | Bearer | Path: `id` UUID | none | `204` | `401, 404, 422, 500` |
| GET | `/units` | Bearer | Query: `limit`, `offset`, `unit_type`, `search` | `{ items: UnitResponse[], meta }` | `200` | `401, 422, 500` |
| GET | `/ingredients/{id}/prices/latest` | Bearer | Path: `id` UUID | `IngredientLatestPriceResponse` | `200` | `401, 404, 422, 500` |
| POST | `/agent/chat` | Bearer | `AgentChatRequest` | `AgentChatResponse` | `200` | `400, 401, 422, 429, 500` |

## Endpoint Details

### 1) POST `/auth/signup`

Purpose:
- Create user account in the preconfigured default tenant

Request:
- Body: `UserSignupLogin`

Success:
- `201 Created`
- Body: `UserSignupResponse`

Errors:
- `400` weak password
- `409` email already exists
- `422` payload type/shape invalid
- `503` default tenant not configured in backend

### 2) POST `/auth/login`

Purpose:
- Authenticate existing user
- Return access token

Request:
- Body: `AuthLoginRequest`

Success:
- `200 OK`
- Body: `AuthTokenResponse`

Errors:
- `401` invalid credentials
- `403` Forbidden - account disabled
- `422` payload type/shape invalid

NOTE: `Status Code 403`: Unlike 401 (which says "I don't know who you are"), 403 says "I know exactly who you are, but you are not allowed to be here."

### 3) GET `/recipes`

Purpose:
- List recipes for authenticated tenant

Query Params:
- `limit`, `offset`
- `status` optional string filter
- `search` optional free text

Success:
- `200 OK`
- Body:

```json
{
  "items": [
    {
      "id": "272e1fc7-b6dc-4e29-95be-548ca138a52b",
      "name": "Kartoffelsalat",
      "description": "Classic potato salad",
      "instructions": "Cook, cool, mix.",
      "status": "active",
      "yield_mode": "weight",
      "portion_size_grams": "250.000",
      "total_raw_weight_grams": "8500.000",
      "total_cooked_weight_grams": "7900.000",
      "portions_count_resolved": "31.6",
      "photo_url": "https://example.com/recipes/kartoffelsalat.jpg",
      "created_at": "2026-03-28T09:30:00Z",
      "updated_at": "2026-03-28T09:40:00Z"
    }
  ],
  "meta": {
    "limit": 20,
    "offset": 0,
    "total": 1
  }
}
```

### 4) POST `/recipes`

Purpose:
- Create a recipe with optional ingredient lines

Request:
- Body: `RecipeWrite`

Success:
- `201 Created`
- Body: `RecipeDetailResponse`

Errors:
- `400` business rule violations
  - active + weight mode without valid `portion_size_grams`
  - negative totals where not allowed
- `404` referenced ingredient not found
- `409`:
  - Recipe name already exists
  - duplicate ingredient line key (`recipe_id`, `ingredient_id`, `sort_order`)

### 5) GET `/recipes/{id}`

Purpose:
- Fetch one recipe by id
- Always include `ingredients` lines with quantities (`quantity`, `unit`, `quantity_grams`) and ingredient display fields

Success:
- `200 OK`
- Body: `RecipeDetailResponse`

Errors:
- `404` recipe not found for tenant

### 6) PATCH `/recipes/{id}`

Purpose:
- Update recipe fields with partial merge semantics

Request:
- Body: `RecipeUpdate` (only provided fields are updated; all fields are optional)

Success:
- `200 OK`
- Body: `RecipeDetailResponse`

Errors:
- same as `POST /recipes` plus `404` when recipe id does not exist

### 7) DELETE `/recipes/{id}`

Purpose:
- Delete recipe

Success:
- `204 No Content`

Errors:
- `404` recipe not found for tenant

### 8) GET `/ingredients`

Purpose:
- List ingredients for authenticated tenant

Query Params:
- `limit`, `offset`
- `ingredient_type` optional string filter
- `search` optional free text
- `is_custom` optional boolean

Success:
- `200 OK`
- Body: `{ items: IngredientResponse[], meta }`

### 9) POST `/ingredients`

Purpose:
- Create ingredient

Request:
- Body: `IngredientWrite`

Success:
- `201 Created`
- Body: `IngredientResponse`

Errors:
- `400` business rule validation failure
- `409` constraint conflict

### 10) GET `/ingredients/{id}`

Purpose:
- Fetch one ingredient by id

Success:
- `200 OK`
- Body: `IngredientResponse`

Errors:
- `404` ingredient not found

### 11) PATCH `/ingredients/{id}`

Purpose:
- Update ingredient fields with partial merge semantics

Request:
- Body: `IngredientUpdate` (only provided fields are updated; all fields are optional)

Success:
- `200 OK`
- Body: `IngredientResponse`

Errors:
- same as `POST /ingredients` plus `404` when ingredient id does not exist

### 12) DELETE `/ingredients/{id}`

Purpose:
- Delete ingredient

Success:
- `204 No Content`

Errors:
- `404` ingredient not found

### 13) GET `/units`

Purpose:
- List supported units and optional gram conversions

Query Params:
- `limit`, `offset`
- `unit_type` optional enum (`weight|volume|piece|custom`)
- `search` optional text over code and localized names

Success:
- `200 OK`
- Body: `{ items: UnitResponse[], meta }`

### 14) GET `/ingredients/{id}/prices/latest`

Purpose:
- Return latest known pricing snapshot for ingredient

Success:
- `200 OK`
- Body: `IngredientLatestPriceResponse`
- if ingredient exists but has no pricing records, return `latest_price: null`

Errors:
- `404` ingredient not found

### 15) POST `/agent/chat`

Purpose:
- Parse text or voice transcript intent
- Execute recipe/ingredient query tool
- Return render-ready response for UI

Request:
- Body: `AgentChatRequest`

Success:
- `200 OK`
- Body: `AgentChatResponse`

Errors:
- `400` unsupported source, empty text, unsupported language
- `429` request throttled

## MVP Data Constraint Mapping

This contract reflects database constraints from the Alembic migration chain:
- `recipes.yield_mode` check (`count|weight`)
- `weight_mode_requires_portion_size_when_active`
- positive/non-negative checks for recipe totals and portions
- `recipe_ingredients.quantity_grams >= 0`
- `ingredient_prices.price_per_gram > 0`
- `units.unit_type` check (`weight|volume|piece|custom`)

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
- Units lookup
- Latest ingredient price lookup
- AI intent processing with voice/text input via `/agent/chat`
- Recipe lookup and scaling workflows rendered on screen

### Not Included in MVP

- Nutrition endpoints
- Allergen/additive endpoints
- WebSocket voice channel
- Agent interaction history API
- Shopping/task/planning/export APIs
