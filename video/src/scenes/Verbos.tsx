import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Camera } from "../components/Camera";
import { Particles, Shockwave, Flash } from "../components/Fx";
import { riseIn, slamIn, slamOut } from "../components/anim";
import { BEAT, SCENES, VERBOS } from "../content";
import { font, theme } from "../theme";

const STEP = BEAT * 3; // uma palavra a cada 3 tempos (54 frames)

/** Cena 2: tipografia cinética. Três verbos batem em sequência, com placa diagonal cruzando o fundo. */
export const Verbos: React.FC = () => {
  const frame = useCurrentFrame();
  const slabX = interpolate(frame, [0, SCENES.verbos], [-900, 900]);
  return (
    <AbsoluteFill style={{ fontFamily: font.family, overflow: "hidden" }}>
      <Camera duration={SCENES.verbos} from={1} to={1.1} panY={-20}>
        <Particles count={40} speed={1.4} seed="v" />
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            width: 2400,
            height: 520,
            marginLeft: -1200 + slabX,
            marginTop: -260,
            transform: "rotate(-14deg)",
            background: `linear-gradient(90deg, transparent, ${theme.navy}, ${theme.blue}, ${theme.navy}, transparent)`,
            opacity: 0.4,
          }}
        />
      </Camera>
      <div style={{ position: "absolute", left: 140, top: 250, ...riseIn(frame, 2, 12, 24) }}>
        <div style={{ fontSize: 46, fontWeight: 500, color: theme.muted, letterSpacing: 4, textTransform: "uppercase" }}>{VERBOS.pre}</div>
      </div>
      {VERBOS.palavras.map((w, i) => {
        const at = i * STEP;
        const out = i < VERBOS.palavras.length - 1 ? (i + 1) * STEP - 6 : SCENES.verbos + 40;
        const active = frame >= at && frame < out + 10;
        if (!active) return null;
        const inS = slamIn(frame, at);
        const outS = frame >= out ? slamOut(frame, out) : {};
        return (
          <div key={w} style={{ position: "absolute", left: 130, top: 360 }}>
            <div style={{ ...inS }}>
              <div style={{ ...outS, fontSize: 205, fontWeight: 900, color: theme.white, letterSpacing: -8, lineHeight: 1, textShadow: `0 0 70px ${theme.glow}` }}>{w}</div>
            </div>
          </div>
        );
      })}
      {VERBOS.palavras.map((_, i) => (
        <React.Fragment key={i}>
          <Shockwave at={i * STEP} size={1400} />
          <Flash at={i * STEP} strength={0.25} />
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};
