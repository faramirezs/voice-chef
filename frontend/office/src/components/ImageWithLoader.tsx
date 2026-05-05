import React, { useEffect, useRef, useState } from 'react';

type Props = {
  src?: string | null;
  alt?: string;
  className?: string;
  // When true, ensure loader animation runs for at least `minUploadDurationMs`.
  uploadPending?: boolean;
  minUploadDurationMs?: number;
  onClick?: () => void;
};

export default function ImageWithLoader({
  src,
  alt = '',
  className,
  uploadPending = false,
  minUploadDurationMs = 10000,
  onClick,
}: Props) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [showLoader, setShowLoader] = useState(false);
  const uploadStartRef = useRef<number | null>(null);
  const minTimerRef = useRef<number | null>(null);

  // If an upload starts, mark start time and show loader immediately
  useEffect(() => {
    if (uploadPending) {
      uploadStartRef.current = Date.now();
      setShowLoader(true);
      setImageLoaded(false);
    } else if (uploadStartRef.current) {
      // Upload finished — ensure minimum duration
      const elapsed = Date.now() - uploadStartRef.current;
      const remaining = Math.max(0, minUploadDurationMs - elapsed);
      if (remaining > 0) {
        if (minTimerRef.current) {
          window.clearTimeout(minTimerRef.current);
        }
        minTimerRef.current = window.setTimeout(() => {
          setShowLoader(false);
          minTimerRef.current = null;
          uploadStartRef.current = null;
        }, remaining);
      } else {
        setShowLoader(false);
        uploadStartRef.current = null;
      }
    }
    return () => {
      if (minTimerRef.current) {
        window.clearTimeout(minTimerRef.current);
      }
    };
  }, [uploadPending, minUploadDurationMs]);

  // When loading a normal image (not upload), show loader until loaded
  useEffect(() => {
    if (!src) {
      setImageLoaded(false);
      return;
    }
    // If an upload is in progress we already show loader — let onLoad handle imageLoaded
    if (!uploadPending) {
      setShowLoader(true);
    }
    // reset imageLoaded so onLoad can trigger again when src changes
    setImageLoaded(false);
  }, [src, uploadPending]);

  const handleOnLoad = () => {
    setImageLoaded(true);
    // If not forced to keep loader for upload, hide it when image loaded
    if (!uploadStartRef.current) {
      setShowLoader(false);
    }
  };

  return (
    <div className={`relative ${className ?? ''}`} onClick={onClick}>
      {uploadPending && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/20 z-10">
          <div className="flex flex-col items-center gap-2">
            <div className="h-10 w-10 rounded-full border-4 border-white border-t-transparent animate-spin" />
            <div className="text-white text-sm">Uploading...</div>
          </div>
        </div>
      )}

      {src ? (
        // eslint-disable-next-line jsx-a11y/alt-text
        <img src={src} alt={alt} onLoad={handleOnLoad} className="w-full h-full object-cover" />
      ) : (
        <div className="w-full h-full flex items-center justify-center text-muted-foreground">
          <div className="text-center">
            <p className="text-lg font-medium">Click here to upload a picture</p>
          </div>
        </div>
      )}
    </div>
  );
}
