#!/usr/bin/env python3
"""Toggle recorder: press ENTER to start recording, press ENTER again to stop.
Sends the audio to the STT service and saves both the .wav and the JSON result."""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import urllib.request
import urllib.error

if not shutil.which("ffmpeg"):
    print("Error: ffmpeg is required but not installed.")
    print("Install it with:")
    print("  macOS:  brew install ffmpeg")
    print("  Linux:  apt install ffmpeg")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = SCRIPT_DIR / "samples"
RESULTS_DIR = SCRIPT_DIR / "results"
STT_URL = os.getenv("STT_URL", "http://localhost:8002/transcribe")


def record_audio(output_path: str) -> subprocess.Popen:
    """Start ffmpeg recording from the default microphone. Returns the process."""
    return subprocess.Popen(
        [
            "ffmpeg", "-y",
            "-f", "avfoundation",
            "-i", ":default",
            "-ac", "1",
            "-ar", "16000",
            "-sample_fmt", "s16",
            output_path,
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_recording(proc: subprocess.Popen):
    """Send quit signal to ffmpeg and wait for it to finish."""
    proc.terminate()
    proc.wait(timeout=5)


def transcribe(audio_path: str) -> dict:
    """Send audio file to STT service via multipart POST."""
    boundary = "----PythonBoundary"
    filename = os.path.basename(audio_path)

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: audio/wav\r\n\r\n"
    ).encode() + audio_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        STT_URL,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("STT Tester")
    print("ENTER = start/stop recording | Ctrl+C = quit")
    print()

    try:
        while True:
            input("Press ENTER to start recording...")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            wav_path = str(SAMPLES_DIR / f"{timestamp}.wav")

            proc = record_audio(wav_path)
            print("\033[91m● REC\033[0m")

            input("Press ENTER to stop...")

            stop_recording(proc)

            if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 100:
                print("Recording too short or failed.\n")
                continue

            print("Transcribing...")
            try:
                result = transcribe(wav_path)
            except Exception as e:
                print(f"Error: {e}\n")
                continue

            json_path = str(RESULTS_DIR / f"{timestamp}.json")
            with open(json_path, "w") as f:
                json.dump(result, f, indent=2)

            text = result.get("text", "")
            lang = result.get("language", "?")
            dur = result.get("duration", 0)
            confidence = result.get("confidence", "?")
            retry = result.get("retry_suggested", False)
            rel_wav = os.path.relpath(wav_path)
            rel_json = os.path.relpath(json_path)

            print(f'"{text}"')
            print(f"[{lang}] {dur}s | confidence: {confidence} | {rel_wav} | {rel_json}")

            if retry:
                print("\033[93mI'm not sure I understood correctly. Please try again.\033[0m")

            print()

    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
