# Kitchen-Pi — Custom Module (Major)

## What this module is

A headless kitchen kiosk: a Raspberry Pi 5 with a 7" touch display and a
ReSpeaker microphone, running Chromium in kiosk mode against the voice-chef
server's kitchen UI over Tailscale, with faster-whisper running locally on
the device for sub-100ms voice transcription.

## Why it deserves Major status

Six distinct technical concerns, each non-trivial in isolation, integrated
into a single deployable device:

### 1. Edge ML inference

faster-whisper transcribes audio on the Pi itself rather than uploading it
to a server. Voice latency is bounded by the audio length plus model
inference time, not by network round-trip — typical end-to-end (button
release → transcript visible) is under 100 ms for short utterances on the
`small` model. The same flow with server-side STT over Tailscale would add
~150–400 ms of upload + processing RTT. For a kitchen UX where the operator
expects "I just stopped talking" to mean "the system has my words,"
sub-100 ms is the difference between feeling responsive and feeling
laggy.

### 2. Cross-host service discovery via Tailscale

The Pi and the server typically live on different networks (kitchen LAN
vs. office LAN, or kitchen LAN vs. home LAN). Tailscale's overlay handles
routing and addressing without DNS configuration, port forwarding, or NAT
punching gymnastics: `https://${SERVER_HOST}/...` resolves to the right
host wherever both ends are. The Pi's only auto-start service on boot is
Tailscale; everything else is brought up explicitly.

### 3. Kiosk-mode Linux deployment

Wayland kiosk Chromium on Pi OS Trixie, with audio routing for the ReSpeaker
mic via a wireplumber rule, a polkit rule allowing the `voice-chef` user to
restart the kiosk systemd unit without sudo, an XDG desktop launcher that
exposes that capability as a "Bring back kiosk" icon, and persistent
Chromium profile so the JWT cookie survives reboots. Each piece is small;
together they make the device usable by a non-developer in a kitchen.

### 4. Lean Pi-side checkout

The Pi only carries `pi/` (configs, scripts, compose) and `stt/` (the
Whisper service it actually runs) on disk — backend, agent, rag, and
frontend source never touch the kiosk device. Achieved with git's
sparse + partial clone (`--filter=blob:none` + `sparse-checkout`), so a
fresh provisioning fetches a few MB instead of the whole repo, and
`git pull` later respects the sparse paths automatically.

### 5. Single-frontend deployment, enabled by the PWA

The kitchen UI is served by the server at `https://${SERVER_HOST}/kitchen/`.
There is no parallel kitchen-frontend container on the Pi. The PWA
(see `docs/pwa.md`) handles offline shell + catalog caching, which is
what the Pi-side container used to do. Removing that duplication eliminated
parallel image builds, parallel runtime-config injection, and a Pi-side
nginx upstream layer that drifted from the server's setup as the
architecture evolved.

### 6. Authentication flow demonstrable from a clean boot

Authentication is plain JWT cookie auth, the same flow a human user goes
through in the office UI. On a freshly-provisioned Pi, the kiosk lands on
the login page; the kitchen-device credentials are typed in once; the
cookie persists in the kiosk profile across reboots. Wiping the profile
returns the Pi to its first-boot state. Nothing about the auth is
Pi-specific — the kitchen is a regular `users` row with `role='kitchen'`,
scoped to its tenant.

## Architecture

```
┌─────────────────────────────────┐
│ Pi (kitchen-pi)                 │      Tailscale       ┌────────────────────────┐
│                                 │  ◄──────────────────►│ Server                 │
│  ┌──────────────────────────┐   │   overlay network    │                        │
│  │ Chromium kiosk           │   │                      │  ┌─────────────────┐   │
│  │ https://${SERVER_HOST}/  │───┼──────────────────────┼─►│ nginx-proxy     │   │
│  │   kitchen/?kiosk=1       │   │                      │  │ (HTTPS termin.) │   │
│  └─────────┬────────────────┘   │                      │  └────┬────────────┘   │
│            │ /stt/transcribe    │                      │       │                │
│            ▼                    │                      │       ▼                │
│  ┌──────────────────────────┐   │                      │  ┌─────────────────┐   │
│  │ stt-tls (nginx)          │   │                      │  │ kitchen-frontend│   │
│  │ https://localhost/       │   │                      │  └─────────────────┘   │
│  └─────────┬────────────────┘   │                      │  ┌─────────────────┐   │
│            ▼                    │                      │  │ backend         │   │
│  ┌──────────────────────────┐   │                      │  └─────────────────┘   │
│  │ stt (faster-whisper)     │   │                      │  ┌─────────────────┐   │
│  │ http://localhost:8002    │   │                      │  │ agent           │   │
│  └──────────────────────────┘   │                      │  └─────────────────┘   │
└─────────────────────────────────┘                      │  ┌─────────────────┐   │
                                                         │  │ rag (+ qdrant)  │   │
                                                         │  └─────────────────┘   │
                                                         └────────────────────────┘
```

Browser-facing traffic over Tailscale is HTTPS terminated at the server's
nginx-proxy. Internal Compose-network traffic on the server is plain HTTP,
which is acceptable because the network boundary is the host. Pi-local
STT goes through the Pi-local TLS shim because the SPA loaded over HTTPS
can't speak to plain HTTP on `localhost` (mixed-content).

## Bringing it up from scratch

The "from scratch" demo is exactly what `pi/scripts/start-kitchen.sh`
demonstrates:

1. Pi boots. Only Tailscale is up.
2. SSH in, run `./pi/scripts/start-kitchen.sh`.
3. Script generates a self-signed cert for the Pi-local STT shim (first
   time only), brings up the STT + stt-tls containers, waits for STT to
   become healthy, enables + starts the kiosk systemd unit.
4. Chromium kiosk launches against `https://${SERVER_HOST}/kitchen/`,
   lands on the login page.
5. Authenticate with the kitchen-device credentials. The JWT cookie is
   stored in `/home/voice-chef/.kiosk-profile`.
6. Subsequent reboots: containers come back via `restart: unless-stopped`;
   systemd brings the kiosk back via `WantedBy=graphical.target`; Chromium
   reopens the kitchen URL with the same profile, cookie still valid, no
   human interaction needed.

To return the Pi to first-boot state: `./pi/scripts/reset-kitchen.sh`.
This disables the kiosk autostart, wipes the kiosk profile (and therefore
the cookie), and tears down the Pi-local containers. Tailscale is left
alone.

## What was rejected, and why

- **Pi running its own kitchen-frontend container** (the original v1
  design). It existed to give the Pi a local SPA for offline blips and
  to reverse-proxy API calls to the server. The PWA solves the first job
  more cleanly, and Tailscale + the server's nginx-proxy solve the second.
  Keeping the duplicate added image builds, runtime config injection, and
  a per-Pi nginx layer that drifted from the server's. Removed.

- **STT routed to the server** (option C2 in the design discussion).
  Operationally simpler — no Pi-local docker, no Pi-local cert. But it
  loses the edge-inference claim that justifies Major-tier scope, and it
  re-creates network dependence for the most latency-sensitive part of
  the voice loop. Rejected.

- **Auto-login via injected `/config.js`** (the kitchen-pi v1 mechanism).
  Required baking the kitchen password into a file served to any HTTP
  client that asked for it, with the justification that the URL was
  behind Tailscale. Manual login at first boot is honest auth, leaves no
  password on disk, and the Chromium kiosk profile makes it a one-time
  cost per session anyway. Rejected.

- **Per-Pi unique credentials**. Useful for per-device attribution, but
  overkill for a single-tenant deployment. The kitchen role represents
  the device class; per-Pi attribution can be layered on later via an
  `X-Device-Id` header without changing the auth model. Future work.

## Future hardening

These aren't blockers but worth knowing:

- **Tailscale-issued TLS certs.** `tailscale cert <hostname>` issues a
  Let's Encrypt cert for a Tailscale-only hostname. Replacing the
  self-signed cert on the server (and dropping the
  `--ignore-certificate-errors` Chromium flag on the Pi) would close the
  last "trust on first use" gap for HTTPS.

- **Device-bound API keys** instead of shared kitchen-user creds. Each
  Pi gets its own long-lived key on provisioning, backend has a
  `device_keys` table mapping key → user. Reduces blast radius if a
  single Pi's storage is compromised, and gives free per-Pi attribution.

- **mTLS for the agent + rag internal channel.** The current
  `INTERNAL_SECRET` shared header is a defensible perimeter pattern; if
  the deployment ever moves multi-host (server split across machines),
  mTLS or a service mesh becomes the right tool.
