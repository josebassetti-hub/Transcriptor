import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Camera } from "../components/Camera";
import { Particles, RisingLine, Shockwave, Flash } from "../components/Fx";
import { riseIn, slamIn } from "../components/anim";
import { ABERTURA, BEAT, SCENES } from "../content";
import { font, theme } from "../theme";

/** Cena 1: abertura fria. A linha ascendente do logo se desenha, barras sobem, "CRESCER." bate no tempo 3. */
export const Abertura: React.FC = () => {
  const frame = useCurrentFrame();
  const hit = BEAT * 3; // 54
  const lineOpacity = interpolate(frame, [hit, hit + 10], [1, 0.35], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ fontFamily: font.family }}>
      <Camera duration={SCENES.abertura} from={1.12} to={1} panX={-30}>
        <Particles count={60} speed={0.8} seed="a" />
        <div style={{ position: "absolute", left: 210, top: 260, opacity: lineOpacity }}>
          <RisingLine at={4} />
        </div>
      </Camera>
      <div style={{ position: "absolute", left: 0, right: 0, top: 300, textAlign: "center", ...riseIn(frame, BEAT * 1, 14, 30) }}>
        <div style={{ fontSize: 44, fontWeight: 500, color: theme.muted, letterSpacing: 6, textTransform: "uppercase" }}>{ABERTURA.pre}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 380, textAlign: "center", ...slamIn(frame, hit) }}>
        <div style={{ fontSize: 300, fontWeight: 900, color: theme.white, letterSpacing: -12, lineHeight: 1, textShadow: `0 0 80px ${theme.glow}` }}>
          {ABERTURA.palavra}
        </div>
      </div>
      <Shockwave at={hit} />
      <Flash at={hit} strength={0.35} />
    </AbsoluteFill>
  );
};
