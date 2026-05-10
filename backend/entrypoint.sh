#!/bin/sh
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL environment variable is not set"
  exit 1
fi
export PYTHONPATH=/code

# Wait for the database to be ready, apply migrations, then start the application server
echo "Waiting for DB migrations..."
until alembic upgrade head; do
  echo "Waiting for database..."
  sleep 2
done

# Run seed image linker only on first initialization
SEED_MARKER="/code/data/.seed_images_linked"
if [ ! -f "$SEED_MARKER" ]; then
  echo "Running seed image linker (first run only)..."
  python -m scripts.link_photos
  mkdir -p /code/data
  touch "$SEED_MARKER"
else
  echo "Seed images already linked (skipping)."
fi

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 80 --reload