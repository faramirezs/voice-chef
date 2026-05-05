#!/bin/sh
# kitchen-frontend nginx startup
# - Substitutes ${BACKEND_HOST} / ${BACKEND_PORT} / ${AGENT_HOST} / ${AGENT_PORT}
#   in the nginx config template
# - Writes /config.js with runtime config consumed by index.html (e.g. OFFICE_URL
#   for the not-logged-in redirect target). Build-time VITE_OFFICE_URL still
#   works as a fallback when this file is absent (e.g. `npm run dev`).
# - Execs nginx in the foreground.
#
# Defaults preserve the server-side Compose-network behaviour so this image
# is a drop-in replacement for the previous static-config build.

set -e

: "${BACKEND_HOST:=backend}"
: "${BACKEND_PORT:=80}"
: "${AGENT_HOST:=agent}"
: "${AGENT_PORT:=8001}"
: "${OFFICE_URL:=http://localhost:8080}"

export BACKEND_HOST BACKEND_PORT AGENT_HOST AGENT_PORT

echo "kitchen-frontend nginx: BACKEND=${BACKEND_HOST}:${BACKEND_PORT}  AGENT=${AGENT_HOST}:${AGENT_PORT}  OFFICE=${OFFICE_URL}"

envsubst '${BACKEND_HOST} ${BACKEND_PORT} ${AGENT_HOST} ${AGENT_PORT}' \
    < /etc/nginx/conf.d/default.conf.template \
    > /etc/nginx/conf.d/default.conf

# Runtime config consumed by index.html. JSON.stringify-style escaping for the
# string value — OFFICE_URL is a plain URL so this is conservative-not-fancy.
escaped_office_url=$(printf '%s' "$OFFICE_URL" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')
cat > /usr/share/nginx/html/config.js <<EOF
window.__APP_CONFIG__ = {
  officeUrl: "${escaped_office_url}"
};
EOF

exec nginx -g "daemon off;"
