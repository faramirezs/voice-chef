import { useEffect } from "react";
import { triggerVoiceRecording } from "@/components/chat/VoiceInput";

/**
 * Subscribes to the wake-word service's SSE endpoint. On each `wake` event,
 * triggers VoiceInput's recording start so the user can speak their query
 * without tapping the mic. Browser EventSource auto-reconnects on disconnect.
 *
 * Path is proxied through the kitchen-frontend's nginx (`/wake/events`)
 * so we stay same-origin. On the server compose (no wake service), the
 * upstream returns 502 and EventSource quietly retries — no UI impact.
 */
const WAKE_EVENTS_PATH = import.meta.env.VITE_WAKE_URL
  ? `${import.meta.env.VITE_WAKE_URL}/events`
  : "/wake/events";

export function useWakeWord(): void {
  useEffect(() => {
    const es = new EventSource(WAKE_EVENTS_PATH);

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as { event?: string; model?: string; score?: number };
        if (data.event === "wake") {
          console.log("[useWakeWord] wake fired", data);
          triggerVoiceRecording();
        }
      } catch (err) {
        console.warn("[useWakeWord] failed to parse SSE message", e.data, err);
      }
    };

    es.onerror = () => {
      // EventSource handles reconnection. Log once per error transition;
      // browsers fire onerror repeatedly while disconnected.
      if (es.readyState === EventSource.CLOSED) {
        console.warn("[useWakeWord] event stream closed");
      }
    };

    return () => {
      es.close();
    };
  }, []);
}
