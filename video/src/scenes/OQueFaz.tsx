import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Camera } from "../components/Camera";
import { Particles, Shockwave, Flash } from "../components/Fx";
import { riseIn, slamIn } from "../components/anim";
import { BEAT, EMPRESA, OQUEFAZ, SCENES } from "../content";
import { font, theme } from "../theme";

/** Cena 2: os dois pilares da Projet batem na tela: FINANCIAMENTOS + INCENTIVOS FISCAIS. */
export const OQueFaz: React.FC = () => {
  const frame = useCurrentFrame();
  const h1 = BEAT * 1;
  const h2 = BEAT * 3;
  const h3 = BEAT * 6;
  const slabX = interpolate(frame, [0, SCENES.oquefaz], [-700, 700]);
  return (
    <AbsoluteFill style={{ fontFamily: font.family, overflow: "hidden" }}>
      <Camera duration={SCENES.oquefaz} from={1} to={1.08} panY={-10}>
        <Particles count={45} speed={1.3} seed="o" />
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            width: 2600,
            height: 420,
            marginLeft: -1300 + slabX,
            marginTop: -210,
            transform: "rotate(-12deg)",
            background: `linear-gradient(90deg, transparent, ${theme.navy}, ${theme.blue}, ${theme.navy}, transparent)`,
            opacity: 0.35,
          }}
        />
      </Camera>
      <div style={{ position: "absolute", top: 90, left: 120, display: "flex", alignItems: "center", gap: 18, ...riseIn(frame, 0, 12, 20) }}>
        <div style={{ width: 54, height: 5, background: theme.blueLight, borderRadius: 3 }} />
        <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: 5, color: theme.blueLight, textTransform: "uppercase" }}>{EMPRESA.desde}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 210, textAlign: "center", ...riseIn(frame, 2, 12, 24) }}>
        <div style={{ fontSize: 46, fontWeight: 500, color: theme.muted, letterSpacing: 6, textTransform: "uppercase" }}>{OQUEFAZ.pre}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 310, textAlign: "center", ...slamIn(frame, h1) }}>
        <div style={{ fontSize: 176, fontWeight: 900, color: theme.white, letterSpacing: -8, lineHeight: 1, textShadow: `0 0 70px ${theme.glow}`, whiteSpace: "nowrap" }}>{OQUEFAZ.pilar1}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 505, textAlign: "center", ...slamIn(frame, h2 - 6, 8) }}>
        <div style={{ fontSize: 90, fontWeight: 900, color: theme.blueLight, lineHeight: 1 }}>{OQUEFAZ.mais}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 610, textAlign: "center", ...slamIn(frame, h2) }}>
        <div style={{ fontSize: 146, fontWeight: 900, color: theme.blueLight, letterSpacing: -8, lineHeight: 1, textShadow: `0 0 70px ${theme.glow}`, whiteSpace: "nowrap" }}>{OQUEFAZ.pilar2}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 830, textAlign: "center", ...riseIn(frame, h3, 14, 30) }}>
        <div style={{ fontSize: 48, fontWeight: 500, color: theme.white }}>{OQUEFAZ.pos}</div>
      </div>
      <Shockwave at={h1} size={1600} />
      <Flash at={h1} strength={0.3} />
      <Shockwave at={h2} size={1600} />
      <Flash at={h2} strength={0.3} />
    </AbsoluteFill>
  );
};
