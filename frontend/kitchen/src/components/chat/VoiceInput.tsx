import { useCallback, useEffect, useRef, useState } from "react";
import { KButton } from "@/components/ui/KButton";

export interface SttResult {
  text: string;
  language: string;
  confidence: string;
  retry_suggested: boolean;
}

interface VoiceInputProps {
  onTranscript: (text: string, sttResult?: SttResult) => void;
  onConfidenceWarning?: (text: string) => void;
  disabled?: boolean;
}

const STT_URL = import.meta.env.VITE_STT_URL ?? "/stt";

// Module-level registry: the VoiceInput instance registers its start/stop
// handlers on mount so external triggers (wake-word, fullscreen stop overlay)
// can drive voice capture without prop-drilling or context. Mirrors the
// _sendMessage pattern in useAgent.ts.
let _startRecording: (() => Promise<void>) | null = null;
let _stopRecording: (() => void) | null = null;

export function triggerVoiceRecording(): void {
  if (_startRecording) {
    void _startRecording();
  } else {
    console.warn("[VoiceInput] triggerVoiceRecording called but no instance is mounted");
  }
}

export function triggerStopVoiceRecording(): void {
  if (_stopRecording) {
    _stopRecording();
  }
}

// Recording-state pub/sub. The fullscreen overlay subscribes to render
// itself when recording is active. State is published on every change
// from the VoiceInput instance.
export interface RecordingState {
  recording: boolean;
  transcribing: boolean;
}

let _currentRecordingState: RecordingState = { recording: false, transcribing: false };
const _recordingStateListeners = new Set<(s: RecordingState) => void>();

export function subscribeRecordingState(cb: (s: RecordingState) => void): () => void {
  _recordingStateListeners.add(cb);
  cb(_currentRecordingState);
  return () => {
    _recordingStateListeners.delete(cb);
  };
}

function _publishRecordingState(s: RecordingState): void {
  _currentRecordingState = s;
  _recordingStateListeners.forEach((cb) => cb(s));
}

export function VoiceInput({
  onTranscript,
  onConfidenceWarning,
  disabled,
}: VoiceInputProps) {
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());

        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        if (blob.size < 100) return;

        setTranscribing(true);
        try {
          const form = new FormData();
          form.append("file", blob, "recording.webm");

          const resp = await fetch(`${STT_URL}/transcribe`, {
            method: "POST",
            body: form,
          });

          if (!resp.ok) {
            console.error("STT error:", resp.status);
            return;
          }

          const result = await resp.json();
          const text = result.text?.trim();

          if (result.retry_suggested) {
            onConfidenceWarning?.(
              text || "I'm not sure I understood correctly. Please try again.",
            );
          }

          if (text) onTranscript(text, result as SttResult);
        } catch (err) {
          console.error("STT request failed:", err);
        } finally {
          setTranscribing(false);
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
    }
  }, [onTranscript, onConfidenceWarning]);

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current = null;
    setRecording(false);
  }, []);

  // Register this instance's start/stop handlers for external triggers
  // (wake word, fullscreen stop overlay). If multiple VoiceInputs are ever
  // mounted, last-mount-wins; in practice there is exactly one in HudVoiceBar.
  useEffect(() => {
    const start = async () => {
      if (recording || transcribing) return;
      await startRecording();
    };
    _startRecording = start;
    _stopRecording = stopRecording;
    return () => {
      if (_startRecording === start) _startRecording = null;
      if (_stopRecording === stopRecording) _stopRecording = null;
    };
  }, [startRecording, stopRecording, recording, transcribing]);

  // Publish recording state to subscribers (e.g. the fullscreen overlay).
  useEffect(() => {
    _publishRecordingState({ recording, transcribing });
  }, [recording, transcribing]);

  const toggle = useCallback(() => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [recording, startRecording, stopRecording]);


  return (
    <KButton
      type="button"
      onClick={toggle}
      disabled={disabled || transcribing}
      aria-label={
        transcribing
          ? "Transcribing..."
          : recording
            ? "Stop recording"
            : "Start voice input"
      }
      variant="ghost"
      size="icon"
      className={`flex-shrink-0 text-2xl shadow-[0_8px_20px_rgba(0,0,0,0.2)]
        ${
          recording
            ? "bg-error text-white ring-error/60 animate-pulse"
            : transcribing
              ? "bg-warning/20 text-warning ring-warning/40 animate-pulse"
              : "bg-surface-alt text-text-muted ring-border/70 hover:text-text hover:bg-border/35"
        }
        `}
    >
      {transcribing ? (
        <svg
          width="28"
          height="28"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="animate-spin"
        >
          <path d="M21 12a9 9 0 1 1-6.219-8.56" />
        </svg>
      ) : recording ? (
        <svg
          width="28"
          height="28"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      ) : (
        <svg
          width="28"
          height="28"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="9" y="2" width="6" height="11" rx="3" />
          <path d="M5 10a7 7 0 0 0 14 0" />
          <line x1="12" y1="19" x2="12" y2="22" />
        </svg>
      )}
    </KButton>
  );
}
