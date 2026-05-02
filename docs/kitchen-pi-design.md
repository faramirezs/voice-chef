# Kitchen Point on Raspberry Pi 5 — Design

**Status:** Approved (brainstorm → spec, 2026-05-02)
**Owner:** Clemens
**Related docs:** [`docs/voice.md`](voice.md), [`docs/voiceNextSteps.md`](voiceNextSteps.md)
**Implementation plan:** TBD via writing-plans skill

---

## 1. Goal & scope

### Goal

Stand up a Raspberry Pi 5 at the kitchen workbench that, on power-on, comes up to the kitchen-frontend in fullscreen kiosk mode, captures audio from the XVF3800 microphone array, transcribes locally with faster-whisper, and routes the transcribed query through the agent on the server to render a recipe card on its 7" touchscreen.

### Phase 1 — In scope

- Hardware assembled and wired (Pi 5 + 7" official Touch Display 2 + XVF3800 + SD card + USB-C power)
- Raspberry Pi OS Trixie (Debian 13-based) 64-bit installed and configured
- Hostname `voice-chef-pi`, default user `voice-chef`
- Chromium in kiosk mode autostarts on boot, points at `http://localhost`
- Kitchen-frontend running locally on the Pi (production-built nginx container)
- STT (`stt/` container, faster-whisper, `tiny` or `base` model) running locally
- XVF3800 set as default ALSA/PipeWire input so browser `MediaRecorder` picks it up automatically
- Tailscale running on Pi and server, configured for stable hostname-based reach across networks
- Pi recovers cleanly from reboot — no manual intervention needed
- Wi-Fi and Ethernet both supported; mDNS for dev fallback, Tailscale for canonical reachability

### Phase 1 — Explicitly out of scope (Phase 2+)

- Wake word (always tap-to-speak in Phase 1; openWakeWord deferred)
- Voice ID / speaker recognition (Phase D per `voiceNextSteps.md`)
- Offline fallback / Pi-side recipe mirror (Phase 2, with three "design for later" commitments preserved here)
- Touchscreen UX tuning (Phase 1.5 — testable only on real hardware, fold into a follow-up after kiosk works)

### Success criteria

Chef walks up to the Pi, taps the mic button, speaks a recipe query, recipe card renders on the touchscreen. End-to-end, hands-free except for the initial tap.

---

## 2. Architecture & topology

```
┌──────────────────────────────────────────────────────────┐
│                       Kitchen Pi                         │
│   Raspberry Pi 5 (8 GB) · Pi OS Trixie 64-bit · Wayland  │
│                                                          │
│  ┌────────────────┐    ┌──────────────────────────────┐  │
│  │  XVF3800 mic   │───▶│  PipeWire default source     │  │
│  └────────────────┘    └──────────────┬───────────────┘  │
│                                       │ MediaRecorder    │
│  ┌──────────────────────────────────┐ │                  │
│  │  Chromium (kiosk, fullscreen)    │◀┘                  │
│  │  http://localhost                │                    │
│  └──────────┬───────────────────────┘                    │
│             │                                            │
│             ▼                                            │
│  ┌──────────────────────┐  ┌──────────────────────────┐  │
│  │  kitchen-frontend    │  │  stt (faster-whisper)    │  │
│  │  (Docker, port 80)   │  │  Docker, port 8002       │  │
│  └──────────┬───────────┘  └────────────▲─────────────┘  │
│             │                            │ /transcribe   │
│             │ /api/* → ${SERVER_HOST}    │               │
│             │ /agent  → ${SERVER_HOST}   │               │
│             │                                            │
│  ┌──────────▼─────────────────────┐                     │
│  │  7" Touch Display 2 (DSI)      │                     │
│  └────────────────────────────────┘                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Tailscale daemon (always on, joins mesh on boot)  │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Tailscale mesh
                          │ (over Wi-Fi / Ethernet / phone hotspot)
                          ▼
┌──────────────────────────────────────────────────────────┐
│   Server (MacBook for dev / Ubuntu for eval & prod)      │
│                                                          │
│  Existing voice-chef Compose stack:                      │
│  • backend  (port 80 → /api/*)                           │
│  • db       (Postgres)                                   │
│  • agent    (port 8001 → AG-UI)                          │
│  • rag      (port 8003 → /search/*)                      │
│  • qdrant   (port 6333)                                  │
│  • kitchen-frontend (also kept here for dev/office use)  │
│                                                          │
│  + Tailscale daemon (hostname `voice-chef-server`)       │
└──────────────────────────────────────────────────────────┘
```

### Service responsibility split

| Concern | Pi | Server | Notes |
|---|---|---|---|
| Display / UI rendering | ✓ | (also, for dev) | Same Docker image, different env |
| Audio capture | ✓ | — | XVF3800 → PipeWire → browser MediaRecorder |
| Transcription (STT) | ✓ | — | Local low-latency; `tiny`/`base` model on Pi |
| LLM agent | — | ✓ | Heavy lifting on the server |
| RAG search | — | ✓ | Qdrant + embeddings on server |
| Recipe data + auth | — | ✓ | Backend + Postgres on server |

### Frontend connection points

| Frontend env var | Resolves to | Notes |
|---|---|---|
| `VITE_API_BASE` | `http://${SERVER_HOST}/api` | recipe data, auth |
| `VITE_AGENT_URL` | `http://${SERVER_HOST}:8001` | AG-UI agent endpoint |
| `VITE_STT_URL` | `http://localhost:8002` | local STT on the Pi |

`SERVER_HOST` is a single env var with one canonical default (`voice-chef-server`, the Tailscale MagicDNS name). Changing the deployment target = update `SERVER_HOST` and restart. No code changes, no rebuild.

### Why this split

- Latency-sensitive paths (audio → text) stay local on the Pi
- Compute-heavy paths (LLM, RAG) stay on the server with horsepower
- Pi has no LLM provider keys, no Postgres credentials — small attack surface
- Server's existing Compose stack doesn't need changes; just needs to be reachable

---

## 3. Hardware

### Bill of materials

| Component | Spec | Connection |
|---|---|---|
| Raspberry Pi 5 | 8 GB RAM | — |
| Official 7" Touch Display 2 | 720 × 1280 (portrait native), capacitive multi-touch | DSI ribbon → DSI 1 port on Pi |
| XVF3800 mic array | USB-C UAC2 | USB 3.0 (blue) port |
| SD card | Class A2, ≥ 32 GB recommended | Pi's microSD slot |
| Power supply | Official 27W USB-C PD | USB-C power input |
| Case | Provided | — |

### Wiring sequence (power off)

1. **DSI ribbon → display** (display side first, then Pi side at DSI 1 — the port nearer USB-C). Cable contacts face the USB-C side on the Pi.
2. **Mount Pi onto display's standoffs.** Touch Display 2 powers and signals the Pi via the DSI ribbon — no GPIO jumper wires required.
3. **SD card** in the slot, image flashed in M1.
4. **XVF3800 → USB 3.0 port** (blue). Audio class device, no driver needed.
5. **Power last.** Use the official 27W PSU; underspecced power throttles USB peripherals.

### Things easy to miss

- **DSI 1 vs DSI 0:** Touch Display 2 goes in DSI 1 (nearer the USB-C port). DSI 0 is for the camera connector by Pi convention.
- **USB 3.0 vs USB 2.0:** XVF3800 in a blue (USB 3.0) port for cleaner power.
- **Default touchscreen orientation:** Pi OS treats the panel as landscape 1280×720 by default. Decide portrait vs landscape mounting before final calibration; rotate via `display_rotate` in `/boot/firmware/config.txt`.

### Power footprint

Pi 5 idle ~3W, 7" touchscreen ~3W, XVF3800 ~1W, kitchen-frontend + stt + Chromium under load ~6W. Comfortable for a 27W PSU.

---

## 4. Software stack on the Pi

### OS

- **Raspberry Pi OS Trixie 64-bit (Desktop)** — Desktop variant, not Lite. Trade ~1.5 GB of disk for a working Wayland session, pre-installed Chromium, pre-configured audio stack.
- Imager configures: hostname `voice-chef-pi`, user `voice-chef`, Wi-Fi credentials, SSH on, locale.

### Audio routing

- Pi OS Trixie uses PipeWire by default.
- XVF3800 set as default input source via `wpctl set-default <id>`, persisted via a wireplumber drop-in config so the choice survives reboots.
- Browser `MediaRecorder` uses the system default automatically — no per-page mic permission to manage once set.

### Docker

- Install via official `get.docker.com` script (works on Trixie arm64).
- Add `voice-chef` user to the `docker` group.

### Pi-side compose file

- **Separate compose at `pi/docker-compose.yml`** that runs only the two services we need on the Pi: `kitchen-frontend` and `stt`.
- Same Dockerfiles as the main project (no fork). Tailored compose file decouples the Pi's runtime from the server's full stack.

### Kitchen-frontend on the Pi

- Built (production) target, served by the existing nginx in the kitchen-frontend container.
- The container's `nginx.conf` is **env-templated at container start** (`envsubst`): `proxy_pass` for `/api/` and `/agent/` resolves to `${SERVER_HOST}`. Frontend code uses relative paths, nginx forwards. Same-origin from the browser → no CORS hassle.
- One env var (`SERVER_HOST=voice-chef-server`) is the only Pi-vs-server difference at deploy time.

### STT on the Pi

- Existing `stt/` container, unchanged Dockerfile.
- Env: `STT_MODEL=base`, `STT_DEVICE=cpu`, `STT_LANGUAGE=` (auto-detect).
- Persistent **model cache volume** (`whisper_models:/models`) so the model isn't re-downloaded on rebuild.

### Tailscale

- Installed via the official Tailscale Debian repo (supports Trixie).
- Brought up with `tailscale up --ssh --hostname=voice-chef-pi`.
- For unattended setup: use a Tailscale **auth key** (`--authkey=...`) instead of the browser flow.
- `tailscale ssh` enabled — lets you SSH into the Pi from anywhere on the user's Tailnet, no port forwarding needed.

### Kiosk + autostart

- Single **systemd unit `kitchen-point.service`** runs a startup script:
  1. Wait for Docker daemon ready.
  2. `docker compose -f /home/voice-chef/kitchen-pi/docker-compose.yml up -d`.
  3. `curl -fs http://localhost/` retry until kitchen-frontend responds (timeout 60 s).
  4. Launch Chromium: `chromium-browser --kiosk --no-first-run --noerrdialogs --start-maximized --user-data-dir=/home/voice-chef/.kiosk-profile http://localhost`.
- `Restart=on-failure` so a crashed Chromium relaunches automatically.
- Persistent `--user-data-dir` so mic permission and other browser state persist across reboots.
- `unclutter` (or built-in cursor hiding) to remove the mouse cursor when idle.

### What's deliberately not on the Pi

- No Postgres, no agent, no rag, no qdrant — server-only.
- No openWakeWord daemon (Phase 2).
- No Pi-side mirror service (Phase 2).
- No frontend dev server / hot reload — that lives on the developer's laptop. The Pi runs the prod build.

---

## 5. Server-side and connectivity

### Server-side requirements

The server runs the existing voice-chef Compose stack — no server-side code changes needed for the Pi to work. The server must:

- Have Tailscale installed, running, and joined under hostname `voice-chef-server`
- Have the existing voice-chef Compose stack running on standard ports (80 backend, 8001 agent)

### Ports the Pi must reach on the server

| Port | Service | Notes |
|---|---|---|
| 80 | backend (`/api/*`) | recipe data, auth |
| 8001 | agent (AG-UI) | voice query routing |

(Pi-internal: `localhost:80` for kitchen-frontend, `localhost:8002` for STT — never exposed beyond the Pi.)

### Connection layers on the Pi

| Layer | Purpose | Notes |
|---|---|---|
| **Tailscale mesh** (always-on) | Application traffic uses this | Stable hostname, works across networks |
| **Wi-Fi (host network)** | Underlying transport | Phone hotspot during eval, home Wi-Fi during dev |
| **Ethernet (host network)** | Underlying transport | Optional in eval; preferred in prod |

Pi runs all three layers in parallel. Tailscale is the application-level path; Wi-Fi/Ethernet just gets the Pi to the internet so Tailscale can establish its mesh.

### Why Tailscale is mandatory in Phase 1

During evaluation on school computers there is no sudo, no Pi joining the school WLAN, and the server may sit on a different network. Tailscale's mesh side-steps all of this — both endpoints come up on a virtual private network and address each other by stable hostnames regardless of physical network.

### `SERVER_HOST` defaults

| Environment | `SERVER_HOST` |
|---|---|
| Dev / Eval / Prod | `voice-chef-server` (Tailscale MagicDNS) |
| Local-only fallback | `macbook.local` (mDNS) — for when developing without Tailscale |

The Tailscale hostname is the canonical value. mDNS is dev-only convenience.

### Subnet considerations

- mDNS / `.local` resolution **does not cross VLAN boundaries**. If the Pi and server end up on separate subnets, fall back to a fixed IP or a hosts entry — but Tailscale removes this concern entirely.
- For Phase 1 dev, both will be on the same Wi-Fi anyway.

---

## 6. Phase 1 build sequence

Each milestone produces something testable. Don't skip ahead.

### Precondition

- Server has Tailscale installed and running, joined under hostname `voice-chef-server`
- Server has the voice-chef Compose stack running on standard ports

### M1 — Pi imaged and bootable

In Raspberry Pi Imager: select Pi OS Trixie 64-bit (Desktop). Advanced options:
- Hostname: `voice-chef-pi`
- User: `voice-chef` + password
- Wi-Fi SSID + password
- SSH enabled (key-based preferred)
- Locale/keyboard

Flash → insert into Pi → power on. **Verify:** `ssh voice-chef@voice-chef-pi.local` succeeds, `cat /etc/os-release` shows Trixie, `uname -m` returns `aarch64`.

### M2 — Touchscreen functional

Touch Display 2 connected via DSI 1. After M1, desktop should be visible. If not, check ribbon orientation. Decide portrait vs landscape; set rotation in `/boot/firmware/config.txt` if needed. **Verify:** tap-and-drag works on the desktop.

### M3 — Audio routing

Plug XVF3800 into a USB 3.0 port. Set as default: `wpctl set-default <id>`. Persist via wireplumber drop-in. **Verify:** `arecord -d 5 -f cd /tmp/test.wav && aplay /tmp/test.wav` records and plays back the XVF3800 input.

### M4 — Docker installed

Install via official script. Add `voice-chef` to `docker` group. **Verify:** `docker run --rm hello-world` works without sudo.

### M5 — Tailscale joined

Install via Tailscale's Debian repo. `sudo tailscale up --ssh --hostname=voice-chef-pi` (browser auth or `--authkey=...`). **Verify:** `tailscale status` shows both peers; `ping voice-chef-server` resolves and responds.

### M6 — Pi compose stack running

Create `/home/voice-chef/kitchen-pi/`. Inside: a `docker-compose.yml` (kitchen-frontend + stt) and a `.env` (SERVER_HOST, STT_MODEL, etc). `docker compose up -d`. **Verify:** `curl -fs http://localhost | head` returns kitchen-frontend HTML; `curl -fs http://localhost:8002/health` returns `{"status":"ok"}`.

### M7 — End-to-end smoke test

From the Pi's desktop browser, open `http://localhost`. Mic permission prompt → accept. Tap mic, speak a recipe query. **Verify:** browser POSTs audio to `localhost:8002` (STT), gets transcript, frontend POSTs to `/agent/...` (proxied to `voice-chef-server:8001`), recipe card renders.

### M8 — Kiosk autostart on boot

Create `/etc/systemd/system/kitchen-point.service` with the startup script described in §4. Reboot the Pi. **Verify:** within ~60 s of power-on, kiosk Chromium showing kitchen-frontend full-screen, no terminal/desktop visible. `pkill chromium` and confirm systemd relaunches.

### M9 — Phase 1 acceptance

All milestones pass on a clean boot. Document device-specific quirks in `pi/README.md`. Tag the commit on the eval-target branch as a known-good baseline.

### Estimated time

Half a day to a day of focused work, spread across sessions, plus contingency for the inevitable USB / display / network surprise.

---

## 7. Phase 2 deferred work + open risks

### Phase 2 — Offline fallback

Three "design for later" commitments preserved in Phase 1 to make this cheap to add later:

1. **Centralized API client in the kitchen-frontend** — every backend call goes through one wrapper. Adding a fallback branch later is a one-file change.
2. **Pi-side mirror service is named in the architecture from day one** — `kitchen-cache`, runs alongside `kitchen-frontend` and `stt` in the Pi compose, port 8004. Documented as an empty seat at the table.
3. **Phase 2 issue tracked at PR time** so it doesn't slip — open a GitHub issue when the Pi PR opens.

Phase 2 implementation:
- `kitchen-cache` on the Pi: small FastAPI + SQLite. Polls `${SERVER_HOST}/api/recipes` every N minutes when reachable, mirrors recipes + ingredients into local SQLite. Schema names match Postgres for portability.
- Kitchen-frontend's API client tries server first; on connection failure, falls through to `localhost:8004`. UI shows a "you're offline" banner with last-sync timestamp.
- Search endpoints on `kitchen-cache`: simple substring on recipe name + name_english. No semantic search offline (RAG stays server-side).
- ~1–2 days when prioritized.

### Phase 2 — Wake word

OpenWakeWord on the Pi as a separate container. Phase 5 in `voice.md` already; ~1–2 days.

### Phase 2.5 — Frontend touchscreen UX pass

Once kiosk is running, look at the kitchen-frontend on the actual 7" panel and iterate. Fold into normal frontend iteration after Phase 1 lands.

### Phase 3+ — Voice ID for attribution

Per `voiceNextSteps.md` and project memory: speaker recognition for personalization (not auth). Lowest priority on the roadmap.

### Open risks for Phase 1

| Risk | Likelihood | Mitigation |
|---|---|---|
| XVF3800 doesn't auto-set as default mic after boot | medium | wireplumber drop-in `.conf` to pin XVF3800; verify across reboots in M3 |
| Chromium doesn't honor remembered mic permission in kiosk mode | medium | `--user-data-dir` for persistent profile; or `--use-fake-ui-for-media-stream` to bypass prompt |
| mDNS unreliable across Tailscale + local Wi-Fi mix | low | always prefer Tailscale hostname; mDNS only as dev fallback |
| Touchscreen orientation mismatch | high | M2 includes a "decide before calibration" gate; both orientations supported via `display_rotate` |
| Pi 5 thermal throttling under sustained STT load | low | passive heatsink usually enough; monitor `vcgencmd measure_temp` |
| Tailscale node expiry during eval | low | use a long-lived auth key; document regen step |
| Phone hotspot + Tailscale routes weirdly | medium | DERP relays bail us out at small latency cost; test before eval day |
| First-boot Wi-Fi config typo makes Pi unreachable | low (high cost) | M1 verifies SSH before unplugging keyboard; keep keyboard available for recovery |

---

## 8. Verification plan

### Per-milestone verification

| Milestone | Pass criterion |
|---|---|
| M1 | `ssh voice-chef@voice-chef-pi.local` works; OS = Trixie; arch = `aarch64` |
| M2 | desktop visible; tap-and-drag works |
| M3 | recorded audio plays back; XVF3800 default after reboot |
| M4 | `docker run --rm hello-world` works without sudo |
| M5 | `tailscale status` shows both peers; `ping voice-chef-server` works |
| M6 | all containers running; HTML from kitchen-frontend; STT health OK |
| M7 | DevTools shows `/transcribe` 200, `/agent/...` SSE stream, recipe card renders |
| M8 | reboot → kiosk live in ≤60 s; `pkill chromium` → systemd relaunches |

### Sanity checks (after any reboot or config change)

```bash
# 1. Pi reachable
ping voice-chef-pi.local
tailscale ping voice-chef-pi
ssh voice-chef@voice-chef-pi

# 2. Default mic
ssh voice-chef@voice-chef-pi 'wpctl status | grep -A2 "Audio/Source"'

# 3. Pi-side containers up
ssh voice-chef@voice-chef-pi 'docker compose -f kitchen-pi/docker-compose.yml ps'

# 4. Server reachable from Pi over Tailscale
ssh voice-chef@voice-chef-pi 'curl -fs http://voice-chef-server/api/recipes?limit=1 | jq .'

# 5. End-to-end probe
ssh voice-chef@voice-chef-pi 'curl -fs -X POST http://localhost:8002/transcribe -F audio=@/tmp/test.wav | jq .text'

# 6. Kiosk service healthy
ssh voice-chef@voice-chef-pi 'systemctl status kitchen-point.service'
```

### Failure-mode rehearsal

Do these once before declaring "done":

- **Power-cycle test:** unplug, wait 10 s, plug back in. Within 60 s, kiosk is live.
- **Server-down test:** stop server's compose, wait 30 s, attempt voice query. STT works locally; agent call fails visibly. Documents the Phase-2-fallback gap honestly.
- **Network-flap test:** disable Wi-Fi on Pi for 30 s, re-enable. Tailscale reconnects within 10 s; voice queries resume without restart.
- **Chromium-crash test:** `pkill chromium` from SSH. systemd relaunches within 5 s.

### Dev-side verification (laptop)

- Continue using `localhost:5174` (vite dev) on the laptop for hot-reload development. Pi only sees the prod build.
- When ready to test on actual hardware: rebuild kitchen-frontend image, push to a registry (or `docker save | ssh ... docker load`), `docker compose pull && up -d` on the Pi.

---

## 9. Open decisions for the implementation phase

These are deliberately deferred to writing-plans / implementation; surfaced here so the spec doesn't pretend they're settled.

- Exact systemd unit content for `kitchen-point.service` (script body, user, restart strategy specifics)
- Exact wireplumber drop-in syntax for default-source pinning across reboots
- Pi-side compose file structure: file path, service name overrides, env var names
- Final Chromium kiosk flag set (especially around mic permissions and crash recovery)
- Auth-key vs browser-flow choice for Tailscale first-time bring-up (depends on whether someone is at the Pi during first setup)
- Exact deployment workflow for kitchen-frontend updates from laptop to Pi (`scp` of dist? registry pull? `docker save | docker load`?)
- Wireplumber-vs-systemd-user-service for persistent default-mic config

---

## 10. References

- [`docs/voice.md`](voice.md) — STT service design, deployment topologies, faster-whisper rationale
- [`docs/voiceNextSteps.md`](voiceNextSteps.md) — overall roadmap including Topic 5 (auth) and the model-investigation tracking
- [Raspberry Pi OS docs](https://www.raspberrypi.com/documentation/computers/os.html)
- [Official 7" Touch Display 2 documentation](https://www.raspberrypi.com/documentation/accessories/display.html)
- [Tailscale install on Debian](https://tailscale.com/kb/1174/install-debian-trixie)
- [PipeWire / wireplumber configuration](https://docs.pipewire.org/page_man_wireplumber_5_md.html)

---

*End of design.*
