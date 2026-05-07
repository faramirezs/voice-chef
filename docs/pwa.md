# Progressive Web App (PWA) — Voice Chef Kitchen

## Subject Requirement

> "Minor: Progressive Web App (PWA) with offline support and installability."

## What's Implemented

The kitchen-frontend (`frontend/kitchen`) is now a PWA:

- **Web App Manifest** at `/manifest.webmanifest` declares the app's identity, icons, theme, and display mode (`standalone` — runs without browser chrome once installed).
- **Service Worker** at `/sw.js` (Workbox-generated) precaches the app shell — HTML, JS, CSS, icons, manifest — so the kitchen UI loads even when the device is offline.
- **Icons** at `/icons/` cover the standard PWA size set: 192×192, 512×512, a 512×512 maskable variant for Android adaptive icons, and an Apple touch icon for iOS home-screen install.

## Architecture

`vite-plugin-pwa` (which wraps Workbox) generates the service worker at build time from a glob of static assets in `dist/`. Registration is auto-injected into `index.html` by the plugin — no manual SW boilerplate in our source code. The service worker runs `autoUpdate`: a new build is picked up on the next page load (skip-waiting + clients-claim).

### Caching strategy

| Path pattern | Strategy | Reason |
|---|---|---|
| `/`, `/assets/*`, `/icons/*`, `/manifest.webmanifest`, `/sw.js` | Precache (cache-first, hash-busted at build) | App shell must work offline |
| `/api/recipes`, `/api/recipes/{id}`, `/api/ingredients`, `/api/ingredients/autocomplete` | StaleWhileRevalidate (7-day TTL, 500-entry cap) | Read-only catalog data — serve cached copy instantly when offline, refresh in background when online |
| `/api/auth/*`, other `/api/*` | NetworkOnly | Auth-sensitive, dynamic — caching breaks correctness |
| `/agent/*` | NetworkOnly | SSE streams cannot be cached |
| `/stt/*` | NetworkOnly | POST uploads with audio bodies |
| `/uploads/*` | NetworkOnly | User-scoped, auth-sensitive |
| `/config.js` | NetworkOnly | Generated at container startup, not by Vite — must always be fresh |

The recipe/ingredient SWR layer means a user who's loaded the catalog while online can browse and search those entries while offline — a meaningful "I lost wifi mid-cook" UX win without the full database-mirror complexity. Cache uses a dedicated `voice-chef-api-cache` so cache-clearing operations can target it specifically.

A SPA navigation fallback is configured: any in-app route serves `index.html` from cache, except for the dynamic paths above (which are denied via `navigateFallbackDenylist` to ensure they hit the network).

### Honest scope of "offline"

The **app shell** works offline — open the kitchen UI, see the rendered layout, navigate around the SPA. Anything that requires the backend (recipes list, voice transcription, agent responses) needs the network. This is the standard PWA pattern; full offline functionality (request queuing, replay) was not in scope for the minor.

## How to Verify (for the evaluator)

### 1. Build the production image

```bash
docker compose up -d --build --force-recreate kitchen-frontend
```

### 2. Open Chromium / Chrome at the kitchen URL

- Server-side: `http://localhost:8082/`
- Pi-side: `http://localhost/?kiosk=1`

Open DevTools (F12).

### 3. Verify manifest

**Application** tab → **Manifest** panel. Should show:

- Name: "Voice Chef Kitchen"
- Short name: "Voice Chef"
- Display: standalone
- Theme color: `#0a0a0a`
- All four icons (192, 512, 512 maskable, apple-touch) listed without errors
- No red warnings or `Manifest: parsing failed` errors

### 4. Verify service worker

**Application** tab → **Service Workers** panel. Should show:

- Status: `activated and is running`
- Source: `/sw.js`
- Scope: `/`

### 5. Verify installability

The Chromium address bar shows an **install icon** (rightmost, looks like a screen with a down-arrow). Or three-dot menu → **Install Voice Chef Kitchen…** Clicking it offers to add the app as a standalone window. After installation, the app launches in its own window with no browser chrome.

On Android (when reachable over HTTPS), Chrome offers an "Add to Home Screen" prompt.

### 6. Verify offline behaviour

DevTools → **Network** tab → tick **Offline** at the top. Reload the page. The app shell still loads (login screen renders, layout intact). Now try a voice query or any `/api/*` action — these fail as expected, and the kitchen surfaces a friendly error toast (existing UX from the agent error handling).

### 7. Verify denylisted paths bypass the cache

While offline:

```
fetch('/api/recipes')  // in DevTools Console
```

Should fail (not return a cached response). Confirms the runtime caching rules are working.

## Limitations & Future Work

- **Maskable icon is the same as the regular 512** — it should ideally have ~25% safe-area padding around the logo for Android adaptive icons. Acceptable for the minor; can iterate when we have a designed asset.
- **HTTPS for phone install**: Chromium accepts `http://localhost` as a secure context for service-worker registration, so install works on the Pi and during development. Phone install over the public internet requires HTTPS, which lands with PR #216 (separate workstream).
- **Auth model**: the kitchen-pi auto-logs in as a `kitchen`-role user via runtime config; a phone-installed PWA falls through to the existing office-login redirect (no auto-login). Same code, different deployments, different behavior — by design.
- **Offline API request queue**: not implemented. Voice queries while offline simply fail; the user retries when connectivity returns.

## Files

- `frontend/kitchen/vite.config.ts` — `VitePWA(...)` plugin registered with manifest, Workbox config, and runtime caching rules.
- `frontend/kitchen/index.html` — `<meta name="theme-color">` and `<link rel="apple-touch-icon">` (manifest `<link>` is auto-injected by the plugin at build).
- `frontend/kitchen/public/icons/` — `icon-192.png`, `icon-512.png`, `icon-maskable-512.png`, `apple-touch-icon.png`, `icon-32.png`.
- `frontend/kitchen/package.json` — `vite-plugin-pwa` devDependency.
- Build artifacts (regenerated each build, not committed): `dist/manifest.webmanifest`, `dist/sw.js`, `dist/workbox-*.js`, `dist/registerSW.js`.
