# Next Steps — Voice Chef

## Context

After completing the STT container (Phase 1), agent integration (Phase 3), four-tier confidence scoring, and merging with main, we're planning the next major features. These address four goals: independence from cloud rate limits, improved transcription accuracy, RAG for the subject requirement, and formalizing the microservices architecture.

---

## Topic 1: Local Model for Agent

**Goal:** Run LLM inference locally to avoid cloud rate limits and API costs.

**Decisions:**
- Runtime: **Ollama** (Docker container, native pydantic-ai support)
- Models: **Qwen 2.5 7B** (primary, ~4.5GB), **Llama 3.3 70B** (optional, ~40GB — fits on 64GB MacBook)
- Architecture: **User configurable** via env var `AGENT_PROVIDER=ollama|openrouter|google`
- Ollama runs as its own Docker container (fits microservices requirement)

**Implementation:**
1. Add `ollama` service to `docker-compose.yml` (image: `ollama/ollama`)
2. Add Ollama provider option in `agent/app/agent.py` (pydantic-ai has native `OllamaModel`)
3. Pre-pull models via startup script or Dockerfile
4. Env vars: `AGENT_PROVIDER`, `OLLAMA_MODEL` (default: `qwen2.5:7b`)

**Files:** `agent/app/agent.py`, `docker-compose.yml`, `docker-compose.override.yml`, `.env.example`

---

## Topic 2: Transcription Accuracy — Three Tiers

**Goal:** Improve speech recognition accuracy through vocabulary priming, user corrections, and voice self-correction.

### Tier 1: Vocabulary Priming (do first)

**What:** Load recipe names, ingredient names, and kitchen vocabulary into Whisper's `initial_prompt` parameter before each transcription.

**Implementation:**
1. STT container fetches recipe + ingredient names from backend on startup (`GET /api/recipes`, `GET /api/ingredients`)
2. Add a static kitchen vocabulary list (cooking verbs, equipment, units)
3. Combine into `initial_prompt` string (max ~224 tokens)
4. Pass to `model.transcribe(audio, initial_prompt=...)`
5. Refresh periodically (every 10 min)

**Files:** `stt/app/transcriber.py`, `stt/app/vocabulary.py` (new)

### Tier 2: Office Frontend Corrections (do next)

**What:** Capture before/after pairs when users edit transcriptions in the office frontend. Auto-apply after N occurrences.

**Implementation:**
1. Add `POST /corrections` and `GET /corrections` endpoints to STT service
2. Store corrections in JSON file (Docker volume)
3. Track frequency per correction pair
4. Auto-apply corrections with frequency >= 2 as post-processing after transcription
5. Office frontend sends correction pairs when user edits transcribed text before sending
6. Word-boundary matching to avoid false positives

**Files:** `stt/app/main.py`, `stt/app/corrections.py` (new), office frontend integration

### Tier 3: Voice Self-Correction (future)

**What:** Agent detects spoken corrections ("no, I meant borscht") and feeds them back to the STT correction system.

**Implementation:**
1. Extend agent system prompt to recognize correction patterns
2. Add `submit_correction` tool to agent
3. Tool calls STT `POST /corrections` endpoint
4. Fully hands-free learning loop in the kitchen

**Files:** `agent/app/agent.py`, agent system prompt

---

## Topic 3: RAG System

**Goal:** Implement Retrieval-Augmented Generation for semantic recipe search. Subject requirement: "Implement a complete RAG system with proper context retrieval and response generation."

**Decisions:**
- Vector store: **ChromaDB** (separate Docker container — strengthens microservices story)
- Embedding model: **Local** (`sentence-transformers/all-MiniLM-L6-v2` or multilingual variant, ~80MB)
- What to embed: **Multiple chunks per recipe** (name, ingredients, instructions — separate embeddings)
- When to index: **Startup + incremental** on database changes (via Valkey pub/sub)
- Agent integration: **New `search_recipes` semantic tool** alongside existing exact-match tools

**Architecture:**
```
Backend DB (Postgres)
    │
    ├── recipe created/updated → publishes event to Valkey
    │
    ▼
Embedding Service / ChromaDB indexer
    │ subscribes to Valkey events
    │ fetches recipe data from backend
    │ generates embeddings (local model)
    │ stores in ChromaDB
    ▼
ChromaDB (vector store)
    │
    ▼
Agent calls search_recipes(query)
    → embeds query
    → similarity search in ChromaDB
    → returns top N matching recipe chunks
    → LLM generates answer from retrieved context
```

**Implementation:**
1. Add `chromadb` service to `docker-compose.yml`
2. Create embedding/indexing service (could be part of agent or standalone)
3. On startup: fetch all recipes from backend, chunk, embed, store in ChromaDB
4. Subscribe to Valkey for recipe update events, re-index incrementally
5. Add `search_recipes(query)` tool to agent — embeds query, searches ChromaDB, returns top 5 chunks with recipe context
6. Update agent system prompt: use `search_recipes` for vague/descriptive queries, `get_recipes_list` for exact name matches

**Files:** `docker-compose.yml`, `agent/app/agent.py`, `agent/app/rag.py` (new), `agent/requirements.txt`

---

## Topic 4: Microservices Architecture

**Goal:** Formalize the microservices architecture. Subject requirement: "Design loosely-coupled services with clear interfaces. Use REST APIs or message queues for communication."

**Decisions:**
- Message queue: **Valkey** (open-source Redis fork, pub/sub for inter-service events)
- API documentation: **Auto-generated** (FastAPI OpenAPI/Swagger, already built-in)
- Health checks: Add `/health` to all services

**Final service map (9 services):**

| Service | Responsibility | Communication |
|---------|---------------|---------------|
| `backend` | Data API (CRUD, auth) | REST `/api/...` |
| `agent` | AI reasoning + tool calling | AG-UI (REST/SSE) |
| `stt` | Speech-to-text | REST `/transcribe` |
| `chromadb` | Vector storage + similarity search | REST (ChromaDB API) |
| `ollama` | Local LLM inference | REST (Ollama API) |
| `valkey` | Message queue (pub/sub) | Valkey protocol |
| `db` | Data persistence | Postgres protocol |
| `office-frontend` | Office UI | HTTP (static) |
| `kitchen-frontend` | Kitchen/voice UI | HTTP (static) |

**Event flows via Valkey pub/sub:**
- `recipe.created` / `recipe.updated` → triggers ChromaDB re-indexing
- `correction.submitted` → STT picks up new correction pairs (Tier 3)

**Implementation:**
1. Add `valkey` service to `docker-compose.yml` (image: `valkey/valkey`)
2. Backend publishes events on recipe CRUD operations
3. Embedding service subscribes to recipe events
4. Add `/health` endpoints to backend and agent
5. Ensure OpenAPI docs are accessible for backend (`/docs`)

**Files:** `docker-compose.yml`, `backend/app/main.py`, `agent/app/main.py`

---

## Implementation Priority

| Priority | Topic | Effort | Impact |
|----------|-------|--------|--------|
| 1 | Topic 2 Tier 1 (vocabulary priming) | Small | Immediate transcription improvement |
| 2 | Topic 1 (Ollama local model) | Small-Medium | Independence from rate limits |
| 3 | Topics 3+4 (RAG + Valkey + microservices) | Large | Subject requirements, implement together |
| 4 | Topic 2 Tier 2 (office corrections) | Medium | Accuracy improvement over time |
| 5 | Topic 2 Tier 3 (voice self-correction) | Medium-Large | Advanced, depends on Tier 2 |

Note: Topics 3 and 4 are intertwined — Valkey is needed for RAG incremental updates. Implement them together.
