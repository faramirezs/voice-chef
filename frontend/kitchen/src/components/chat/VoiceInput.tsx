import { useCallback, useEffect, useRef, useState } from "react";
import { KButton } from "@/components/ui/KButton";

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

const SpeechRecognitionCtor =
  typeof window !== "undefined"
    ? (window.SpeechRecognition ?? window.webkitSpeechRecognition)
    : undefined;

const ERROR_MESSAGES: Record<string, string> = {
  "not-allowed": "Microphone access denied. Please allow microphone in browser settings.",
  "no-speech": "No speech detected. Try again.",
  "network": "Speech service unavailable. Check your internet connection.",
  "aborted": "Speech recognition was aborted.",
  "audio-capture": "No microphone found. Please connect a microphone.",
  "service-not-allowed":
    "Speech service not allowed. Check browser permissions.",
};

export function VoiceInput({ onTranscript, disabled }: VoiceInputProps) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const errorTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();
      if (errorTimerRef.current) clearTimeout(errorTimerRef.current);
    };
  }, []);

  const showError = useCallback((msg: string) => {
    setError(msg);
    if (errorTimerRef.current) clearTimeout(errorTimerRef.current);
    errorTimerRef.current = setTimeout(() => setError(null), 5000);
  }, []);

  const toggle = useCallback(async () => {
    if (!SpeechRecognitionCtor) return;

    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }

    // Request microphone permission before starting recognition
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      // Release immediately — recognition will request its own stream
      stream.getTracks().forEach((t) => t.stop());
    } catch {
      showError(
        "Microphone access denied. Please allow microphone in browser settings."
      );
      return;
    }

    const recognition = new SpeechRecognitionCtor();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (e: SpeechRecognitionEvent) => {
      const transcript = Array.from(e.results)
        .map((r: SpeechRecognitionResult) => r[0]?.transcript)
        .join("");
      if (transcript) onTranscript(transcript);
    };

    recognition.onerror = (e: SpeechRecognitionErrorEvent) => {
      const msg =
        ERROR_MESSAGES[e.error] ?? `Voice error: ${e.error}`;
      console.error("[VoiceInput] Speech recognition error:", e.error, e.message);
      showError(msg);
      setListening(false);
    };

    recognition.onend = () => setListening(false);

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  }, [listening, onTranscript, showError]);

  if (!SpeechRecognitionCtor) return null;

  return (
    <div className="relative flex-shrink-0">
      <KButton
        type="button"
        onClick={toggle}
        disabled={disabled}
        aria-label={listening ? "Stop recording" : "Start voice input"}
        variant="ghost"
        size="icon"
        className={`text-2xl shadow-[0_8px_20px_rgba(0,0,0,0.2)]
          ${
            listening
              ? "bg-primary text-[#16270f] ring-primary/60 animate-pulse"
              : "bg-surface-alt text-text-muted ring-border/70 hover:text-text hover:bg-border/35"
          }
        `}
      >
        {listening ? (
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
      {error && (
        <div
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2
            whitespace-nowrap rounded bg-destructive/90 px-3 py-1.5
            text-sm text-white shadow-lg
            animate-in fade-in slide-in-from-bottom-1 duration-200"
        >
          {error}
        </div>
      )}
    </div>
  );
}
