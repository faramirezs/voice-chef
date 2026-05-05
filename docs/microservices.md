# Microservices Architecture — Voice Chef

## What Voice Chef is, and why microservices fits

Voice Chef is an AI-driven kitchen assistant. It combines a tenant-scoped data
API for recipes and ingredients, a tool-calling LLM agent that orchestrates
work on the user's behalf, on-device speech-to-text for hands-free input, a
hybrid (dense + sparse) vector index for semantic search over the recipe
catalog, and two distinct frontends — an office UI for recipe authoring and a
kitchen UI optimized for greasy-hands voice interaction.

These responsibilities have meaningfully different runtime profiles. The STT
service loads a Whisper checkpoint into memory; the RAG service holds a
multilingual sentence-transformer model; the agent streams responses via SSE
with bounded tool-call budgets; the backend serves CRUD plus static uploads
from a Postgres-backed store. They scale, restart, and fail differently. A
microservice shape is the natural fit: each concern lives behind a clear,
narrow interface, and the platform composes them via Docker Compose with a
single shared bridge network.

## Service map

All services run inside the `app-network` Docker bridge defined in the root
`docker-compose.yml` and reach each other by service name.

| Service | Responsibility | Interface | Repo location |
|---|---|---|---|
| `backend` | Tenant-scoped CRUD for recipes, ingredients, users, file uploads, and JWT-based auth. | REST under `/api/...`; static files at `/uploads/...`; OpenAPI at `/docs`; `GET /health`. | `backend/` (Dockerfile at `backend/Dockerfile`, app entry at `backend/app/main.py`) |
| `agent` | Pydantic-AI tool-calling LLM agent. Orchestrates calls to `backend` (recipes, ingredients) and `rag` (semantic search) on behalf of the kitchen frontend. | AG-UI streaming protocol over `POST /` (SSE); OpenAPI at `/docs`; `GET /health`. | `agent/` (`agent/Dockerfile`, `agent/app/main.py`) |
| `stt` | Stateless audio-to-text transcription using a local Whisper model. | REST `POST /transcribe` (multipart upload); OpenAPI at `/docs`; `GET /health`. | `stt/` (`stt/Dockerfile`, `stt/app/main.py`) |
| `rag` | Vector indexer + hybrid (dense + sparse BM25) search over recipes and ingredients. Backfills from `backend` on startup and polls for changes. | REST `POST /search/recipes`, `POST /search/ingredients`; OpenAPI at `/docs`; `GET /health`. | `rag/` (`rag/Dockerfile`, `rag/app/main.py`) |
| `qdrant` | Vector store backing the `rag` service. | Qdrant HTTP API on 6333, gRPC on 6334. | Image `qdrant/qdrant:latest` (no source in repo) |
| `db` | Persistent storage for backend data; the only stateful service besides Qdrant. | PostgreSQL 17 wire protocol on 5432. | Image `postgres:17.8`; init scripts in `db/init/` |
| `office-frontend` | React/Vite SPA for recipe authoring and management; talks to `backend`. | Static HTTP served by nginx on container port 80 (host 8080). | `frontend/office/` |
| `kitchen-frontend` | React/Vite SPA for the kitchen tablet; talks to `agent` over AG-UI and to `stt` for voice input. | Static HTTP served by nginx on container port 80 (host 8082). | `frontend/kitchen/` |

## Why REST instead of a message queue

The 42 subject permits either REST APIs or message queues. We chose REST for
three reasons.

First, every current inter-service interaction is request/response. The agent
calls the backend for recipe data and the rag service for semantic hits; the
kitchen frontend uploads audio to STT and waits for the transcript; the office
frontend reads and writes through the backend. None of these flows is
naturally pub/sub.

Second, FastAPI gives us OpenAPI schema generation, request validation, and an
interactive `/docs` page for free. The interfaces are self-describing for both
reviewers and the frontend developers — no separate IDL to maintain.

Third, a synchronous HTTP boundary is one less moving part to operate compared
to running and monitoring a broker.

A pub/sub layer (Valkey, the open-source Redis fork) is on the roadmap
specifically for event-driven re-indexing of the RAG vector store — when a
recipe is created or updated in the backend, an event would tell `rag` to
re-embed only that record. Today `rag` solves the same problem more bluntly:
its lifespan handler runs a backfill on startup when the Qdrant collections
are empty, and it polls thereafter (`EMBEDDING_POLL_SECONDS`, default 30s).
Polling is good enough at the current data volume; the broker is a future
optimization, not load-bearing.

## Loose coupling in practice

Each service has its own image, its own Dockerfile, and its own port mapping
in `docker-compose.yml`. Concretely:

- `docker compose stop agent` leaves the office frontend, backend, rag, and
  STT fully operational. Only the kitchen voice flow degrades.
- `docker compose stop rag` is intended to leave the agent's exact-match
  tooling against the backend functional; only semantic search would be
  unavailable. Graceful degradation here depends on the agent's HTTP
  error handling and isn't yet exercised by an automated test.
- Each Python service has its own `requirements.txt` and can be exercised in
  isolation against mocked dependencies. The agent's tools are registered via
  pydantic-ai's tool registry rather than direct imports of backend code.
- Deployments are per-service: swapping the Whisper model size by rebuilding
  the `stt` image does not touch the agent or the backend; switching the
  agent's underlying LLM provider is an environment-variable change
  (`AGENT_PROVIDER`) on a single service.

## Interfaces and discovery

Every FastAPI service (`backend`, `agent`, `stt`, `rag`) exposes its OpenAPI
schema and a Swagger UI at `/docs`. A reviewer or new contributor can inspect
the public surface of any service without reading code.

The agent additionally speaks the AG-UI streaming protocol on `POST /` for
the kitchen frontend's chat UX, with usage limits enforced server-side
(request and tool-call budgets in `agent/app/main.py`).

Inside the Compose network, services address each other by DNS name —
`http://backend:80`, `http://rag:8003`, `http://qdrant:6333` — driven by the
`BACKEND_URL`, `RAG_SERVICE_URL`, `QDRANT_URL` environment variables wired in
`docker-compose.yml`. For the kitchen-pi deployment scenario, where the
kitchen tablet may run on a different host than the rest of the stack,
Tailscale provides cross-host service discovery so the same service-name
addressing continues to work.

## Operational endpoints

Each FastAPI service exposes `GET /health` returning
`{"status": "ok", "service": "<name>"}`. The endpoints are
unauthenticated liveness probes — usable for `curl` checks from outside
the network and as the test target for Docker Compose `healthcheck:`
directives in a future hardening pass.

Today only the `db` service has a Compose-level `healthcheck` block.
Extending the pattern to backend, agent, stt, and rag — and converting
`depends_on` to use `condition: service_healthy` — is tracked but not done.

## Reference

Planned improvements — Valkey pub/sub for event-driven RAG re-indexing and
formal Compose `healthcheck:` wiring on all FastAPI services — are described
in `docs/voiceNextSteps.md` under Topic 4 ("Microservices Architecture").
