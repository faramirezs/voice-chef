#!/bin/bash
# Voice Chef — Pi teardown.
#
# Returns the Pi to a clean state — only Tailscale will be running after this.
# Run manually whenever you want to start fresh from the login screen.
#
# Wipes:
#   - The Chromium kiosk profile (cookie, localStorage, IndexedDB, cache)
#   - The local containers (STT + stt-tls); the named volumes (whisper
#     model cache) are intentionally kept so the next start-kitchen.sh
#     doesn't have to re-download ~250 MB. To wipe them too, follow up
#     with `docker compose down --volumes` from pi/.
#   - The auto-start of the kiosk systemd unit
#
# Does NOT touch:
#   - Tailscale (its own systemd unit, always-on)
#   - The repo, .env, ssl/ certificates, or any committed config
#
# After this script, the Pi is back to "freshly-provisioned" state and
# ready for start-kitchen.sh to run again.

set -euo pipefail

KIOSK_PROFILE_DIR="/home/voice-chef/.kiosk-profile"
COMPOSE_DIR="/home/voice-chef/voice-chef/pi"

echo "[reset-kitchen] disabling kiosk autostart + stopping it"
sudo systemctl disable --now kitchen-point.service 2>/dev/null || true

# In case Chromium is still running for any reason.
pkill chromium 2>/dev/null || true

echo "[reset-kitchen] wiping kiosk profile (${KIOSK_PROFILE_DIR})"
rm -rf "$KIOSK_PROFILE_DIR"

echo "[reset-kitchen] tearing down Pi-local containers"
cd "$COMPOSE_DIR"
docker compose down

cat <<'EOF'

[reset-kitchen] done.
  - Kiosk autostart disabled; reboot now will leave the Pi at a desktop.
  - Run start-kitchen.sh to bring everything back up for a new session.
EOF
