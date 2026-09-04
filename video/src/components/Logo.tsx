import React from "react";
import { Img, staticFile } from "remotion";

/** Logo Projet (PNG com fundo transparente gerado a partir de public/logo.jpg). */
export const Logo: React.FC<{ width?: number; style?: React.CSSProperties }> = ({ width = 640, style }) => (
  <div
    style={{
      background: "#FFFFFF",
      borderRadius: 28,
      padding: `${width * 0.06}px ${width * 0.08}px`,
      boxShadow: "0 30px 80px rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.35) inset",
      display: "inline-block",
      ...style,
    }}
  >
    <Img src={staticFile("logo.png")} style={{ width, display: "block" }} />
  </div>
);
