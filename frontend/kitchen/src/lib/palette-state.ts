import { useSyncExternalStore } from "react";

let _isOpen = false;
const _listeners = new Set<() => void>();

function _notify() { _listeners.forEach((fn) => fn()); }

export function openPalette(): void { _isOpen = true; _notify(); }
export function closePalette(): void { _isOpen = false; _notify(); }
export function togglePalette(): void { _isOpen = !_isOpen; _notify(); }

export function usePaletteOpen(): boolean {
  return useSyncExternalStore(
    (cb: () => void) => { _listeners.add(cb); return () => { _listeners.delete(cb); }; },
    () => _isOpen,
  );
}
