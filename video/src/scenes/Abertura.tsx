import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Logo } from "../components/Logo";
import { useEnter, useSceneFade } from "../components/anim";
import { EMPRESA, SCENES } from "../content";
import { font, theme } from "../theme";

export const Abertura: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useSceneFade(SCENES.abertura.duration, 10, 14);
  const logoIn = spring({ frame, fps, config: { damping: 200, stiffness: 60, mass: 1.2 } });
  const scale = 0.92 + 0.08 * logoIn;
  const lineW = interpolate(frame, [20, 60], [0, 520], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const desc = useEnter(38);
  const desde = useEnter(52);
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center", justifyContent: "center", fontFamily: font.family }}>
      <div style={{ transform: `scale(${scale})`, opacity: logoIn }}>
        <Logo width={720} />
      </div>
      <div style={{ height: 4, width: lineW, background: `linear-gradient(90deg, transparent, ${theme.blueLight}, transparent)`, marginTop: 56 }} />
      <div style={{ ...desc, marginTop: 30, fontSize: 40, fontWeight: 600, color: theme.white, letterSpacing: 0.5 }}>
        {EMPRESA.descricao}
      </div>
      <div style={{ ...desde, marginTop: 14, fontSize: 28, fontWeight: 500, color: theme.muted, letterSpacing: 4, textTransform: "uppercase" }}>
        {EMPRESA.desde}
      </div>
    </AbsoluteFill>
  );
};
