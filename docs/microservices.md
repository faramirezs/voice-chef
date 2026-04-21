# Microservices Module — Voice Chef

## Subject Requirement

> "Major: Backend as microservices.
> Design loosely-coupled services with clear interfaces.
> Use REST APIs or message queues for communication.
> Each service should have a single responsibility."

## Current State

### What already satisfies the requirement

Voice Chef is already a multi-service Docker Compose application with clear service boundaries:

| Service | Responsibility | Interface | Status |
|---------|---------------|-----------|--------|
| `backend` | Data API (CRUD, auth) | REST `/api/...` | Running |
| `agent` | AI reasoning + tool calling | AG-UI (REST/SSE) | Running |
| `stt` | Speech-to-text transcription | REST `/transcribe`, `/health` | Running |
| `db` | Data persistence | Postgres protocol | Running |
| `office-frontend` | Office UI | HTTP (static) | Running |
| `kitchen-frontend` | Kitchen/voice UI | HTTP (static) | Running |

- 6 services, each with a single responsibility
- REST APIs for inter-service communication
- Docker Compose networking for service discovery
- Services are independently buildable and deployable

### What's missing

| Gap | Description | Effort |
|-----|-------------|--------|
| **Health endpoints** | `backend` and `agent` lack `/health` endpoints. Only `stt` has one. | Small |
| **Docker healthchecks** | Only `db` has a healthcheck in `docker-compose.yml`. Backend, agent, and stt need them. | Small |
| **Message queue** | No event-driven communication. All inter-service calls are synchronous REST. | Medium |
| **API documentation** | FastAPI auto-generates OpenAPI/Swagger docs but accessibility not verified. | Small |

---

## Changes Required to Existing Code

### 1. Add `/health` endpoint to backend

**File:** `backend/app/main.py`

Add a simple health check endpoint:
```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

### 2. Add `/health` endpoint to agent

**File:** `agent/app/main.py`

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

### 3. Add Docker healthchecks

**File:** `docker-compose.yml`

Add healthcheck blocks to `backend`, `agent`, and `stt` services:

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:80/health"]
    interval: 10s
    timeout: 5s
    retries: 3

agent:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
    interval: 10s
    timeout: 5s
    retries: 3

stt:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
    interval: 10s
    timeout: 5s
    retries: 3
```

Update `depends_on` blocks to use `condition: service_healthy` where appropriate.

### 4. Verify API documentation

**File:** `backend/app/main.py`

FastAPI generates OpenAPI docs automatically at `/docs` (Swagger UI) and `/redoc`. Verify these are accessible and not disabled. No code change expected — just confirmation.

### 5. Add Valkey message queue

**New service in `docker-compose.yml`:**
```yaml
valkey:
  image: valkey/valkey:latest
  ports:
    - "6379"
  networks:
    - app-network
  healthcheck:
    test: ["CMD", "valkey-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 3
```

**Backend changes:**

| File | Change |
|------|--------|
| `backend/requirements.txt` | Add `valkey` or `redis` Python client |
| `backend/app/core/events.py` (new) | Valkey connection + publish helper |
| `backend/app/api/routes/recipe.py` | Publish `recipe.created`, `recipe.updated`, `recipe.deleted` events after CRUD operations |

**Environment:**

| File | Change |
|------|--------|
| `docker-compose.yml` | Add `VALKEY_URL: valkey://valkey:6379` to backend and agent environments |
| `.env.example` | Add `VALKEY_URL=valkey://valkey:6379` |

### 6. Event subscribers (consumers)

Services that need to react to events subscribe to Valkey channels:

| Subscriber | Event | Action |
|------------|-------|--------|
| Embedding service / ChromaDB indexer | `recipe.created`, `recipe.updated` | Re-index recipe in vector store |
| STT service (future, Tier 3) | `correction.submitted` | Load new correction pair |

---

## Target Architecture (after all changes)

```
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│   Office    │  │   Kitchen    │  │  Raspi/ESP32  │
│  Frontend   │  │  Frontend    │  │  (future)     │
└──────┬──────┘  └──────┬───────┘  └──────┬────────┘
       │                │                  │
       │ REST           │ REST+AG-UI       │ REST
       ▼                ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Backend    │  │    Agent     │  │     STT      │
│  /api/...    │  │  AG-UI SSE   │  │ /transcribe  │
│  /health     │  │  /health     │  │ /health      │
└──────┬───────┘  └──────┬───────┘  └──────────────┘
       │                 │
       │ pub             │ query
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│    Valkey    │  │   ChromaDB   │
│  pub/sub     │  │  vectors     │
└──────┬───────┘  └──────────────┘
       │ sub
       ▼
┌──────────────┐  ┌──────────────┐
│  Embedding   │  │    Ollama    │
│  Indexer     │  │  local LLM   │
└──────────────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │
│  /health     │
└──────────────┘
```

### Service count: 9

All services communicate via REST APIs or Valkey pub/sub. Each has a single responsibility and a health endpoint. Services are independently deployable.

---

## Implementation Order

1. **Health endpoints + Docker healthchecks** — smallest change, immediate compliance
2. **Valkey service + backend event publishing** — enables event-driven communication
3. **ChromaDB + embedding indexer** — subscribes to Valkey events (part of RAG implementation)
4. **Ollama** — local LLM service (part of local model implementation)

Steps 2-4 are covered in detail in `docs/voiceNextSteps.md`.
