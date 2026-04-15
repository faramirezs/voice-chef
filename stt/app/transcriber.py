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

# Confidence tiers: each check can downgrade the tier
_TIERS = ["none", "low", "medium", "high"]


def _downgrade(tier: str, steps: int = 1) -> str:
    """Downgrade a confidence tier by N steps, flooring at 'none'."""
    idx = _TIERS.index(tier)
    return _TIERS[max(0, idx - steps)]


def _assess_confidence(
    text: str,
    lang_prob: float,
    duration: float,
    segment_list: list[dict],
) -> str:
    """Assess transcription confidence using multiple signals."""
    if not text:
        return "none"

    tier = "high"

    # Check 1: any segment is likely silence/noise
    for seg in segment_list:
        if seg["no_speech_prob"] > 0.6:
            return "none"

    # Check 2: hallucination detection via compression ratio
    for seg in segment_list:
        if seg["compression_ratio"] > 2.4:
            tier = _downgrade(tier)
            break

    # Check 3: low average log probability across segments
    logprobs = [s["avg_logprob"] for s in segment_list]
    if logprobs:
        mean_logprob = sum(logprobs) / len(logprobs)
        if mean_logprob < -1.0:
            tier = _downgrade(tier)

    # Check 4: language detection uncertainty
    if lang_prob < 0.5:
        tier = _downgrade(tier)

    # Check 5: too few words for audio duration (likely noise with hallucinated words)
    word_count = len(text.split())
    if duration > 3.0 and word_count / duration < 0.5:
        tier = _downgrade(tier)

    return tier


def transcribe(audio_path: str) -> dict:
    """Transcribe an audio file and return text, language, segments, and confidence."""
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
            "avg_logprob": round(seg.avg_logprob, 3),
            "no_speech_prob": round(seg.no_speech_prob, 3),
            "compression_ratio": round(seg.compression_ratio, 2),
        })
        full_text_parts.append(seg.text.strip())

    text = " ".join(full_text_parts)
    lang_prob = round(info.language_probability, 2)
    duration = round(info.duration, 2)

    confidence = _assess_confidence(text, lang_prob, duration, segment_list)

    return {
        "text": text,
        "language": info.language,
        "language_probability": lang_prob,
        "confidence": confidence,
        "retry_suggested": confidence not in ("high", "medium"),
        "duration": duration,
        "segments": segment_list,
    }
