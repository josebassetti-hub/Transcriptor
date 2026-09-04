import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

/** Movimento de câmera contínuo (push-in/pan) aplicado ao conteúdo da cena. */
export const Camera: React.FC<{
  duration: number;
  from?: number;
  to?: number;
  panX?: number;
  panY?: number;
  children: React.ReactNode;
}> = ({ duration, from = 1, to = 1.08, panX = 0, panY = 0, children }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, duration], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s = from + (to - from) * p;
  return (
    <AbsoluteFill style={{ transform: `scale(${s}) translate(${panX * p}px, ${panY * p}px)`, transformOrigin: "50% 50%" }}>
      {children}
    </AbsoluteFill>
  );
};
