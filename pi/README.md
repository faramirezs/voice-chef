# Voice Chef — Kitchen Pi

Phase-1 deployment artifacts for running the kitchen point on a Raspberry Pi 5 + 7" Touch Display 2 + reSpeaker XVF3800 4-Mic Array.

## What this directory contains

| Path | Purpose |
|---|---|
| `docker-compose.yml` | Pi-only Compose stack: kitchen-frontend + stt |
| `.env.example` | Template for `.env` — copy and fill in `SERVER_HOST`, etc. |
| `systemd/kitchen-point.service` | systemd unit that auto-starts the kitchen point on boot |
| `scripts/kitchen-point-start.sh` | Startup script invoked by the systemd unit |
| `wireplumber/51-respeaker-default.conf` | WirePlumber drop-in to pin the reSpeaker XVF3800 as the default audio source |

## Architecture in one paragraph

The Pi runs the kitchen UI (kitchen-frontend), audio capture (XVF3800 → PipeWire → browser `MediaRecorder`), and STT (faster-whisper) locally. The agent, backend, db, rag, and qdrant run on a separate **server** reachable from the Pi via Tailscale. One env var (`SERVER_HOST`) configures where the server lives. See [`docs/kitchen-pi-design.md`](../docs/kitchen-pi-design.md) for full architectural rationale.

## Quick reference — first install on a fresh Pi

After Pi imaging, audio routing, Docker, and Tailscale are in place (see [`docs/kitchen-pi-plan.md`](../docs/kitchen-pi-plan.md) for the full sequence):

```bash
# Clone the repo on the Pi — this directory IS the runtime location
git clone https://github.com/faramirezs/voice-chef.git ~/voice-chef
cd ~/voice-chef/pi

# Configure
cp .env.example .env
$EDITOR .env                                  # SERVER_HOST, SERVER_TAILSCALE_IP,
                                              # KITCHEN_EMAIL, KITCHEN_PASSWORD, etc.

# Bring up the Pi-only stack (kitchen-frontend + stt)
docker compose up -d --build

# Install audio config (WirePlumber drop-in)
sudo mkdir -p /etc/wireplumber/wireplumber.conf.d/
sudo cp ~/voice-chef/pi/wireplumber/51-respeaker-default.conf /etc/wireplumber/wireplumber.conf.d/
systemctl --user restart wireplumber

# Install kiosk autostart
sudo install -m 0755 ~/voice-chef/pi/scripts/kitchen-point-start.sh /usr/local/bin/
sudo install -m 0644 ~/voice-chef/pi/systemd/kitchen-point.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kitchen-point.service

# Install kiosk-recovery launcher
# (polkit rule lets voice-chef restart the kiosk without sudo password;
#  desktop icon gives a one-click "bring kiosk back" after Alt+F4)
sudo install -m 0644 ~/voice-chef/pi/polkit/50-kitchen-kiosk.rules /etc/polkit-1/rules.d/
sudo systemctl restart polkit
cp ~/voice-chef/pi/desktop/bring-back-kiosk.desktop ~/Desktop/
chmod +x ~/Desktop/bring-back-kiosk.desktop
gio set ~/Desktop/bring-back-kiosk.desktop metadata::trusted true
```

Note: the file manager may show an "Execute file" confirmation dialog on the first double-click of the Voice-Chef icon; choose **Execute**. Some Pi OS Trixie file managers ignore the gio trust flag and the dialog reappears each time — clicking Execute remains a one-click recovery.

After `enable --now`, the Pi will:
1. Bring up the Compose stack (kitchen-frontend on port 80, stt on 8002).
2. Wait for the kitchen-frontend to respond.
3. Launch Chromium in fullscreen kiosk mode against `http://localhost`.

On every subsequent boot, the same flow runs automatically.

## Updating the kitchen-frontend on the Pi

After making changes on your laptop and pushing to the branch the Pi tracks:

```bash
ssh voice-chef@voice-chef-pi
cd ~/voice-chef
git pull
cd pi
docker compose up -d --build --force-recreate kitchen-frontend
# If kiosk autostart is installed and the Compose change should also reload Chromium:
sudo systemctl restart kitchen-point.service
```

## When the kitchen user's cookie expires

In normal operation the kitchen-pi auto-authenticates on each page load via `KITCHEN_EMAIL` / `KITCHEN_PASSWORD` (see `frontend/kitchen/src/lib/auth.ts:tryKitchenLogin`). If you reboot, hard-refresh, or close & reopen Chromium, the silent re-login runs again — no user action needed.

If a JWT expires *mid-session* (60-hour token lifetime), the running SPA hits a 401 mid-stream and the user sees an error toast. Workarounds:

1. **Refresh the page** (touchscreen → swipe-down or `F5` over SSH) — bootstrap silently re-logs in.
2. **Restart the kiosk service** to clear any stale state:

   ```bash
   ssh voice-chef@voice-chef-pi
   sudo systemctl restart kitchen-point.service
   ```

3. **Future improvement:** make the kitchen frontend silently re-login on mid-session 401 (currently only the initial-load 401 triggers `tryKitchenLogin`).

## Quirks captured during install

(Filled in as discovered during the actual Pi setup.)

- **reSpeaker XVF3800 device name:** the Seeed Studio variant enumerates as `Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_*` in PipeWire (USB vendor ID `2886`), not the bare-XMOS naming. The wireplumber drop-in regex matches this prefix.
- **`arecord` without `-D`:** fails on Pi OS Trixie because the legacy ALSA default-route isn't bridged to PipeWire. Browser MediaRecorder uses PipeWire directly and is unaffected. For command-line testing, use `arecord -D plughw:2,0` (or whatever card index the reSpeaker enumerates as).
- **Squeekboard auto-launches** on Pi OS Trixie Desktop via `/etc/xdg/autostart/squeekboard.desktop`. Disabling the systemd user service alone is insufficient — also create a user-level autostart override at `~/.config/autostart/squeekboard.desktop` with `Hidden=true` and `X-GNOME-Autostart-enabled=false`.
