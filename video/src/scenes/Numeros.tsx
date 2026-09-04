import React from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from "remotion";
import { Camera } from "../components/Camera";
import { Counter } from "../components/Counter";
import { Particles, Shockwave, Flash } from "../components/Fx";
import { riseIn } from "../components/anim";
import { BEAT, EMPRESA, SCENES } from "../content";
import { font, theme } from "../theme";

/** Cena 7: contador +1.000 com barras subindo (eco do logo) e explosão de partículas no fim da contagem. */
export const Numeros: React.FC = () => {
  const frame = useCurrentFrame();
  const countDur = BEAT * 4; // 72
  const done = 6 + countDur;
  const bars = Array.from({ length: 14 });
  return (
    <AbsoluteFill style={{ fontFamily: font.family, overflow: "hidden" }}>
      <Camera duration={SCENES.numeros} from={1} to={1.1} panY={-15}>
        <Particles count={40} speed={1} seed="n" />
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 560, display: "flex", alignItems: "flex-end", gap: 26, padding: "0 60px" }}>
          {bars.map((_, i) => {
            const h = interpolate(frame - i * 3, [0, 60], [0, 120 + i * 30 + random(`b${i}`) * 60], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
            return <div key={i} style={{ flex: 1, height: h, borderRadius: "8px 8px 0 0", background: `linear-gradient(180deg, rgba(95,179,232,0.35), rgba(46,127,192,0.05))`, border: "1px solid rgba(255,255,255,0.10)", borderBottom: "none" }} />;
          })}
        </div>
      </Camera>
      <div style={{ position: "absolute", left: 0, right: 0, top: 200, textAlign: "center", ...riseIn(frame, 0, 12, 30) }}>
        <div style={{ fontSize: 40, fontWeight: 700, color: theme.blueLight, letterSpacing: 10, textTransform: "uppercase" }}>{EMPRESA.desde}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 270, textAlign: "center", ...riseIn(frame, 4, 14, 60) }}>
        <div style={{ fontSize: 400, fontWeight: 900, color: theme.white, letterSpacing: -18, lineHeight: 1, textShadow: `0 0 90px ${theme.glow}` }}>
          <Counter to={EMPRESA.operacoes} delay={6} duration={countDur} prefix="+" />
        </div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 720, textAlign: "center", ...riseIn(frame, 20, 14, 30) }}>
        <div style={{ fontSize: 60, fontWeight: 500, color: theme.white }}>{EMPRESA.operacoesLabel}</div>
      </div>
      <Shockwave at={done} size={2200} />
      <Flash at={done} strength={0.4} />
    </AbsoluteFill>
  );
};
