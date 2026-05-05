#!/bin/bash
# Voice Chef — Kitchen Point startup script.
#
# Invoked by /etc/systemd/system/kitchen-point.service on boot.
#
# Steps:
#   1. Bring up the Pi-side Compose stack (kitchen-frontend + stt)
#   2. Wait for kitchen-frontend to respond
#   3. Launch Chromium in kiosk mode against http://localhost
#
# Chromium uses a persistent --user-data-dir so the kitchen user's login
# cookie survives reboots.

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
