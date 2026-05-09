FROM python:3.11-slim

WORKDIR /code

COPY backend/entrypoint.sh /code/entrypoint.sh
COPY backend/requirements.txt /code/requirements.txt
COPY assets/recipe_seed_images /assets/recipe_seed_images
COPY backend/scripts/link_photos.py /code/scripts/link_photos.py
COPY backend/scripts/__init__.py /code/scripts/__init__.py

RUN chmod +x /code/entrypoint.sh
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
	pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY backend/app /code/app
COPY alembic.ini /code/alembic.ini
COPY /db /code/db

CMD ["/code/entrypoint.sh"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]
