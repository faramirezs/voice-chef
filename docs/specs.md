# Voice Chef -- Product Specification

**Version:** 1.2
**Date:** 2026-03-17
**Status:** Draft
**Working Title:** Voice Chef (subject to change)

**Schema baseline (current state):** `db/schema_alembic_010.sql`

---

## 1. Product Vision

Voice Chef is the knowledge base of the commercial kitchen. It is a full-stack web application with an AI-powered command palette and a voice interface that gives kitchen staff instant access to recipes, nutrition data, cost calculations, and daily task management -- hands-free or on-screen.

The system treats AI agents as first-class database citizens. The primary consumer of the database is the agent, not a human clicking through CRUD forms. Every table, index, and permission is designed for agent-driven reads and writes, with traditional UI as a complementary interface.

### Core Principles

- **Agent-first data architecture** -- the AI agent is the primary DB consumer; schema, indexes, and permissions are optimized for agent tool-calling patterns
- **Voice in, screen out** -- voice is input-only (no TTS); the agent processes voice commands and renders results on the companion screen
- **Commercial kitchen focus** -- built for professional kitchens with EU compliance requirements (allergens, nutrition labeling, QUID)
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

### 3.1 Current State (Schema 010)

Agent persistence is not yet modeled as dedicated database entities in schema 010.

Current database-backed logging for actions:
- `audit_logs` only

Planned but not yet in schema 010:
- `agents`
- `agent_interactions`

### 3.2 MVP Behavior

For MVP, the assistant runtime is application-managed and can execute recipe lookup, scaling, and cost workflows, while persistence remains limited to current schema entities.

### 3.3 Planned Agent Data Model (Post-MVP)

Post-MVP target remains:
- first-class agent identities per tenant
- interaction-level logs (raw input, parsed intent, latency, errors)
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

### 4.2 Voice Flow

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
[WebSocket → Cloud Backend]
    │
    ▼
[FastAPI Agent Runtime] ── LLM intent parsing + tool calling ──►
    │ structured response
    ▼
[WebSocket → RPi] ── beep/chime confirmation
    │
    ▼
[WebSocket → Browser] ── UI update (recipe, list, etc.)
```

### 4.3 Activation

- **Primary**: Custom wake word ("Hey Chef" or similar) via OpenWakeWord/Porcupine, processed locally on RPi
- **Fallback**: Button in the web app UI (for when the kitchen is too noisy)

### 4.4 Output

- **No text-to-speech** -- voice is input-only
- **Audio feedback**: Confirmation beeps/chimes played through RPi speaker
  - Short beep: command received
  - Double beep: action completed
  - Error tone: command not understood
- **Visual feedback**: Results rendered on the companion screen (browser)

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
- WebSocket transit: ~50ms
- LLM intent + tool call: ~200-400ms (cloud, with function calling)
- Screen render: ~50ms

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
- Filter by category, tags, allergens
- Sort by name, date, cost
- Quick actions: scale, duplicate, delete

#### 5.2.2 Recipe Detail / Editor
- **Ingredients tab** (default view): Ingredient list with quantities, units, and scaling controls
- **Instructions tab**: Step-by-step cooking instructions (rich text)
- **Nutrition tab**: EU-format nutrition table per 100g and per serving
- **Allergens tab**: Auto-detected allergens with override capability
- **Cost tab**: Ingredient costs, margin, suggested selling price
- **Compliance tab** (Phase 2): Full EU label preview, QUID percentages

#### 5.2.3 AI Chat / Command Palette
- Unified thread showing both voice transcripts and typed messages
- Command palette UX (keyboard-first, fast)
- **MVP**: read + scale + cost queries (no recipe creation/editing via chat)
- **Post-MVP**: full CRUD parity -- anything you can do in the UI, you can do in chat
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

## 6. Data Model (Current Schema 010)

This section documents only what exists in `db/schema_alembic_010.sql`.

### 6.1 Current Database Objects

Tables:
- `additives`
- `alembic_version`
- `allergens`
- `audit_logs`
- `categories`
- `files`
- `ingredient_additives`
- `ingredient_allergens`
- `ingredient_merge_audit`
- `ingredient_nutrition`
- `ingredient_prices`
- `ingredient_units`
- `ingredients`
- `nutrition_facts`
- `recipe_categories`
- `recipe_ingredients`
- `recipe_nutrition`
- `recipe_photos`
- `recipe_tags`
- `recipe_versions`
- `recipes`
- `tags`
- `tenants`
- `units`
- `users`

Views:
- `ingredient_prices_latest`

### 6.2 Schema Agreement Matrix (Current vs Planned)

| Capability | Schema 010 Status | Scope |
|---|---|---|
| Recipe CRUD data model | Present (`recipes`, `recipe_ingredients`) | MVP |
| Yield model (`yield_mode`, `portion_size_grams`, resolved metrics) | Present (`recipes`) | MVP |
| Ingredient master + nutrition | Present (`ingredients`, `ingredient_nutrition`) | MVP |
| Unit conversion model | Present (`units`, `ingredient_units`, `quantity_grams`) | MVP |
| Pricing model | Present (`ingredient_prices`, `ingredient_prices_latest`) | MVP |
| Categories/tags | Present (`categories`, `tags`, join tables) | MVP |
| Allergens/additives mapping | Present (`allergens`, `additives`, join tables) | MVP |
| Recipe photos/files | Present (`recipe_photos`, `files`) | Post-MVP feature wiring |
| Recipe versioning | Present (`recipe_versions`) | Post-MVP feature wiring |
| Audit logging baseline | Present (`audit_logs`) | MVP |
| Agent identities and interaction logs | Not present | Post-MVP |
| Shopping/task tables | Not present | Post-MVP |
| RLS policies | Not present in schema 010 | Post-MVP |

### 6.3 Schema 010 Cross-Check Table (Detailed)

| Item | Schema 010 Evidence | Cross-Check Result |
|---|---|---|
| Core tenant and user entities | `tenants`, `users` tables exist | PASS |
| Recipe core entities | `recipes`, `recipe_ingredients` tables exist | PASS |
| Yield model fields | `recipes` includes `yield_mode`, `portion_size_grams`, `total_raw_weight_grams`, `total_cooked_weight_grams`, `portions_count_resolved` | PASS |
| Yield validation constraints | `valid_yield_mode` and `weight_mode_requires_portion_size_when_active` constraints exist on `recipes` | PASS |
| Ingredient master and nutrition | `ingredients` and `ingredient_nutrition` tables exist | PASS |
| Canonical unit system | `units`, `ingredient_units`, and `recipe_ingredients.quantity_grams` exist | PASS |
| Price model and latest price read model | `ingredient_prices` table and `ingredient_prices_latest` view exist | PASS |
| Price safety checks | `ingredient_prices_price_per_gram_positive` check constraint exists | PASS |
| Recipe ingredient guardrail | `recipe_ingredients_quantity_grams_non_negative` check constraint exists | PASS |
| Category and tag taxonomy | `categories`, `tags`, `recipe_categories`, `recipe_tags` exist | PASS |
| Allergen and additive taxonomy | `allergens`, `additives`, `ingredient_allergens`, `ingredient_additives` exist | PASS |
| Recipe version storage | `recipe_versions` exists | PASS |
| Recipe media and file storage | `recipe_photos` and `files` exist | PASS |
| Nutrition linkage model | `recipe_nutrition` links to `nutrition_facts` (no `recipe_nutrition_cache` table) | PASS |
| Baseline audit logging | `audit_logs` exists | PASS |
| Agent persistence tables | `agents` and `agent_interactions` tables absent | PLANNED (NOT IN 010) |
| Shopping/task persistence tables | `shopping_lists`, `shopping_list_items`, `task_lists`, `task_items` absent | PLANNED (NOT IN 010) |
| RLS policies in schema dump | No `CREATE POLICY` entries in schema 010 dump | PLANNED (NOT IN 010) |

---

## 7. API Specification

### 7.1 REST API (FastAPI)

Base path: `/api/v1/`

#### Current (MVP + schema-backed)
| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Email/password login (office/admin) |
| POST | `/auth/refresh` | Refresh JWT token |
| GET | `/recipes` | List recipes |
| POST | `/recipes` | Create recipe |
| GET | `/recipes/{id}` | Get recipe detail |
| PUT | `/recipes/{id}` | Update recipe |
| DELETE | `/recipes/{id}` | Delete recipe |
| POST | `/recipes/{id}/scale` | Scale recipe |
| GET | `/recipes/{id}/cost` | Calculate recipe cost |
| GET | `/recipes/{id}/versions` | List versions |
| GET | `/recipes/{id}/versions/{version}` | Get version |
| POST | `/recipes/{id}/versions` | Create version |
| GET | `/ingredients` | List/search ingredients |
| POST | `/ingredients` | Create ingredient |
| GET | `/ingredients/{id}` | Get ingredient |
| PUT | `/ingredients/{id}` | Update ingredient |
| DELETE | `/ingredients/{id}` | Delete ingredient |
| GET | `/units` | List canonical units |
| GET | `/ingredients/{id}/units` | List ingredient-specific unit conversions |
| POST | `/ingredients/{id}/units` | Create ingredient-specific conversion |
| PUT | `/ingredients/{id}/units/{unit_code}` | Update ingredient-specific conversion |
| DELETE | `/ingredients/{id}/units/{unit_code}` | Delete ingredient-specific conversion |
| GET | `/allergens` | List allergen records |
| GET | `/additives` | List additive records |
| GET | `/recipes/{id}/allergens` | Resolve recipe allergens |
| GET | `/categories` | List categories |
| POST | `/categories` | Create category |
| GET | `/tags` | List tags |
| POST | `/tags` | Create tag |

#### Planned (Post-MVP)
| Method | Path | Description |
|---|---|---|
| POST | `/recipes/{id}/plan` | Service planning workflow |
| GET | `/shopping-lists` | Shopping list model |
| POST | `/shopping-lists/items` | Shopping list mutation |
| PATCH | `/shopping-lists/items/{id}` | Shopping list mutation |
| DELETE | `/shopping-lists/items/{id}` | Shopping list mutation |
| GET | `/tasks` | Task list model |
| POST | `/tasks` | Task mutation |
| PATCH | `/tasks/{id}` | Task mutation |
| DELETE | `/tasks/{id}` | Task mutation |
| POST | `/agent/chat` | Agent interaction API |
| WS | `/agent/voice` | Voice transcript channel |
| GET | `/agent/interactions` | Agent interaction history |
| POST | `/recipes/{id}/exports` | Export workflow |
| GET | `/exports/{id}` | Export workflow |
| GET | `/recipes/{id}/exports` | Export workflow |

### 7.2 WebSocket Protocol

WebSocket protocol is planned for voice/chat runtime phases and is not required for MVP data-model agreement.

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
- MVP chat scope: recipe read, scaling, and cost workflows
- Post-MVP chat scope: full CRUD parity with UI and list/task operations

### 8.2 Example Interactions

```
User (voice): "Kartoffelsalat für 100 Personen"
Agent: Scaled Kartoffelsalat to 100 portions. [View Recipe →]

User (typed): "food cost for schnitzel"
Agent: Schnitzel — €2.34/portion (ingredients: €1.87, margin: 25%). [View Details →]

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
        "name": "calculate_cost",
        "description": "Calculate food cost for a recipe",
        "parameters": { "recipe_id": "uuid", "portions": "number" }
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
        "description": "Get allergens for a recipe",
        "parameters": { "recipe_id": "uuid" }
    },
    {
        "name": "get_recipe_nutrition",
        "description": "Get nutrition facts for a recipe",
        "parameters": { "recipe_id": "uuid" }
    },
    # ... CRUD tools for all entities
]
```

---

## 9. Cost Calculation Model

### 9.1 MVP Scope

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
- **Data (current schema 010)**: multilingual columns exist in `units` (`name_de`, `name_en`), while `allergens` and `additives` currently store a single `name` field.
- **Data (planned)**: expand multilingual coverage for allergens/additives and broader ingredient labeling fields.
- **Screen output**: UI language configurable per tenant

### 10.2 Default Languages (MVP)

- English (primary)
- German

---

## 11. Phased Delivery Plan

**Team**: 3-5 developers (1 dedicated to voice pipeline from Week 3)
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

### Phase 1: MVP -- Web App + AI Chat (Weeks 1-3)

**Goal**: Functional web app with recipe management, AI chat (read + scale + cost queries), and data migration. Deployable to production.

| Week | Deliverables |
|---|---|
| 1 | Project setup (FastAPI + React + Docker Compose + PostgreSQL 16), new schema via Alembic, tenant/user models |
| 2 | Recipe CRUD (backend + frontend), ingredient database with nutrition, recipe scaling, cost calculation (ingredient cost + configurable margin) |
| 3 | AI chat integration (LLM + tool calling for read/scale/cost queries), command palette UI, data migration from existing Neon/Rezeptrechner DB, deploy to production Docker host |

**MVP Deliverables**:
- Recipe CRUD (create, edit, delete, duplicate)
- Recipe scaling (recalculate quantities for N portions)
- Ingredient database with nutrition data (seeded from existing Neon DB + average market prices for gaps)
- Nutrition display per recipe (based on ingredient data)
- Food cost calculation: ingredient cost + configurable margin = suggested selling price
- AI chat / command palette (read + scale + cost queries; no recipe creation via chat yet)
- Data migration: Alembic scripts transforming old Neon schema → new Docker PostgreSQL schema
- Responsive web app (any device, any browser)

**NOT in MVP** (deferred):
- Shopping list → Phase 3
- Task/prep checklist → Phase 3
- Allergen auto-detection → Phase 3
- EU compliance labels / PDF export → Phase 6+
- Full CRUD via AI chat → Phase 3
- Voice interface → Phases 2 + 4

### Phase 2: Voice Pipeline (Weeks 3-4)

**Goal**: Build and validate the voice pipeline as a standalone subsystem. Proves hardware, STT, and LLM intent parsing work end-to-end, independent of the main app.

**Team allocation**: 1 dedicated voice developer. Rest of team works on Phase 3.

| Week | Deliverables |
|---|---|
| 3 | RPi setup, ReSpeaker XVF3800 driver integration, wake word engine (OpenWakeWord / Porcupine), local STT setup (faster-whisper) |
| 4 | WebSocket connection to FastAPI backend, full standalone pipeline: RPi → STT → WebSocket → LLM intent parsing → structured JSON response, audio feedback (beeps/chimes) |

**Phase 2 Deliverable**: Standalone voice demo -- a developer speaks a command ("Kartoffelsalat für 100"), the RPi transcribes it locally, sends the transcript to the server via WebSocket, the LLM parses intent into structured JSON (`{intent: "scale_recipe", recipe: "Kartoffelsalat", portions: 100}`), and a confirmation beep plays. The server logs the interaction but does **not** execute the intent against the database.

### Phase 3: Extras (Weeks 3-5)

**Goal**: Add shopping lists, task checklists, allergen display, and expand AI chat to full CRUD parity. Runs in parallel with Phase 2.

**Team allocation**: 2-4 developers (everyone except the voice dev).

| Week | Deliverables |
|---|---|
| 3 | Shopping list backend + frontend (simple: add/remove/check items) |
| 4 | Task/prep checklist backend + frontend (simple: title + pending/done status), allergen display per recipe (from ingredient-allergen mappings in DB) |
| 5 | Expand AI chat to full CRUD parity (create/edit recipes via chat), add shopping list and task commands to agent tool set |

**Phase 3 Deliverables**:
- Shopping list management (add/remove/check, screen-only initially)
- Task/prep checklist (daily view, add/check/remove)
- Allergen display per recipe (based on ingredient-allergen data, not auto-detection)
- AI chat with full CRUD parity (all entities)
- Agent tool coverage for shopping lists and tasks

### Phase 4: Voice Integration (Week 5)

**Goal**: Connect the standalone voice pipeline (Phase 2) to the live application. Voice commands now execute real database actions.

| Week | Deliverables |
|---|---|
| 5 | Wire voice WebSocket to agent runtime, voice transcripts appear in unified chat thread, agent executes intents from voice input (recipe lookup, scaling, shopping list, tasks), end-to-end simulation testing |

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
- 83 recipe-level nutrition records (recipe_nutrition + nutrition_facts)
- 13 tenants (12 test scaffolds, 1 real), 0 users

### 12.2 Implementation Files

- `alembic/versions/001_initial_schema.py` to `alembic/versions/010_canonical_backfill_on_migration.py` -- authoritative migration chain ending at schema 010
- `scripts/seed_from_neon.py` -- Python migration script (Neon read-only -> Docker PostgreSQL)
- `scripts/reference_data/allergens.json` -- reference allergen data used during migration
- `scripts/reference_data/additives.json` -- reference additive data used during migration
- `scripts/reference_data/units.json` -- 18 standard kitchen units with gram conversion factors

### 12.3 Migration Steps

Run in order:
1. `alembic upgrade head` -- creates empty schema in Docker PostgreSQL
2. `python scripts/seed_from_neon.py --source $NEON_URL --target $DATABASE_URL` -- schema-010-oriented migration flow:

| Step | Table | Rows | Transformation |
|---|---|---|---|
| 1 | `allergens` | 31 | Seed from reference JSON into current `code` + `name` model |
| 2 | `additives` | 32 | Seed from reference JSON into current `code` + `name` model |
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
| 14 | `recipe_nutrition` | 83 | Link recipe nutrition through `nutrition_facts` records |
| 15 | `recipe_versions` | as available | Persist historical snapshots where available |

### 12.4 Key Design Decisions

- **Grams-canonical unit system**: All quantities and prices are stored canonically in grams (`quantity_grams`, `price_per_gram`). Display units (`quantity`, `unit`) are preserved alongside for UX. A `units` reference table with gram conversion factors and an `ingredient_units` table for ingredient-specific overrides (e.g. 1 egg = 58g) provide the conversion layer. Cost = `quantity_grams × price_per_gram`. Nutrition = `(quantity_grams / 100) × per_100g`.
- **Canonical yield model**: Recipes support portion-first and weight-first authoring via `yield_mode`. Recipe-level metrics (`total_raw_weight_grams`, `total_cooked_weight_grams`, `portions_count_resolved`) are derived to make API/UI output deterministic.
- **Activation guardrail for weight mode**: `status='active'` recipes in `yield_mode='weight'` must provide `portion_size_grams`.
- **Allergen/additive IDs regenerated**: New UUIDs in target; junction tables remapped via current code lookup model
- **Ingredient prices constraint**: Partial unique index (`WHERE supplier_id IS NOT NULL` / `IS NULL`) instead of standard UNIQUE to handle NULL supplier_id
- **Recipe time columns**: schema 010 currently keeps legacy text-oriented time fields; normalization can continue in a later migration.
- **No neon_auth migration**: Auth is handled by simple FastAPI JWT (users table + bcrypt in Python). The neon_auth schema is not carried over.
- **Validation**: Script compares source/target row counts and verifies unit/pricing backfill coverage (`quantity_grams`, `price_per_gram`) plus relation integrity across mapped tables.

---

## 13. Success Criteria

### Phase 1: MVP (Weeks 1-3)
- [ ] Kitchen staff can look up any recipe by name (web + chat)
- [ ] Recipes can be scaled to any number of portions with recalculated quantities
- [ ] Food cost per portion is calculated (ingredient cost + margin)
- [ ] AI chat handles read, scale, and cost queries correctly
- [ ] < 100 existing recipes migrated successfully from Neon to Docker PostgreSQL
- [ ] App runs in Docker Compose and is accessible from any browser
- [ ] Deployed to production Docker host

### Phase 2: Voice Pipeline (Weeks 3-4)
- [ ] RPi + ReSpeaker captures audio and transcribes locally via faster-whisper
- [ ] Wake word activates reliably in office/lab environment
- [ ] Full pipeline produces structured intent JSON from spoken commands
- [ ] Confirmation beep plays on successful intent parse

### Phase 3: Extras (Weeks 3-5)
- [ ] Shopping list is functional (add/remove/check items)
- [ ] Task checklist is functional (add/check/remove)
- [ ] Allergens display correctly per recipe
- [ ] AI chat can create and edit recipes (full CRUD parity)

### Phase 4: Voice Integration (Week 5)
- [ ] Voice commands execute real DB actions (recipe lookup, scaling, list management)
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
