#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="logs"
LOG_FILE="$LOG_DIR/dump_upgrade_blast_check.log"

mkdir -p "$LOG_DIR"

DB_URL="${DATABASE_URL:-postgresql+psycopg://recipe_user:recipe_pass123@localhost:5432/recipe_db}"

{
  echo "[blast-check] started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "[blast-check] resetting database volume (docker compose down -v)"
} | tee "$LOG_FILE"

docker compose down -v >> "$LOG_FILE" 2>&1

echo "[blast-check] starting db service" | tee -a "$LOG_FILE"
docker compose up -d db >> "$LOG_FILE" 2>&1

echo "[blast-check] waiting for db health" | tee -a "$LOG_FILE"
for i in $(seq 1 30); do
  if docker compose exec -T db pg_isready -U recipe_user -d recipe_db >/dev/null 2>&1; then
    echo "[blast-check] db is healthy" | tee -a "$LOG_FILE"
    break
  fi
  if [[ "$i" -eq 30 ]]; then
    echo "[blast-check] db did not become healthy in time" | tee -a "$LOG_FILE"
    exit 1
  fi
  sleep 2
done

echo "[blast-check] waiting for stable SQL connectivity" | tee -a "$LOG_FILE"
stable_ok=0
for i in $(seq 1 40); do
  if docker compose exec -T db psql -U recipe_user -d recipe_db -c "SELECT 1;" >/dev/null 2>&1; then
    stable_ok=$((stable_ok + 1))
    if [[ "$stable_ok" -ge 2 ]]; then
      echo "[blast-check] SQL connectivity is stable" | tee -a "$LOG_FILE"
      break
    fi
  else
    stable_ok=0
  fi

  if [[ "$i" -eq 40 ]]; then
    echo "[blast-check] SQL connectivity did not stabilize in time" | tee -a "$LOG_FILE"
    exit 1
  fi
  sleep 2
done

echo "[blast-check] running alembic upgrade head against dump-initialized db" | tee -a "$LOG_FILE"
set +e
.venv/bin/alembic -c alembic.ini -x db_url="$DB_URL" upgrade head >> "$LOG_FILE" 2>&1
ALEMBIC_EXIT=$?
set -e

echo "[blast-check] alembic exit code: $ALEMBIC_EXIT" | tee -a "$LOG_FILE"

echo "[blast-check] current alembic_version rows:" | tee -a "$LOG_FILE"
docker compose exec -T db psql -U recipe_user -d recipe_db -c "SELECT version_num FROM alembic_version;" >> "$LOG_FILE" 2>&1 || true

echo "[blast-check] finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG_FILE"

exit "$ALEMBIC_EXIT"
