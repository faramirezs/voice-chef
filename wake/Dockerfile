# Python 3.11 (not 3.12) because openWakeWord pulls in tflite-runtime as a
# hard Linux dependency, and tflite-runtime ships wheels for cp310/cp311
# only on linux/arm64 (the Pi). cp312 wheels don't exist as of late 2025.
FROM python:3.11-slim

# libportaudio2 is needed by sounddevice; libsndfile1 by some openwakeword codepaths.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libportaudio2 \
        libsndfile1 \
        alsa-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# openwakeword downloads its model files on first use; pre-fetch them here so
# the container starts up immediately even on a slow link.
RUN python -c "import openwakeword; openwakeword.utils.download_models()"

COPY app/ ./app/

EXPOSE 8004

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
