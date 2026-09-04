import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Camera } from "../components/Camera";
import { Chapter } from "../components/Chapter";
import { Hits } from "../components/Hits";
import { Particles } from "../components/Fx";
import { Kicker } from "../components/Kicker";
import { INCENTIVOS, SCENES } from "../content";
import { font, theme } from "../theme";

/** Capítulo 02: incentivos fiscais. Abertura de capítulo e três hits de números gigantes com raios ao fundo. */
export const Incentivos: React.FC = () => {
  const frame = useCurrentFrame();
  const rays = Array.from({ length: 24 });
  const foot = interpolate(frame - INCENTIVOS.abertura, [30, 50], [0, 0.9], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
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
      <Chapter numero={INCENTIVOS.numero} titulo={INCENTIVOS.titulo} sub={INCENTIVOS.sub} duration={INCENTIVOS.abertura} />
      {frame >= INCENTIVOS.abertura ? <Kicker text={INCENTIVOS.kicker} delay={INCENTIVOS.abertura} /> : null}
      <Hits hits={INCENTIVOS.hits} offset={INCENTIVOS.abertura} sceneDuration={SCENES.incentivos} />
      <div style={{ position: "absolute", bottom: 60, left: 0, right: 0, textAlign: "center", fontSize: 24, color: theme.muted, opacity: foot }}>{INCENTIVOS.rodape}</div>
    </AbsoluteFill>
  );
};
