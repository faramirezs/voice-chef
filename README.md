This project has been created as part of the 42 curriculum by @alramire, @mpeshko, @mekundur, @cbotel, @dmlasko.

# Voice Chef

A voice-driven kitchen assistant for professional and home cooks. Voice Chef pairs a recipe-authoring web app with a hands-free, tablet-mounted kitchen assistant that listens, searches, and renders recipes on demand — driven by an LLM agent with semantic recipe search (RAG) and on-device speech-to-text.


## Description

**Voice Chef** is a multi-tenant web application built around two complementary user experiences:

- **Office UI** — a desktop SPA for recipe authoring: structured ingredients, yield modes (count or weight), categories/tags, file uploads (recipe PDFs, photos), versioning, and analytics.
- **Kitchen UI** — a tablet UI optimised for greasy hands. The user speaks; an LLM agent decides whether to search the catalog (semantic + lexical), open a recipe, scale portions, or answer follow-up questions. Responses stream into slot-based UI panels (recipe canvas, sticky info, confirmation chips, toasts) driven by the agent itself.

### Key features

- **Two purpose-built React frontends** — an *office* SPA (Vite + React 19 + Tailwind 4) for recipe authoring with a custom design system, advanced search/filter/sort/pagination, and file uploads; and a *kitchen* optimised for greasy-hands tablet use.
- **FastAPI backend** — tenant-scoped REST API for users, recipes, ingredients, and uploads, backed by PostgreSQL + SQLModel and protected by Argon2 + JWT auth.
- **Voice-first kitchen flow** — push-to-talk on a tablet → on-device Whisper transcription → AG-UI streamed agent response → slot-based UI updates.
- **Tool-calling LLM agent** — Llama-3.3-70B (NVIDIA NIM) with provider failover (OpenRouter, OpenAI). The agent calls backend CRUD and the RAG service via typed tools.
- **Hybrid semantic search (RAG)** — Qdrant with dense (multilingual sentence-transformer) + sparse (BM25) fused via RRF; backfills on startup, polls for changes.
- **Microservices** — backend, agent, rag, stt as independent FastAPI services behind an HTTPS-terminating nginx reverse proxy.
- **Continuous deployment** — GitHub Actions → Hetzner VPS, gated by a 4-stage Schema Drift checker.
- **Raspberry Pi kitchen point** — a Pi-based thin client running Chromium kiosk + local Whisper STT, connected to the central server over Tailscale.

## Instructions

### Prerequisites

- Docker Desktop ≥ 4.30 (or Docker Engine + Compose v2)
- `make` (GNU make 3.81+)
- `openssl` (for generating shared secrets)
- ~10 GB free disk for images + Qdrant + Postgres volumes
- Latest stable Google Chrome (the only officially supported browser)

### Setup

```bash
# 1. Clone
git clone <repo-url>
cd voice-chef

# 2. Configure environment
cp .env.example .env

# 3. Generate the three required secrets
echo "INTERNAL_SECRET=$(openssl rand -base64 32)" >> .env
echo "QDRANT_API_KEY=$(openssl rand -base64 32)" >> .env
echo "SECRET_KEY=$(openssl rand -base64 32)" >> .env

# 4. Set your AI provider key (NVIDIA NIM by default)
#    Edit .env: AGENT_API_KEY=<your-key>

# 5. Set Postgres credentials
#    Edit .env: POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD

# 6. Bring the stack up
make prod              # production: builds with --no-cache, runs detached
# OR
make dev               # development: hot-reload, mounted volumes
#OR
make help              # show the list of useful make targets
```

Open `https://localhost/` and sign up. The kitchen UI is at `https://localhost/kitchen/`.

> **Note:** the stack uses a self-signed TLS certificate. Chrome will warn on first visit — accept the warning to proceed.

## Resources

### Documentation and references

- **FastAPI** — https://fastapi.tiangolo.com (backend, agent, rag, stt)
- **SQLModel** — https://sqlmodel.tiangolo.com (ORM)
- **Alembic** — https://alembic.sqlalchemy.org (migrations + custom drift gate)
- **pydantic-ai** — https://ai.pydantic.dev (tool-calling agent runtime + AG-UI adapter)
- **AG-UI protocol** — https://docs.ag-ui.com (streaming UI events)
- **Qdrant** — https://qdrant.tech (vector store; hybrid dense+sparse)
- **fastembed / BM25** — https://qdrant.github.io/fastembed (sparse vectors)
- **sentence-transformers** — https://sbert.net (`paraphrase-multilingual-mpnet-base-v2`)
- **faster-whisper** — https://github.com/SYSTRAN/faster-whisper (STT, CTranslate2 backend)
- **React 19 + Vite + Tailwind 4** — frontends
- **TanStack Query** — server-state cache for both frontends
- **nginx** — TLS termination + reverse proxy

### How AI was used

This project was built collaboratively with AI assistants. The team used AI for the following, and reviewed all generated content before merging:

- **Code generation & refactoring** — boilerplate (React form handlers, Pydantic schemas, Alembic migrations skeletons), then human-edited.
- **Prompt engineering for the agent** — iterating the system prompt for the kitchen assistant, including cross-lingual matching guidance and search-result-honesty rules (prefer "no match found" over wrong recipe).
- **RAG threshold tuning** — pair-debugging the dense+sparse score fusion and the dynamic relevance cutoff.
- **Documentation** — drafting the architectural docs in `docs/` (microservices, frontend, voice, migrations).
- **CI/CD** — initial draft of the Schema Drift Gate workflow and the SSH-based deploy step.

The team avoided letting AI write any single component end-to-end without review. Every PR was reviewed by at least one human teammate before merge.

## Team Information

| Member | Role(s) |
|---|---|
| @alramire | **Product Owner & Tech Lead** |
| @mpeshko | **Developer** |
| @mekundur | **Developer** |
| @cbotel | **Developer** |
| @dmlasko | **Project Manager & Developer** |

## Project Management

- **Work tracking** — GitHub Issues, organized by feature (recipe authoring, voice loop, RAG, infra). Every change goes through a Pull Request; PRs reference issues by number.
- **Code review** — at least one human reviewer per PR. 
- **Communication** — Slack for sync chat and stand-ups; PR comments for code-specific discussion; longer architectural decisions captured in `docs/`.
- **Quality gates** — every push runs `build-check.yml` (Node + Python sanity) and `schema-drift.yml` (4-stage Alembic drift checker). Deployments to the VPS are gated on the drift gate passing.

## Technical Stack

### Frontend

- **React 19** (Vite-bundled, TypeScript) — selected over Vue/Svelte for ecosystem maturity and team familiarity.
- **Tailwind CSS 4** + custom CSS-variable design tokens (oklch colour palette, typography) — see `frontend/office/src/index.css`.
- **TanStack Query** — server-state cache, optimistic mutations, background refetch.
- **AG-UI client** — streaming agent events, decoded into slot updates.

### Backend

- **FastAPI** + Pydantic v2 — async-capable, OpenAPI for free, type-safe schemas. Chosen over Flask/Django for first-class async + streaming and over NestJS to keep the language stack consistent with the AI services.
- **SQLModel** (Pydantic + SQLAlchemy) — single source of truth between API schemas and ORM models.
- **Alembic** — schema migrations with a custom 4-gate drift checker (`db/test/conftest.py`) preventing model/DB skew.
- **Argon2** password hashing, **JWT (HS256)** session tokens — issued via FastAPI's OAuth2 password flow (`OAuth2PasswordRequestForm` on `/login`, `OAuth2PasswordBearer` on protected routes) and accepted as either an `Authorization: Bearer` header or an `access_token` cookie.
- **Per-service requirements.txt** — backend, agent, rag, stt each isolate their dependencies.

### Database

- **PostgreSQL 17.8** — chosen for SQLModel maturity, JSONB for flexible per-tenant settings, strong concurrency, and well-understood operations. Each tenant's data is row-scoped via `tenant_id` foreign keys.
- **Qdrant** (vector store) — supports hybrid dense + sparse search natively, exposes a stable HTTP API, and runs as a single container.

### AI / ML

- **Llama-3.3-70B** via NVIDIA NIM (default), with **OpenRouter** and **OpenAI** as failover providers — switchable at runtime via `AGENT_PROVIDER`.
- **pydantic-ai** — typed tool-calling agent runtime; usage budgets enforced server-side (`request_limit=25`, `tool_calls_limit=10`).
- **AG-UI streaming protocol** (POST + SSE) — server-to-client streaming of agent events including custom `ui.render`/`ui.clear` envelopes.
- **faster-whisper** (CTranslate2 backend) — Whisper STT, runs on Pi (tiny/base) and on the server (base/small/medium).

### Infrastructure

- **Docker Compose** — single-host orchestration; 9 services on a shared bridge network.
- **nginx-proxy** — TLS termination (self-signed dev cert, Let's Encrypt-ready), single public surface for all browser-facing routes.
- **GitHub Actions** — `build-check` (per-PR), `schema-drift` (4-gate Alembic checker), `deploy` (SSH-based push to Hetzner VPS, Alembic migrations on remote, health check).
- **Tailscale** (Raspberry Pi and VPS) — connects the Pi kitchen point to the central server over a private mesh.

## Database Schema

The schema is multi-tenant: every domain row carries a `tenant_id`. Below is the high-level shape; full DDL is generated from the SQLModel models in `backend/app/models/` and managed by Alembic.

```
                          ┌─────────────┐
                          │   tenants   │
                          │  (id, slug, │
                          │ name, ...)  │
                          └──────┬──────┘
                                 │ 1:N
            ┌────────────┬───────┼───────┬────────────┬──────────────┐
            ▼            ▼       ▼       ▼            ▼              ▼
       ┌────────┐  ┌─────────┐  ...  ┌──────────┐  ┌──────────┐  ┌────────┐
       │ users  │  │ recipes │       │ingredients│  │categories│  │  tags  │
       └───┬────┘  └────┬────┘       └─────┬────┘  └────┬─────┘  └───┬────┘
           │            │                  │            │            │
           │ created_by │                  │            │            │
           └────────────┘                  │            │            │
                        │ M:N via          │            │            │
                        ├─ recipe_ingredients ──────────┘            │
                        │                                            │
                        ├─ recipe_categories ────────────────────────┘
                        │
                        ├─ recipe_tags
                        │
                        ├─ recipe_versions   (1:N audit history)
                        └─ recipe_nutrition_cache  (1:1 cache)
```

### Tables and key fields

| Table | Key fields | Notes |
|---|---|---|
| `tenants` | `id` (UUID PK), `slug` (unique), `name`, `is_active`, `settings` (JSONB) | Top of the multi-tenant tree |
| `users` | `id` (UUID PK), `email` (unique), `password_hash` (Argon2), `role` (`admin`/`editor`/`viewer`), `is_active`, `tenant_id` (FK) | Argon2 + JWT auth |
| `recipes` | `id`, `name`, `description`, `instructions`, `yield_mode` (`count`/`weight`), `yield_amount`, `portion_size_grams`, `status` (`draft`/`active`/`archived`), `is_component`, `tenant_id`, `created_by` | Check-constrained yield model |
| `recipe_ingredients` | composite PK (`recipe_id`, `ingredient_id`, …) | M:N junction with quantities and units |
| `ingredients` | `id`, `name`, `tenant_id` | Tenant-scoped catalog |
| `ingredient_details` | nutrition + sourcing per ingredient | 1:1 with `ingredients` |
| `categories` / `tags` | tenant-scoped taxonomies | M:N via `recipe_categories` / `recipe_tags` |
| `recipe_versions` | `id`, `recipe_id` (FK), serialized snapshot, `created_at` | Audit history |
| `recipe_nutrition_cache` | `recipe_id` (PK + FK), per-100g breakdown | 1:1 cache |
| `units` | unit conversions and abbreviations | Reference table |
| `audit_logs` | request-level audit trail | Cross-cutting |
| `agents` / `agent_interactions` | per-tenant agent config + interaction log | For voice/AI module |
| `tasks` / `shopping_lists` | kitchen-side checklist features | Tenant-scoped |

Full migration history lives in `alembic/versions/`. The 4-stage Schema Drift Gate (`db/test/conftest.py`) blocks any model change that hasn't produced a corresponding migration.

## Features List

| Feature | Description |
|---|---|
| Tenant-based signup & login | Email/password, Argon2 hashing, JWT cookie + bearer; password strength validation |
| Recipe authoring (office) | Create/edit recipes with structured ingredients |
| File uploads (PDFs, photos) | Multi-layer client + server validation, progress bar, preview, delete |
| Recipe search (office) | Name filter, status filter, 6 sort orders, paginated 24/48/96 |
| Office design system | 20 reusable UI primitives + design tokens (oklch palette) |
| Kitchen voice loop | Push-to-talk → STT → AG-UI agent → slot-based UI render |
| Slot-based agent UI | `AgentSlotProvider` registry; agent emits `ui.render` / `ui.clear` to canvas/sticky/chips/toasts |
| Recipe detail / scaling (kitchen) | Yield-mode-aware portion scaling, ingredient table |
| Tool-calling LLM agent | Multi-provider, per-request notification dedupe, cross-lingual prompt |
| RAG service | Qdrant hybrid dense+sparse, dynamic relevance threshold, backfill + polling sync |
| STT service | faster-whisper, multipart `/transcribe` endpoint, language auto-detect |
| Microservices topology | 9-service Compose stack, REST inter-service, internal-secret bypass for agent→backend |
| HTTPS reverse proxy | nginx-proxy with self-signed cert; single public surface; perimeter TLS model |
| CI: build check | Per-PR Node + Python syntax/import sanity |
| CI: Schema Drift Gate | 4-stage Alembic drift checker (autogenerate + replay + pytest-alembic) |
| CD: VPS deploy | SSH → Hetzner → `make prod` → Alembic migrate → health check |
| Raspberry Pi kitchen point | Sparse-clone provisioning, Chromium kiosk, local STT, nginx TLS shim, systemd autostart |
| Privacy / Terms pages | `/privacy` and `/terms` routes accessible from signup and footer |
| Architectural docs | `docs/` — microservices, frontend, voice, migrations, vision |

## Modules

**Total: 21 points**

### Web

| Module | Pts | Owner(s) | Justification & implementation |
|---|---|---|---|
| **Major: Frontend + Backend frameworks** | 2 | @dmlasko, @mpeshko, @mekundur | React 19 (Vite, TypeScript) for both office and kitchen frontends; FastAPI for backend, agent, rag, stt. |
| **Minor: ORM** | 1 | @mpeshko, @mekundur, @dmlasko | SQLModel across all `backend/app/models/`, with `Relationship(back_populates=...)` and Alembic migrations. |
| **Minor: Search filters / sorting / pagination** | 1 | @mekundur, @dmlasko, @mpeshko | `frontend/office/src/components/recipes/RecipeList.tsx` — name filter, draft/active/all filter, 6 sort orders, page size (24/48/96) + prev/next. Backend supports `status`, `name`, `sort_by`, `offset`, `limit`. |
| **Minor: Custom design system** | 1 | @dmlasko, @mpeshko | 20 reusable primitives in `frontend/office/src/components/ui/` (Button, Card, Dialog, Input, Select, Avatar, Combobox, Sheet, Sidebar, Tooltip, …). Design tokens (oklch palette, typography, radius/spacing scale) in `index.css`. |
| **Minor: File upload + management** | 1 | @mekundur, @dmlasko | `frontend/office/src/pages/FilesPage.tsx`. PDFs with multi-layer client validation (size ≤ 100 MB, MIME, extension, header bytes), server-side re-validation, upload progress bar, preview link, delete with confirmation. |
| **Major: Public API** | 2 | @mekundur | Backend exposes a tenant-scoped REST API under `/api/...` with GET/POST/PUT/DELETE across `/recipes`, `/ingredients`, `/users`, `/auth`, `/uploads/images`, `/uploads/pdfs` (>5 endpoints). OpenAPI + Swagger UI at `/docs`. **⚠ See "Known limitations" below — rate limiting and a public API-key scheme are pending.** |

### Artificial Intelligence

| Module | Pts | Owner(s) | Justification & implementation |
|---|---|---|---|
| **Major: LLM system interface** | 2 | @alramire | `agent/` service. pydantic-ai with multi-provider switch (NVIDIA NIM / OpenRouter / OpenAI) via `AGENT_PROVIDER` + `AGENT_MODEL`. Streaming SSE responses via `AGUIAdapter.dispatch_request()`. Server-side rate limiting via `UsageLimits(request_limit=25, tool_calls_limit=10)`. Error handling on tool calls + provider failures. |
| **Major: RAG** | 2 | @cbotel | `rag/` service. Qdrant collections for recipes + ingredients. Hybrid retrieval: dense (`paraphrase-multilingual-mpnet-base-v2`) + sparse (BM25 via fastembed) fused with RRF (k=1). Dynamic relevance threshold (`max(ABSOLUTE_FLOOR, top * RELATIVE_FACTOR)`) replaces fixed cutoff. Backfill on startup + 30-second polling sync against backend; `POST /reindex` for manual rebuild. Used by the agent's `search_recipes` / `search_ingredients` tools to answer user questions with retrieved context. |
| **Minor: Voice / speech integration** | 1 | @cbotel | `stt/` service. faster-whisper (CTranslate2 backend); `POST /transcribe` accepts multipart audio (wav/mp3/ogg/flac/webm). Kitchen frontend records via push-to-talk, uploads to STT, feeds transcript into the agent. Model switchable via `STT_MODEL`. |

### Devops

| Module | Pts | Owner(s) | Justification & implementation |
|---|---|---|---|
| **Major: Backend as microservices** | 2 | @cbotel, @alramire | 9 Compose services (`backend`, `agent`, `rag`, `stt`, `db`, `qdrant`, `office-frontend`, `kitchen-frontend`, `nginx-proxy`). Each owns its Dockerfile and `requirements.txt`. REST inter-service (agent → backend, rag → backend, agent → rag). Single-responsibility split documented in `docs/microservices.md`. Loose coupling demonstrable: `docker compose stop agent` leaves the office UI fully operational. |

### Modules of choice

| Module | Pts | Owner(s) | Justification & implementation |
|---|---|---|---|
| **Major: Agent-driven UI rendering protocol** | 2 | @alramire | We chose this module because a voice-first kitchen assistant requires more than a traditional chatbot interface. In a cooking environment, the assistant must dynamically display the correct UI state (recipe cards, ingredient chips, notifications, overlays) without requiring manual navigation.<br><br>To solve this, we built a custom layer on top of AG-UI streaming where the server-side agent decides which UI component should be rendered and into which named slot on the kitchen client (canvas / sticky / chips / notifications / overlay). The protocol uses versioned envelopes such as `{ type: "ui.render", version: "1", component, slot, ...props }` and `ui.clear` for slot reset. The client's `AgentSlotProvider` + component registry resolves the envelope to a typed React component and mounts it. This inverts the usual chat UX: instead of a static UI consuming agent text, the agent drives a dynamic UI. The technical challenges included typed component resolution, slot lifecycle management, request-scoped notification deduplication, `ui.clear` synchronization, parallel tool-call race conditions, and synchronization between streamed agent events and frontend state. This architecture adds major value because it transforms the assistant from a simple text interface into a context-aware interactive kitchen system capable of guiding users hands-free during cooking.<br><br>It deserves Major status because it introduces a non-trivial custom frontend/backend protocol, dynamic runtime UI composition, streaming synchronization logic, and a fully custom rendering pipeline beyond standard CRUD or chat functionality. See `frontend/kitchen/src/agent-ui/types.ts` and `frontend/kitchen/src/components/layout/AgentSlotProvider.tsx`. |
| **Major: Continuous deployment + VPS** | 2 | @alramire | We chose this module to ensure reliable production deployment and to eliminate manual deployment errors during rapid development. The project uses a full CI/CD pipeline built around GitHub Actions and a Hetzner VPS deployment target.<br><br>The infrastructure includes three workflows (371 lines total): `build-check.yml` (per-PR Node + Python syntax/import sanity), `schema-drift.yml` (4-stage Alembic drift checker — autogenerate replay, pytest-alembic, drift_check.py — gates `main`), and `deploy.yml` (SSH-based deploy to a Hetzner VPS, gated on the drift gate, runs `make prod` remotely with `--no-cache` rebuild, then `alembic upgrade head` and a health check). One of the main technical challenges addressed was database schema drift, where mismatches between migrations and ORM models could silently break production deployments. To solve this, the pipeline performs migration replay, autogenerated drift checks, and `pytest-alembic` validation before deployment is allowed. Additional complexity comes from concurrency protection (`cancel-in-progress: false` so a deploy cannot be interrupted mid-migration), remote orchestration, automated migration execution, and post-deploy health verification. This adds significant value because the project can safely deploy backend, frontend, and database changes with reproducible builds and automated validation.<br><br>It deserves Major status because the infrastructure goes far beyond basic hosting: it includes advanced CI validation gates, automated production deployment, migration safety guarantees, VPS orchestration, and deployment reliability engineering. |
| **Major: Raspberry Pi kitchen point** | 2 | @cbotel | We chose this module because the project is designed as a real kitchen assistant rather than only a browser application. A dedicated kitchen device allows hands-free interaction, always-on voice control, and a persistent cooking interface directly in the physical environment where recipes are used. The implementation is based on a Raspberry Pi 5 running a Chromium kiosk connected to the kitchen frontend over Tailscale. A major technical challenge was enabling secure local speech-to-text processing while preserving HTTPS compatibility required by browser microphone APIs. This was solved using a local nginx TLS shim so the HTTPS frontend can securely call `https://localhost/stt/`. This module adds significant value because it turns the software platform into a deployable physical appliance with edge AI inference and local audio processing, improving latency and privacy by keeping kitchen audio on-device.<br><br>It deserves Major status because it combines embedded Linux configuration, networking, kiosk infrastructure, local AI inference, hardware integration, secure HTTPS communication, and automated provisioning into a production-ready hardware/software system. |

## License & credits

This project is an academic submission for the 42 curriculum. All third-party licenses are respected per their dependency manifests (`backend/requirements.txt`, `agent/requirements.txt`, `rag/requirements.txt`, `stt/requirements.txt`, `frontend/*/package.json`).
