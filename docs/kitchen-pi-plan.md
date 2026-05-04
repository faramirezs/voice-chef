# Kitchen Point on Raspberry Pi 5 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a working voice-driven kitchen point on a Raspberry Pi 5, end-to-end from fresh hardware to autostart kiosk.

**Architecture:** Hybrid topology. The Pi runs the kitchen UI, audio capture, and STT locally; the server (MacBook for dev / Ubuntu for eval+prod) runs the agent, backend, db, rag, and qdrant. Pi and server reach each other over a Tailscale mesh. Frontend on the Pi is the same Docker image as the server's, just templated to proxy to a different backend host.

**Tech stack:** Pi OS Trixie 64-bit (Desktop), Docker, Tailscale, PipeWire, faster-whisper, Chromium kiosk, env-templated nginx (envsubst), systemd, the existing voice-chef Compose stack (backend / agent / rag / qdrant / db).

**Source spec:** [`docs/kitchen-pi-design.md`](kitchen-pi-design.md) — all "why" decisions live there.

**Auth context (post-PR #183, important):** The backend now requires authentication on browser-proxied paths. Only the agent has a shared-secret bypass. The kitchen Pi must log in once as a "kitchen" user and rely on the JWT cookie persisting in the Chromium profile. See `frontend/docs/AUTH_JWT_Flow.md` for the full flow.

---

## File map

### Files committed in this branch (live in the repo)

| Path | What it is | Phase introduced |
|---|---|---|
| `docs/kitchen-pi-design.md` | Spec (already exists) | (existing) |
| `docs/kitchen-pi-plan.md` | This plan, committed copy | Phase B |
| `pi/README.md` | Quick-reference for setting up and operating the Pi | Phase B |
| `pi/docker-compose.yml` | Pi-only Compose stack (kitchen-frontend + stt) | Phase B |
| `pi/.env.example` | Example env vars for Pi runtime | Phase B |
| `pi/systemd/kitchen-point.service` | systemd unit for autostart | Phase B |
| `pi/scripts/kitchen-point-start.sh` | Startup script invoked by the unit | Phase B |
| `pi/wireplumber/51-xvf3800-default.conf` | Pin XVF3800 as default audio source | Phase B |
| `frontend/kitchen/nginx.conf.template` | Env-templated nginx config (replaces `nginx.conf` in container build) | Phase B |
| `frontend/kitchen/docker-entrypoint.sh` | Runs envsubst on the template, then exec nginx | Phase B |
| `frontend/kitchen/Dockerfile` (modify) | Use entrypoint; install envsubst (gettext) | Phase B |
| `docker-compose.yml` (modify) | Pass new env vars to `kitchen-frontend` with backwards-compatible defaults | Phase B |

### Files that exist only on the Pi (not in repo)

| Path | What it is |
|---|---|
| `/home/voice-chef/kitchen-pi/docker-compose.yml` | Copy of `pi/docker-compose.yml` |
| `/home/voice-chef/kitchen-pi/.env` | Real values for `SERVER_HOST`, `STT_MODEL`, etc. |
| `/etc/systemd/system/kitchen-point.service` | Copy of `pi/systemd/kitchen-point.service` |
| `/usr/local/bin/kitchen-point-start.sh` | Copy of `pi/scripts/kitchen-point-start.sh` |
| `/etc/wireplumber/wireplumber.conf.d/51-xvf3800-default.conf` | Copy of the wireplumber drop-in |
| `/home/voice-chef/.kiosk-profile/` | Persistent Chromium profile (cookies, mic permission) |

---

## Phase A — Server-side preflight

The server must be ready before the Pi can talk to it. Do these on the server (MacBook for dev, Ubuntu box for eval/prod).

### Task A.1: Server is on latest `main` with PR #183 + #185 merged

**Files:**
- Read: `/Users/clemens/Documents/Claude/Transcendence/voice-chef` (current repo on the server)

- [ ] **Step 1: Fetch and align**

```bash
git fetch origin
git checkout main
git pull --ff-only
git log --oneline -3
```

Expected: most recent commit is `df3cba3` or later (`Merge pull request #185 from faramirezs/179-frontend-recipe-page-with-ingredients`), `d359ede` for PR #183 should be visible in recent history.

- [ ] **Step 2: Read the auth flow docs**

```bash
cat frontend/docs/AUTH_JWT_Flow.md | head -100
```

Expected: documentation about JWT cookie flow, expiration handling, kitchen ↔ office redirect.

### Task A.2: Generate `INTERNAL_SECRET` and update server `.env`

**Files:**
- Modify: `.env` on the server

- [ ] **Step 1: Generate a random secret**

```bash
openssl rand -hex 32
```

Expected: 64-character hex string. Copy it.

- [ ] **Step 2: Add to `.env`**

Add the line (or update if present):

```
INTERNAL_SECRET=<the 64-character hex string from step 1>
```

- [ ] **Step 3: Restart agent + backend so they pick up the new env**

```bash
docker compose up -d --force-recreate backend agent
```

Expected: both containers recreate, healthy.

- [ ] **Step 4: Verify the secret reached both containers**

```bash
docker compose exec backend printenv INTERNAL_SECRET
docker compose exec agent printenv INTERNAL_SECRET
```

Expected: same 64-character string in both. **They MUST match exactly.**

### Task A.3: Verify the server's auth bypass for the agent works

- [ ] **Step 1: Test agent → backend internal call**

```bash
SECRET=$(grep ^INTERNAL_SECRET= .env | cut -d= -f2)
curl -fs -H "X-Internal-Secret: $SECRET" http://localhost:8000/api/recipes?limit=1 | jq .
```

Expected: HTTP 200, JSON with `items` array.

- [ ] **Step 2: Confirm browser-style call (no header) gets 401**

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/recipes?limit=1
```

Expected: `401`. (This is the new correct behaviour — auth required for unauthenticated browser-style calls.)

### Task A.4: Create a "kitchen" user account on the server

The kitchen Pi will log in as this user. The user's permissions should be the standard kitchen-tablet shape (read recipes, scale temporarily; no destructive ops). For Phase 1, a normal user is fine — the destructive-action restriction lives in the SYSTEM_PROMPT and the chosen agent tools.

**Files:**
- Modify: server's database (via `/api/auth/signup`)

- [ ] **Step 1: Sign up the kitchen user via the API**

```bash
curl -fs -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"kitchen@voice-chef.local","password":"<choose-a-strong-password>","first_name":"Kitchen","last_name":"Point"}' \
  | jq .
```

Replace `<choose-a-strong-password>` with a real password and **save it somewhere secure** — you'll type it once on the Pi during first-boot login.

Expected: HTTP 200/201, JSON response with `access_token` and user details.

- [ ] **Step 2: Confirm login works**

```bash
curl -fs -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"kitchen@voice-chef.local","password":"<your-password>"}' \
  | jq '.access_token | .[0:20] + "..."'
```

Expected: a JWT prefix, indicating successful login.

### Task A.5: Server has Tailscale running under hostname `voice-chef-server`

- [ ] **Step 1: Install Tailscale (if not already)**

On macOS: download from https://tailscale.com/download/mac. On Ubuntu: `curl -fsSL https://tailscale.com/install.sh | sh`.

- [ ] **Step 2: Bring it up with the right hostname**

```bash
sudo tailscale up --hostname=voice-chef-server
# follow the auth URL printed; sign in with your Tailscale account
```

- [ ] **Step 3: Verify**

```bash
tailscale status
```

Expected: this device appears at the top with hostname `voice-chef-server` and a `100.x.y.z` Tailscale IP. (No other peers needed yet — the Pi joins later.)

- [ ] **Step 4: Confirm MagicDNS works**

```bash
ping -c 2 voice-chef-server
```

Expected: pings 100.x.y.z. If "name resolution failure", enable MagicDNS in the Tailscale admin console (https://login.tailscale.com/admin/dns).

---

## Phase B — Repo preparation (on developer laptop)

Create and commit all the files the Pi will consume. The Pi pulls these from a `git clone` of the repo (Task F.1).

### Task B.1: Create `pi/` directory and initial README

**Files:**
- Create: `pi/README.md`

- [ ] **Step 1: Create directory and README**

```bash
mkdir -p pi/{systemd,scripts,wireplumber}
```

- [ ] **Step 2: Write `pi/README.md`**

```markdown
# Voice Chef — Kitchen Pi

Phase-1 deployment artifacts for running the kitchen point on a Raspberry Pi 5.

## What this directory contains

| Path | Purpose |
|---|---|
| `docker-compose.yml` | Compose stack for the Pi: kitchen-frontend + stt only |
| `.env.example` | Template for `.env` — copy and fill in `SERVER_HOST`, etc. |
| `systemd/kitchen-point.service` | systemd unit that auto-starts the kitchen point on boot |
| `scripts/kitchen-point-start.sh` | Startup script invoked by the systemd unit |
| `wireplumber/51-xvf3800-default.conf` | Wireplumber drop-in to pin XVF3800 as the default audio source |

## Quick reference

```bash
# On the Pi, after first boot:
cd ~/kitchen-pi
cp .env.example .env
$EDITOR .env                                       # set SERVER_HOST etc.
docker compose up -d                               # start kitchen-frontend + stt
sudo cp systemd/kitchen-point.service /etc/systemd/system/
sudo cp scripts/kitchen-point-start.sh /usr/local/bin/
sudo cp wireplumber/51-xvf3800-default.conf /etc/wireplumber/wireplumber.conf.d/
sudo systemctl daemon-reload
sudo systemctl enable --now kitchen-point.service
```

For full step-by-step setup, see [`docs/kitchen-pi-plan.md`](../docs/kitchen-pi-plan.md).
For architectural rationale, see [`docs/kitchen-pi-design.md`](../docs/kitchen-pi-design.md).

## Updating the kitchen-frontend on the Pi

After making changes on your laptop and pushing to the branch the Pi tracks:

```bash
ssh voice-chef@voice-chef-pi
cd voice-chef
git pull
cd pi
docker compose pull        # if images come from a registry
# OR
docker compose build       # if building locally
docker compose up -d
```
```

- [ ] **Step 3: Commit** (don't add other Pi files yet; committed at the end of Phase B)

```bash
git add pi/README.md
git commit -m "pi: add directory and README"
```

### Task B.2: Write `pi/docker-compose.yml`

**Files:**
- Create: `pi/docker-compose.yml`

- [ ] **Step 1: Write the compose file**

```yaml
services:
  kitchen-frontend:
    image: voice-chef-kitchen-frontend:latest
    build:
      context: ../frontend/kitchen/
    ports:
      - "80:80"
    environment:
      # nginx envsubst targets — point the proxy at the server (via Tailscale)
      API_HOST: ${SERVER_HOST}
      API_PORT: "80"
      AGENT_HOST: ${SERVER_HOST}
      AGENT_PORT: "8001"
    depends_on:
      - stt
    restart: unless-stopped

  stt:
    image: voice-chef-stt:latest
    build:
      context: ../stt/
    ports:
      - "8002:8002"
    environment:
      STT_MODEL: ${STT_MODEL:-base}
      STT_LANGUAGE: ${STT_LANGUAGE:-}
      STT_DEVICE: ${STT_DEVICE:-cpu}
    volumes:
      - whisper_models:/models
    restart: unless-stopped

volumes:
  whisper_models:
```

- [ ] **Step 2: Verify compose file syntax**

```bash
docker compose -f pi/docker-compose.yml config --quiet
```

Expected: exits cleanly (no output on success).

### Task B.3: Write `pi/.env.example`

**Files:**
- Create: `pi/.env.example`

- [ ] **Step 1: Write the env template**

```bash
cat > pi/.env.example <<'EOF'
# Pi-side runtime env
# Copy to .env and fill in values appropriate for the deployment target.

# Server hostname (Tailscale MagicDNS preferred; mDNS as fallback)
# Used by kitchen-frontend's nginx to proxy /api/ and /agent/ to the server.
SERVER_HOST=voice-chef-server

# faster-whisper model size:
#   tiny  — Pi 5 friendly, lower accuracy
#   base  — Pi 5 friendly, recommended baseline
#   small — borderline on a Pi 5; only if you need more accuracy
STT_MODEL=base

# Force a language code (e.g., en, de, fr) or leave blank for auto-detect.
STT_LANGUAGE=

# CPU only on the Pi (no GPU available)
STT_DEVICE=cpu
EOF
```

### Task B.4: Env-templated nginx for kitchen-frontend

This is the core change that lets the same kitchen-frontend image run on both server and Pi with different proxy targets. **Step-by-step is critical here** because we must not break the server's existing setup.

**Files:**
- Create: `frontend/kitchen/nginx.conf.template`
- Create: `frontend/kitchen/docker-entrypoint.sh`
- Modify: `frontend/kitchen/Dockerfile`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Read the existing nginx.conf to understand what to template**

```bash
cat frontend/kitchen/nginx.conf
```

Note the `proxy_pass http://backend:80/` and `proxy_pass http://agent:8001/` lines — these are what we'll template.

- [ ] **Step 2: Write the templated config**

```bash
cat > frontend/kitchen/nginx.conf.template <<'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # SPA routing — all non-file requests go to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API traffic to FastAPI
    location /api/ {
        proxy_pass http://${API_HOST}:${API_PORT}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy agent traffic to Agent service
    location /agent/ {
        proxy_pass http://${AGENT_HOST}:${AGENT_PORT}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_read_timeout 1h;
    }
}
EOF
```

- [ ] **Step 3: Write the docker-entrypoint script**

```bash
cat > frontend/kitchen/docker-entrypoint.sh <<'EOF'
#!/bin/sh
set -e

# Defaults preserve the server-side Compose-network behaviour.
: "${API_HOST:=backend}"
: "${API_PORT:=80}"
: "${AGENT_HOST:=agent}"
: "${AGENT_PORT:=8001}"

export API_HOST API_PORT AGENT_HOST AGENT_PORT

echo "kitchen-frontend nginx: API_HOST=$API_HOST:$API_PORT  AGENT_HOST=$AGENT_HOST:$AGENT_PORT"

envsubst '${API_HOST} ${API_PORT} ${AGENT_HOST} ${AGENT_PORT}' \
    < /etc/nginx/conf.d/default.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
EOF
chmod +x frontend/kitchen/docker-entrypoint.sh
```

- [ ] **Step 4: Modify the Dockerfile to install envsubst and use the entrypoint**

Open `frontend/kitchen/Dockerfile`. Replace the runtime stage (everything after `FROM nginx:1.28-alpine AS runtime`) with:

```dockerfile
FROM nginx:1.28-alpine AS runtime
RUN apk add --no-cache gettext
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN mkdir -p /var/cache/nginx/client_temp \
        /var/cache/nginx/proxy_temp \
        /var/cache/nginx/fastcgi_temp \
        /var/cache/nginx/uwsgi_temp \
        /var/cache/nginx/scgi_temp \
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid \
    && chown nginx:nginx /etc/nginx/conf.d
USER nginx
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
```

(The old static `nginx.conf` is no longer copied — the template replaces it.)

- [ ] **Step 5: Delete the now-unused static `nginx.conf`**

```bash
git rm frontend/kitchen/nginx.conf
```

- [ ] **Step 6: Update `docker-compose.yml` so server's kitchen-frontend gets the new env vars**

Open `docker-compose.yml`. In the `kitchen-frontend` service, add an `environment:` block under it:

```yaml
  kitchen-frontend:
    build:
      context: ./frontend/kitchen/
    ports:
      - "8082:80"
    networks:
      - app-network
    environment:
      API_HOST: ${API_HOST:-backend}
      API_PORT: ${API_PORT:-80}
      AGENT_HOST: ${AGENT_HOST:-agent}
      AGENT_PORT: ${AGENT_PORT:-8001}
    depends_on:
      - agent
```

The `:-` defaults preserve the existing server-side behaviour (no `.env` change required for the server).

- [ ] **Step 7: Rebuild kitchen-frontend on laptop and verify the server case still works**

```bash
docker compose build kitchen-frontend
docker compose up -d --force-recreate kitchen-frontend
sleep 3
docker compose logs kitchen-frontend --tail 5
```

Expected log line: `kitchen-frontend nginx: API_HOST=backend:80  AGENT_HOST=agent:8001`.

- [ ] **Step 8: Smoke-test the proxy paths still work on the laptop**

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/api/recipes?limit=1
```

Expected: 200 (the index page) and 401 (recipes — unauthenticated). The 401 confirms the proxy is reaching the backend correctly; the auth wall is the new expected behaviour from PR #183.

- [ ] **Step 9: Commit**

```bash
git add frontend/kitchen/nginx.conf.template \
        frontend/kitchen/docker-entrypoint.sh \
        frontend/kitchen/Dockerfile \
        frontend/kitchen/nginx.conf \
        docker-compose.yml
git commit -m "kitchen-frontend: env-templated nginx proxy targets

Replaces hardcoded backend:80 / agent:8001 in nginx.conf with envsubst
templating against API_HOST / API_PORT / AGENT_HOST / AGENT_PORT. Defaults
preserve the existing server-side Docker-network behaviour; the Pi-side
override points the proxy at SERVER_HOST (Tailscale).

No server-side env change required — defaults match the original config."
```

### Task B.5: Write the systemd unit

**Files:**
- Create: `pi/systemd/kitchen-point.service`

- [ ] **Step 1: Write the unit file**

```bash
cat > pi/systemd/kitchen-point.service <<'EOF'
[Unit]
Description=Voice Chef — Kitchen Point
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple
User=voice-chef
Group=voice-chef
ExecStart=/usr/local/bin/kitchen-point-start.sh
Restart=on-failure
RestartSec=10
TimeoutStartSec=120

# Wayland session for kiosk Chromium
Environment=WAYLAND_DISPLAY=wayland-0
Environment=XDG_RUNTIME_DIR=/run/user/1000

[Install]
WantedBy=graphical.target
EOF
```

(`UID 1000` is the default for the first user, which is `voice-chef` on a fresh Pi OS install. If yours differs after first boot, adjust `XDG_RUNTIME_DIR=/run/user/<actual-uid>`.)

### Task B.6: Write the startup script

**Files:**
- Create: `pi/scripts/kitchen-point-start.sh`

- [ ] **Step 1: Write the script**

```bash
cat > pi/scripts/kitchen-point-start.sh <<'EOF'
#!/bin/bash
# Voice Chef — Kitchen Point startup script.
# 1. Brings up the Pi-side Compose stack
# 2. Waits for kitchen-frontend health
# 3. Launches Chromium in kiosk mode

set -euo pipefail

COMPOSE_DIR="/home/voice-chef/kitchen-pi"
KIOSK_URL="http://localhost"
KIOSK_PROFILE_DIR="/home/voice-chef/.kiosk-profile"
HEALTH_TIMEOUT=60

echo "[kitchen-point] $(date -Iseconds) — bringing up Compose stack"
cd "$COMPOSE_DIR"
docker compose up -d

echo "[kitchen-point] waiting up to ${HEALTH_TIMEOUT}s for kitchen-frontend"
for i in $(seq 1 "$HEALTH_TIMEOUT"); do
    if curl -fs --max-time 2 "$KIOSK_URL" > /dev/null 2>&1; then
        echo "[kitchen-point] kitchen-frontend ready after ${i}s"
        break
    fi
    sleep 1
done

if ! curl -fs --max-time 2 "$KIOSK_URL" > /dev/null 2>&1; then
    echo "[kitchen-point] ERROR: kitchen-frontend did not respond within ${HEALTH_TIMEOUT}s" >&2
    exit 1
fi

echo "[kitchen-point] launching Chromium kiosk"
exec chromium-browser \
    --kiosk \
    --no-first-run \
    --noerrdialogs \
    --disable-restore-session-state \
    --disable-features=TranslateUI \
    --autoplay-policy=no-user-gesture-required \
    --user-data-dir="$KIOSK_PROFILE_DIR" \
    --start-maximized \
    "$KIOSK_URL"
EOF
chmod +x pi/scripts/kitchen-point-start.sh
```

### Task B.7: Write wireplumber drop-in for default mic

**Files:**
- Create: `pi/wireplumber/51-xvf3800-default.conf`

- [ ] **Step 1: Write the config**

```bash
cat > pi/wireplumber/51-xvf3800-default.conf <<'EOF'
# Pin the XMOS XVF3800 as the default audio source.
# Higher priority.* values cause Wireplumber to auto-select this device
# as the default capture source whenever it is present.

monitor.alsa.rules = [
    {
        matches = [
            {
                node.name = "~alsa_input.usb-XMOS_XVF3800.*"
            }
        ]
        actions = {
            update-props = {
                priority.driver  = 2000
                priority.session = 2000
            }
        }
    }
]
EOF
```

(The `~` prefix is a regex match — XVF3800's exact device name varies by firmware. If the regex doesn't match on the actual Pi, we'll find the real `node.name` in Phase D and adjust.)

### Task B.8: Commit pi/* contents

- [ ] **Step 1: Stage and commit**

```bash
git add pi/docker-compose.yml \
        pi/.env.example \
        pi/systemd/kitchen-point.service \
        pi/scripts/kitchen-point-start.sh \
        pi/wireplumber/51-xvf3800-default.conf
git commit -m "pi: add Phase 1 deployment artifacts

- docker-compose.yml: Pi-only stack (kitchen-frontend + stt)
- .env.example: SERVER_HOST + STT_* env template
- systemd/kitchen-point.service: autostart unit
- scripts/kitchen-point-start.sh: startup orchestration
- wireplumber/51-xvf3800-default.conf: pin XVF3800 as default mic"
```

### Task B.9: Copy the plan into `docs/` for the eventual PR

Mirroring the spec pattern (local copy in `docs/superpowers/plans/`, committed copy in `docs/`).

- [ ] **Step 1: Copy the plan and adjust paths**

```bash
cp docs/superpowers/plans/2026-05-04-kitchen-pi.md docs/kitchen-pi-plan.md
sed -i '' 's|\.\./\.\./kitchen-pi-design\.md|kitchen-pi-design.md|g' docs/kitchen-pi-plan.md
```

- [ ] **Step 2: Commit**

```bash
git add docs/kitchen-pi-plan.md
git commit -m "docs: add kitchen-pi implementation plan"
```

---

## Phase C — Pi imaging and first boot (M1)

### Task C.1: Imager configuration captured (already done by user)

**Files:** none (action on the imager UI)

- [ ] **Step 1: Confirm Imager settings before flash**
  - Device: Raspberry Pi 5
  - OS: Raspberry Pi OS (64-bit, Trixie-based, Desktop)
  - Storage: target SD card
  - Hostname: `voice-chef-pi`
  - User: `voice-chef` + chosen password
  - Wi-Fi: SSID + password (phone hotspot, or home Wi-Fi for first boot)
  - Locale + keyboard
  - SSH: enabled, public key authorised (paste from `cat ~/.ssh/id_ed25519.pub`)
  - Services: Raspberry Pi Connect enabled (optional backup access)

- [ ] **Step 2: Flash and verify**

Click "Yes" to apply settings, "Yes" to overwrite SD, wait for write + verification.

- [ ] **Step 3: Eject SD card cleanly**

(macOS: Imager usually ejects automatically. Otherwise: Finder → eject.)

### Task C.2: First boot

**Files:** none (physical action)

- [ ] **Step 1: Insert SD card into the Pi**

- [ ] **Step 2: Connect Touch Display 2 via DSI 1**

DSI 1 = the connector closer to the USB-C power port. Silver contacts face the USB-C side on the Pi.

- [ ] **Step 3: Plug XVF3800 into a blue (USB 3.0) port**

(Optional at this step but harmless — the audio config happens in Phase D.)

- [ ] **Step 4: Connect power last**

Use the official 27W PSU. Wait ~2–3 minutes — first boot runs initial config and reboots itself.

### Task C.3: SSH access

**Files:** none

- [ ] **Step 1: From your laptop, SSH in via mDNS**

```bash
ssh voice-chef@voice-chef-pi.local
```

Expected: shell prompt without password (key-based auth from Imager). If mDNS doesn't resolve, find the Pi's IP from your router's admin panel and `ssh voice-chef@<ip>` instead.

### Task C.4: OS sanity checks

**Files:** none

- [ ] **Step 1: Verify OS, arch, hostname**

```bash
cat /etc/os-release | head -3
uname -m
hostname
```

Expected:
- `PRETTY_NAME` includes "Trixie" or "Debian 13"
- `aarch64`
- `voice-chef-pi`

- [ ] **Step 2: Check available disk and RAM**

```bash
df -h /
free -h
```

Expected: at least ~20 GB free disk, ~7.5 GB total RAM.

- [ ] **Step 3: Run system update**

```bash
sudo apt update
sudo apt full-upgrade -y
```

Expected: completes without errors. May take 5–15 minutes depending on network.

- [ ] **Step 4: Reboot to apply kernel updates if any**

```bash
sudo reboot
```

Wait ~30s, then SSH back in.

---

## Phase D — Touchscreen and audio (M2 + M3)

### Task D.1: Touchscreen working

**Files:** none

- [ ] **Step 1: Look at the Pi**

The Pi OS desktop should be visible on the 7" panel.

- [ ] **Step 2: Test capacitive touch**

Tap and drag an icon on the desktop. Tap a menu. Confirm it's responsive.

- [ ] **Step 3: Decide orientation (portrait or landscape)**

Default is landscape (1280×720). For most kitchen mounts landscape is fine. Decide before continuing.

### Task D.2: Set rotation if needed

**Files:**
- Modify: `/boot/firmware/config.txt` (only if rotating)

- [ ] **Step 1: If keeping landscape, skip to D.3**

- [ ] **Step 2: For 90° (portrait)**

```bash
sudo sed -i.bak '/^display_rotate=/d' /boot/firmware/config.txt
echo 'display_rotate=1' | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

(Wait, SSH back in.)

- [ ] **Step 3: Confirm orientation**

Look at the screen — orientation matches the chosen value. Touch coordinates also rotate (single-tap on a corner icon should still hit it).

### Task D.3: XVF3800 detected by PipeWire

**Files:** none

- [ ] **Step 1: Confirm USB enumeration**

```bash
lsusb | grep -i XMOS
```

Expected: line containing `XMOS` and `XVF3800`. If nothing, re-seat the USB cable in a blue port.

- [ ] **Step 2: List audio sources**

```bash
wpctl status | grep -A 20 "Audio"
```

Expected: an `XMOS XVF3800 Voice Processor` (or similar) entry under "Sources."

- [ ] **Step 3: Note the source ID**

Find the line like `*  ID. node-name [vol]` under Sources. The leading `ID.` (e.g., `42.`) is what you'll use in the next step.

### Task D.4: Set XVF3800 as default source (live)

**Files:** none

- [ ] **Step 1: Set as default**

```bash
wpctl set-default <ID-from-D.3>
```

- [ ] **Step 2: Verify**

```bash
wpctl status | grep -A 5 "Audio" | grep -E "^\s+\*"
```

Expected: the `*` (default marker) is now next to XVF3800.

- [ ] **Step 3: Record + playback test**

```bash
arecord -d 5 -f cd /tmp/test.wav
aplay /tmp/test.wav
```

Speak into the XVF3800 during the 5-second record. Expected: playback is recognisable.

### Task D.5: Persist XVF3800 as default across reboots

**Files:**
- Create: `/etc/wireplumber/wireplumber.conf.d/51-xvf3800-default.conf`

- [ ] **Step 1: First, verify the regex in the drop-in matches the actual node name**

```bash
wpctl status | grep -i xmos
```

If the device name differs from `alsa_input.usb-XMOS_XVF3800*`, get the exact name with:

```bash
pactl list sources short | grep -i xmos
# or
wpctl inspect <ID-from-D.3> | grep node.name
```

If the actual name doesn't match the regex, edit `pi/wireplumber/51-xvf3800-default.conf` on your laptop, regenerate, and re-copy. (Likely the regex `~alsa_input.usb-XMOS_XVF3800.*` will match — XMOS device names are stable.)

- [ ] **Step 2: Clone the repo on the Pi (we need it now for the wireplumber config)**

```bash
git clone https://github.com/faramirezs/voice-chef.git ~/voice-chef
cd ~/voice-chef
git checkout kitchen-pi   # or main, once kitchen-pi is merged
```

- [ ] **Step 3: Install the drop-in**

```bash
sudo mkdir -p /etc/wireplumber/wireplumber.conf.d/
sudo cp ~/voice-chef/pi/wireplumber/51-xvf3800-default.conf /etc/wireplumber/wireplumber.conf.d/
systemctl --user restart wireplumber
```

- [ ] **Step 4: Reboot and verify persistence**

```bash
sudo reboot
```

After SSH back in:

```bash
wpctl status | grep -A 3 "Sources" | grep "^\s+\*"
```

Expected: `*` next to XMOS XVF3800. **This is the critical test** — if persistence doesn't work, the kiosk will pick the wrong mic on next boot.

---

## Phase E — Docker and Tailscale (M4 + M5)

### Task E.1: Install Docker

**Files:** none

- [ ] **Step 1: Run the official installer**

```bash
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
sudo sh /tmp/get-docker.sh
```

Expected: completes, Docker is installed and the daemon is started.

- [ ] **Step 2: Add `voice-chef` to the docker group**

```bash
sudo usermod -aG docker voice-chef
```

- [ ] **Step 3: Log out and SSH back in (group membership only takes effect on new sessions)**

```bash
exit
ssh voice-chef@voice-chef-pi.local
```

- [ ] **Step 4: Verify Docker works without sudo**

```bash
docker run --rm hello-world
```

Expected: "Hello from Docker!" message.

### Task E.2: Install Tailscale

**Files:** none

- [ ] **Step 1: Add the Tailscale repo and install**

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Expected: Tailscale installed via the official script (handles Trixie automatically).

### Task E.3: Generate a Tailscale auth key

**Files:** none (action in the Tailscale admin UI)

- [ ] **Step 1: Open the admin panel**

Navigate to https://login.tailscale.com/admin/settings/keys (in your laptop's browser).

- [ ] **Step 2: Generate a key**

Click "Generate auth key…" — choose:
- Reusable: yes (so you can re-flash without regenerating)
- Ephemeral: no
- Tags: leave blank (or add `tag:kitchen-pi` if you've configured ACLs)
- Expires in: 90 days (or longer if convenient)

Click "Generate" — copy the `tskey-auth-...` string.

### Task E.4: Bring Tailscale up on the Pi

**Files:** none

- [ ] **Step 1: `tailscale up` with the auth key**

```bash
sudo tailscale up --ssh --hostname=voice-chef-pi --authkey=<paste-the-tskey>
```

Expected: completes silently (no browser auth needed because we used the key).

- [ ] **Step 2: Verify status**

```bash
tailscale status
```

Expected: `voice-chef-pi` and `voice-chef-server` both listed; ages and online status visible.

- [ ] **Step 3: Verify reach to the server**

```bash
ping -c 3 voice-chef-server
```

Expected: pings 100.x.y.z, low-millisecond RTT typical for Tailscale on the same physical network.

- [ ] **Step 4: Verify the server's services are reachable from the Pi**

```bash
curl -fs http://voice-chef-server/api/recipes?limit=1
```

Expected: HTTP 401 with JSON body `{"detail":"Not authenticated"}` (the new auth wall — proves the path works).

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://voice-chef-server:8001/
```

Expected: `405` (agent allows POST only — 405 means the path is reachable).

---

## Phase F — Pi services (M6)

### Task F.1: Configure the Pi's runtime directory

**Files:**
- Create: `~/kitchen-pi/.env` (on the Pi)
- Use: `~/voice-chef/pi/docker-compose.yml`

- [ ] **Step 1: Create runtime layout**

```bash
mkdir -p ~/kitchen-pi
cp ~/voice-chef/pi/docker-compose.yml ~/kitchen-pi/
cp ~/voice-chef/pi/.env.example ~/kitchen-pi/.env
```

- [ ] **Step 2: Edit `.env` with real values**

```bash
nano ~/kitchen-pi/.env
```

Set:
```
SERVER_HOST=voice-chef-server
STT_MODEL=base
STT_LANGUAGE=
STT_DEVICE=cpu
```

- [ ] **Step 3: Verify compose config**

```bash
cd ~/kitchen-pi
docker compose config --quiet
```

Expected: exits cleanly. If it complains about missing variables, check the `.env` file.

### Task F.2: Build and start the Pi-side stack

**Files:** none

- [ ] **Step 1: Build the images on the Pi**

```bash
cd ~/kitchen-pi
docker compose build
```

Expected: kitchen-frontend builds (Vite build + nginx runtime; ~3-8 min on Pi 5), then stt builds (faster-whisper deps; ~2-5 min).

- [ ] **Step 2: Start the stack**

```bash
docker compose up -d
```

Expected: both containers come up.

- [ ] **Step 3: Wait for STT model download (first run)**

```bash
docker compose logs -f stt | grep -i "model\|loaded\|started"
```

Watch for "Model downloaded" or "Application startup complete." Press Ctrl+C when ready.

- [ ] **Step 4: Verify both services**

```bash
curl -fs http://localhost/ | head -5
curl -fs http://localhost:8002/health
```

Expected: HTML (kitchen-frontend) and `{"status":"ok"}` (stt).

- [ ] **Step 5: Verify the proxied paths reach the server**

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/api/recipes?limit=1
```

Expected: `401`. (Proves the proxy is reaching `voice-chef-server:80` — auth wall is the new normal.)

### Task F.3: First-time login flow on the Pi

**Files:** none — manual action in the Pi's browser

The kitchen-frontend now requires user login. We log in once as the `kitchen` user; the JWT cookie persists in the Chromium profile.

- [ ] **Step 1: Open kitchen-frontend in the Pi's desktop browser**

Tap on the Pi's desktop, open Chromium, navigate to `http://localhost`.

- [ ] **Step 2: Follow the login redirect**

Expected: redirect to the office-frontend login page (or an in-kitchen login page, depending on the auth flow). Email: `kitchen@voice-chef.local`, password: the one you set in Task A.4.

- [ ] **Step 3: After login, verify you land on the kitchen UI**

You should see the kitchen-frontend with whatever the post-login state is. If you see API errors, recheck Task A.4 and Task F.2 step 5.

- [ ] **Step 4: Verify the cookie persists**

```bash
docker compose -f ~/kitchen-pi/docker-compose.yml ps
```

Then quit + reopen Chromium (or just navigate away and back). The session should still be active without re-login.

(If the cookie does NOT persist after closing the browser: the kiosk in Phase G uses `--user-data-dir=/home/voice-chef/.kiosk-profile`, but for THIS step we're using the default Chromium profile. Either log in again here using a Chromium with the kiosk profile dir, OR plan to log in once after Phase G.)

---

## Phase G — Authentication persistence (post-PR-#183 work)

### Task G.1: Pre-warm the kiosk Chromium profile

The kiosk in Phase H launches Chromium with `--user-data-dir=/home/voice-chef/.kiosk-profile`. We must log in via THAT profile so cookies live where the kiosk will read them.

**Files:**
- Create: `/home/voice-chef/.kiosk-profile/` (created by Chromium first launch)

- [ ] **Step 1: Launch Chromium with the kiosk profile manually**

```bash
chromium-browser \
    --user-data-dir=/home/voice-chef/.kiosk-profile \
    --no-first-run \
    http://localhost
```

(Don't add `--kiosk` here — we want a normal window so we can interact with the login flow.)

- [ ] **Step 2: Log in as `kitchen@voice-chef.local`**

Same credentials as Task F.3.

- [ ] **Step 3: Verify the kitchen UI loads with valid auth**

The mic button, recipe browse — all should work.

- [ ] **Step 4: Close Chromium**

The cookie now lives in `/home/voice-chef/.kiosk-profile/Default/Cookies` and will be picked up when the kiosk relaunches.

### Task G.2: Document re-login flow

**Files:**
- Modify: `pi/README.md`

- [ ] **Step 1: Add a "When the cookie expires" section**

Append to `pi/README.md`:

```markdown
## When the kitchen user's cookie expires

The kitchen UI redirects to login. Either:

1. **Touchscreen re-login:** tap the email/password fields on the login page; on-screen keyboard appears (if not, install `squeekboard` and configure auto-show). Re-enter `kitchen@voice-chef.local` + password.

2. **Remote re-login** (faster for an admin):

   ```bash
   ssh voice-chef@voice-chef-pi
   chromium-browser --user-data-dir=/home/voice-chef/.kiosk-profile http://localhost
   # log in via the SSH-tunneled X11/Wayland forward, or use rpi-connect to drive the screen remotely
   ```

3. **Future improvement:** lengthen JWT expiry on the server (in `backend/app/api/routes/auth.py`), or wire a "remember me" toggle that issues a long-lived cookie for the kitchen user.
```

- [ ] **Step 2: Commit**

```bash
cd ~/voice-chef
git add pi/README.md
git commit -m "pi: document kitchen user re-login flow when cookie expires"
```

---

## Phase H — End-to-end smoke test (M7)

### Task H.1: Voice query through the agent

**Files:** none

- [ ] **Step 1: From the Pi's desktop browser, open `http://localhost`**

Cookie should already be set from Task G.1.

- [ ] **Step 2: Open DevTools → Network tab → preserve log**

(F12 in Chromium → Network.)

- [ ] **Step 3: Tap the mic button and speak: "Show me something with chickpeas"**

- [ ] **Step 4: Watch the Network tab for the trajectory**

Expected:
- `POST /transcribe` to `localhost:8002` → 200, response includes `text` field with the transcript
- `POST /agent/...` → SSE stream with `RUN_STARTED`, `TOOL_CALL_START` (search_recipes), `TOOL_CALL_RESULT` (recipes.list), `TOOL_CALL_START` (get_recipe_detail), `RUN_FINISHED`
- A recipe card should render in the kitchen UI's canvas (`Hummus Bowl` if the corpus matches the design's reference data)

- [ ] **Step 5: If anything fails, capture logs**

```bash
docker compose -f ~/kitchen-pi/docker-compose.yml logs --tail 50 stt
```

Common failure modes and fixes:
- `RUN_ERROR` with 401 → re-do Task G.1 (cookie missing/expired)
- STT returns empty text → check XVF3800 is the default mic (`wpctl status`)
- Network timeout to `voice-chef-server` → check Tailscale (`tailscale ping voice-chef-server`)

---

## Phase I — Kiosk autostart (M8)

### Task I.1: Install the systemd unit and startup script on the Pi

**Files:**
- Modify: `/etc/systemd/system/kitchen-point.service`
- Modify: `/usr/local/bin/kitchen-point-start.sh`

- [ ] **Step 1: Install both files**

```bash
sudo cp ~/voice-chef/pi/systemd/kitchen-point.service /etc/systemd/system/
sudo cp ~/voice-chef/pi/scripts/kitchen-point-start.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/kitchen-point-start.sh
```

- [ ] **Step 2: Verify the service definition**

```bash
sudo systemctl daemon-reload
systemctl cat kitchen-point.service
```

Expected: shows the unit file content.

### Task I.2: Test the startup script manually first

**Files:** none

- [ ] **Step 1: Stop any running compose stack**

```bash
cd ~/kitchen-pi && docker compose down
```

- [ ] **Step 2: Run the startup script directly**

```bash
/usr/local/bin/kitchen-point-start.sh
```

Expected: Compose stack comes up, "kitchen-frontend ready after Ns" log line appears, then Chromium launches in kiosk mode on the touchscreen.

- [ ] **Step 3: Press Ctrl+C in the SSH session**

Chromium dies, but the Compose stack remains running (that's fine — `docker compose up -d` is detached; the script's foreground process is just Chromium).

### Task I.3: Enable the systemd service

**Files:** none

- [ ] **Step 1: Enable + start**

```bash
sudo systemctl enable --now kitchen-point.service
```

- [ ] **Step 2: Check status**

```bash
sudo systemctl status kitchen-point.service
```

Expected: `Active: active (running)`. Chromium should be on the touchscreen in kiosk mode.

### Task I.4: Reboot and verify autostart

**Files:** none

- [ ] **Step 1: Reboot**

```bash
sudo reboot
```

- [ ] **Step 2: Wait 60 seconds, then look at the touchscreen**

Expected: kiosk Chromium showing the kitchen UI fullscreen, no terminal/desktop visible. Cookie still valid → no login prompt.

- [ ] **Step 3: Tap mic, speak a query, verify recipe renders**

(Same trajectory as Task H.1.)

### Task I.5: Crash recovery test

**Files:** none

- [ ] **Step 1: SSH in and kill Chromium**

```bash
ssh voice-chef@voice-chef-pi
pkill chromium
```

- [ ] **Step 2: Watch the touchscreen**

Expected: brief black screen, then Chromium relaunches within ~10 seconds (systemd's `Restart=on-failure RestartSec=10`).

- [ ] **Step 3: Verify the kitchen UI is live again**

Tap the screen, exercise the UI.

---

## Phase J — Phase 1 acceptance (M9)

### Task J.1: Run the sanity-check suite from the spec

**Files:** none

- [ ] **Step 1: From your laptop, run all six checks from the spec's Verification plan**

```bash
ping voice-chef-pi.local
tailscale ping voice-chef-pi
ssh voice-chef@voice-chef-pi 'wpctl status | grep -A2 "Audio/Source"'
ssh voice-chef@voice-chef-pi 'docker compose -f kitchen-pi/docker-compose.yml ps'
ssh voice-chef@voice-chef-pi 'systemctl status kitchen-point.service'
ssh voice-chef@voice-chef-pi 'curl -fs http://localhost:8002/health'
```

All six should return clean output.

### Task J.2: Failure-mode rehearsal

**Files:** none

- [ ] **Step 1: Power-cycle test**

Unplug the Pi for 10s, plug back in. Expect: kiosk live within 60s, recipe card render works on first voice query.

- [ ] **Step 2: Server-down test**

On the server: `docker compose stop backend agent`. Wait 30s. On the Pi, attempt a voice query.

Expected: STT still works (returns transcript). Agent call fails visibly. Recipe browse via the kitchen UI fails with an error state. **This is the documented Phase-2-fallback gap.**

Restart the server stack: `docker compose start backend agent`. Pi should resume working without intervention.

- [ ] **Step 3: Network-flap test**

On the Pi:
```bash
sudo nmcli radio wifi off
sleep 30
sudo nmcli radio wifi on
```

Expected: Tailscale reconnects within 10s (`tailscale status` shows "online" again). Voice queries resume working.

- [ ] **Step 4: Chromium-crash test**

`ssh voice-chef@voice-chef-pi 'pkill chromium'`. Expected: relaunches in ~10s.

### Task J.3: Document quirks discovered during install

**Files:**
- Modify: `pi/README.md`

- [ ] **Step 1: Add a "Quirks" section to `pi/README.md` with anything that surprised you**

Examples to capture if relevant:
- Touchscreen orientation chosen
- Whether the wireplumber regex needed tweaking for the actual XVF3800 device name
- Wi-Fi credentials lifecycle (e.g., "phone hotspot during eval, home Wi-Fi during dev")
- Tailscale auth key expiry note
- Re-login frequency and whether the JWT lifetime needs adjustment for kitchen use

- [ ] **Step 2: Commit**

```bash
cd ~/voice-chef
git add pi/README.md
git commit -m "pi: document install-time quirks"
```

### Task J.4: Push the kitchen-pi branch

**Files:** none

- [ ] **Step 1: Push**

```bash
git push -u origin kitchen-pi
```

- [ ] **Step 2: Open PR (or save for later)**

When ready, `gh pr create` against `main`. The PR brings: spec, plan, `pi/` artifacts, and the env-templated kitchen-frontend.

---

## Self-review (filled in inline)

**Spec coverage:** every milestone M1–M9 from `docs/kitchen-pi-design.md` maps to tasks in Phases C–J. Phase A (server preflight) and B (repo prep) are net-additions to make the plan actually executable. Phase G (auth persistence) was added because PR #183 changed the auth model; it's not in the spec but is implied by it (mentioned as "Tailscale and auth-related env" in §5).

**Placeholder scan:** every code/config block contains the actual content. No "TBD", "TODO", or "fill in later" left in the body. The only deliberate vagueness is in Task J.3 ("document quirks"), which can only be filled in during install.

**Type/name consistency:**
- `voice-chef` user, `voice-chef-pi` hostname, `voice-chef-server` Tailscale hostname — consistent across all phases.
- `SERVER_HOST` env var name — consistent.
- `kitchen-point.service` systemd unit name — consistent.
- The wireplumber regex `~alsa_input.usb-XMOS_XVF3800.*` — assumed to match; D.5 includes a fallback for if it doesn't.
- Task A.4's user email `kitchen@voice-chef.local` — referenced consistently in F.3 and G.1.

**Scope:** focused on Phase 1 only. Phase 2 (offline fallback, wake word, voice ID) is explicitly NOT in this plan — those are separate plans when the time comes.

---

## Execution

Plan complete and saved to `docs/superpowers/plans/2026-05-04-kitchen-pi.md` (local) and `docs/kitchen-pi-plan.md` (committed once Phase B.9 runs).

**Two execution options:**

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints

A complication for this particular plan: many tasks are physical actions on the Pi that the human must do (insert SD card, plug in cables, walk over to the touchscreen). These can't be automated. The "implementer" for this plan is partly an agent (for repo-prep tasks B.x and any post-install scripting) and partly the human (for everything in C–J). A reasonable split:

- Phase A + Phase B → agent or human, both work
- Phase C–J → human, with agent assistance for individual command verification

Which approach do you want?
