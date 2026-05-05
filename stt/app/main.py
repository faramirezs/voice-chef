import tempfile
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .transcriber import transcribe

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_CONTENT_TYPES = {
    "audio/wav", "audio/x-wav", "audio/wave",
    "audio/mpeg", "audio/mp3",
    "audio/ogg", "audio/flac",
    "audio/webm",
}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "stt"}


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Accept an audio file upload and return the transcription."""
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio type: {file.content_type}. "
                   f"Supported: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )

    suffix = _suffix_from_filename(file.filename or "audio.wav")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = transcribe(tmp_path)
    finally:
        os.unlink(tmp_path)

    return result


def _suffix_from_filename(filename: str) -> str:
    """Extract file extension, defaulting to .wav."""
    _, ext = os.path.splitext(filename)
    return ext if ext else ".wav"
