import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";
import path from "path";

export default defineConfig(({ mode }) => ({
  // In production, the kitchen frontend is mounted at /kitchen/ behind the
  // shared nginx-proxy (see PR #216). In dev (Vite dev server) it serves
  // at root. vite-plugin-pwa picks up `base` automatically and prefixes
  // start_url, scope, icon paths in the generated manifest accordingly.
  base: mode === "production" ? "/kitchen/" : "/",
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      // Auto-update: new SW takes over on next page load via skipWaiting() +
      // clients.claim(). Trade-off: a deploy mid-session can interrupt
      // streaming agent responses (the new SW activates and can re-claim the
      // page). Acceptable for a kitchen kiosk that updates rarely; if mid-
      // session interruptions become a real problem, switch to
      // registerType: "prompt" + a "new version available, refresh?" toast.
      registerType: "autoUpdate",
      // Static assets that should be served alongside the manifest. The icons
      // live in public/icons/ so Vite copies them to dist/icons/.
      includeAssets: ["icons/*.png", "favicon.svg"],
      manifest: {
        // `id` is the stable identifier for the installed app, separate from
        // `start_url`. Hard-coding it means the install survives even if we
        // ever change the start path (e.g. moving to "/kitchen/" once the
        // HTTPS proxy lands).
        id: "/voice-chef-kitchen",
        name: "Voice Chef Kitchen",
        short_name: "Voice Chef",
        description: "Voice-first AI cooking assistant",
        theme_color: "#0a0a0a",
        background_color: "#0a0a0a",
        display: "standalone",
        orientation: "any",
        // Mode-aware absolute path. In production behind the HTTPS proxy
        // the kitchen mounts at /kitchen/; in dev (Vite, no proxy) it
        // mounts at root. Safari on macOS doesn't always honor relative
        // start_urls when installing via "Add to Dock" — explicit absolute
        // makes the intent unambiguous to Chrome (which respects manifest
        // start_url) while staying within the auto-prefixed scope.
        start_url: mode === "production" ? "/kitchen/" : "/",
        icons: [
          { src: "icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png" },
          {
            src: "icons/icon-maskable-512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
      workbox: {
        // Precache the app shell (HTML, JS, CSS, icons, manifest) so reload
        // works offline. globPatterns picks up everything Vite emits to dist/.
        globPatterns: ["**/*.{js,css,html,svg,png,ico,webmanifest}"],
        // SPA navigation fallback: any in-app route serves index.html from
        // cache. The cached entry is base-prefixed by Workbox at build time,
        // so the fallback path must match — /kitchen/index.html in
        // production behind the HTTPS proxy, /index.html in dev. Wrong
        // value = navigation fallback misses the cache and the user sees
        // the network error instead of the SPA shell when offline.
        navigateFallback:
          mode === "production" ? "/kitchen/index.html" : "/index.html",
        navigateFallbackDenylist: [
          /^\/api/,
          /^\/agent/,
          /^\/stt/,
          /^\/wake/,
          /^\/uploads/,
          /^\/docs/,
          /^\/openapi\.json/,
          /^\/config\.js$/,
        ],
        // The two rules below are mutually exclusive by URL pattern, so
        // their order in the array isn't load-bearing — but Workbox does
        // evaluate first-match-wins, so we keep the SWR rule first by
        // convention to match how a reader naturally scans top-to-bottom.
        runtimeCaching: [
          {
            // Stale-while-revalidate for the read-only catalog endpoints —
            // recipes and ingredients (including detail and autocomplete
            // subpaths). Cached responses serve immediately when offline or
            // on slow networks; online requests still hit the backend in the
            // background to keep the cache fresh on the next page view.
            // Workbox defaults to GET-only, so writes are unaffected.
            urlPattern: ({ url }: { url: URL }) =>
              /^\/api\/(recipes|ingredients)(\/|$)/.test(url.pathname),
            handler: "StaleWhileRevalidate" as const,
            options: {
              cacheName: "voice-chef-api-cache",
              expiration: {
                maxEntries: 500,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 7 days
              },
              cacheableResponse: {
                // Only cache successful same-origin responses. We never
                // make cross-origin API calls, so opaque (status 0)
                // responses don't occur — listing them would be a footgun
                // (each opaque entry charges ~7 MB against quota).
                // 4xx/5xx are excluded so an auth failure doesn't poison
                // the cache and persist after the user logs in.
                statuses: [200],
              },
            },
          },
          {
            // Auth-sensitive, dynamic, streaming, runtime-generated — never
            // cache. Explicitly excludes /api/recipes and /api/ingredients
            // (handled by the SWR rule above) so the two patterns don't
            // overlap — keeps the rule set order-independent.
            //
            // Catches /api/auth, /api/uploads, other /api/*, /agent/*,
            // /stt/*, /wake/*, /uploads/*, and /config.js (the runtime-
            // config script generated by the kitchen-frontend container's
            // entrypoint).
            urlPattern: ({ url }: { url: URL }) => {
              const p = url.pathname;
              if (p === "/config.js") return true;
              if (/^\/(agent|stt|wake|uploads)\//.test(p)) return true;
              // /api/* but NOT /api/recipes or /api/ingredients
              if (/^\/api\//.test(p)) {
                return !/^\/api\/(recipes|ingredients)(\/|$)/.test(p);
              }
              return false;
            },
            handler: "NetworkOnly" as const,
          },
        ],
      },
      devOptions: {
        // Disable PWA in dev mode by default; flip to true when actively
        // testing the SW locally with `npm run dev`.
        enabled: false,
      },
    }),
  ],
  server: {
    host: true,
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://backend:80',
        changeOrigin: true,
      },
      '/agent': {
        target: 'http://agent:8001',
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/agent/, ''),
      },
      '/stt': {
        target: 'http://stt:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/stt/, ''),
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
