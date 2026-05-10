# Kitchen-Pi

The kitchen-pi is a Raspberry Pi 5 with a 7" touch display and a ReSpeaker
microphone, running as a kiosk against the voice-chef server's kitchen UI
over Tailscale.

## What runs on the Pi

| Component | Where |
|---|---|
| Chromium kiosk | `kitchen-point.service` (systemd) |
| faster-whisper STT | `stt` container (`pi/docker-compose.yml`) |
| TLS shim in front of STT | `stt-tls` container, exposes `https://localhost/stt/...` |
| Bring-back-kiosk launcher | `pi/desktop/bring-back-kiosk.desktop` (XDG icon) |
| Audio routing | `pi/wireplumber/51-respeaker-default.conf` |
| Polkit rule (`systemctl restart` without sudo) | `pi/polkit/50-kitchen-kiosk.rules` |
| Tailscale | system service, always on (provisioned outside this repo) |

What does **not** run on the Pi: the kitchen frontend SPA itself. It's
served by the server at `https://${SERVER_HOST}/kitchen/`. The PWA service
worker handles offline shell + catalog cache; we don't need a parallel
Pi-side deployment. See `docs/pwa.md` for the rationale and `docs/kitchen-pi.md`
for the full module narrative.

## First-time setup

These steps are run once on a fresh Pi. They produce a Pi that, when
booted, brings up Tailscale only — nothing else auto-starts until
`start-kitchen.sh` is run.

### 1. Pi OS install

Use Raspberry Pi Imager to flash Pi OS Trixie (Wayland session).

### 2. Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Verify the Pi can reach the server:

```bash
ping -c1 $SERVER_HOST     # whatever Tailscale name your server has
curl -k https://$SERVER_HOST/api/health
```

### 3. Docker + Compose plugin

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker voice-chef
# Log out/in once for the group change to take effect.
```

### 4. Repo + scripts

The Pi only needs `pi/` and `stt/` from the repo — everything else (backend,
agent, rag, frontend, docs) is dead weight on a kiosk device. Use a sparse
+ partial clone so only those two directories actually land on disk:

```bash
git clone --no-checkout --filter=blob:none <repo-url> /home/voice-chef/voice-chef
cd /home/voice-chef/voice-chef
git sparse-checkout init --cone
git sparse-checkout set pi stt
git checkout main

cd pi
cp .env.example .env
$EDITOR .env                              # set SERVER_HOST

sudo install -m 755 scripts/kitchen-point-start.sh /usr/local/bin/
sudo install -m 644 systemd/kitchen-point.service /etc/systemd/system/
sudo install -m 644 polkit/50-kitchen-kiosk.rules /etc/polkit-1/rules.d/
mkdir -p ~/.config/wireplumber/main.lua.d
install -m 644 wireplumber/51-respeaker-default.conf \
    ~/.config/wireplumber/main.lua.d/

# Desktop launcher (file manager may show "Execute / Mark trusted" prompt
# the first time; click through once and the icon persists).
install -m 755 desktop/bring-back-kiosk.desktop ~/Desktop/
gio set ~/Desktop/bring-back-kiosk.desktop metadata::trusted true
```

### 5. Reboot

```bash
sudo reboot
```

After this, the Pi boots to a desktop. Tailscale is up. Nothing else
runs automatically until you bring it up.

## Bringing the kitchen up

SSH in (or open a terminal on the Pi) and run:

```bash
cd /home/voice-chef/voice-chef/pi
./scripts/start-kitchen.sh
```

The script:
1. Generates a self-signed cert for the Pi-local STT TLS shim (first run only)
2. Brings up the STT + stt-tls containers
3. Waits for STT to respond
4. Enables and starts `kitchen-point.service`

Chromium launches into kiosk mode and lands on the login page. Authenticate
with the kitchen-device credentials. The JWT cookie persists in
`/home/voice-chef/.kiosk-profile` across reboots, so subsequent reboots
relaunch the kiosk already logged in — until the cookie expires or the
profile is wiped.

## Tearing down

```bash
cd /home/voice-chef/voice-chef/pi
./scripts/reset-kitchen.sh
```

This:
- Disables and stops `kitchen-point.service`
- Wipes `/home/voice-chef/.kiosk-profile` (cookie, localStorage, cache)
- Tears down the Pi-local containers and their volumes
- Leaves Tailscale, the repo, the `.env`, and the cert in place

After this the Pi is back to "freshly-provisioned" state.

## Bring-back-kiosk launcher

The `bring-back-kiosk.desktop` icon on the desktop runs
`systemctl restart kitchen-point.service` (allowed without sudo via the
polkit rule). Useful when an operator hits Alt+F4 with greasy hands and
needs to recover without touching a keyboard.

## Why this layout

For the architectural rationale — why we removed the Pi-side
kitchen-frontend container, why STT stays on the Pi, why the Pi
authenticates as a kitchen-role user manually rather than via auto-login —
see `docs/kitchen-pi.md`.
