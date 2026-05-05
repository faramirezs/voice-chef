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

### Tier 1: Vocabulary Priming (do first — confirmed top priority 2026-05-01)

**Why this is now top priority:** RAG retrieval testing on 2026-05-01 (after the rag search endpoints landed) showed that pure dense embedding fails on common voice-input edge cases — typos, transliterations, EN/DE keyboard variants. Hybrid retrieval helps as a downstream safety net, but **fixing the input at the source via Whisper's vocabulary priming has higher ROI for the voice path**: it prevents most of the fuzz from existing in the first place. See "Quality observations" in the RAG plan for concrete failures (`tagine` → `Tajine`, `haehnchen` → `Hähnchen`). Hybrid retrieval and STT priming are complementary layers.

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

**Status update 2026-05-01:** infrastructure delivered (Qdrant + rag + backfill + search endpoints) on branch `rag`. Vector store is **Qdrant**, not ChromaDB (decision documented in commit history). Hybrid retrieval (Phase A.5) is the next step before agent integration — pure dense fails on typos and transliterations. Detailed plan in `~/.claude/plans/3-let-s-look-precious-noodle.md`.

### Deferred query-rewriter (Layer 3) — defer until needed

A separate query-rewriting layer (translate `eggplant` → `Aubergine`, normalize abbreviations) was discussed. Three model options if/when needed:
- **Static EN↔DE kitchen-vocabulary lookup** (recommended start) — bounded vocab, deterministic, ~50–100 term pairs cover ~95% of cross-lingual queries
- **Small LLM piggybacking on Ollama** (when Topic 1 lands) — `qwen2.5:1.5b` is a natural fit, marginal cost ~zero alongside the agent's main model
- **Skip entirely** — STT priming + hybrid retrieval may make this layer unnecessary

Reactive only — don't preemptively build the service; revisit after seeing what slips through priming + hybrid in real usage.

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

## Topic 5: Authentication Architecture

**Goal:** Decide how the agent, rag, STT, and frontends authenticate so multi-tenant isolation is enforced consistently. Aligns RAG queries with the existing tenant-scoped backend.

**Decision (after research and group discussion 2026-04-30):** Mixed pattern — industry standard for multi-tenant RAG (Confluence, Notion AI, Glean, Copilot Workspace).

| Layer | Auth pattern | Reason |
|-------|-------------|--------|
| **rag indexer** | Service account (Pattern A) | Indexer must read everything to build the vector store; can't run "as every user." Stores `tenant_id` in vector payload. |
| **rag search endpoints** | User's JWT (Pattern B) | Decode JWT → extract `tenant_id` → add Qdrant filter at query time |
| **Agent** | User's JWT (Pattern B) | Frontend forwards JWT in AG-UI request; agent attaches it to every backend + rag call |
| **STT** | None | Stateless audio→text utility; no user data lives there |
| **Kitchen frontend** | Defined "kitchen user" with limited scope | Shared tablet, GDPR-friendly, gets scoped permissions: read recipes, scale temporarily — NOT delete, update, destroy |
| **Office frontend** | Per-user JWT (existing) | Already in place; delete/update/destroy require this |

### Voice biometrics — not for auth

Voice recognition as a *login* mechanism is GDPR-sensitive (special-category biometric data, Art. 9) and far too imprecise for a noisy kitchen environment.

**Allowed use of voice ID:** *attribution/personalization only*, for security-uncritical features.
- Example: "What's next on my list?" → voice ID picks the right todo list. If misidentified, user just says "I'm not Alejo, I'm Nico" — no harm done.
- Implementation hint: a small `voice-id` service mirroring `rag` (Resemblyzer or ECAPA-TDNN embeddings, match against enrolled chef voices).

### Wake word

Separate concern from auth. Pure UX trigger (Porcupine, OpenWakeWord, Snowboy). Add independently when the kitchen UX needs hands-free activation.

**Files (when implemented):** new helper in `agent/app/auth.py`, new login flow in `rag/app/auth.py`, frontend JWT-forwarding in kitchen `useAgent.ts`.

---

## Topic 6: Pi WiFi onboarding (provisioning at first boot)

**Goal:** Let a kitchen-pi connect to a new WiFi network without SSH or a keyboard. Required for any deployment scenario where the device moves between locations (school evaluation, demo, customer site) — currently the WiFi credentials are baked into the SD-card image at flash time, which means re-imaging to change networks.

**Pattern (industry standard):**
1. On boot, Pi tries to connect to the saved WiFi.
2. If no saved network or all saved networks fail within a timeout, Pi switches to AP (access-point) mode and broadcasts its own SSID (e.g. `kitchen-pi-setup`).
3. User joins that AP from a phone or laptop. A captive portal / web UI on the Pi shows nearby networks and accepts SSID + password.
4. Pi saves credentials, drops AP mode, reconnects to the chosen network. AP comes back automatically if the connection fails again.

**Recommended tool: [`comitup`](https://davesteele.github.io/comitup/)** — Debian package designed for exactly this. Headless-Pi friendly, integrates with NetworkManager/wpa_supplicant, has a built-in captive portal. Apache-2.0 licensed.

Alternatives evaluated:
- **`RaspAP`** — full router admin UI, overkill for "just join a WiFi."
- **Custom `hostapd` + `wpa_supplicant` script** — works but a bunch of edge cases (network switching, race conditions on NetworkManager); reinventing comitup poorly.

**Implementation outline:**
1. `apt install comitup` on the Pi (one-time during image preparation).
2. Configure `/etc/comitup.conf` — set the AP SSID prefix, captive-portal port, optional preshared password.
3. Update `pi/README.md` provisioning checklist to remove the wpa_supplicant.conf step and add the AP-on-first-boot flow.
4. Verify the kiosk auto-start (`kitchen-point.service`) doesn't fight comitup's network state — comitup typically pauses graphical services during AP-mode setup; we need to confirm the kitchen UI degrades gracefully (already does — silent re-login + error toast).
5. Smoke test: flash a fresh SD card, boot, see the AP SSID, join it, configure WiFi, watch Pi connect.

**Files (when implemented):** `pi/README.md` (provisioning section), possibly `pi/scripts/configure-wifi-onboarding.sh` (one-shot installer that runs `apt install comitup` + drops the config file in place), and a documentation note in `docs/kitchen-pi-design.md` about the boot-state machine.

**Effort:** half-day for the integration + testing on a real Pi (most of which is verifying the kiosk service plays nicely with comitup's network-state transitions).

---

## Known issues / coordinate with backend owner

- ~~**Agent's `get_recipes_list` is broken on `main`** since the tenant-auth refactor.~~ **Resolved by PR #181** (merged into main 2026-05-01): `agent/app/agent.py` now forwards `Authorization` + cookie headers from the frontend to backend calls via a request-scoped `ContextVar` (`agent/app/context.py`). Backend's `get_current_user` also adds a Docker-internal-IP bypass returning a synthetic admin user — both ends of the auth chain are addressed.
- ~~**API responses do not expose `tenant_id`.**~~ **Resolved differently by PR #181:** the indexer doesn't need `tenant_id` on responses anymore because the backend now defaults to `DEFAULT_TENANT_ID` env var for internal Docker requests (`backend/app/core/deps.py`). Multi-tenant isolation will instead be wired via JWT forwarding when the kitchen frontend sends the user's token end-to-end. Tenant filtering on the rag service stays a placeholder until that wiring is complete.
- **Investigate change of agent model.** Llama 3.3 70B doesn't reliably honor "stop after one tool call" / "exactly once" instructions in the system prompt. PR #181 added tool-level dedup (per-request `(level, message)` cache for `show_notification`) which catches *identical* repeats, but the LLM still bypasses it by generating *different* messages each time. Symptom (observed 2026-05-01 post-merge): even on the chickpeas *positive* path where the recipe renders correctly, the LLM appends 5+ varied `show_notification` calls before hitting `tool_calls_limit=10`. Bounded in cost; cosmetic in UX. Worth A/B-ing: DeepSeek V4 Flash, Qwen 2.5 72B, and a local Ollama model once Topic 1 lands.

---

## Implementation Priority

| Priority | Topic | Effort | Impact |
|----------|-------|--------|--------|
| 1 | Topic 6 (Pi WiFi onboarding via comitup) | Half-day | Unblocks deployments at any new location without re-imaging |
| 2 | Topic 2 Tier 1 (vocabulary priming) | Small | Immediate transcription improvement |
| 3 | Topic 1 (Ollama local model) | Small-Medium | Independence from rate limits |
| 4 | Topics 3+4 (RAG + Valkey + microservices) | Large | Subject requirements, implement together |
| 5 | Topic 5 (Auth: mixed pattern + kitchen-user scope) | Medium | Required before production-readiness for multi-tenant |
| 6 | Investigate alternative agent model (DeepSeek/Qwen/Ollama) | Small | Better prompt-following on negative-path scenarios |
| 7 | Topic 2 Tier 2 (office corrections) | Medium | Accuracy improvement over time |
| 8 | Topic 2 Tier 3 (voice self-correction) | Medium-Large | Advanced, depends on Tier 2 |
| 9 | Voice-ID service (attribution only, not auth) | Medium | UX nicety — personalization, audit trails |

Note: Topics 3 and 4 are intertwined — Valkey is needed for RAG incremental updates. Implement them together.
