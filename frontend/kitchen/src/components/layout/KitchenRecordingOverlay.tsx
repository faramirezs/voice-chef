import { triggerStopVoiceRecording } from "@/components/chat/VoiceInput";

/**
 * Fullscreen overlay shown while VoiceInput is actively recording. Gives the
 * kitchen user clear feedback ("yes, I heard you") and a large, elbow-tappable
 * stop target. Tapping anywhere on the overlay (button or backdrop) ends the
 * recording. Mounted by HudCanvas based on a recording-state subscription.
 */
export function KitchenRecordingOverlay() {
  const stop = () => triggerStopVoiceRecording();

  return (
    <div
      className="fixed inset-0 z-[60] bg-black/60 flex flex-col items-center justify-center cursor-pointer"
      onClick={stop}
      role="presentation"
    >
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          stop();
        }}
        aria-label="Stop recording"
        className="
          w-64 h-64 rounded-full bg-error text-white
          flex items-center justify-center
          shadow-[0_20px_60px_rgba(0,0,0,0.5)]
          ring-8 ring-error/40
          hover:scale-105 active:scale-95 transition-transform
          focus:outline-none focus-visible:ring-8 focus-visible:ring-white/60
        "
      >
        <svg
          width="96"
          height="96"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      </button>
      <p className="mt-10 text-3xl font-semibold text-white tracking-wide">
        Listening…
      </p>
      <p className="mt-3 text-base text-white/70">Tap anywhere to stop</p>
    </div>
  );
}
