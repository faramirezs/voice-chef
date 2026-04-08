#!/usr/bin/env bash

set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

LOG_FILE="${DRIFT_LOG_FILE:-logs/drift_gate_local.log}"
PENDING_REV_ID="${PENDING_REV_ID:-pending_check_tmp_local}"
PENDING_MSG="${PENDING_MSG:-verify_no_pending_local_gate}"
PENDING_FILE="db/alembic/versions/${PENDING_REV_ID}_${PENDING_MSG}.py"
MANAGED_PATTERN="${MANAGED_TABLE_PATTERN:-users|tenants|recipes}"

mkdir -p "$(dirname "$LOG_FILE")"

set +e

echo "Schema drift local run started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$LOG_FILE"

echo "== GATE 1: alembic upgrade head ==" >> "$LOG_FILE"
alembic -c alembic.ini upgrade head >> "$LOG_FILE" 2>&1
G1=$?

echo "== GATE 2: drift_check.py ==" >> "$LOG_FILE"
python db/scripts/drift_check.py >> "$LOG_FILE" 2>&1
G2=$?

echo "== GATE 3: pytest schema drift ==" >> "$LOG_FILE"
pytest db/test/test_schema_drift.py -q --maxfail=1 --disable-warnings --tb=short --test-alembic >> "$LOG_FILE" 2>&1
G3=$?

echo "== GATE 4: pending autogenerate check ==" >> "$LOG_FILE"
alembic -c alembic.ini revision --autogenerate -m "$PENDING_MSG" --rev-id "$PENDING_REV_ID" >> "$LOG_FILE" 2>&1
G4=$?

if [ -f "$PENDING_FILE" ] && grep -qE "op\.(create|drop|add|alter)" "$PENDING_FILE"; then
    if grep -E "op\.(create|drop|add|alter)" "$PENDING_FILE" | grep -qiE "$MANAGED_PATTERN"; then
        echo "❌ Pending schema operations detected for managed tables (${MANAGED_PATTERN})." >> "$LOG_FILE"
        grep -E "op\.(create|drop|add|alter)" "$PENDING_FILE" | grep -iE "$MANAGED_PATTERN" >> "$LOG_FILE"
        G4=1
    else
        echo "ℹ️ Pending autogenerate operations detected only outside managed scope; Gate 4 pass." >> "$LOG_FILE"
        G4=0
    fi
fi

RESULT="RESULT migration=$G1 drift_script=$G2 pytest_drift=$G3 pending_autogen=$G4"
echo "$RESULT" | tee -a "$LOG_FILE"

rm -f "$PENDING_FILE"

if [ "$G1" -ne 0 ] || [ "$G2" -ne 0 ] || [ "$G3" -ne 0 ] || [ "$G4" -ne 0 ]; then
    exit 1
fi

exit 0
