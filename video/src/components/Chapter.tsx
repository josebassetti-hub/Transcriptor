import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Shockwave, Flash } from "./Fx";
import { riseIn, slamIn, slamOut } from "./anim";
import { font, theme } from "../theme";

/** Abertura de capítulo: número fantasma gigante, título e subtítulo/selo. Sai em `duration`. */
export const Chapter: React.FC<{ numero: string; titulo: string; sub: string; duration: number; pill?: boolean }> = ({ numero, titulo, sub, duration, pill }) => {
  const frame = useCurrentFrame();
  if (frame > duration + 14) return null;
  const outS = frame >= duration - 6 ? slamOut(frame, duration - 6) : {};
  const ghost = interpolate(frame, [0, 12], [0, 0.12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: font.family, ...outS }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 40, textAlign: "center", fontSize: 900, fontWeight: 900, color: theme.blueLight, opacity: ghost, letterSpacing: -40, lineHeight: 1 }}>
        {numero}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 380, textAlign: "center", ...slamIn(frame, 0, 10) }}>
        <div style={{ fontSize: 170, fontWeight: 900, color: theme.white, letterSpacing: -6, lineHeight: 1, textShadow: `0 0 80px ${theme.glow}`, whiteSpace: "nowrap" }}>{titulo}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 600, textAlign: "center", ...riseIn(frame, 10, 12, 30) }}>
        {pill ? (
          <span style={{ display: "inline-block", padding: "14px 44px", borderRadius: 999, border: `2px solid ${theme.blueLight}`, color: theme.white, fontSize: 40, fontWeight: 700, letterSpacing: 8 }}>{sub}</span>
        ) : (
          <div style={{ fontSize: 56, fontWeight: 500, color: theme.blueLight }}>{sub}</div>
        )}
      </div>
      <Shockwave at={0} size={2000} />
      <Flash at={0} strength={0.4} />
    </div>
  );
};
