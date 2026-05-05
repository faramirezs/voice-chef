#!/bin/sh
# kitchen-frontend nginx startup
# Substitutes ${BACKEND_HOST} / ${BACKEND_PORT} / ${AGENT_HOST} / ${AGENT_PORT}
# in the nginx config template, then exec nginx in the foreground.
#
# Defaults preserve the server-side Compose-network behaviour so this image
# is a drop-in replacement for the previous static-config build.

set -e

: "${BACKEND_HOST:=backend}"
: "${BACKEND_PORT:=80}"
: "${AGENT_HOST:=agent}"
: "${AGENT_PORT:=8001}"

export BACKEND_HOST BACKEND_PORT AGENT_HOST AGENT_PORT

echo "kitchen-frontend nginx: BACKEND=${BACKEND_HOST}:${BACKEND_PORT}  AGENT=${AGENT_HOST}:${AGENT_PORT}"

envsubst '${BACKEND_HOST} ${BACKEND_PORT} ${AGENT_HOST} ${AGENT_PORT}' \
    < /etc/nginx/conf.d/default.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
