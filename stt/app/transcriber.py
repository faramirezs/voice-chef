import os
from faster_whisper import WhisperModel

STT_MODEL = os.getenv("STT_MODEL", "small")
STT_DEVICE = os.getenv("STT_DEVICE", "cpu")
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "")

# Compute type: int8 is fastest on CPU, float16 for CUDA
_compute_type = "float16" if STT_DEVICE == "cuda" else "int8"

model = WhisperModel(
    STT_MODEL,
    device=STT_DEVICE,
    compute_type=_compute_type,
    download_root="/models",
)


def transcribe(audio_path: str) -> dict:
    """Transcribe an audio file and return text, language, and segments."""
    language = STT_LANGUAGE if STT_LANGUAGE else None

    segments, info = model.transcribe(
        audio_path,
        language=language,
        beam_size=5,
        vad_filter=True,
    )

    segment_list = []
    full_text_parts = []
    for seg in segments:
        segment_list.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })
        full_text_parts.append(seg.text.strip())

    text = " ".join(full_text_parts)
    lang_prob = round(info.language_probability, 2)

    if not text or lang_prob < 0.4:
        confidence = "none"
    elif lang_prob < 0.7:
        confidence = "low"
    else:
        confidence = "high"

    return {
        "text": text,
        "language": info.language,
        "language_probability": lang_prob,
        "confidence": confidence,
        "retry_suggested": confidence != "high",
        "duration": round(info.duration, 2),
        "segments": segment_list,
    }
