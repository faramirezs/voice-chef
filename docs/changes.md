# Changes to Existing Files — STT Service Integration

This documents all modifications to files that existed before this branch, for group discussion.

## Modified Files

### 1. `docker-compose.yml`

**What changed:**
- Added `stt` service block (port **8002**, on `app-network`, no dependencies on other services)
- Added `whisper_models` named volume (persists downloaded model files across container rebuilds)

**Discussion points:**
- **Port 8002** — new port exposed to host. Confirm no conflict with other team members' setups.
- The STT service is **standalone** — it does not `depends_on` any other service. It only needs network access if another service calls it.
- The `whisper_models:/models` volume avoids re-downloading ~150MB+ model files on every rebuild.

### 2. `docker-compose.override.yml`

**What changed:**
- Added `stt` service dev override: mounts `./stt/app` for hot-reload during development
- Added `whisper_models` volume declaration (must match production compose)

### 3. `.env.example`

**What changed:**
- Added three new environment variables:
  - `STT_MODEL=base` — whisper model size (tiny/base/small/medium/large-v3)
  - `STT_LANGUAGE=` — empty = auto-detect, or force a language code (en, es, de, etc.)
  - `STT_DEVICE=cpu` — compute device (cpu or cuda)

**Action needed:** Team members should add these to their local `.env` files after pulling.

### 4. `.gitignore`

**What changed:**
- Added `stt/tests/samples/` — excludes recorded audio files from git

### 5. `.gitattributes` (new file)

**What changed:**
- Created `.gitattributes` with `merge=ours` strategy for `stt/tests/results/*.json`
- STT test result JSONs are committed and pushed but will never cause merge conflicts — on merge, the current branch's version is kept silently

**Action needed:** Each team member must run this once to register the merge driver:
```bash
git config merge.ours.driver true
```

### 6. `Makefile`

**What changed:**
- Added three new targets: `stt-build`, `stt-build-nocache`, `stt-recreate` (mirrors existing agent-* pattern)
- Added these to help text and `.PHONY` declaration
- Fixed duplicate `.PHONY` line (was already present from prior commit, just extended it)

## Interface Contract (for group discussion)

### STT Service API

**Base URL:** `http://stt:8002` (internal) or `http://localhost:8002` (host)

**Endpoints:**

| Method | Path | Content-Type | Request | Response |
|--------|------|-------------|---------|----------|
| GET | `/health` | — | — | `{"status": "ok"}` |
| POST | `/transcribe` | `multipart/form-data` | `file` field with audio (WAV, MP3, OGG, FLAC, WebM) | See below |

**Response format for `/transcribe`:**
```json
{
  "text": "the full transcribed text",
  "language": "en",
  "language_probability": 0.98,
  "confidence": "high",
  "retry_suggested": false,
  "duration": 3.45,
  "segments": [
    {
      "start": 0.0,
      "end": 1.52,
      "text": "the full"
    },
    {
      "start": 1.52,
      "end": 3.45,
      "text": "transcribed text"
    }
  ]
}
```

**Error responses:**
- `415` — unsupported audio content type
- `422` — missing file field

### New Port Allocation

| Service | Port | Status |
|---------|------|--------|
| frontend | 8080 (prod) / 5173 (dev) | existing |
| db | 5432 | existing |
| fastapi | 80 (internal) / 8000 (dev) | existing |
| agent | 8001 | existing |
| **stt** | **8002** | **new** |

### New Volume

| Volume | Purpose |
|--------|---------|
| `whisper_models` | Persists faster-whisper model downloads (~150MB for `base`) |
