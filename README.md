# Voice Chef

Voice Chef is a web application for professional kitchens. It keeps recipes, ingredients and portion math in one place, and it lets cooks read that data hands-free at the prep station. The problem it solves: recipes and food cost live in spreadsheets and in the memory of senior staff, so standards and portion sizes drift the moment one person leaves. Voice Chef moves that knowledge into a central recipe database with two interfaces. A head chef or kitchen manager authors recipes in a desktop app (Office UI). A cook speaks a request in a tablet app (Kitchen UI): a speech-to-text service turns the audio into text, an LLM agent decides which operation to run, and the answer appears as a rendered recipe card rather than a wall of chat text. The kitchen also has a typed command palette, so voice is optional.

The stack runs on one machine with `make dev`. Current state: see [Project status and ownership](#project-status-and-ownership).

## Architecture

Two React frontends, three FastAPI services, PostgreSQL, and an nginx reverse proxy. Development mode runs five containers plus the database; the Vite dev servers proxy requests straight to the services and nginx stays off (it is assigned the `disabled` profile in `docker-compose.override.yml`). Production mode runs all seven; nginx terminates TLS and is the only published entry point.

```mermaid
flowchart TB
    subgraph Clients
        OFF["Office UI<br/>frontend/office<br/>:5173"]
        KIT["Kitchen UI<br/>frontend/kitchen<br/>:5174"]
    end

    NGX["nginx-proxy<br/>:80 / :443<br/>prod only"]

    BE["backend<br/>FastAPI :8000 dev, :80 in Docker"]
    AG["agent<br/>pydantic-ai + AG-UI :8001"]
    STT["stt<br/>faster-whisper :8002"]
    PG[("PostgreSQL 17.8<br/>:5432")]
    LLM["LLM provider<br/>NVIDIA NIM, OpenRouter or OpenAI"]

    OFF -->|"/api"| NGX
    KIT -->|"/api, /agent, /stt"| NGX
    NGX --> BE
    NGX --> AG
    NGX --> STT
    AG -->|"REST /api"| BE
    AG -->|HTTPS| LLM
    BE --> PG
```

| Component | Code | Responsibility | Dev port |
| --- | --- | --- | --- |
| `office-frontend` | `frontend/office/` | React 19 + Vite + TypeScript SPA. Sign up, log in, author recipes and ingredients, upload photos and PDFs, manage API keys, menu planner. | 5173 |
| `kitchen-frontend` | `frontend/kitchen/` | React 19 + Vite SPA for a tablet. Voice bar, command palette, and slot-based canvas that renders agent output. | 5174 |
| `backend` | `backend/` | FastAPI REST API. Auth (JWT + cookie), users, recipes, ingredients, units, file uploads, API keys, and a separate public API. Runs Alembic migrations on start. | 8000 |
| `agent` | `agent/` | pydantic-ai agent served through the AG-UI adapter over SSE. Calls backend REST endpoints as tools and emits UI events. | 8001 |
| `stt` | `stt/` | FastAPI service around faster-whisper (CTranslate2). `POST /transcribe` returns text, language, segments and a confidence tier. | 8002 |
| `db` | `db/` | PostgreSQL 17.8. Schema dump, reference data and legacy seed data in `db/init/`, migrations in `db/alembic/`. | 5432 |
| `nginx-proxy` | `nginx-proxy/` | TLS termination and reverse proxy. Generates a self-signed certificate on first start. Production only. | 80, 443 |

### How data flows

1. Office requests: the SPA sends `/api/...` to the Vite proxy, which forwards to the backend. Authentication is a JWT in an `access_token` cookie (set by the backend, httpOnly) with the `Authorization: Bearer` header as a fallback. Passwords are hashed with Argon2.
2. Voice path: the kitchen records `audio/webm` with the browser `MediaRecorder`, posts it to `/stt/transcribe`, and receives the transcript with a confidence tier (`high`, `medium`, `low` or `none`). Low confidence transcripts are prefixed with a warning marker before they are sent on.
3. Agent path: the kitchen posts to `/agent/` as an AG-UI run. The agent streams events back (run started, tool call, state snapshot, custom `ui.render` events). Its tools are `get_recipes_list`, `get_recipe_detail`, `scale_recipe`, `apply_recipe_changes`, `render_component`, `show_notification`, `show_chip`, `clear_slot` and `suggest_recipe_improvements`.
4. Tool calls: agent tools call the backend REST API. Auth headers from the browser request are forwarded, and the agent also sends an `X-Internal-Secret` header that the backend accepts for service-to-service calls. See `docs/authentication.md` for the limits of that bypass.
5. Scaling: `scale_recipe` fetches the recipe, computes the target portion count and sends a state snapshot. The kitchen recomputes the ingredient quantities in the browser (`frontend/kitchen/src/hooks/useRecipeScaling.ts`) and shows the result in a scaling bar. The chef then confirms, and `apply_recipe_changes` writes the new values through the backend.
6. Persistence: the backend writes through SQLModel and SQLAlchemy to PostgreSQL. `backend/entrypoint.sh` waits for the database, runs `alembic upgrade head`, and links seed recipe photos on the first run.

The database schema has 13 Alembic revisions. Multi-tenancy is present at the schema level: rows carry `tenant_id`, and the backend falls back to `DEFAULT_TENANT_ID` when a tenant is not resolved.

## Local setup

### Prerequisites

- Docker Engine with Compose v2 (Docker Desktop 4.30 or newer). Verified with Docker 29.1.3 and Compose v2.
- GNU make.
- One LLM provider key: NVIDIA NIM (default), OpenRouter or OpenAI. The `agent` container exits at startup if no key is set.
- Disk space for the Docker images plus the Whisper model, which downloads into the `whisper_models` volume on first transcription (the default `base` model is roughly 150 MB).
- A microphone and browser permission for the voice flow. The typed command palette works without one.

### Environment file

```bash
git clone git@github.com:faramirezs/voice-chef.git
cd voice-chef
cp .env.example .env
```

Then edit `.env` and set at least:

| Variable | Purpose |
| --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database name and credentials. |
| `SECRET_KEY` | JWT signing key, at least 32 bytes. Generate with `openssl rand -base64 32`. |
| `INTERNAL_SECRET` | Shared secret for agent to backend calls. Generate with `openssl rand -base64 32`. |
| `AGENT_API_KEY` | Provider key. `AGENT_PROVIDER` selects `nvidia` (default), `openrouter` or `openai`. |

Optional: `AGENT_MODEL` (`.env.example` sets `meta/llama-3.3-70b-instruct`; the Compose fallback is `deepseek-ai/deepseek-v4-flash`), `AGENT_BASE_URL`, `STT_MODEL` (default `base`), `STT_DEVICE`, `STT_LANGUAGE`, `DOMAIN_NAME` (used in the generated TLS certificate), `SQL_ECHO`, `DEFAULT_TENANT_ID`.

### Start the stack

```bash
make dev            # dev stack, hot reload, direct ports (build from cache)
make dev-re         # same, but rebuilds every image with --no-cache
make prod           # production layout behind nginx with a self-signed certificate
make help           # list every target
```

`make dev` creates `.env` from `.env.example` if it is missing. In dev mode the services are reachable at:

| URL | Service |
| --- | --- |
| http://localhost:5173 | Office UI |
| http://localhost:5174 | Kitchen UI |
| http://localhost:8000 | Backend API (`/` answers `{"message": "Hello voice-chef"}`) |
| http://localhost:8000/api/public/docs | Swagger for the public API |
| localhost:5432 | PostgreSQL |

In production mode (`make prod`) only nginx publishes ports. Use `https://localhost/` for the office UI and `https://localhost/kitchen/` for the kitchen UI. The certificate is self-signed, so the browser shows a warning on the first visit. nginx routes `/`, `/kitchen/`, `/api/`, `/api/public/`, `/agent/` and `/stt/`. The `/uploads/`, `/docs` and `/openapi.json` blocks in `nginx-proxy/nginx.conf` are commented out, so file URLs and the main Swagger UI are not served through the proxy.

Useful targets besides the start commands: `make status` (containers, volumes, images), `make logs`, `make down`, `make stop`, `make clean` (containers and images, keeps volumes), `make fclean` (removes volumes too, deletes the database), `make db-connect` (psql shell), `make dev-back` (db and backend only), `make dev-back-office` (db, backend, office UI).

### Docker Compose Workflows

#### Development
This setup uses the `dev` stage of the Dockerfile (Vite with Hot Module Replacement).

```bash
make dev
```

#### Production (Local Test)
To test the production build (Nginx serving static files) locally, run the base file **without** the override:

```bash
make prod
```

To display states of containers, volumes and network

```bash
make status
```

To stop the application and remove containers and images

```bash
make clean
```

#### Useful commands and debug commands

##### Start Docker

```bash
open -a Docker
```

##### LOGS

To see what's happening "under the hood" of any service, view the logs in real time:

```bash
docker compose logs -f [service_name]
```

##### Fix the port conflict

For example, a port for DB. Make sure no other service is using port 5432 on your host.

```bash
sudo lsof -i :5432
```

Another example: nginx port

Check if you have a local nginx running:

```bash
sudo lsof -i :80
# check if nginx is running (outside Docker)
sudo systemctl status nginx
# If you want to stop nginx on your host
sudo systemctl stop nginx
```

##### How to activate the virtual environment for Python

```bash
# If your virtual environment is named ".venv"
source .venv/bin/activate
```

## Demo path

The database seeds itself on first start. `db/init/04_legacy_data.sql` loads 12,301 ingredient rows, 83 recipe rows, 13 tenant rows and 305 nutrition rows. All seeded recipes belong to the tenant in `DEFAULT_TENANT_ID`, and signup assigns new users to that same tenant, so a fresh account sees the seed data immediately. Recipe and ingredient names come from the source data and are mostly German.

1. Run `make dev` and wait until the backend log shows `Starting FastAPI` (the container runs the migrations first).
2. Open http://localhost:5173, click **Sign up**, create an account, then log in. The office app is the only place with a login form.
3. Open http://localhost:5174 in a second tab. The kitchen has no login form. It calls `GET /api/auth/me` with the office session cookie and redirects to the office login page if the cookie is missing.
4. In the kitchen, press `Cmd + K` (or `Ctrl + K`) to open the command palette and type part of a seeded recipe name, for example `Bali Bowl`. Press Enter.
5. The agent calls `get_recipes_list`, the palette shows the matches, and selecting one renders the recipe card in the canvas: ingredients, quantities, yield mode and weights.
6. With a recipe on screen, type `scale to 20` (or `double`, `halve`) in the palette. The scaling bar appears with recomputed quantities and weights. Saying `apply`, or clicking the confirmation chip the agent places in the bottom bar, calls `apply_recipe_changes`, which writes the new yield values to the backend.
7. For the voice path, press the microphone button in the voice bar at the bottom of the kitchen screen, allow microphone access, and speak the same request. The transcript appears as a chip; a low-confidence transcript shows a warning before it is submitted.

To exercise the agent without a browser, the AG-UI endpoint accepts a plain POST:

```bash
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "threadId": "thread-001",
    "runId": "run-001",
    "state": {},
    "messages": [{"id": "msg-001", "role": "user", "content": "show recipe Bali Bowl"}],
    "tools": [],
    "context": [],
    "forwardedProps": {}
  }'
```

The response is an SSE stream of `RUN_STARTED`, tool call and `CUSTOM` (`ui.render`) events. See `agent/readme.md` for the same example with more detail.

## Test status

There is one automated test suite in the repository: the database schema drift suite.

| Item | Detail |
| --- | --- |
| Suite | `db/test/test_schema_drift.py` with fixtures in `db/test/conftest.py` |
| Runner | pytest plus the `pytest-alembic` plugin. The file also runs direct `compare_metadata` and SQLAlchemy `inspect()` audits of columns, indexes and constraints. |
| Requirement | A running PostgreSQL database and `DATABASE_URL` exported. `conftest.py` raises at import time if `DATABASE_URL` is missing. |
| Result | 132 tests pass against a fresh `postgres:17.8` database after `alembic upgrade head` (verified 2026-09-17 with `--test-alembic`). |

```bash
export DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/DBNAME
python -m pip install "pytest>=8.3" "pytest-alembic>=0.11" "psycopg[binary]>=3.2"
alembic -c alembic.ini upgrade head
python -m pytest db/test/test_schema_drift.py -q --test-alembic
```

`make drift-gate-local` runs a stricter four gate version of the same check against the database in your `.env`: `alembic upgrade head`, then `db/scripts/drift_check.py`, then the pytest file, then a pending autogenerate check that fails if the models produce new migration operations.

What does not exist yet: no pytest suite for `backend/app`, no test runner or `test` script in either frontend `package.json`, and `pytest` / `pytest-alembic` are not listed in `backend/requirements.txt` (the CI workflow installs them in a separate step). `stt/tests/record_and_test.py` and `stt/tests/voice_chat.py` are interactive scripts for a human with `ffmpeg` and a microphone; they are not wired into a test runner.

Continuous integration covers three things:

- `build-check.yml`: `npm ci` + `npm run build` for both frontends, and `py_compile` plus `from app.main import app` for the backend.
- `schema-drift.yml`: the drift gate twice, once against a database built from the migrations and once against a database built from `db/init/01_dump.sql`, plus Alembic-specific pytest checks.
- `deploy.yml`: SSH deployment to a Hetzner VPS with `make prod`, triggered after the schema drift workflow succeeds.

## Project status and ownership

This is a team project, not a solo repository.

- Git history shows five accounts: `mekundur` (199 commits), `faramirezs` (161), `MaryPeshko` (144), `dmitrijslasko` (109) and `minorSeventhMusic` (1).
- It is a course project. The repository contains the branches `257-school-computers-deployment-branch` and `265-school-deployment-branch-2`, and a draft README on the `readme` branch says the project was created as part of the 42 curriculum. One commit author uses a `student.42berlin.de` address. The repository does not name a team.
- Current state: the code is frozen. The last commit on `main` is from 2026-05-10 and the last push to the repository was 2026-05-12. The repository is public and not archived. 41 issues and 4 pull requests are open, and many of them describe features that were never built.
- Working today: signup and login (JWT in a cookie, Argon2 hashing), recipe CRUD with photo and PDF uploads, ingredient CRUD with pagination, search and filters, API key management, the public API with API-key auth and per-route rate limits, menu planner, the kitchen command palette and voice bar, agent-driven recipe rendering, portion scaling, and the STT service.
- Not built: semantic or RAG search (the compose file contains no vector store), real-time WebSocket updates, a Raspberry Pi client, and working pages for tasks, timers, analytics, calculator, notes and general settings, which show "Coming soon" or static sample data. The menu planner keeps its entries in browser state only, because there is no menu API endpoint. Database models exist for recipe versions, task lists, shopping lists, audit logs and nutrition, but no API route or page reads them yet.
