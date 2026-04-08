#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

TMP_CONTAINER="vc_dump_regen_db"
TMP_PORT="55432"
DB_NAME="recipe_db"
DB_USER="recipe_user"
DB_PASS="recipe_pass123"
DB_URL="postgresql+psycopg://${DB_USER}:${DB_PASS}@localhost:${TMP_PORT}/${DB_NAME}"

cleanup() {
  docker rm -f "$TMP_CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup

echo "[dump-regen] starting temporary postgres container on port ${TMP_PORT}"
docker run -d --name "$TMP_CONTAINER" \
  -e POSTGRES_DB="$DB_NAME" \
  -e POSTGRES_USER="$DB_USER" \
  -e POSTGRES_PASSWORD="$DB_PASS" \
  -p "${TMP_PORT}:5432" \
  postgres:17.8 >/dev/null

echo "[dump-regen] waiting for postgres readiness"
for i in $(seq 1 60); do
  if docker exec "$TMP_CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    echo "[dump-regen] postgres is ready"
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "[dump-regen] postgres did not become ready in time" >&2
    exit 1
  fi
  sleep 1
done

echo "[dump-regen] applying migrations to head"
DATABASE_URL="$DB_URL" .venv/bin/alembic -c alembic.ini upgrade head

echo "[dump-regen] exporting schema-only dump to db/init/01_dump.sql"
docker exec "$TMP_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --schema-only > db/init/01_dump.sql

echo "[dump-regen] completed"
