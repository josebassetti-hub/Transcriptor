import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

/** Círculo azul com "check" desenhado por stroke animado. */
export const Check: React.FC<{ delay?: number; size?: number }> = ({ delay = 0, size = 56 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: frame - delay, fps, config: { damping: 12, stiffness: 160 } });
  const draw = interpolate(frame - delay - 6, [0, 14], [40, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" style={{ transform: `scale(${pop})`, flexShrink: 0 }}>
      <circle cx="28" cy="28" r="26" fill={theme.blue} />
      <path
        d="M16 29 L25 37 L41 20"
        fill="none"
        stroke="#fff"
        strokeWidth="5"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray="40"
        strokeDashoffset={draw}
      />
    </svg>
  );
};
