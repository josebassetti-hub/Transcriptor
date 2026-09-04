import React from "react";
import { AbsoluteFill } from "remotion";
import { LETTERBOX } from "../theme";

/** Barras cinematográficas iguais às da vinheta, por cima de tudo. */
export const Letterbox: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none", zIndex: 100 }}>
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: LETTERBOX, background: "#000" }} />
    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: LETTERBOX, background: "#000" }} />
  </AbsoluteFill>
);
