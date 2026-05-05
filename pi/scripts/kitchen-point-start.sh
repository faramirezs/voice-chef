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

COMPOSE_DIR="/home/voice-chef/voice-chef/pi"
KIOSK_URL="http://localhost/?kiosk=1"
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
# Flag rationale:
#   --kiosk                              fullscreen, no window chrome, no tab UI
#   --no-first-run / --noerrdialogs      skip welcome modal & restore-session prompts
#   --disable-restore-session-state      don't show the "restore tabs" prompt after a crash
#   --disable-features=TranslateUI       no auto-translate prompt
#   --autoplay-policy=no-user-gesture-required  agent SSE / chime sounds work without a click
#   --use-fake-ui-for-media-stream       auto-grant getUserMedia (mic) without a permission prompt
#   --password-store=basic               use a plaintext local store, never block on gnome-keyring
#   --user-data-dir=$KIOSK_PROFILE_DIR   persistent profile so cookies/localStorage survive reboots
#   --start-maximized                    starts at the display's full size (kiosk does this anyway)
#   --ozone-platform=wayland             use Wayland directly (Pi OS Trixie session is Wayland);
#                                        without this, Chromium falls back to X11 and fails under
#                                        systemd because there's no DISPLAY.
#   --force-device-scale-factor=1.5      scale the whole UI 1.5× for the 7" touch display.
#                                        Iterate this number live (edit + restart service) until
#                                        the kitchen feels right; a proper touch-targeted UI
#                                        redesign is a separate workstream.
exec chromium \
    --kiosk \
    --ozone-platform=wayland \
    --force-device-scale-factor=1.5 \
    --no-first-run \
    --noerrdialogs \
    --disable-restore-session-state \
    --disable-features=TranslateUI \
    --autoplay-policy=no-user-gesture-required \
    --use-fake-ui-for-media-stream \
    --password-store=basic \
    --user-data-dir="$KIOSK_PROFILE_DIR" \
    --start-maximized \
    "$KIOSK_URL"
