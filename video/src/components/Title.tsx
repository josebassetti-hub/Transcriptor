import React from "react";
import { useEnter } from "./anim";
import { font, theme } from "../theme";

/** Título de cena com sublinhado azul que se estende. */
export const Title: React.FC<{ text: string; sub?: string; delay?: number; align?: "left" | "center" }> = ({
  text,
  sub,
  delay = 0,
  align = "left",
}) => {
  const a = useEnter(delay);
  const b = useEnter(delay + 8);
  return (
    <div style={{ textAlign: align, fontFamily: font.family }}>
      <div
        style={{
          ...a,
          fontSize: 64,
          fontWeight: 800,
          color: theme.white,
          letterSpacing: -1,
          lineHeight: 1.1,
        }}
      >
        {text}
      </div>
      <div
        style={{
          height: 6,
          width: 140 * a.progress,
          background: `linear-gradient(90deg, ${theme.blue}, ${theme.blueLight})`,
          borderRadius: 3,
          margin: align === "center" ? "18px auto 0" : "18px 0 0",
        }}
      />
      {sub ? (
        <div style={{ ...b, fontSize: 30, color: theme.muted, marginTop: 16, fontWeight: 500 }}>{sub}</div>
      ) : null}
    </div>
  );
};
