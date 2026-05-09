# syntax=docker/dockerfile:1.6
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
# Cache mount persists pip's download cache across builds even when this
# layer is invalidated (e.g., when requirements.txt changes). Drops the
# multi-minute torch redownload to seconds on subsequent rebuilds.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY app/ ./app/
EXPOSE 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
