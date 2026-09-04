import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Title } from "../components/Title";
import { useSceneFade } from "../components/anim";
import { ESTRUTURACAO, SCENES } from "../content";
import { font, theme } from "../theme";

const START = 40; // frame em que a timeline começa a acender
const STEP = 52; // frames entre etapas

export const Estruturacao: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useSceneFade(SCENES.estruturacao.duration);
  const n = ESTRUTURACAO.etapas.length;
  const lineP = interpolate(frame, [START, START + STEP * (n - 1)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: fade, padding: "110px 140px", fontFamily: font.family }}>
      <Title text={ESTRUTURACAO.titulo} sub={ESTRUTURACAO.subtitulo} />
      <div style={{ position: "relative", marginTop: 210, height: 480 }}>
        {/* trilho */}
        <div style={{ position: "absolute", left: 0, right: 0, top: 53, height: 4, background: theme.line, borderRadius: 2 }} />
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 53,
            height: 4,
            width: `${lineP * 100}%`,
            background: `linear-gradient(90deg, ${theme.navy}, ${theme.blue}, ${theme.blueLight})`,
            borderRadius: 2,
            boxShadow: `0 0 18px ${theme.blue}`,
          }}
        />
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          {ESTRUTURACAO.etapas.map((et, i) => {
            const d = START + i * STEP;
            const pop = spring({ frame: frame - d, fps, config: { damping: 14, stiffness: 150 } });
            const txt = interpolate(frame - d, [4, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            const ty = (1 - txt) * 24;
            return (
              <div key={et.n} style={{ width: 300, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center" }}>
                <div
                  style={{
                    width: 110,
                    height: 110,
                    borderRadius: 55,
                    background: `linear-gradient(135deg, ${theme.blue}, ${theme.navy})`,
                    border: `4px solid ${theme.bg}`,
                    boxShadow: `0 0 0 4px ${theme.blue}, 0 12px 30px rgba(0,0,0,0.4)`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#fff",
                    fontWeight: 800,
                    fontSize: 40,
                    transform: `scale(${pop})`,
                  }}
                >
                  {et.n}
                </div>
                <div style={{ opacity: txt, transform: `translateY(${ty}px)`, marginTop: 40 }}>
                  <div style={{ fontSize: 34, fontWeight: 700, color: theme.white, lineHeight: 1.15 }}>{et.titulo}</div>
                  <div style={{ fontSize: 25, color: theme.muted, marginTop: 12, lineHeight: 1.3 }}>{et.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
