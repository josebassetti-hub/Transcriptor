import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Camera } from "../components/Camera";
import { Particles } from "../components/Fx";
import { Kicker } from "../components/Kicker";
import { springAt } from "../components/anim";
import { BEAT, PORQUE, SCENES } from "../content";
import { font, theme } from "../theme";

/** Cena 6: quatro cartões em 3D voam da direita e se encaixam, com leve inclinação constante. */
export const Porque: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const drift = interpolate(frame, [0, SCENES.porque], [-3, 3]);
  return (
    <AbsoluteFill style={{ fontFamily: font.family, overflow: "hidden" }}>
      <Camera duration={SCENES.porque} from={1.05} to={1} panX={-25}>
        <Particles count={45} speed={0.9} seed="q" />
      </Camera>
      <Kicker text={PORQUE.titulo} />
      <div style={{ position: "absolute", left: 120, right: 120, top: 220, bottom: 140, perspective: 1400 }}>
        <div style={{ position: "absolute", inset: 0, transform: `rotateY(${drift}deg)`, transformStyle: "preserve-3d", display: "grid", gridTemplateColumns: "1fr 1fr", gridTemplateRows: "1fr 1fr", gap: 40 }}>
          {PORQUE.itens.map((it, i) => {
            const at = 6 + i * BEAT;
            const p = springAt(frame, fps, at, { damping: 16, stiffness: 120, mass: 0.8 });
            const tx = (1 - p) * 900;
            const ry = (1 - p) * 55;
            const op = interpolate(frame - at, [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            const check = interpolate(frame - at - 8, [0, 12], [40, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
            return (
              <div
                key={it.titulo}
                style={{
                  opacity: op,
                  transform: `translateX(${tx}px) rotateY(${ry}deg)`,
                  transformStyle: "preserve-3d",
                  background: "linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04))",
                  border: "1px solid rgba(255,255,255,0.18)",
                  borderRadius: 28,
                  padding: "44px 52px",
                  display: "flex",
                  gap: 34,
                  alignItems: "center",
                  boxShadow: "0 30px 80px rgba(0,0,0,0.45)",
                }}
              >
                <svg width="84" height="84" viewBox="0 0 56 56" style={{ flexShrink: 0 }}>
                  <circle cx="28" cy="28" r="26" fill={theme.blue} />
                  <path d="M16 29 L25 37 L41 20" fill="none" stroke="#fff" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="40" strokeDashoffset={check} />
                </svg>
                <div>
                  <div style={{ fontSize: 52, fontWeight: 800, color: theme.white, letterSpacing: -1.5, lineHeight: 1.05 }}>{it.titulo}</div>
                  <div style={{ fontSize: 30, color: theme.muted, marginTop: 12 }}>{it.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
