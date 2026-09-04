import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Camera } from "../components/Camera";
import { Counter } from "../components/Counter";
import { Particles, Shockwave, Flash } from "../components/Fx";
import { Kicker } from "../components/Kicker";
import { riseIn, slamIn, slamOut } from "../components/anim";
import { BEAT, INCENTIVOS, SCENES } from "../content";
import { font, theme } from "../theme";

const STEP = BEAT * 6; // 108 frames por "hit"

/** Cena 5: três hits de números gigantes (67,5% / 27% / ICMS) com raios girando ao fundo. */
export const Incentivos: React.FC = () => {
  const frame = useCurrentFrame();
  const rays = Array.from({ length: 24 });
  return (
    <AbsoluteFill style={{ fontFamily: font.family, overflow: "hidden" }}>
      <Camera duration={SCENES.incentivos} from={1} to={1.08}>
        <Particles count={50} speed={1.2} seed="i" />
        <div style={{ position: "absolute", left: "50%", top: "50%", width: 0, height: 0, transform: `rotate(${frame * 0.2}deg)` }}>
          {rays.map((_, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                left: 0,
                top: -3,
                width: 1400,
                height: 6,
                transformOrigin: "0 50%",
                transform: `rotate(${(360 / rays.length) * i}deg)`,
                background: `linear-gradient(90deg, rgba(95,179,232,0.0), rgba(95,179,232,${i % 2 ? 0.10 : 0.05}), transparent)`,
              }}
            />
          ))}
        </div>
      </Camera>
      <Kicker text={INCENTIVOS.titulo} />
      {INCENTIVOS.hits.map((h, i) => {
        const at = i * STEP;
        const out = i < INCENTIVOS.hits.length - 1 ? (i + 1) * STEP - 6 : SCENES.incentivos + 40;
        if (frame < at || frame > out + 12) return null;
        const outS = frame >= out ? slamOut(frame, out) : {};
        return (
          <div key={h.rotulo} style={{ position: "absolute", inset: 0, ...outS }}>
            <div style={{ position: "absolute", left: 0, right: 0, top: 250, textAlign: "center", ...riseIn(frame, at + 4, 10, 20) }}>
              <div style={{ fontSize: 40, fontWeight: 700, color: theme.blueLight, letterSpacing: 10 }}>{h.rotulo}</div>
            </div>
            <div style={{ position: "absolute", left: 0, right: 0, top: 320, textAlign: "center", ...slamIn(frame, at, 10) }}>
              <div style={{ fontSize: h.valor !== null ? 400 : 330, fontWeight: 900, color: theme.white, letterSpacing: -18, lineHeight: 1, textShadow: `0 0 90px ${theme.glow}` }}>
                {h.valor !== null ? <Counter to={h.valor} from={h.valor * 0.6} delay={at} duration={26} decimals={h.valor % 1 === 0 ? 0 : 1} suffix={h.sufixo} /> : h.texto}
              </div>
            </div>
            <div style={{ position: "absolute", left: 0, right: 0, top: 760, textAlign: "center", ...riseIn(frame, at + 10, 12, 30) }}>
              <div style={{ fontSize: 54, fontWeight: 500, color: theme.white }}>{h.desc}</div>
            </div>
          </div>
        );
      })}
      {INCENTIVOS.hits.map((_, i) => (
        <React.Fragment key={i}>
          <Shockwave at={i * STEP} size={1800} />
          <Flash at={i * STEP} strength={0.3} />
        </React.Fragment>
      ))}
      <div style={{ position: "absolute", bottom: 60, left: 0, right: 0, textAlign: "center", fontSize: 24, color: theme.muted, opacity: interpolate(frame, [30, 50], [0, 0.9], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        {INCENTIVOS.rodape}
      </div>
    </AbsoluteFill>
  );
};
