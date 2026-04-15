# Voice Input — Speech-to-Text Service

## Overview

Add a local speech-to-text (STT) Docker container to Voice Chef so kitchen staff can speak commands to the AI agent instead of typing. The service transcribes audio from an XVF3800 microphone array and forwards the text to the existing Pydantic AI agent.

## Decisions

### Model: faster-whisper (CTranslate2)

**Chosen over:** Vosk, Moonshine

**Reasons:**
- OpenAI Whisper re-packaged with CTranslate2 — 4x faster inference, ~3x less memory than stock Whisper
- 99-language multilingual support out of the box
- Most widely deployed open-source STT model with large community
- Model size tiers scale to hardware via a single environment variable (`STT_MODEL`):
  - `tiny` (~75MB RAM) — Raspi 5 viable, acceptable accuracy
  - `base` (~150MB RAM) — Raspi 5 viable, better accuracy
  - `small` (~500MB RAM) — server without GPU, good accuracy
  - `medium` / `large-v3` — server with GPU, best accuracy

**Rejected alternatives:**
- **Vosk** — true native streaming and lighter footprint, but noticeably lower accuracy especially in noisy kitchen environments and with multilingual input. Fewer supported languages (~20 vs 99). Could revisit as a Raspi 5 fallback if faster-whisper `tiny` proves too slow.
- **Moonshine** (Useful Sensors) — designed for edge, very fast on CPU, but English-only which disqualifies it for multilingual kitchen staff.

### Audio Transport: WebSocket (primary) + HTTP POST (fallback)

**WebSocket** handles both streaming and utterance-based transcription:
- Streaming mode: client sends 1-2 second audio chunks, server returns partial transcripts
- Utterance-based mode: client sends all chunks then a "done" signal, server returns final transcript
- Same protocol for both — the difference is when the end signal is sent

**HTTP POST** as a simpler fallback endpoint:
- Upload a complete audio file (.wav), get text back
- Useful for testing, batch processing, or simple integrations

### Wake Word: External (not in STT container)

**Decision:** Keep wake word / voice activation outside the STT service.

**Reasons:**
- The XVF3800 has built-in voice activity detection (VAD) — use that as the initial trigger
- Separation of concerns: STT container receives audio, returns text. No activation logic.
- Future option: add openWakeWord (~50MB, CPU-light) as a sidecar container or directly on the Pi for custom wake words like "Hey Chef"

### Deployment Topologies

Two supported configurations from one codebase:

1. **Edge-only** — Raspi 5 (8GB) + XVF3800, STT runs on the Pi with `tiny` or `base` model
2. **Split architecture** — XVF3800 captures audio via ESP32 or Pi, streams to a server running STT in Docker with `small`/`medium`/`large-v3` model

## Architecture

```
                                    WebSocket (audio chunks)
┌───────────────────────┐          OR HTTP POST (audio file)
│  XVF3800 + Raspi 5 /  │ ─────────────────────────────────────┐
│  ESP32 (capture)       │                                       │
└───────────────────────┘                                       ▼
                                                    ┌──────────────────────┐
                                                    │  stt (Docker)        │
                                                    │  faster-whisper      │
                                                    │  FastAPI + WebSocket │
                                                    │  port 8002           │
                                                    └──────────┬───────────┘
                                                               │ transcribed text
                                                               ▼
                                                    ┌──────────────────────┐
                                                    │  agent (Docker)      │
                                                    │  Pydantic AI         │
                                                    │  port 8001           │
                                                    └──────────────────────┘
```

### Service Integration in Docker Compose

The STT service joins the existing stack as a fifth container:

| Service            | Port | Role                              |
|--------------------|------|-----------------------------------|
| office-frontend    | 8080 | React/Vite UI (office)            |
| kitchen-frontend   | 8082 | React/Vite UI (kitchen, voice)    |
| db                 | 5432 | Postgres 17.8                     |
| fastapi            | 80   | Python API layer                  |
| agent              | 8001 | Pydantic AI culinary assistant    |
| **stt**            | **8002** | **faster-whisper transcription** |

The STT container sits on the same `app-network` and has no dependency on other services — it's a standalone transcription endpoint.

## Implementation Plan

### Phase 1: STT Container (MVP)

**Goal:** Dockerized faster-whisper service with HTTP POST endpoint, integrated into Compose.

- [ ] Create `stt/` directory structure:
  - `stt/Dockerfile`
  - `stt/requirements.txt`
  - `stt/app/main.py` — FastAPI app with `/transcribe` POST endpoint
  - `stt/app/transcriber.py` — faster-whisper model loading and inference
- [ ] Implement HTTP POST endpoint:
  - Accepts audio file upload (WAV, MP3, OGG)
  - Returns JSON `{ "text": "...", "language": "en", "segments": [...] }`
  - Model selected via `STT_MODEL` environment variable (default: `base`)
- [ ] Add `stt` service to `docker-compose.yml`:
  - Port 8002
  - Environment: `STT_MODEL`, optional `STT_LANGUAGE` (auto-detect if unset)
  - On `app-network`
- [ ] Add dev overrides in `docker-compose.override.yml`
- [ ] Add Makefile targets: `stt-build`, `stt-build-nocache`, `stt-recreate`
- [ ] Test with curl: upload a .wav file, verify transcription

### Phase 2: WebSocket Streaming

**Goal:** Real-time transcription via WebSocket connection.

- [ ] Add WebSocket endpoint `/ws/transcribe` to the STT service
- [ ] Protocol design:
  - Client sends binary audio frames (16-bit PCM, 16kHz)
  - Client sends JSON `{"type": "end"}` to signal end of utterance
  - Server sends JSON `{"type": "partial", "text": "..."}` for interim results
  - Server sends JSON `{"type": "final", "text": "...", "language": "..."}` on end
- [ ] Implement audio buffer accumulation and chunked inference
- [ ] Test with a simple Python WebSocket client script

### Phase 3: Agent Integration

**Goal:** Connect STT output to the agent service.

**Decision:** Option B — client orchestrates (STT → Client → Agent). Both services stay independent. A message broker (Option C) was considered but rejected as overkill — the agent uses AG-UI (request/response), not pub/sub. Option A (STT calls agent) was ruled out to avoid coupling.

**Two integration paths:**

1. **Kitchen frontend** (browser) — mic button records via MediaRecorder API, POSTs audio to STT, fills text input with transcription, user confirms and sends to agent via AG-UI protocol
2. **Standalone CLI** (`stt/tests/voice_chat.py`) — terminal-based voice chat for headless/Raspi deployment

- [x] Replace Web Speech API in VoiceInput.tsx with local STT container
  - Uses MediaRecorder API (browser-native, no cloud dependency)
  - POSTs audio blob to STT service
  - Shows confidence warning when `retry_suggested` is true
  - Added `VITE_STT_URL` env var for STT endpoint
- [x] Create standalone voice_chat.py CLI (record → transcribe → confirm → agent → stream response)
- [ ] End-to-end test with agent running: speak → transcribe → agent response

### Phase 4: Audio Capture Client

**Goal:** Client software for the Raspi 5 / ESP32 to capture from XVF3800 and stream to STT.

- [ ] Raspi 5 capture script (Python):
  - Read from XVF3800 via ALSA/PulseAudio
  - Stream audio chunks over WebSocket to STT service
  - Handle XVF3800 VAD signals for utterance boundaries
- [ ] ESP32 firmware (stretch goal):
  - I2S audio capture from XVF3800
  - WiFi WebSocket client to stream audio to STT service

### Phase 5: Wake Word (Optional)

**Goal:** Custom "Hey Chef" activation.

- [ ] Evaluate openWakeWord as sidecar container or on-device process
- [ ] Train/configure custom wake word model
- [ ] Integrate with audio capture pipeline: wake word triggers STT streaming

## Confidence Scoring

Four-tier confidence system using multiple signals from faster-whisper:

| Tier | Meaning | `retry_suggested` | Client action |
|------|---------|-------------------|---------------|
| `high` | Transcription reliable | `false` | Send to agent |
| `medium` | Probably correct, some uncertainty | `false` | Show to user, let them review |
| `low` | Likely contains errors | `true` | Warn user, suggest re-record |
| `none` | No usable speech detected | `true` | Ask to retry |

### Scoring signals

Starting at "high", each failing check downgrades the tier:

| Signal | Threshold | Effect |
|--------|-----------|--------|
| `no_speech_prob` | > 0.6 (any segment) | Immediately "none" |
| `compression_ratio` | > 2.4 (any segment) | Downgrade one tier (hallucination) |
| `avg_logprob` | < -1.0 (mean across segments) | Downgrade one tier |
| `language_probability` | < 0.5 | Downgrade one tier |
| Words per second | < 0.5 for > 3s audio | Downgrade one tier |

Multiple checks can compound (e.g., bad logprob + low language confidence = two downgrades).

### Per-segment scores in API response

Each segment now includes `avg_logprob`, `no_speech_prob`, and `compression_ratio` for client-side inspection or future per-word confidence display.

## Agent Voice-Awareness

When confidence is below "high", STT metadata is prepended to the user message sent to the agent:

```
[voice, confidence: medium, language: uk]
Show me the borsh recipe
```

The agent's system prompt instructs it to:
- Apply fuzzy matching on recipe names, ingredient names, and kitchen terms
- Be more lenient with interpretation when confidence is low/medium
- Ask for confirmation when intent is ambiguous
- Treat "high" confidence input as reliable text

This allows the agent to leverage its domain knowledge (recipe database, kitchen vocabulary) to correct transcription errors that the STT model can't catch on its own.

### Future improvements (not yet implemented)
- **Level 2:** Per-segment confidence so the agent knows which words are uncertain
- **Level 3:** Beam search alternatives — pass top N transcription hypotheses to the agent

## Environment Variables

| Variable       | Default  | Description                                      |
|----------------|----------|--------------------------------------------------|
| `STT_MODEL`    | `base`   | faster-whisper model size: tiny, base, small, medium, large-v3 |
| `STT_LANGUAGE` | (auto)   | Force language code (e.g., `en`, `es`, `de`). Auto-detects if unset |
| `STT_DEVICE`   | `cpu`    | Compute device: `cpu` or `cuda`                  |
| `VITE_STT_URL` | `http://localhost:8002` | STT service URL for kitchen frontend |

## Dependencies

```
faster-whisper>=1.1.0
fastapi[standard]>=0.135.2
uvicorn>=0.42.0
python-multipart>=0.0.9
websockets>=13.0
```

## Notes

- The faster-whisper model files are downloaded on first container start and should be cached in a Docker volume to avoid re-downloading on rebuild
- For Raspi 5 deployment, the same Dockerfile works but should use `STT_MODEL=tiny` or `STT_MODEL=base` and `STT_DEVICE=cpu`
- The XVF3800 provides beam-formed, noise-cancelled audio which significantly improves transcription accuracy in noisy kitchen environments
- Audio format for WebSocket: 16-bit PCM at 16kHz mono — this is what faster-whisper expects and avoids transcoding overhead
- Consider adding a model volume in Compose to persist downloaded models across container rebuilds

## Progress

- [x] Decision: faster-whisper as STT engine
- [x] Decision: WebSocket + HTTP POST transport
- [x] Decision: Wake word handled externally
- [x] Decision: Two deployment topologies from one codebase
- [x] Design document created
- [x] Phase 1: STT Container (MVP)
- [ ] Phase 2: WebSocket Streaming
- [x] Phase 3: Agent Integration (frontend + standalone CLI)
- [ ] Phase 4: Audio Capture Client
- [ ] Phase 5: Wake Word (Optional)
