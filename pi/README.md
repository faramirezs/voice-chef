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
# Clone the repo on the Pi
git clone https://github.com/faramirezs/voice-chef.git ~/voice-chef
cd ~/voice-chef

# Set up the runtime directory
mkdir -p ~/kitchen-pi
cp pi/docker-compose.yml ~/kitchen-pi/
cp pi/.env.example ~/kitchen-pi/.env
$EDITOR ~/kitchen-pi/.env                     # set SERVER_HOST etc.

# Bring up the stack
cd ~/kitchen-pi
docker compose up -d

# Install autostart + audio config
sudo cp ~/voice-chef/pi/systemd/kitchen-point.service /etc/systemd/system/
sudo cp ~/voice-chef/pi/scripts/kitchen-point-start.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/kitchen-point-start.sh
sudo mkdir -p /etc/wireplumber/wireplumber.conf.d/
sudo cp ~/voice-chef/pi/wireplumber/51-respeaker-default.conf /etc/wireplumber/wireplumber.conf.d/
sudo systemctl daemon-reload
sudo systemctl enable --now kitchen-point.service
```

## Updating the kitchen-frontend on the Pi

After making changes on your laptop and pushing to the branch the Pi tracks:

```bash
ssh voice-chef@voice-chef-pi
cd voice-chef
git pull
cd ~/kitchen-pi
docker compose pull        # if images come from a registry
# OR
docker compose build       # if building locally
docker compose up -d
```

## When the kitchen user's cookie expires

The kitchen UI redirects to login. Two recovery paths:

1. **Touchscreen re-login:** tap the email/password fields; on-screen keyboard appears (install `squeekboard` if not already present). Re-enter `kitchen@voice-chef.local` + password.
2. **Remote re-login** (faster for an admin):

   ```bash
   ssh voice-chef@voice-chef-pi
   chromium-browser --user-data-dir=/home/voice-chef/.kiosk-profile http://localhost
   # log in via SSH-tunneled X11/Wayland, or use rpi-connect to drive the screen
   ```

3. **Future improvement:** lengthen JWT expiry on the server, or wire a "remember me" toggle for the kitchen user.

## Quirks captured during install

(Filled in as discovered during the actual Pi setup.)

- **reSpeaker XVF3800 device name:** the Seeed Studio variant enumerates as `Seeed_Studio_reSpeaker_XVF3800_4-Mic_Array_*` in PipeWire (USB vendor ID `2886`), not the bare-XMOS naming. The wireplumber drop-in regex matches this prefix.
- **`arecord` without `-D`:** fails on Pi OS Trixie because the legacy ALSA default-route isn't bridged to PipeWire. Browser MediaRecorder uses PipeWire directly and is unaffected. For command-line testing, use `arecord -D plughw:2,0` (or whatever card index the reSpeaker enumerates as).
- **Squeekboard auto-launches** on Pi OS Trixie Desktop via `/etc/xdg/autostart/squeekboard.desktop`. Disabling the systemd user service alone is insufficient — also create a user-level autostart override at `~/.config/autostart/squeekboard.desktop` with `Hidden=true` and `X-GNOME-Autostart-enabled=false`.
