import React from "react";
import { useCurrentFrame } from "remotion";
import { riseIn } from "./anim";
import { font, theme } from "../theme";

/** Rótulo pequeno em caixa alta com traço azul (canto superior esquerdo). */
export const Kicker: React.FC<{ text: string; delay?: number; style?: React.CSSProperties }> = ({ text, delay = 0, style }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: "absolute", top: 90, left: 120, display: "flex", alignItems: "center", gap: 18, fontFamily: font.family, ...riseIn(frame, delay, 12, 20), ...style }}>
      <div style={{ width: 54, height: 5, background: theme.blueLight, borderRadius: 3 }} />
      <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: 5, color: theme.blueLight, textTransform: "uppercase" }}>{text}</div>
    </div>
  );
};
