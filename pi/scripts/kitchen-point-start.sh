#!/bin/bash
# Voice Chef — Kitchen Point kiosk launcher.
#
# Invoked by /etc/systemd/system/kitchen-point.service. The systemd unit is
# enabled by start-kitchen.sh at setup and disabled by reset-kitchen.sh.
# While enabled, this script runs:
#   - on initial start (`systemctl start kitchen-point.service`)
#   - on every reboot (because the unit is in graphical.target)
#
# Containers (STT + stt-tls) come up via their `restart: unless-stopped`
# policy on the same boot — we don't bring them up here, that's
# start-kitchen.sh's job.

set -euo pipefail

ENV_FILE="/home/voice-chef/voice-chef/pi/.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

KIOSK_URL="https://${SERVER_HOST}/kitchen/?kiosk=1"
KIOSK_PROFILE_DIR="/home/voice-chef/.kiosk-profile"

# Wait for the server to be reachable before launching Chromium.
# Without this, on a fresh boot Chromium can race ahead of Tailscale/network
# readiness — the SPA's first /api/auth/me call fails with a network error
# (treated identically to 401 by getCurrentUser), the SPA redirects to
# /login, and the login page sees a valid cookie and bounces to office root.
# Net effect: kiosk lands on the office start page instead of /kitchen/.
echo "[kitchen-point] $(date -Iseconds) — waiting for ${SERVER_HOST} to respond"
for i in $(seq 1 60); do
    if curl -kfsS --max-time 3 "https://${SERVER_HOST}/kitchen/" >/dev/null 2>&1; then
        echo "[kitchen-point] server reachable after ${i}×2s"
        break
    fi
    sleep 2
done

echo "[kitchen-point] $(date -Iseconds) — launching Chromium kiosk → ${KIOSK_URL}"

# --ignore-certificate-errors accepts both the server's self-signed cert
# (perimeter HTTPS via nginx-proxy) and the Pi-local self-signed cert
# (https://localhost/stt/...).
exec chromium \
    --kiosk \
    --ignore-certificate-errors \
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
