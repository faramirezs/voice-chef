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
: "${KITCHEN_EMAIL:=}"
: "${KITCHEN_PASSWORD:=}"

export BACKEND_HOST BACKEND_PORT AGENT_HOST AGENT_PORT

# Don't log password (KITCHEN_PASSWORD is intentionally omitted).
if [ -n "$KITCHEN_EMAIL" ]; then
    kitchen_login_status="enabled (email=${KITCHEN_EMAIL})"
else
    kitchen_login_status="disabled"
fi
echo "kitchen-frontend nginx: BACKEND=${BACKEND_HOST}:${BACKEND_PORT}  AGENT=${AGENT_HOST}:${AGENT_PORT}  OFFICE=${OFFICE_URL}  KITCHEN_LOGIN=${kitchen_login_status}"

envsubst '${BACKEND_HOST} ${BACKEND_PORT} ${AGENT_HOST} ${AGENT_PORT}' \
    < /etc/nginx/conf.d/default.conf.template \
    > /etc/nginx/conf.d/default.conf

# Runtime config consumed by index.html. Escape backslashes and double quotes so
# arbitrary URL/password values don't break the JS string literal.
js_escape() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}
escaped_office_url=$(js_escape "$OFFICE_URL")
escaped_kitchen_email=$(js_escape "$KITCHEN_EMAIL")
escaped_kitchen_password=$(js_escape "$KITCHEN_PASSWORD")
cat > /usr/share/nginx/html/config.js <<EOF
window.__APP_CONFIG__ = {
  officeUrl: "${escaped_office_url}",
  kitchenEmail: "${escaped_kitchen_email}",
  kitchenPassword: "${escaped_kitchen_password}"
};
EOF

exec nginx -g "daemon off;"
