#!/usr/bin/env python3
"""Voice chat with the agent: record speech, transcribe via STT, send to agent.
ENTER to record, ENTER to stop, ENTER to send to agent (or 'r' to re-record)."""

import json
import os
import platform
import shutil
import subprocess
import sys
import uuid
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

_system = platform.system()
if _system == "Darwin":
    _FF_INPUT = ["-f", "avfoundation", "-i", ":default"]
elif _system == "Linux":
    _FF_INPUT = ["-f", "pulse", "-i", "default"]
else:
    print(f"Error: unsupported platform '{_system}' for audio recording.")
    print("Supported: macOS (Darwin), Linux")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = SCRIPT_DIR / "samples"
RESULTS_DIR = SCRIPT_DIR / "results"
STT_URL = os.getenv("STT_URL", "http://localhost:8002/transcribe")
AGENT_URL = os.getenv("AGENT_URL", "http://localhost:8001/")


def record_audio(output_path: str) -> subprocess.Popen:
    """Start ffmpeg recording from the default microphone."""
    return subprocess.Popen(
        [
            "ffmpeg", "-y",
            *_FF_INPUT,
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
    """Stop ffmpeg recording."""
    proc.terminate()
    proc.wait(timeout=5)


def transcribe(audio_path: str) -> dict:
    """Send audio file to STT service."""
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


def send_to_agent(messages: list, thread_id: str) -> str:
    """Send messages to the agent via AG-UI protocol, return the response text."""
    run_id = str(uuid.uuid4())

    payload = json.dumps({
        "threadId": thread_id,
        "runId": run_id,
        "state": {},
        "messages": messages,
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }).encode()

    req = urllib.request.Request(
        AGENT_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
    )

    response_text = []
    with urllib.request.urlopen(req, timeout=60) as resp:
        for line in resp:
            line = line.decode("utf-8").strip()
            if not line.startswith("data: "):
                continue
            try:
                event = json.loads(line[6:])
            except json.JSONDecodeError:
                continue

            event_type = event.get("type", "")

            if event_type == "TEXT_MESSAGE_CONTENT":
                delta = event.get("delta", "")
                response_text.append(delta)
                print(delta, end="", flush=True)

            elif event_type == "RUN_ERROR":
                error_msg = event.get("message", "Unknown error")
                print(f"\nAgent error: {error_msg}")
                return ""

    print()  # newline after streamed response
    return "".join(response_text)


def main():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    thread_id = str(uuid.uuid4())
    messages = []
    msg_counter = 0

    print("Voice Chef — Voice Chat")
    print("ENTER = start/stop recording | Ctrl+C = quit")
    print(f"STT: {STT_URL}")
    print(f"Agent: {AGENT_URL}")
    print()

    try:
        while True:
            # --- Record ---
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

            # --- Transcribe ---
            print("Transcribing...")
            try:
                result = transcribe(wav_path)
            except Exception as e:
                print(f"STT error: {e}\n")
                continue

            json_path = str(RESULTS_DIR / f"{timestamp}.json")
            with open(json_path, "w") as f:
                json.dump(result, f, indent=2)

            text = result.get("text", "")
            confidence = result.get("confidence", "?")
            retry = result.get("retry_suggested", False)

            print(f'You: "{text}"')
            print(f"[confidence: {confidence}]")

            if retry:
                print("\033[93mI'm not sure I understood correctly.\033[0m")

            # --- Confirm ---
            choice = input("ENTER to send | 'r' to re-record | 'e' to edit: ").strip().lower()

            if choice == "r":
                print("Re-recording...\n")
                continue

            if choice == "e":
                text = input("Type your message: ").strip()
                confidence = "high"  # typed input is reliable
                if not text:
                    print("Empty message, skipping.\n")
                    continue

            if not text:
                print("Nothing to send.\n")
                continue

            # --- Send to agent ---
            # Augment voice input with STT metadata so the agent can
            # apply fuzzy matching when confidence is low
            if confidence != "high":
                lang = result.get("language", "?")
                agent_text = (
                    f"[voice, confidence: {confidence}, language: {lang}]\n"
                    f"{text}"
                )
            else:
                agent_text = text

            msg_counter += 1
            messages.append({
                "id": f"msg-{msg_counter}",
                "role": "user",
                "content": agent_text,
            })

            print("\nChef: ", end="", flush=True)
            try:
                response = send_to_agent(messages, thread_id)
            except Exception as e:
                print(f"\nAgent error: {e}")
                messages.pop()  # remove failed message from history
                msg_counter -= 1
                print()
                continue

            if response:
                msg_counter += 1
                messages.append({
                    "id": f"msg-{msg_counter}",
                    "role": "assistant",
                    "content": response,
                })

            print()

    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
