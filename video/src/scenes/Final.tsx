import React from "react";
import { AbsoluteFill, Img, interpolate, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { riseIn, springAt } from "../components/anim";
import { BEAT, EMPRESA, SCENES } from "../content";
import { font, theme } from "../theme";

/** Cena final: cartão de encerramento claro. Logo original sem moldura, frase e telefones. Fade-out no fim. */
export const Final: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = springAt(frame, fps, 2, { damping: 16, stiffness: 100, mass: 0.9 });
  const sweep = interpolate(frame, [12, 46], [-40, 140], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const end = SCENES.final;
  const fadeOut = interpolate(frame, [end - 24, end], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pulse = 1 + 0.06 * Math.sin((frame / BEAT) * Math.PI * 2);
  const drift = frame / 30;
  return (
    <AbsoluteFill style={{ fontFamily: font.family, background: "#F5F7FA" }}>
      {/* fundo claro com brilhos azuis suaves em movimento */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(1000px 700px at ${28 + 6 * Math.sin(drift * 0.4)}% ${25 + 5 * Math.cos(drift * 0.3)}%, rgba(95,179,232,0.22), transparent 65%),
                       radial-gradient(900px 600px at ${78 - 5 * Math.sin(drift * 0.25)}% ${80 + 4 * Math.sin(drift * 0.35)}%, rgba(31,47,107,0.14), transparent 65%),
                       linear-gradient(160deg, #FFFFFF 0%, #F1F4F9 55%, #E6ECF4 100%)`,
        }}
      />
      {/* partículas claras */}
      <AbsoluteFill>
        {Array.from({ length: 40 }).map((_, i) => {
          const x = random(`fx${i}`) * 100;
          const y = ((random(`fy${i}`) * 120 - (frame * (0.4 + random(`fv${i}`))) / 14) % 120 + 120) % 120 - 10;
          const s = 3 + random(`fs${i}`) * 5;
          return <div key={i} style={{ position: "absolute", left: `${x}%`, top: `${y}%`, width: s, height: s, borderRadius: s, background: theme.blue, opacity: 0.12 + random(`fo${i}`) * 0.2 }} />;
        })}
      </AbsoluteFill>
      <AbsoluteFill style={{ opacity: fadeOut, alignItems: "center", justifyContent: "center", textAlign: "center" }}>
        <div style={{ position: "relative", transform: `scale(${0.8 + 0.2 * p})`, opacity: Math.min(1, p * 1.4), width: 860 }}>
          <Img src={staticFile("logo.png")} style={{ width: 860, display: "block", filter: "drop-shadow(0 20px 40px rgba(31,47,107,0.18))" }} />
          <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
            <div style={{ position: "absolute", top: -100, bottom: -100, left: `${sweep}%`, width: 180, transform: "rotate(20deg)", background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.85), transparent)" }} />
          </div>
        </div>
        <div style={{ marginTop: 70, fontSize: 60, fontWeight: 800, color: theme.navy, letterSpacing: -1.5, ...riseIn(frame, BEAT * 1.5, 14, 40) }}>{EMPRESA.fraseFinal}</div>
        <div style={{ marginTop: 38, display: "flex", gap: 44, alignItems: "center", ...riseIn(frame, BEAT * 3, 14, 30) }}>
          {EMPRESA.telefones.map((t, i) => (
            <React.Fragment key={t}>
              {i > 0 ? <div style={{ width: 12, height: 12, borderRadius: 6, background: theme.blue, transform: `scale(${pulse})` }} /> : null}
              <div style={{ fontSize: 48, fontWeight: 700, color: theme.blue, fontVariantNumeric: "tabular-nums", letterSpacing: 1 }}>{t}</div>
            </React.Fragment>
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
