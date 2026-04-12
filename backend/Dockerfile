FROM python:3.11-slim

WORKDIR /code

COPY backend/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY backend/app /code/app
COPY alembic.ini /code/alembic.ini
COPY db /code/db

# Wait for the database to be ready, apply migrations, then start the application server
CMD ["sh", "-c", "until alembic upgrade head; do echo 'Waiting for database to be ready...'; sleep 2; done && uvicorn app.main:app --host 0.0.0.0 --port 80 --reload"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]
