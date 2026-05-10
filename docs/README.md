_This project has been created as part of the 42 curriculum by <team_member>, <team_member>, <team_member>, <team_member>, <team_member>._

# Voice Chef

A voice-driven kitchen assistant for professional and home cooks. Voice Chef pairs a recipe-authoring web app with a hands-free, tablet-mounted kitchen assistant that listens, searches, and renders recipes on demand — driven by an LLM agent with semantic recipe search (RAG) and on-device speech-to-text.

## Description

**Voice Chef** is a multi-tenant web application built around two complementary user experiences:

- **Office UI** — a desktop SPA for recipe authoring: structured ingredients, yield modes (count or weight), categories/tags, file uploads (recipe PDFs, photos), versioning, and analytics.
- **Kitchen UI** — a PWA-installable tablet UI optimised for greasy hands. The user speaks; an LLM agent decides whether to search the catalog (semantic + lexical), open a recipe, scale portions, set timers, or answer follow-up questions. Responses stream into slot-based UI panels (recipe canvas, sticky info, confirmation chips, toasts) driven by the agent itself.

### Key features

- **Two purpose-built React frontends** — an *office* SPA (Vite + React 19 + Tailwind 4) for recipe authoring with a custom design system, advanced search/filter/sort/pagination, and file uploads; and a *kitchen* PWA optimised for greasy-hands tablet use.
- **Multi-tenant FastAPI backend** — tenant-scoped REST API for users, recipes, ingredients, and uploads, backed by PostgreSQL + SQLModel and protected by Argon2 + JWT auth.
- **Voice-first kitchen flow** — push-to-talk on a tablet → on-device Whisper transcription → AG-UI streamed agent response → slot-based UI updates.
- **Tool-calling LLM agent** — Llama-3.3-70B (NVIDIA NIM) with provider failover (OpenRouter, OpenAI). The agent calls backend CRUD and the RAG service via typed tools.
- **Hybrid semantic search (RAG)** — Qdrant with dense (multilingual sentence-transformer) + sparse (BM25) fused via RRF; backfills on startup, polls for changes.
- **Microservices** — backend, agent, rag, stt as independent FastAPI services behind an HTTPS-terminating nginx reverse proxy.
- **Continuous deployment** — GitHub Actions → Hetzner VPS, gated by a 4-stage Schema Drift checker.
- **Raspberry Pi kitchen point** — a Pi-based thin client running Chromium kiosk + local Whisper STT, connected to the central server over Tailscale.
- **Installable PWA** — kitchen UI works offline for recipe browsing once cached.

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

# 7. First-time DB schema
docker compose exec backend alembic upgrade head
```

Open `https://localhost/` and sign up. The kitchen UI is at `https://localhost/kitchen/`.

> **Note:** the stack uses a self-signed TLS certificate. Chrome will warn on first visit — accept the warning to proceed.

### Useful Make targets

| Target | What it does |
|---|---|
| `make dev` / `make dev-re` | Dev stack (cached / no-cache rebuild) |
| `make prod` | Production stack (no-cache rebuild, detached) |
| `make down` / `make stop` / `make start` | Lifecycle |
| `make status` / `make logs` | Observability |
| `make drift-gate-local` | Run the 4-gate schema drift checks locally before pushing |
| `make db-connect` | Open a `psql` shell in the db container |
| `make fclean` | **Destructive:** removes containers, volumes, images (wipes DB) |

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
- **VitePWA / Workbox** — PWA service worker for kitchen
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

> All names below are placeholders pending final assignment.

| Member | Role(s) | Responsibilities |
|---|---|---|
| `<team_member>` | **Product Owner & Project Manager** | < add information > |
| `<team_member>` | **Tech Lead** | < add information > |
| `<team_member>` | **Developer** | < add information > |
| `<team_member>` | **Developer** | < add information > |
| `<team_member>` | **Developer** | < add information > |

## Project Management

- **Work tracking** — GitHub Issues, organized by feature (recipe authoring, voice loop, RAG, infra). Every change goes through a Pull Request; PRs reference issues by number.
- **Code review** — at least one human reviewer per PR. 
- **Communication** — Slack for sync chat and stand-ups; PR comments for code-specific discussion; longer architectural decisions captured in `docs/`.
- **Quality gates** — every push runs `build-check.yml` (Node + Python sanity) and `schema-drift.yml` (4-stage Alembic drift checker). Deployments to the VPS are gated on the drift gate passing.

## Technical Stack

### Frontend

- **React 19** (Vite-bundled, TypeScript) — selected over Vue/Svelte for ecosystem maturity and team familiarity.
- **Tailwind CSS 4** + custom CSS-variable design tokens (oklch colour palette, Figtree typography) — see `frontend/office/src/index.css`.
- **TanStack Query** — server-state cache, optimistic mutations, background refetch.
- **VitePWA / Workbox** (kitchen only) — installable PWA, runtime caching for offline recipe browsing.
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
- **paraphrase-multilingual-mpnet-base-v2** (768-dim dense) + **BM25** (sparse) fused via Reciprocal Rank Fusion, k=1 — handles cross-lingual queries (e.g., German ↔ English recipe names).
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

| Feature | Owner(s) | Description |
|---|---|---|
| Multi-tenant signup & login | `<team_member>` | Email/password, Argon2 hashing, JWT cookie + bearer; password strength validation |
| Recipe authoring (office) | `<team_member>` | Create/edit recipes with structured ingredients, yield modes, categories/tags |
| File uploads (PDFs, photos) | `<team_member>` | Multi-layer client + server validation, progress bar, preview, delete |
| Recipe search (office) | `<team_member>` | Name filter, status filter, 6 sort orders, paginated 24/48/96 |
| Office design system | `<team_member>` | 20 reusable UI primitives + design tokens (oklch palette, Figtree typography) |
| Kitchen voice loop | `<team_member>` | Push-to-talk → STT → AG-UI agent → slot-based UI render |
| Slot-based agent UI | `<team_member>` | `AgentSlotProvider` registry; agent emits `ui.render` / `ui.clear` to canvas/sticky/chips/toasts |
| Kitchen PWA | `<team_member>` | Installable manifest, Workbox runtime caching, offline recipe browsing |
| Recipe detail / scaling (kitchen) | `<team_member>` | Yield-mode-aware portion scaling, ingredient table, sticky controls |
| Tool-calling LLM agent | `<team_member>` | Multi-provider, usage budgets, per-request notification dedupe, cross-lingual prompt |
| RAG service | `<team_member>` | Qdrant hybrid dense+sparse, RRF fusion, dynamic relevance threshold, backfill + polling sync |
| STT service | `<team_member>` | faster-whisper, multipart `/transcribe` endpoint, language auto-detect |
| Microservices topology | `<team_member>` | 9-service Compose stack, REST inter-service, internal-secret bypass for agent→backend |
| HTTPS reverse proxy | `<team_member>` | nginx-proxy with self-signed cert; single public surface; perimeter TLS model |
| CI: build check | `<team_member>` | Per-PR Node + Python syntax/import sanity |
| CI: Schema Drift Gate | `<team_member>` | 4-stage Alembic drift checker (autogenerate + replay + pytest-alembic) |
| CD: VPS deploy | `<team_member>` | SSH → Hetzner → `make prod` → Alembic migrate → health check |
| Raspberry Pi kitchen point | `<team_member>` | Sparse-clone provisioning, Chromium kiosk, local STT, nginx TLS shim, systemd autostart |
| Privacy / Terms pages | `<team_member>` | `/privacy` and `/terms` routes accessible from signup and footer |
| Architectural docs | `<team_member>` | `docs/` — microservices, frontend, voice, migrations, PWA, vision |

## Modules

**Total: 24 points** (9 Major × 2 + 6 Minor × 1)

### Web

| Module | Pts | Owner(s) | Justification & implementation |
|---|---|---|---|
| **Major: Frontend + Backend frameworks** | 2 | `<team_member>` | React 19 (Vite, TypeScript) for both office and kitchen frontends; FastAPI for backend, agent, rag, stt. Both qualify under IV.1. |
| **Minor: ORM** | 1 | `<team_member>` | SQLModel across all `backend/app/models/`, with `Relationship(back_populates=...)` and Alembic migrations. |
| **Minor: Search filters / sorting / pagination** | 1 | `<team_member>` | `frontend/office/src/components/recipes/RecipeList.tsx` — name filter, draft/active/all filter, 6 sort orders, page size (24/48/96) + prev/next. Backend supports `status`, `name`, `sort_by`, `offset`, `limit`. |
| **Minor: Custom design system** | 1 | `<team_member>` | 20 reusable primitives in `frontend/office/src/components/ui/` (Button, Card, Dialog, Input, Select, Avatar, Combobox, Sheet, Sidebar, Tooltip, …) + 5 K* primitives in kitchen. Design tokens (oklch palette, Figtree typography, radius/spacing scale) in `index.css`. |
| **Minor: File upload + management** | 1 | `<team_member>` | `frontend/office/src/pages/FilesPage.tsx`. PDFs with multi-layer client validation (size ≤ 100 MB, MIME, extension, header bytes), server-side re-validation, upload progress bar, preview link, delete with confirmation. |
| **Minor: PWA** | 1 | `<team_member>` | VitePWA in `frontend/kitchen/vite.config.ts` — auto-update service worker, manifest with PWA icons (192/512), `display: standalone`. Workbox runtime caching: SWR for catalog, NetworkOnly for auth/agent/STT. Installable; offline recipe browsing once cached. |
| **Major: Public API** | 2 | `<team_member>` | Backend exposes a tenant-scoped REST API under `/api/...` with GET/POST/PUT/DELETE across `/recipes`, `/ingredients`, `/users`, `/auth`, `/uploads/images`, `/uploads/pdfs` (>5 endpoints). OpenAPI + Swagger UI at `/docs`. **⚠ See "Known limitations" below — rate limiting and a public API-key scheme are pending.** |
| **Major: Real-time features (WebSockets / similar)** | 2 | `<team_member>` | Agent responses stream over AG-UI's POST + SSE protocol. **⚠ See "Known limitations" below — broadcast-across-clients is pending.** |

### Artificial Intelligence

| Module | Pts | Owner(s) | Justification & implementation |
|---|---|---|---|
| **Major: LLM system interface** | 2 | `<team_member>` | `agent/` service. pydantic-ai with multi-provider switch (NVIDIA NIM / OpenRouter / OpenAI) via `AGENT_PROVIDER` + `AGENT_MODEL`. Streaming SSE responses via `AGUIAdapter.dispatch_request()`. Server-side rate limiting via `UsageLimits(request_limit=25, tool_calls_limit=10)`. Error handling on tool calls + provider failures. |
| **Major: RAG** | 2 | `<team_member>` | `rag/` service. Qdrant collections for recipes + ingredients. Hybrid retrieval: dense (`paraphrase-multilingual-mpnet-base-v2`) + sparse (BM25 via fastembed) fused with RRF (k=1). Dynamic relevance threshold (`max(ABSOLUTE_FLOOR, top * RELATIVE_FACTOR)`) replaces fixed cutoff. Backfill on startup + 30-second polling sync against backend; `POST /reindex` for manual rebuild. Used by the agent's `search_recipes` / `search_ingredients` tools to answer user questions with retrieved context. |
| **Minor: Voice / speech integration** | 1 | `<team_member>` | `stt/` service. faster-whisper (CTranslate2 backend); `POST /transcribe` accepts multipart audio (wav/mp3/ogg/flac/webm). Kitchen frontend records via push-to-talk, uploads to STT, feeds transcript into the agent. Model switchable via `STT_MODEL`. |

### Devops

| Module | Pts | Owner(s) | Justification & implementation |
|---|---|---|---|
| **Major: Backend as microservices** | 2 | `<team_member>` | 9 Compose services (`backend`, `agent`, `rag`, `stt`, `db`, `qdrant`, `office-frontend`, `kitchen-frontend`, `nginx-proxy`). Each owns its Dockerfile and `requirements.txt`. REST inter-service (agent → backend, rag → backend, agent → rag). Single-responsibility split documented in `docs/microservices.md`. Loose coupling demonstrable: `docker compose stop agent` leaves the office UI fully operational. |

### Modules of choice

| Module | Pts | Owner(s) | Justification & implementation |
|---|---|---|---|
| **Major: Agent-driven UI rendering protocol** | 2 | `<team_member>` | A custom layer on top of AG-UI streaming: the **server-side agent** decides which UI component to render and into which named slot on the kitchen client (canvas / sticky / chips / notifications / overlay). The protocol is a versioned envelope `{ type: "ui.render", version: "1", component, slot, ...props }` (and `ui.clear` for slot reset). The client's `AgentSlotProvider` + component registry resolves the envelope to a typed React component and mounts it. This inverts the usual chat UX: instead of a static UI consuming agent text, the agent drives a dynamic UI. We chose this because hands-free kitchen work needs the assistant to *show* the right thing (the recipe canvas, the next-step chip) — not just speak. The technical complexity is in the slot lifecycle (per-request notification dedupe, ui.clear-on-no-match, parallel-tool-call race handling) and the kitchen-client registry. See `frontend/kitchen/src/agent-ui/types.ts` and `frontend/kitchen/src/components/layout/AgentSlotProvider.tsx`. |
| **Major: Continuous deployment + VPS** | 2 | `<team_member>` | Three GitHub Actions workflows (371 lines total): `build-check.yml` (per-PR Node + Python sanity), `schema-drift.yml` (4-gate Alembic checker — autogenerate replay, pytest-alembic, drift_check.py — gates `main`), and `deploy.yml` (SSH-based deploy to a Hetzner VPS, gated on the drift gate, runs `make prod` remotely with `--no-cache` rebuild, then `alembic upgrade head` and a health check). Concurrency-protected (`cancel-in-progress: false`) so a deploy can't be interrupted mid-migration. Justifies Major status because the schema drift gate is non-trivial CI infrastructure that prevents a whole class of production bugs the team had hit before. |
| **Major: Raspberry Pi kitchen point** | 2 | `<team_member>` | A physical kitchen tablet built on Raspberry Pi 5: Chromium kiosk → `https://${SERVER_HOST}/kitchen/` over Tailscale; **local** faster-whisper STT (so audio never leaves the kitchen); nginx TLS shim so the HTTPS PWA can call `https://localhost/stt/`; sparse git clone (`--filter=blob:none` + sparse-checkout) pulls only `pi/` + `stt/`. systemd autostart, polkit rules for the kiosk user, wireplumber config for the ReSpeaker audio HAT, race-free network-wait on boot. Files under `pi/` (compose, nginx, scripts, systemd, polkit, wireplumber, README). Justifies Major status because it integrates real hardware (audio HAT, kiosk display), edge inference (local Whisper), private networking (Tailscale), and a custom provisioning model (sparse clone). |

## Individual Contributions

> _To be added by the team._

## License & credits

This project is an academic submission for the 42 curriculum. All third-party licenses are respected per their dependency manifests (`backend/requirements.txt`, `agent/requirements.txt`, `rag/requirements.txt`, `stt/requirements.txt`, `frontend/*/package.json`).
