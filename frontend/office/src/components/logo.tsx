import React from "react";
import logoSvg from "@/assets/voice-chef-logo.svg?raw";

export function Logo({ size = 128, className = "" }: { size?: number | string; className?: string }) {
  const style: React.CSSProperties = {
    width: typeof size === "number" ? `${size}px` : size,
    height: "auto",
    display: "inline-block",
    lineHeight: 0,
  };

  return (
    <span
      className={className}
      style={style}
      dangerouslySetInnerHTML={{ __html: logoSvg }}
      aria-hidden={true}
    />
  );
}
