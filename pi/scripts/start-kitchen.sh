#!/bin/bash
# Voice Chef — Pi setup / session bootstrap.
#
# Run once after SSH-ing into a fresh Pi to bring everything up:
#   1. Generate the self-signed cert for the Pi-local STT TLS shim if missing
#   2. Bring up local containers (STT + stt-tls) via docker compose
#   3. Wait for STT to respond
#   4. Enable + start the kiosk systemd unit
#
# After this runs once:
#   - The kiosk launches Chromium against the server's kitchen URL
#   - The login page renders; authenticate with the kitchen-device credentials
#   - The JWT cookie persists in --user-data-dir across reboots
#   - On reboot, containers auto-restart (unless-stopped) and systemd brings
#     the kiosk back automatically; no human interaction needed
#
# To tear everything back to a clean state, run reset-kitchen.sh.

set -euo pipefail

REPO_DIR="/home/voice-chef/voice-chef"
COMPOSE_DIR="${REPO_DIR}/pi"
ENV_FILE="${COMPOSE_DIR}/.env"
CERT_DIR="${COMPOSE_DIR}/ssl"
HEALTH_TIMEOUT=60

if [ ! -f "$ENV_FILE" ]; then
    echo "[start-kitchen] ERROR: ${ENV_FILE} missing." >&2
    echo "[start-kitchen] Copy ${COMPOSE_DIR}/.env.example to .env and edit SERVER_HOST." >&2
    exit 1
fi

# 1. Self-signed cert for the Pi-local STT TLS shim.
# The Pi has openssl by default; generating on the host is simpler than
# pulling openssl into the nginx:alpine image at runtime.
if [ ! -f "${CERT_DIR}/localhost.crt" ]; then
    mkdir -p "$CERT_DIR"
    openssl req -x509 -nodes -newkey rsa:2048 \
        -keyout "${CERT_DIR}/localhost.key" \
        -out   "${CERT_DIR}/localhost.crt" \
        -days 3650 \
        -subj "/CN=localhost" \
        -addext "subjectAltName=DNS:localhost"
    chmod 600 "${CERT_DIR}/localhost.key"
    echo "[start-kitchen] generated self-signed cert for Pi-local STT"
fi

# 2. Bring up Pi-local containers.
echo "[start-kitchen] starting Pi-local stack (STT + TLS shim)"
cd "$COMPOSE_DIR"
docker compose up -d

# 3. Wait for STT to be reachable through the TLS shim.
echo "[start-kitchen] waiting up to ${HEALTH_TIMEOUT}s for STT"
for i in $(seq 1 "$HEALTH_TIMEOUT"); do
    if curl -fks --max-time 2 https://localhost/stt/health > /dev/null 2>&1; then
        echo "[start-kitchen] STT healthy after ${i}s"
        break
    fi
    sleep 1
done

if ! curl -fks --max-time 2 https://localhost/stt/health > /dev/null 2>&1; then
    echo "[start-kitchen] WARNING: STT did not become healthy in ${HEALTH_TIMEOUT}s" >&2
    echo "[start-kitchen] Continuing anyway — kiosk will launch but voice may be unavailable" >&2
fi

# 4. Enable + start the kiosk systemd unit. `enable --now` does both:
# starts immediately AND wires WantedBy=graphical.target so reboots
# bring it back. reset-kitchen.sh undoes this.
echo "[start-kitchen] enabling + starting kitchen-point.service"
sudo systemctl enable --now kitchen-point.service

cat <<'EOF'

[start-kitchen] done.
  - Chromium kiosk should be launching against the server's kitchen URL.
  - On the login screen, authenticate with the kitchen-device credentials.
  - The cookie persists across reboots in /home/voice-chef/.kiosk-profile.
  - Run reset-kitchen.sh to wipe state and disable autostart.
EOF
