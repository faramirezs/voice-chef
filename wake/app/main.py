"""Wake-word detection service for the kitchen-pi kiosk.

Listens to the default ALSA capture device (the reSpeaker XVF3800 on a
real Pi), runs openWakeWord against the audio stream, and publishes
`{"event":"wake", ...}` messages on an SSE endpoint. The kitchen-frontend
subscribes and triggers voice recording on each wake.

Environment:
    WAKE_MODELS         comma-separated openWakeWord model names (default: hey_jarvis)
    WAKE_THRESHOLD      detection score threshold 0–1 (default: 0.5)
    WAKE_COOLDOWN_MS    minimum gap between two wake events (default: 1500)
    WAKE_SAMPLE_RATE    capture sample rate in Hz (default: 16000)
    WAKE_DEVICE         optional sounddevice device index/name override
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

import numpy as np
import sounddevice as sd
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openwakeword.model import Model

logger = logging.getLogger("wake")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

WAKE_MODELS = [m.strip() for m in os.getenv("WAKE_MODELS", "hey_jarvis").split(",") if m.strip()]
WAKE_THRESHOLD = float(os.getenv("WAKE_THRESHOLD", "0.5"))
WAKE_COOLDOWN_MS = int(os.getenv("WAKE_COOLDOWN_MS", "1500"))
WAKE_SAMPLE_RATE = int(os.getenv("WAKE_SAMPLE_RATE", "16000"))
WAKE_DEVICE = os.getenv("WAKE_DEVICE")  # sounddevice index or None

# openWakeWord expects 1280-sample frames at 16 kHz (80 ms windows).
FRAME_SAMPLES = 1280

# Each connected SSE client gets its own queue. The audio loop publishes
# wake events into all queues simultaneously.
_subscribers: set[asyncio.Queue[dict]] = set()
_subscribers_lock = asyncio.Lock()


async def _publish(event: dict) -> None:
    async with _subscribers_lock:
        for q in list(_subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


async def _audio_loop() -> None:
    """Capture audio in a portaudio callback thread, push into an asyncio
    queue, and run openWakeWord inference on the main event loop."""
    logger.info(
        "loading openWakeWord models=%s threshold=%.2f cooldown_ms=%d sample_rate=%d",
        WAKE_MODELS, WAKE_THRESHOLD, WAKE_COOLDOWN_MS, WAKE_SAMPLE_RATE,
    )
    model = Model(wakeword_models=WAKE_MODELS)
    loop = asyncio.get_running_loop()
    audio_queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=20)

    def _enqueue(arr: np.ndarray) -> None:
        try:
            audio_queue.put_nowait(arr)
        except asyncio.QueueFull:
            # Drop a frame rather than lag the audio thread.
            pass

    def _capture_callback(indata, frames, time_info, status):  # noqa: ANN001
        # Runs in the portaudio callback thread, NOT the asyncio thread.
        if status:
            logger.warning("sounddevice status: %s", status)
        mono = indata[:, 0].copy() if indata.ndim == 2 else indata.copy()
        loop.call_soon_threadsafe(_enqueue, mono)

    try:
        stream = sd.InputStream(
            samplerate=WAKE_SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=FRAME_SAMPLES,
            device=WAKE_DEVICE if WAKE_DEVICE else None,
            callback=_capture_callback,
        )
    except Exception:
        logger.exception("failed to open audio device — wake service will idle")
        return

    last_fire_ms: dict[str, int] = {}

    with stream:
        logger.info("audio capture started; listening for wake words")
        while True:
            chunk = await audio_queue.get()
            scores = model.predict(chunk)
            now_ms = int(time.time() * 1000)
            for keyword, score in scores.items():
                if score < WAKE_THRESHOLD:
                    continue
                if now_ms - last_fire_ms.get(keyword, 0) < WAKE_COOLDOWN_MS:
                    continue
                last_fire_ms[keyword] = now_ms
                logger.info("wake detected keyword=%s score=%.3f", keyword, score)
                await _publish({
                    "event": "wake",
                    "model": keyword,
                    "score": round(float(score), 3),
                    "ts": now_ms,
                })


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(_audio_loop(), name="wake-audio-loop")
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str | list[str]]:
    return {"status": "ok", "models": WAKE_MODELS}


@app.get("/events")
async def events() -> StreamingResponse:
    """SSE stream of wake events. One client per browser tab."""
    queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=64)

    async with _subscribers_lock:
        _subscribers.add(queue)

    async def gen() -> AsyncIterator[bytes]:
        try:
            yield b": connected\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(msg)}\n\n".encode("utf-8")
                except asyncio.TimeoutError:
                    # Periodic keep-alive comment so intermediaries don't time out.
                    yield b": keep-alive\n\n"
        finally:
            async with _subscribers_lock:
                _subscribers.discard(queue)

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
