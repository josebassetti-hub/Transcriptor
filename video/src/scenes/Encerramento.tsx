import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Logo } from "../components/Logo";
import { useEnter } from "../components/anim";
import { EMPRESA, SCENES } from "../content";
import { font, theme } from "../theme";

export const Encerramento: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fadeIn = interpolate(frame, [0, 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const logoIn = spring({ frame: frame - 4, fps, config: { damping: 200, stiffness: 70 } });
  const frase = useEnter(30);
  const tel = useEnter(58);
  const end = SCENES.encerramento.duration;
  const fadeOut = interpolate(frame, [end - 20, end], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: fadeIn * fadeOut, alignItems: "center", justifyContent: "center", fontFamily: font.family, textAlign: "center" }}>
      <div style={{ transform: `scale(${0.94 + 0.06 * logoIn})`, opacity: logoIn }}>
        <Logo width={600} />
      </div>
      <div style={{ ...frase, marginTop: 60, fontSize: 52, fontWeight: 700, color: theme.white, letterSpacing: -1 }}>
        {EMPRESA.fraseFinal}
      </div>
      <div style={{ ...tel, marginTop: 34, display: "flex", gap: 40, alignItems: "center" }}>
        {EMPRESA.telefones.map((t, i) => (
          <React.Fragment key={t}>
            {i > 0 ? <div style={{ width: 8, height: 8, borderRadius: 4, background: theme.blueLight }} /> : null}
            <div style={{ fontSize: 40, fontWeight: 600, color: theme.blueLight, fontVariantNumeric: "tabular-nums" }}>{t}</div>
          </React.Fragment>
        ))}
      </div>
    </AbsoluteFill>
  );
};
