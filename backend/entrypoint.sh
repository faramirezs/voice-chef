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

echo "Running seed image linker..."
python -m scripts.link_photos

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 80 --reload