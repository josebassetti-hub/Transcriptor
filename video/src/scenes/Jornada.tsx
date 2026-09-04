import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { Particles } from "../components/Fx";
import { Kicker } from "../components/Kicker";
import { riseIn, slamIn } from "../components/anim";
import { JORNADA, SCENES } from "../content";
import { font, theme } from "../theme";

const STATION_W = 1500; // distância entre estações (px)
const HOLD = 50; // frames parado em cada estação
const TRAVEL = 18; // frames viajando até a próxima

/** Cena 4: a câmera viaja lateralmente por uma trilha com 5 estações (paralaxe em 3 camadas). */
export const Jornada: React.FC = () => {
  const frame = useCurrentFrame();
  const n = JORNADA.etapas.length;
  const per = HOLD + TRAVEL; // 68
  // posição da câmera (índice da estação, contínuo)
  const seg = Math.min(n - 1, Math.floor(frame / per));
  const local = frame - seg * per;
  const travelP = seg >= n - 1 ? 0 : interpolate(local, [HOLD, HOLD + TRAVEL], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const cam = seg + travelP;
  const x = -cam * STATION_W;
  // pequena inclinação e zoom durante a viagem, para dar "peso" ao movimento
  const tilt = Math.sin(travelP * Math.PI) * 2.2;
  const zoom = 1 + Math.sin(travelP * Math.PI) * 0.06;
  const pathY = 640;
  return (
    <AbsoluteFill style={{ fontFamily: font.family, overflow: "hidden" }}>
      {/* camada de fundo (paralaxe lento) */}
      <div style={{ position: "absolute", inset: 0, transform: `translateX(${x * 0.25}px)` }}>
        <Particles count={90} speed={0.6} seed="j" />
        {JORNADA.etapas.map((et, i) => (
          <div key={et.n} style={{ position: "absolute", left: 560 + i * STATION_W * 0.25 * 4, top: 120, fontSize: 620, fontWeight: 900, color: "rgba(255,255,255,0.035)", letterSpacing: -30, lineHeight: 1 }}>
            {et.n}
          </div>
        ))}
      </div>
      {/* camada principal */}
      <div style={{ position: "absolute", inset: 0, transform: `scale(${zoom}) rotate(${tilt}deg)`, transformOrigin: "50% 60%" }}>
        <div style={{ position: "absolute", inset: 0, transform: `translateX(${x}px)` }}>
          {/* trilha ascendente contínua */}
          <svg width={STATION_W * n + 1920} height={1080} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
            <defs>
              <linearGradient id="jl" x1="0" x2="1">
                <stop offset="0" stopColor={theme.navy} />
                <stop offset="1" stopColor={theme.blueLight} />
              </linearGradient>
            </defs>
            <path
              d={`M -200 ${pathY + 80} ` + JORNADA.etapas.map((_, i) => `L ${960 + i * STATION_W} ${pathY - i * 22}`).join(" ") + ` L ${960 + n * STATION_W} ${pathY - n * 22 - 60}`}
              fill="none"
              stroke="url(#jl)"
              strokeWidth="6"
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity="0.9"
            />
          </svg>
          {JORNADA.etapas.map((et, i) => {
            const cx = 960 + i * STATION_W;
            const cy = pathY - i * 22;
            const arrive = i * per; // frame em que a câmera chega
            const vis = 1 - Math.min(1, Math.max(0, Math.abs(cam - i) - 0.15) * 2.2);
            const ringP = interpolate(frame - arrive, [0, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.back(2)) });
            return (
              <div key={et.n} style={{ position: "absolute", left: cx, top: cy, opacity: vis }}>
                {/* marcador */}
                <div
                  style={{
                    position: "absolute",
                    left: -34,
                    top: -34,
                    width: 68,
                    height: 68,
                    borderRadius: 34,
                    background: theme.blueLight,
                    boxShadow: `0 0 0 14px rgba(95,179,232,0.18), 0 0 50px ${theme.glow}`,
                    transform: `scale(${ringP})`,
                  }}
                />
                {/* número gigante */}
                <div style={{ position: "absolute", left: -60, top: -560, ...slamIn(frame, arrive + 2, 10) }}>
                  <div style={{ fontSize: 260, fontWeight: 900, color: theme.blueLight, letterSpacing: -12, lineHeight: 1, opacity: 0.9, textShadow: `0 0 60px ${theme.glow}` }}>{et.n}</div>
                </div>
                {/* título e descrição */}
                <div style={{ position: "absolute", left: -20, top: -300, width: 1100, ...riseIn(frame, arrive + 8, 12, 40) }}>
                  <div style={{ fontSize: 88, fontWeight: 800, color: theme.white, letterSpacing: -3, lineHeight: 1.02 }}>{et.titulo}</div>
                  <div style={{ fontSize: 38, fontWeight: 500, color: theme.muted, marginTop: 18 }}>{et.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <Kicker text={JORNADA.titulo} delay={0} />
      {/* progresso das etapas (canto superior direito) */}
      <div style={{ position: "absolute", top: 96, right: 120, display: "flex", gap: 12 }}>
        {JORNADA.etapas.map((_, i) => (
          <div key={i} style={{ width: 54, height: 6, borderRadius: 3, background: i <= seg ? theme.blueLight : "rgba(255,255,255,0.15)" }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
