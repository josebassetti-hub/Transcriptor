import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { useEnter, useSceneFade } from "../components/anim";
import { DESAFIO, SCENES } from "../content";
import { font, theme } from "../theme";

const Icon: React.FC<{ kind: number; delay: number }> = ({ kind, delay }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - delay, [0, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const stroke = theme.blueLight;
  if (kind === 0) {
    // expansão: seta subindo com barras
    return (
      <svg width="120" height="120" viewBox="0 0 120 120">
        {[0, 1, 2, 3].map((i) => (
          <rect key={i} x={14 + i * 24} y={100 - (20 + i * 18) * p} width="16" height={(20 + i * 18) * p} rx="3" fill={theme.blue} opacity={0.9} />
        ))}
        <path d="M14 78 L46 52 L66 66 L104 24" fill="none" stroke={stroke} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="160" strokeDashoffset={160 * (1 - p)} />
        <path d="M84 24 L104 24 L104 44" fill="none" stroke={stroke} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" opacity={p} />
      </svg>
    );
  }
  if (kind === 1) {
    // modernização: engrenagem
    return (
      <svg width="120" height="120" viewBox="0 0 120 120" style={{ transform: `rotate(${p * 90}deg)` }}>
        {[...Array(8)].map((_, i) => (
          <rect key={i} x="54" y="8" width="12" height="22" rx="3" fill={theme.blue} transform={`rotate(${i * 45} 60 60)`} />
        ))}
        <circle cx="60" cy="60" r="30" fill="none" stroke={stroke} strokeWidth="8" strokeDasharray="190" strokeDashoffset={190 * (1 - p)} />
        <circle cx="60" cy="60" r="10" fill={stroke} opacity={p} />
      </svg>
    );
  }
  // capital de giro: ciclo de setas
  return (
    <svg width="120" height="120" viewBox="0 0 120 120">
      <path d="M92 44 A36 36 0 0 0 28 44" fill="none" stroke={theme.blue} strokeWidth="8" strokeLinecap="round" strokeDasharray="120" strokeDashoffset={120 * (1 - p)} />
      <path d="M28 76 A36 36 0 0 0 92 76" fill="none" stroke={stroke} strokeWidth="8" strokeLinecap="round" strokeDasharray="120" strokeDashoffset={120 * (1 - p)} />
      <path d="M92 26 L92 46 L72 46" fill="none" stroke={theme.blue} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" opacity={p} />
      <path d="M28 94 L28 74 L48 74" fill="none" stroke={stroke} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" opacity={p} />
    </svg>
  );
};

export const Desafio: React.FC = () => {
  const fade = useSceneFade(SCENES.desafio.duration);
  const l1 = useEnter(6);
  const l2 = useEnter(40);
  return (
    <AbsoluteFill style={{ opacity: fade, justifyContent: "center", padding: "0 160px", fontFamily: font.family }}>
      <div style={{ ...l1, fontSize: 84, fontWeight: 800, color: theme.white, letterSpacing: -2, lineHeight: 1.05 }}>
        {DESAFIO.linha1}
      </div>
      <div style={{ ...l2, fontSize: 56, fontWeight: 500, color: theme.blueLight, marginTop: 22, letterSpacing: -0.5 }}>
        {DESAFIO.linha2}
      </div>
      <div style={{ display: "flex", gap: 90, marginTop: 90 }}>
        {DESAFIO.itens.map((it, i) => {
          const e = useEnter(90 + i * 14);
          return (
            <div key={it} style={{ ...e, display: "flex", alignItems: "center", gap: 26 }}>
              <Icon kind={i} delay={96 + i * 14} />
              <div style={{ fontSize: 34, fontWeight: 600, color: theme.white }}>{it}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
