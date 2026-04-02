# Voice Chef -- Product Specification

**Version:** 1.3
**Date:** 2026-03-27
**Status:** Draft
**Working Title:** Voice Chef (subject to change)

**Schema baseline (current state):** Alembic revision 011 (`011_drop_selected_legacy_fields`)

---

There are 14 sections with sub-sections in this document. There are approximately 12 to 20 pages of text, so it's super hard to navigate and impossible to memorize all the topics. 

Please insert a formatted table of contents with clickable links at the beginning of the file.

## Table of Contents

- [1. Product Vision](#1-product-vision)
  - [Core Principles](#core-principles)
- [2. System Architecture](#2-system-architecture)
  - [2.1 High-Level Overview](#21-high-level-overview)
  - [2.2 Tech Stack](#22-tech-stack)
  - [2.3 Deployment Model](#23-deployment-model)
- [3. Agent Architecture](#3-agent-architecture)
  - [3.1 Current State (Schema 011)](#31-current-state-schema-011)
  - [3.2 MVP Behavior](#32-mvp-behavior)
  - [3.3 Planned Agent Data Model (Post-MVP)](#33-planned-agent-data-model-post-mvp)
- [4. Voice Pipeline](#4-voice-pipeline)
  - [4.1 Hardware](#41-hardware)
  - [4.2 Voice Flow (MVP)](#42-voice-flow-mvp)
  - [4.3 Activation](#43-activation)
  - [4.4 Output](#44-output)
  - [4.5 Error Handling](#45-error-handling)
  - [4.6 Concurrency](#46-concurrency)
  - [4.7 Latency Target](#47-latency-target)
  - [4.8 Later Voice Scope](#48-later-voice-scope)
- [5. Frontend Specification](#5-frontend-specification)
  - [5.1 Design Principles](#51-design-principles)
  - [5.2 Core Views](#52-core-views)
  - [5.3 Authentication](#53-authentication)
  - [5.4 Offline Capability](#54-offline-capability)
  - [5.5 Real-Time Updates](#55-real-time-updates)
- [6. Data Model (Current Schema 011)](#6-data-model-current-schema-011)
  - [6.1 Current Database Objects](#61-current-database-objects)
  - [6.2 Schema Agreement Matrix (Current vs MVP Runtime)](#62-schema-agreement-matrix-current-vs-mvp-runtime)
  - [6.3 Schema 011 Cross-Check Table (Detailed)](#63-schema-011-cross-check-table-detailed)
- [7. API Specification](#7-api-specification)
  - [7.1 REST API (FastAPI)](#71-rest-api-fastapi)
  - [7.2 WebSocket Protocol](#72-websocket-protocol)
- [8. AI Chat / Command Palette](#8-ai-chat--command-palette)
  - [8.1 Interface Design](#81-interface-design)
  - [8.2 Example Interactions](#82-example-interactions)
  - [8.3 LLM Tool Calling](#83-llm-tool-calling)
- [9. Cost Calculation Model](#9-cost-calculation-model)
  - [9.1 Later Scope](#91-later-scope)
  - [9.2 Configuration](#92-configuration)
- [10. Internationalization (i18n)](#10-internationalization-i18n)
  - [10.1 Strategy](#101-strategy)
  - [10.2 Default Languages (MVP)](#102-default-languages-mvp)
- [11. Phased Delivery Plan](#11-phased-delivery-plan)
  - [Phase 1: MVP -- Auth + CRUD + Voice Intent (Weeks 1-3)](#phase-1-mvp----auth--crud--voice-intent-weeks-1-3)
  - [Phase 2: Voice Pipeline Hardening (Weeks 3-4)](#phase-2-voice-pipeline-hardening-weeks-3-4)
  - [Phase 3: Extended Features (Weeks 3-5)](#phase-3-extended-features-weeks-3-5)
  - [Phase 4: Voice Realtime Transport (Week 5)](#phase-4-voice-realtime-transport-week-5)
  - [Phase 5: Pilot & Hardening (Weeks 6-8)](#phase-5-pilot--hardening-weeks-6-8)
  - [Future: Phase 6+ (Post-Pilot)](#future-phase-6-post-pilot)
- [12. Migration Plan](#12-migration-plan)
  - [12.1 Source](#121-source)
  - [12.2 Implementation Files](#122-implementation-files)
  - [12.3 Migration Steps](#123-migration-steps)
  - [12.4 Key Design Decisions](#124-key-design-decisions)
- [13. Success Criteria](#13-success-criteria)
  - [Phase 1: MVP (Weeks 1-3)](#phase-1-mvp-weeks-1-3)
  - [Phase 2: Voice Pipeline (Weeks 3-4)](#phase-2-voice-pipeline-weeks-3-4)
  - [Phase 3: Extras (Weeks 3-5)](#phase-3-extras-weeks-3-5)
  - [Phase 4: Voice Integration (Week 5)](#phase-4-voice-integration-week-5)
  - [Phase 5: Pilot (Weeks 6-8)](#phase-5-pilot-weeks-6-8)
- [14. Open Questions & Risks](#14-open-questions--risks)

---

## 1. Product Vision

Voice Chef is the knowledge base of the commercial kitchen. It is a full-stack web application with an AI-powered command palette and voice input that gives kitchen staff instant access to recipes and ingredient workflows -- hands-free or on-screen.

For this MVP, the core target is reliable user authentication, recipe and ingredient CRUD, and practical voice intent execution that returns results to screen quickly.

### Core Principles

- **MVP-first delivery** -- prioritize signup/login, recipe CRUD, ingredient CRUD, and voice intent execution before broader feature sets
- **Voice in, screen out** -- voice is input-only (no TTS); the agent processes voice commands and renders results on the companion screen
- **Commercial kitchen focus** -- built for professional kitchens with practical day-one workflows
- **Multilingual from day one** -- kitchen staff speaks German, English, Spanish, Turkish, and more; the system must handle all
- **Single agent now, multi-agent ready** -- one orchestrating agent today, architecture supports splitting into specialized agents later

---

## 2. System Architecture

### 2.1 High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│           DOCKER HOST (VPS / On-Premise)                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │   FastAPI     │  │  Cloud LLM   │  │  PostgreSQL 16    │  │
│  │   Backend     │◄─┤  (GPT/Claude)│  │  (Docker)         │  │
│  │   (Docker)    │  └──────────────┘  │                   │  │
│  │              │                    │  - Recipes         │  │
│  │  - REST API  │◄──────────────────►│  - Ingredients     │  │
│  │  - WebSocket │                    │  - Nutrition       │  │
│  │  - Agent     │                    │  - Agent logs      │  │
│  │    Runtime   │                    │                   │  │
│  └──────┬───────┘                    └───────────────────┘  │
│         │                                                    │
│  ┌──────┴───────┐                                            │
│  │  React SPA    │  (Nginx / Caddy, Docker)                  │
│  │  Frontend     │                                           │
│  └──────┬───────┘                                            │
└─────────┼────────────────────────────────────────────────────┘
          │
          │ HTTPS / WebSocket
          │
    ┌─────┴──────────────────────────────────────────┐
    │              KITCHEN                            │
    │                                                 │
    │  ┌──────────────┐      ┌────────────────────┐  │
    │  │  Browser      │      │  Raspberry Pi 5    │  │
    │  │  (any device) │      │  + ReSpeaker       │  │
    │  │              │      │  XVF3800           │  │
    │  │  - Recipe UI  │      │                    │  │
    │  │  - AI Chat    │      │  - Wake word       │  │
    │  │  - Lists      │      │  - Local STT       │  │
    │  │  - Tasks      │      │  - WebSocket → API │  │
    │  └──────────────┘      └────────────────────┘  │
    │                                                 │
    └─────────────────────────────────────────────────┘
```

### 2.2 Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend** | FastAPI (Python 3.12+) | Async, type-safe, OpenAPI auto-gen, inspired by [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) |
| **ORM** | SQLModel | Pydantic + SQLAlchemy hybrid, type-safe models shared between API and DB |
| **Database** | PostgreSQL 16 (Docker) | Self-managed in Docker Compose, same image for dev/staging/prod |
| **Migrations** | Alembic | Already in use, proven with SQLModel |
| **Frontend** | React + TypeScript + Vite | Modern SPA, responsive, any-device support |
| **UI Library** | Tailwind CSS + shadcn/ui | Consistent, accessible, fast to build |
| **State** | TanStack Query (React Query) | Server state management, auto-refetch polling |
| **Forms** | React Hook Form + Zod | Type-safe validation |
| **AI/LLM** | Cloud LLM (OpenAI / Anthropic) | Best quality for intent understanding and tool calling |
| **Voice STT** | Local (faster-whisper / Whisper.cpp) | Runs on RPi, offline-capable, sub-1s transcription |
| **Wake Word** | OpenWakeWord or Picovoice Porcupine | Local on-device, custom keyword |
| **Edge Device** | Raspberry Pi 5 + ReSpeaker XVF3800 | Far-field 4-mic array, noise suppression for kitchen |
| **Protocol** | WebSocket (RPi ↔ Server) | Persistent, bidirectional, low-latency |
| **Containerization** | Docker + Docker Compose | Dev/prod parity |
| **CI/CD** | GitHub Actions | Automated testing and deployment |

### 2.3 Deployment Model

**Docker Compose everywhere**: same `docker-compose.yml` for development, staging, and production. All services (FastAPI, PostgreSQL, Nginx/Caddy, Redis) run as containers. No managed database services -- fully self-contained and portable.

- **Server**: VPS (Hetzner, DigitalOcean) or on-premise, running Docker Compose
- **Database**: PostgreSQL 16 container with persistent volume
- **Frontend**: React SPA served by Nginx/Caddy container
- **Edge**: Raspberry Pi 5 per kitchen (local audio processing only)
- **Backups**: To be defined during Phase 5 pilot (pg_dump to cloud storage)

This architecture supports future multi-kitchen SaaS: each tenant shares the same deployment, isolated by RLS. For on-premise customers, the entire stack can be deployed on a local server.

---

## 3. Agent Architecture

### 3.1 Current State (Schema 011)

Schema 011 contains `agents` and `agent_interactions` tables, but MVP runtime scope uses only a limited agent execution path.

MVP focus:
- `POST /agent/chat` for text and voice transcript intent execution
- backend tool/query execution for recipe and ingredient workflows
- response payloads designed for direct screen rendering

Deferred to later:
- interaction history API exposure from `agent_interactions`
- realtime WebSocket voice channel

### 3.2 MVP Behavior

For MVP, the assistant runtime is application-managed and executes:
- recipe lookup
- recipe scaling by portions
- recipe scaling by ingredient constraint

Outputs are returned as render-ready responses for the UI.

### 3.3 Planned Agent Data Model (Post-MVP)

Post-MVP target remains:
- fuller use of interaction telemetry and history
- realtime voice transport and session model
- specialist-agent routing architecture

---

## 4. Voice Pipeline

### 4.1 Hardware

- **Microphone**: ReSpeaker XVF3800 USB 4-mic array
  - Far-field voice capture (up to 5m)
  - On-board noise suppression and echo cancellation
  - Critical for kitchen noise (hood fans, timers, clanging)
- **Edge compute**: Raspberry Pi 5 (4GB+ RAM)
  - USB-connected to ReSpeaker
  - Runs wake word detection + local STT
  - WebSocket client to cloud backend

### 4.2 Voice Flow (MVP)

```
Cook speaks
    │
    ▼
[ReSpeaker XVF3800] ── noise suppression, beam-forming ──►
    │
    ▼
[RPi - Wake Word Engine] ── "Hey Chef" detected? ──►
    │ YES
    ▼
[RPi - Local STT] ── faster-whisper / Whisper.cpp ──►
    │ transcript text
    ▼
[HTTP POST /agent/chat]
    │
    ▼
[FastAPI Agent Runtime] ── LLM intent parsing + tool calling ──►
    │ structured response
    ▼
[HTTP response] ── intent result payload
  │
  ▼
[Browser UI render] ── recipe/list update
```

### 4.3 Activation

- **Primary**: Custom wake word ("Hey Chef" or similar) via OpenWakeWord/Porcupine, processed locally on RPi
- **Fallback**: Button in the web app UI (for when the kitchen is too noisy)

### 4.4 Output

- **No text-to-speech** -- voice is input-only
- **Visual feedback**: Results rendered on the companion screen (browser)
- **Audio feedback**: Optional local confirmation cues can be added later

### 4.5 Error Handling

When the agent can't understand the input:
1. Play error tone
2. Wait for the cook to repeat
3. No screen notification on failure -- keep it simple

### 4.6 Concurrency

One voice interaction at a time per ReSpeaker/RPi. First speaker wins. Queuing is not needed for MVP -- a single kitchen typically has one mic station.

### 4.7 Latency Target

**Under 1 second** end-to-end from speech completion to screen update:
- Wake word detection: ~100ms (local)
- STT transcription: ~300-500ms (local, faster-whisper)
- HTTP transit: ~50-120ms
- LLM intent + tool call: ~200-400ms (cloud, with function calling)
- Screen render: ~50ms

### 4.8 Later Voice Scope

Deferred to later milestone:
- WS `/agent/voice` realtime channel
- interaction history retrieval API
- richer transport/session semantics

---

## 5. Frontend Specification

### 5.1 Design Principles

- **Any device, any browser** -- fully responsive, works on phone, tablet, and desktop
- **Touch-friendly** -- large tap targets for kitchen use (wet/dirty hands)
- **High contrast** -- readable in bright kitchen lighting
- **Ingredients-first** -- when showing a recipe, the scaled ingredient list is the primary view

### 5.2 Core Views

#### 5.2.1 Recipe List
- Grid/list toggle
- Search by name (full-text)
- Filter by category, tags, allergens (later)
- Sort by name, date, cost
- Quick actions: scale, duplicate, delete

#### 5.2.2 Recipe Detail / Editor
- **Ingredients tab** (default view): Ingredient list with quantities, units, and scaling controls
- **Instructions tab**: Step-by-step cooking instructions (rich text)
- **Nutrition tab** (later): EU-format nutrition table per 100g and per serving
- **Allergens tab** (later): Auto-detected allergens with override capability
- **Cost tab** (later): Ingredient costs, margin, suggested selling price
- **Compliance tab** (later): Full EU label preview, QUID percentages

#### 5.2.3 AI Chat / Command Palette
- Unified thread showing both voice transcripts and typed messages
- Command palette UX (keyboard-first, fast)
- **MVP**: ask for a recipe and scale workflows via intent execution
- **Post-MVP**: broader entity operations and history workflows
- Shows what the agent did (e.g., "Scaled Kartoffelsalat to 100 portions")
- Persistent within session, scrollable history

#### 5.2.4 Shopping List (Post-MVP, Phase 3)
- Simple list: item name, quantity, unit, checked/unchecked
- Add via chat/voice or manual entry
- Check off items as purchased

#### 5.2.5 Task / Prep Checklist (Post-MVP, Phase 3)
- Simple checklist: task title, status (pending/done)
- Add via chat/voice or manual entry
- Daily view

#### 5.2.6 Ingredient Database
- Browse/search all ingredients
- View nutrition data per ingredient
- View pricing and supplier info
- Create custom ingredients

#### 5.2.7 Settings / Admin
- Tenant configuration
- User management (for office/admin access)
- Ingredient database management
- Category/tag management

### 5.3 Authentication

- **Kitchen devices**: No authentication required. The kitchen device is always logged into the tenant session. Admin tasks require separate login.
- **Office/admin access**: Standard email/password login via the web app.

### 5.4 Offline Capability

- **Read-only offline** via PWA service worker
- Recent and frequently accessed recipes cached locally
- Shopping list and task list cached for viewing
- All writes require an active connection

### 5.5 Real-Time Updates

- **Phase 1 (MVP)**: React Query polling (auto-refetch every 10s) -- sufficient for single-screen kitchens
- **Phase 2**: WebSocket-based push for multi-screen kitchens (reuse the RPi WebSocket infrastructure)

---

## 6. Data Model (Current Schema 011)

This section documents what exists after Alembic revision 011 and distinguishes runtime MVP scope from later scope.

### 6.1 Current Database Objects

Tables:
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

Views:
- `ingredient_prices_latest`

### 6.2 Schema Agreement Matrix (Current vs MVP Runtime)

| Capability | Schema 011 Status | Scope |
|---|---|---|
| Recipe CRUD data model | Present (`recipes`, `recipe_ingredients`) | MVP |
| Yield model (`yield_mode`, `portion_size_grams`, resolved metrics) | Present (`recipes`) | MVP |
| Ingredient master (`ingredients`) | Present | MVP |
| Unit conversion model | Present (`units`, `ingredient_units`, `quantity_grams`) | MVP |
| Pricing model | Present (`ingredient_prices`, `ingredient_prices_latest`) | MVP support for scaling math |
| User management model (`users`) | Present | MVP |
| Agent command model (`agents`) | Present | MVP limited usage |
| Agent interaction history (`agent_interactions`) | Present | Later |
| Categories/tags | Present | Later |
| Allergens/additives mapping | Present | Later |
| Nutrition-facing API usage | Present table support | Later |
| Recipe versioning | Present (`recipe_versions`) | Later |
| Audit logging baseline | Present (`audit_logs`) | MVP |
| Shopping/task tables | Present | Later |
| RLS policies | Present in migration chain | Later runtime enforcement |

### 6.3 Schema 011 Cross-Check Table (Detailed)

| Item | Schema 011 Evidence | Cross-Check Result |
|---|---|---|
| Core tenant and user entities | `tenants`, `users` tables exist | PASS |
| Recipe core entities | `recipes`, `recipe_ingredients` tables exist | PASS |
| Yield model fields | `recipes` includes `yield_mode`, `portion_size_grams`, `total_raw_weight_grams`, `total_cooked_weight_grams`, `portions_count_resolved` | PASS |
| Yield validation constraints | `valid_yield_mode` and `weight_mode_requires_portion_size_when_active` constraints exist on `recipes` | PASS |
| Ingredient master | `ingredients` table exists | PASS |
| Canonical unit system | `units`, `ingredient_units`, and `recipe_ingredients.quantity_grams` exist | PASS |
| Price model and latest price read model | `ingredient_prices` table and `ingredient_prices_latest` view exist | PASS |
| Price safety checks | `ingredient_prices_price_per_gram_positive` check constraint exists | PASS |
| Recipe ingredient guardrail | `recipe_ingredients_quantity_grams_non_negative` check constraint exists | PASS |
| Category and tag taxonomy | `categories`, `tags`, `recipe_categories`, `recipe_tags` exist | PASS |
| Allergen and additive taxonomy | `allergens`, `additives`, `ingredient_allergens`, `ingredient_additives` exist | PASS |
| Recipe version storage | `recipe_versions` exists | PASS |
| Nutrition cache model | `recipe_nutrition_cache` exists | PASS |
| Baseline audit logging | `audit_logs` exists | PASS |
| Agent persistence tables | `agents` and `agent_interactions` tables exist | PASS |
| Shopping/task persistence tables | `shopping_lists`, `shopping_list_items`, `task_lists`, `task_items` exist | PASS |
| RLS policies in migration chain | `ENABLE ROW LEVEL SECURITY` and `CREATE POLICY` entries exist | PASS |
| Migration 011 cleanup | selected recipe legacy columns and `ingredient_merge_audit` removed | PASS |

---

## 7. API Specification

### 7.1 REST API (FastAPI)

Base path: `/api/v1/`

#### Current MVP Contract
| Method | Path | Description |
|---|---|---|
| POST | `/auth/signup` | Email/password signup (office/admin) |
| POST | `/auth/login` | Email/password login (office/admin) |
| GET | `/recipes` | List recipes |
| POST | `/recipes` | Create recipe |
| GET | `/recipes/{id}` | Get recipe detail |
| PUT | `/recipes/{id}` | Update recipe |
| DELETE | `/recipes/{id}` | Delete recipe |
| GET | `/ingredients` | List/search ingredients |
| POST | `/ingredients` | Create ingredient |
| GET | `/ingredients/{id}` | Get ingredient |
| PUT | `/ingredients/{id}` | Update ingredient |
| DELETE | `/ingredients/{id}` | Delete ingredient |
| POST | `/agent/chat` | Voice/text intent processing and execution |

#### Planned (Post-MVP)
| Method | Path | Description |
|---|---|---|
| WS | `/agent/voice` | Realtime voice transcript channel |
| GET | `/agent/interactions` | Agent interaction history |
| POST | `/recipes/{id}/scale` | Explicit scaling endpoint |
| GET | `/recipes/{id}/cost` | Cost read model |
| GET | `/units` | List canonical units |
| GET | `/ingredients/{id}/units` | List ingredient-specific unit conversions |
| POST | `/ingredients/{id}/units` | Create ingredient-specific conversion |
| PUT | `/ingredients/{id}/units/{unit_code}` | Update ingredient-specific conversion |
| DELETE | `/ingredients/{id}/units/{unit_code}` | Delete ingredient-specific conversion |
| GET | `/allergens` | List allergen records |
| GET | `/additives` | List additive records |
| GET | `/recipes/{id}/allergens` | Resolve recipe allergens |
| GET | `/recipes/{id}/nutrition` | Nutrition read model |
| GET | `/categories` | List categories |
| POST | `/categories` | Create category |
| GET | `/tags` | List tags |
| POST | `/tags` | Create tag |
| POST | `/recipes/{id}/plan` | Service planning workflow |
| GET | `/shopping-lists` | Shopping list model |
| POST | `/shopping-lists/items` | Shopping list mutation |
| PATCH | `/shopping-lists/items/{id}` | Shopping list mutation |
| DELETE | `/shopping-lists/items/{id}` | Shopping list mutation |
| GET | `/tasks` | Task list model |
| POST | `/tasks` | Task mutation |
| PATCH | `/tasks/{id}` | Task mutation |
| DELETE | `/tasks/{id}` | Task mutation |
| POST | `/recipes/{id}/exports` | Export workflow |
| GET | `/exports/{id}` | Export workflow |
| GET | `/recipes/{id}/exports` | Export workflow |

### 7.2 WebSocket Protocol

WebSocket protocol is deferred and not part of MVP delivery.

MVP transport for voice/text intent is HTTP via `POST /agent/chat`.

#### RPi → Server (voice transcript)
```json
{
  "type": "transcript",
  "text": "Gib mir das Rezept für Kartoffelsalat für 100 Personen",
  "language": "de",
  "confidence": 0.94,
  "timestamp": "2026-03-12T14:30:00Z"
}
```

#### Server → RPi (audio feedback)
```json
{
  "type": "feedback",
  "sound": "confirm" | "error" | "listening",
  "timestamp": "2026-03-12T14:30:01Z"
}
```

#### Server → Browser (UI update)
```json
{
  "type": "navigate",
  "view": "recipe_detail",
  "data": { "recipe_id": "...", "scaled_portions": 100 }
}
```

---

## 8. AI Chat / Command Palette

### 8.1 Interface Design

The chat is a unified thread that serves as both the voice transcript log and a text-based command palette. It lives as a persistent panel in the app (sidebar or bottom drawer).

- Voice transcripts appear as incoming messages (marked with a mic icon)
- Typed messages appear as standard chat bubbles
- Agent responses show what action was taken + result preview
- MVP chat scope: recipe lookup and scaling intent workflows
- Post-MVP chat scope: nutrition/allergen and operations workflows

### 8.2 Example Interactions

```
User (voice): "Kartoffelsalat für 100 Personen"
Agent: Scaled Kartoffelsalat to 100 portions. [View Recipe →]

User (typed): "Scale tomato soup to 8 portions"
Agent: Scaled Tomato Soup to 8 portions. [View Recipe →]

User (voice): "I only have 500g tomatoes, scale this recipe"
Agent: Scaled recipe by ingredient constraint (tomatoes 500g). [View Recipe →]

-- Post-MVP examples --
User (typed): "add 10kg potatoes to shopping list"
Agent: Added 10kg Kartoffeln to Shopping List. [View List →]

User (voice): "was muss ich heute vorbereiten"
Agent: Today's prep list (3 items):
  ☐ Kartoffeln schälen (50kg)
  ☐ Dressing anrühren
  ☐ Salat waschen
[View Tasks →]
```

### 8.3 LLM Tool Calling

The agent uses structured function calling (OpenAI/Anthropic tool use) to execute actions:

```python
tools = [
    {
        "name": "search_recipes",
        "description": "Search recipes by name or ingredients",
        "parameters": { "query": "string", "limit": "integer" }
    },
    {
        "name": "scale_recipe",
        "description": "Scale a recipe to a target number of portions",
        "parameters": { "recipe_id": "uuid", "target_portions": "number" }
    },
    {
      "name": "scale_recipe_by_ingredient_constraint",
      "description": "Scale a recipe based on available amount of one ingredient",
      "parameters": {
        "recipe_id": "uuid",
        "ingredient_id": "uuid",
        "available_grams": "number"
      }
    },
    # post-MVP tools below
    {
      "name": "add_shopping_item",
      "description": "Add an item to the shopping list",
      "parameters": { "name": "string", "quantity": "number", "unit": "string" }
    },
    {
      "name": "add_task",
      "description": "Add a task to the prep checklist",
      "parameters": { "title": "string" }
    },
    {
      "name": "get_recipe_allergens",
      "description": "Get allergens for a recipe (post-MVP)",
      "parameters": { "recipe_id": "uuid" }
    },
    {
      "name": "get_recipe_nutrition",
      "description": "Get nutrition facts for a recipe (post-MVP)",
      "parameters": { "recipe_id": "uuid" }
    },
    # ... CRUD tools for all entities
]
```

---

## 9. Cost Calculation Model

### 9.1 Later Scope

Cost and nutrition read models are deferred in this MVP and planned for the next milestone.

When enabled:

**Ingredient cost + configurable margin = suggested selling price**

All math uses grams-canonical values (`quantity_grams`, `price_per_gram`), making unit conversion a non-issue:

```
Ingredient Cost   = quantity_grams × price_per_gram
Recipe Food Cost  = Σ (ingredient_cost)
Total Raw Weight  = Σ (recipe_ingredients.quantity_grams)
Total Cooked      = Total Raw Weight × reduction_factor
Resolved Portions =
  if yield_mode='count'  -> yield_amount
  if yield_mode='weight' ->
    if yield_amount is provided and convertible -> output_weight_grams / portion_size_grams
    else -> Total Cooked / portion_size_grams
Cost Per Portion  = Recipe Food Cost / Resolved Portions
Cost Per 100g     = Recipe Food Cost / (Total Cooked / 100)
Suggested Price   = Cost Per Portion / (1 - margin_percentage)
```

Similarly, nutrition is trivially computed from `quantity_grams`:

```
Ingredient Nutrition = (quantity_grams / 100) × nutrition_per_100g
Recipe Nutrition     = Σ (ingredient_nutrition)
Nutrition Per Portion = Recipe Nutrition / Resolved Portions
Nutrition Per 100g    = Recipe Nutrition × 100 / Total Cooked
```

### 9.2 Configuration

- Margin percentage is configurable per tenant (default: 25%)
- Currency: EUR (default), other can be supported later
- Prices are stored per ingredient per supplier
- `price_per_gram` is derived on write: `price_per_unit / grams_per_unit`

---

## 10. Internationalization (i18n)

### 10.1 Strategy

Multilingual from day one. The system handles:

- **Voice input**: Local STT (faster-whisper) supports German, English, Spanish, Turkish, and 90+ other languages natively
- **LLM processing**: Cloud LLM handles multilingual intent understanding natively
- **UI strings**: i18n framework (react-i18next) with language files
- **Data (current schema 011)**: multilingual columns exist in `units`, `allergens`, and `additives` (`name_de`, `name_en`).
- **Data (planned)**: expand multilingual coverage across broader ingredient labeling fields.
- **Screen output**: UI language configurable per tenant

### 10.2 Default Languages (MVP)

- English (primary)
- German

---

## 11. Phased Delivery Plan

**Team**: 5 developers (1 dedicated to voice pipeline from Week 3)

**Hardware**: Raspberry Pi 5 + ReSpeaker XVF3800 already available

**Total timeline**: 8 weeks to production pilot

```
Week  1 ──── 2 ──── 3 ──── 4 ──── 5 ──── 6 ──── 7 ──── 8
      ├─ Phase 1: MVP ─┤
                  ├ Phase 2: Voice ┤
                  ├── Phase 3: Extras ──┤
                              ├─ P4 ┤
                                    ├── Phase 5: Pilot ──┤
```

### Phase 1: MVP -- Auth + CRUD + Voice Intent (Weeks 1-3)

**Goal**: Functional app with signup/login, recipe and ingredient CRUD, and HTTP-first voice/text intent execution for recipe lookup and scaling.

| Week | Deliverables |
|---|---|
| 1 | Project setup (FastAPI + React + Docker Compose + PostgreSQL 16), schema 011 baseline, tenant/user models |
| 2 | Recipe CRUD and ingredient CRUD (backend + frontend), deterministic scaling engine |
| 3 | AI/voice intent integration (`POST /agent/chat`) for recipe lookup and scaling, deploy to production Docker host |

**MVP Deliverables**:
- User signup and login
- Recipe CRUD (create, edit, delete)
- Ingredient CRUD (create, edit, delete)
- AI chat / command palette intent execution for:
  - asking for a recipe
  - scaling by portions
  - scaling by ingredient constraint
- Data migration: Alembic scripts transforming old Neon schema → new Docker PostgreSQL schema
- Responsive web app (any device, any browser)

**NOT in MVP** (deferred):
- Shopping list → Phase 3
- Task/prep checklist → Phase 3
- Nutrition APIs and UI → Phase 3+
- Allergen/additive APIs and UI → Phase 3+
- EU compliance labels / PDF export → Phase 6+
- Full CRUD via AI chat → Phase 3+
- WebSocket voice transport → Phase 4+

### Phase 2: Voice Pipeline Hardening (Weeks 3-4)

**Goal**: Build and validate the voice pipeline as a standalone subsystem. Proves hardware, STT, and LLM intent parsing work end-to-end, independent of the main app.

**Team allocation**: 1 dedicated voice developer. Rest of team works on Phase 3.

| Week | Deliverables |
|---|---|
| 3 | RPi setup, ReSpeaker XVF3800 driver integration, wake word engine (OpenWakeWord / Porcupine), local STT setup (faster-whisper) |
| 4 | Full standalone pipeline: RPi → STT → HTTP `/agent/chat` → LLM intent parsing → structured response |

**Phase 2 Deliverable**: Standalone voice demo -- a developer speaks a command ("Kartoffelsalat für 100"), the RPi transcribes it locally, sends transcript text through `/agent/chat`, and receives structured execution output used by the UI.

### Phase 3: Extended Features (Weeks 3-5)

**Goal**: Add nutrition and allergen features, then broader operations workflows.

**Team allocation**: 2-4 developers (everyone except the voice dev).

| Week | Deliverables |
|---|---|
| 3 | Nutrition read models and API wiring |
| 4 | Allergen/additive read models and recipe allergen resolution |
| 5 | Optional expansion to shopping/tasks and broader AI command set |

**Phase 3 Deliverables**:
- Nutrition display and APIs
- Allergen/additive display and APIs
- Optional shopping/task workflows
- Expanded AI command coverage

### Phase 4: Voice Realtime Transport (Week 5)

**Goal**: Add optional WebSocket realtime transport after MVP stability.

| Week | Deliverables |
|---|---|
| 5 | Wire WS `/agent/voice` to agent runtime, stream transcripts/events, end-to-end simulation testing |

**Phase 4 Deliverable**: A cook says "Hey Chef, Kartoffelsalat für 100" and sees the scaled recipe on the browser screen within 1 second. Voice transcripts appear in the AI chat thread alongside typed messages.

### Phase 5: Pilot & Hardening (Weeks 6-8)

**Goal**: Deploy the full stack (web app + voice) to a single real commercial kitchen. Remotely managed. Measure, fix, iterate.

| Week | Deliverables |
|---|---|
| 6 | Deploy to pilot kitchen, remote monitoring setup (Sentry, structured logging), error tracking, initial staff walkthrough |
| 7 | Measure: voice activation accuracy in real kitchen noise, STT accuracy, end-to-end latency, LLM tool-call success rate. Fix top issues from field data. |
| 8 | Iterate: UX refinements from kitchen feedback, performance optimization (query tuning, caching), define backup strategy, pilot retrospective, roadmap for Phase 6+ |

**Pilot setup**: Single commercial kitchen, remotely managed. Kitchen staff operates independently; dev team monitors logs and metrics remotely.

**Pilot success criteria**:
- [ ] Web app used daily by kitchen staff without developer intervention
- [ ] Voice activation > 90% accuracy at 3m in kitchen conditions
- [ ] End-to-end voice latency < 1 second
- [ ] Zero data-loss incidents
- [ ] Staff satisfaction feedback collected

**Note**: EU compliance (allergen declaration labels, QUID, nutrition PDF export) is **not** required for the pilot. The pilot kitchen handles allergen compliance outside our system.

### Future: Phase 6+ (Post-Pilot)

Prioritized based on pilot feedback:
- EU-compliant nutrition label PDF generation
- Allergen auto-detection engine
- QUID percentage calculation
- Batch PDF export and print integration
- Multi-kitchen deployment (SaaS onboarding)
- PostgreSQL backup automation (pg_dump → cloud storage cron)
- RLS penetration testing for multi-tenant security
- Advanced cost model (labor + packaging + overhead)

---

## 12. Migration Plan

### 12.1 Source

Existing Neon PostgreSQL database (`neondb`) with 22 business tables. Neon is the test/learning deployment only -- production runs on Docker PostgreSQL 17.8

**Source data volumes** (queried live):
- 12,427 ingredients (6,298 with BLS keys, 322 with nutrition data)
- 83 recipes (all draft, all belong to one real tenant)
- 861 recipe_ingredients, 201 ingredient_prices
- 31 allergens (German only), 20 of 32 additives
- 154 ingredient_allergens, 60 ingredient_additives
- 83 recipe-level nutrition records (legacy nutrition structures from source DB)
- 13 tenants (12 test scaffolds, 1 real), 0 users

### 12.2 Implementation Files

- `alembic/versions/001_initial_schema.py` to `alembic/versions/011_drop_selected_legacy_fields.py` -- authoritative migration chain ending at schema 011
- `scripts/seed_from_neon.py` -- Python migration script (Neon read-only -> Docker PostgreSQL)
- `scripts/reference_data/allergens.json` -- reference allergen data used during migration
- `scripts/reference_data/additives.json` -- reference additive data used during migration
- `scripts/reference_data/units.json` -- 18 standard kitchen units with gram conversion factors

### 12.3 Migration Steps

Run in order:
1. `alembic upgrade head` -- creates empty schema in Docker PostgreSQL
2. `python scripts/seed_from_neon.py --source $NEON_URL --target $DATABASE_URL` -- schema-011-oriented migration flow:

| Step | Table | Rows | Transformation |
|---|---|---|---|
| 1 | `allergens` | 31 | Seed from reference JSON into `code` + multilingual names model |
| 2 | `additives` | 32 | Seed from reference JSON into `code` + multilingual names model |
| 3 | `units` | 18 | Seed from reference JSON, standard kitchen units with gram conversion factors |
| 4 | `tenants` | 1 | Filter to real tenant only, skip 12 test scaffolds |
| 5 | `ingredients` | 12,427 | Preserve canonical ingredient identity fields and relationships |
| 6 | `ingredient_nutrition` | 322 | Direct copy, preserves numeric precision |
| 7 | `ingredient_prices` | 201 | Normalize empty strings to NULL; compute `price_per_gram` from unit |
| 8 | `ingredient_allergens` | 154 | Remap allergen UUIDs via code lookup (old UUID -> new UUID) |
| 9 | `ingredient_additives` | 60 | Remap additive UUIDs via code lookup |
| 10 | `categories` | 7 | Assign to real tenant |
| 11 | `recipes` | 83 | Normalize yield fields and backfill canonical weight/portion metrics |
| 12 | `recipe_ingredients` | 861 | Field mapping + compute `quantity_grams` from quantity × grams_per_unit |
| 13 | `recipes` (backfill) | 83 | Compute `total_raw_weight_grams`, `total_cooked_weight_grams`, `portions_count_resolved` |
| 14 | `recipe_nutrition_cache` | as available | Populate cached recipe nutrition model where needed |
| 15 | `recipe_versions` | as available | Persist historical snapshots where available |

### 12.4 Key Design Decisions

- **Grams-canonical unit system**: All quantities and prices are stored canonically in grams (`quantity_grams`, `price_per_gram`). Display units (`quantity`, `unit`) are preserved alongside for UX. A `units` reference table with gram conversion factors and an `ingredient_units` table for ingredient-specific overrides (e.g. 1 egg = 58g) provide the conversion layer. Cost = `quantity_grams × price_per_gram`. Nutrition = `(quantity_grams / 100) × per_100g`.
- **Canonical yield model**: Recipes support portion-first and weight-first authoring via `yield_mode`. Recipe-level metrics (`total_raw_weight_grams`, `total_cooked_weight_grams`, `portions_count_resolved`) are derived to make API/UI output deterministic.
- **Activation guardrail for weight mode**: `status='active'` recipes in `yield_mode='weight'` must provide `portion_size_grams`.
- **Allergen/additive IDs regenerated**: New UUIDs in target; junction tables remapped via current code lookup model
- **Ingredient prices constraint**: Partial unique index (`WHERE supplier_id IS NOT NULL` / `IS NULL`) instead of standard UNIQUE to handle NULL supplier_id
- **Recipe time columns**: schema 011 keeps current legacy-oriented time fields; normalization can continue in a later migration.
- **No neon_auth migration**: Auth is handled by simple FastAPI JWT (users table + bcrypt in Python). The neon_auth schema is not carried over.
- **Validation**: Script compares source/target row counts and verifies unit/pricing backfill coverage (`quantity_grams`, `price_per_gram`) plus relation integrity across mapped tables.

---

## 13. Success Criteria

### Phase 1: MVP (Weeks 1-3)
- [ ] Users can sign up and log in (office/admin flow)
- [ ] Kitchen staff can look up any recipe by name (web + chat)
- [ ] Recipes can be scaled to any number of portions with recalculated quantities
- [ ] Food cost per portion is calculated (ingredient cost)
- [ ] AI chat handles read, scale, and cost queries correctly
- [ ] App runs in Docker Compose and is accessible from any browser
- [ ] Deployed to production Docker host

### Phase 2: Voice Pipeline (Weeks 3-4)
- [ ] RPi + ReSpeaker captures audio and transcribes locally via faster-whisper
- [ ] Wake word activates reliably in office/lab environment
- [ ] Full pipeline produces structured intent JSON from spoken commands
- [ ] UI receives render-ready response for successful intent parse

### Phase 3: Extras (Weeks 3-5)
- [ ] Nutrition APIs and UI are functional
- [ ] Allergens/additives display correctly per recipe
- [ ] Optional shopping/task flows are functional
- [ ] AI command coverage expanded beyond MVP

### Phase 4: Voice Integration (Week 5)
- [ ] Voice commands execute real DB actions (recipe lookup and scaling)
- [ ] Voice transcripts appear in unified chat thread
- [ ] End-to-end latency < 1 second in lab conditions

### Phase 5: Pilot (Weeks 6-8)
- [ ] System runs in a real kitchen for 3 weeks without critical failures
- [ ] Voice activation > 90% accuracy at 3m in kitchen noise
- [ ] Kitchen staff operates without developer intervention
- [ ] Performance metrics collected and reviewed

---

## 14. Open Questions & Risks

| Item | Status | Notes |
|---|---|---|
| Wake word selection ("Hey Chef"?) | Open | Need to test recognition accuracy with kitchen noise during pilot |
| RPi model (Pi 5 4GB vs 8GB) | Open | Depends on STT model size; faster-whisper tiny vs small |
| ReSpeaker XVF3800 Linux driver maturity | Risk | Verify RPi 5 kernel compatibility; hardware is available for testing |
| Local STT model (tiny vs small vs medium) | Open | Trade-off: speed vs accuracy in noisy environment |
| Cloud LLM latency budget | Risk | Need < 400ms for tool calling; may need prompt optimization or model selection |
| Docker PostgreSQL backup strategy | Open | Must be defined during Phase 5 before pilot handles real data |
| Existing data quality | Risk | Rezeptrechner/Neon data may have inconsistencies; migration scripts need validation |
| Missing ingredient prices | Mitigated | Seed with average market prices; kitchen refines over time |
| Multi-kitchen tenant isolation | Deferred | RLS policies designed but not penetration-tested until Phase 6+ |
| Pilot kitchen internet reliability | Risk | Voice pipeline depends on cloud LLM; offline fallback is chat-only web app |
