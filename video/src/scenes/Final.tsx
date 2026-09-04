import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Logo } from "../components/Logo";
import { Particles, Shockwave, Flash } from "../components/Fx";
import { riseIn, springAt } from "../components/anim";
import { BEAT, EMPRESA, SCENES } from "../content";
import { font, theme } from "../theme";

/** Cena 8: revelação do logo com varredura de luz, frase final e telefones. Fade-out no fim. */
export const Final: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = springAt(frame, fps, 0, { damping: 18, stiffness: 110, mass: 0.9 });
  const sweep = interpolate(frame, [10, 40], [-60, 160], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const end = SCENES.final;
  const fadeOut = interpolate(frame, [end - 24, end], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pulse = 1 + 0.06 * Math.sin((frame / BEAT) * Math.PI * 2);
  return (
    <AbsoluteFill style={{ fontFamily: font.family, opacity: fadeOut, alignItems: "center", justifyContent: "center", textAlign: "center" }}>
      <Particles count={60} speed={0.7} seed="f" />
      <div style={{ position: "relative", transform: `scale(${0.7 + 0.3 * p})`, opacity: Math.min(1, p * 1.5) }}>
        <Logo width={680} />
        {/* varredura de luz sobre o logo */}
        <div style={{ position: "absolute", inset: 0, borderRadius: 28, overflow: "hidden", pointerEvents: "none" }}>
          <div style={{ position: "absolute", top: -100, bottom: -100, left: `${sweep}%`, width: 160, transform: "rotate(20deg)", background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.75), transparent)" }} />
        </div>
      </div>
      <div style={{ marginTop: 64, fontSize: 60, fontWeight: 800, color: theme.white, letterSpacing: -1.5, ...riseIn(frame, BEAT * 1.5, 14, 40) }}>{EMPRESA.fraseFinal}</div>
      <div style={{ marginTop: 40, display: "flex", gap: 44, alignItems: "center", ...riseIn(frame, BEAT * 3, 14, 30) }}>
        {EMPRESA.telefones.map((t, i) => (
          <React.Fragment key={t}>
            {i > 0 ? <div style={{ width: 12, height: 12, borderRadius: 6, background: theme.blueLight, transform: `scale(${pulse})`, boxShadow: `0 0 20px ${theme.glow}` }} /> : null}
            <div style={{ fontSize: 46, fontWeight: 700, color: theme.blueLight, fontVariantNumeric: "tabular-nums", letterSpacing: 1 }}>{t}</div>
          </React.Fragment>
        ))}
      </div>
      <Shockwave at={0} size={2000} />
      <Flash at={0} strength={0.45} />
    </AbsoluteFill>
  );
};
