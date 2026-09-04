import React from "react";
import { AbsoluteFill } from "remotion";
import { LETTERBOX } from "../theme";

/** Área segura entre as barras, com padding lateral. */
export const Safe: React.FC<{
  children: React.ReactNode;
  justify?: "flex-start" | "center" | "flex-end" | "space-between";
  align?: "flex-start" | "center" | "flex-end";
  padX?: number;
  padY?: number;
  style?: React.CSSProperties;
}> = ({ children, justify = "center", align = "center", padX = 120, padY = 60, style }) => (
  <AbsoluteFill
    style={{
      top: LETTERBOX, bottom: LETTERBOX, height: "auto",
      display: "flex", flexDirection: "column", justifyContent: justify, alignItems: align,
      padding: `${padY}px ${padX}px`, boxSizing: "border-box", ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);
