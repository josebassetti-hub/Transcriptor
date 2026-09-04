import React from "react";
import { interpolate, useCurrentFrame, Easing } from "remotion";
import { C, FONT } from "../theme";

const ease = Easing.out(Easing.cubic);

/** Trecho de texto onde a palavra AQUI (e variantes) fica em âmbar. */
export const withAccent = (text: string, accent = C.amber) => {
  const parts = text.split(/(AQUI\.?|AQUI,)/g);
  return parts.map((p, i) => (p.startsWith("AQUI") ? <span key={i} style={{ color: accent }}>{p}</span> : <React.Fragment key={i}>{p}</React.Fragment>));
};

type RevealProps = {
  text: React.ReactNode;
  /** frame (dentro da cena) em que o texto começa a entrar */
  from: number;
  /** frame em que começa a sair (opcional) */
  until?: number;
  size?: number;
  weight?: 400 | 500 | 700 | 800;
  color?: string;
  metallic?: boolean;
  upper?: boolean;
  tracking?: number; // em
  align?: "left" | "center" | "right";
  maxWidth?: number;
  lineHeight?: number;
  duration?: number; // frames da entrada
  style?: React.CSSProperties;
};

/** Texto que entra por máscara horizontal (esquerda → direita), com brilho metálico opcional. */
export const Reveal: React.FC<RevealProps> = ({
  text, from, until, size = 64, weight = 800, color = C.white, metallic = false, upper = true,
  tracking = 0.18, align = "center", maxWidth = 1500, lineHeight = 1.18, duration = 18, style,
}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + duration], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const out = until === undefined ? 1 : interpolate(frame, [until, until + 10], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  if (frame < from || out <= 0) return null;
  const shine = interpolate(frame, [from + 4, from + duration + 22], [-60, 160], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const metallicStyle: React.CSSProperties = metallic
    ? {
        backgroundImage: `linear-gradient(100deg, ${C.silverDark} 0%, ${C.silver} 35%, #ffffff 50%, ${C.silver} 65%, ${C.silverDark} 100%)`,
        backgroundSize: "220% 100%",
        backgroundPosition: `${shine}% 0`,
        WebkitBackgroundClip: "text",
        backgroundClip: "text",
        color: "transparent",
      }
    : { color };
  return (
    <div
      style={{
        fontFamily: FONT, fontWeight: weight, fontSize: size, textTransform: upper ? "uppercase" : "none",
        letterSpacing: `${tracking}em`, textAlign: align, maxWidth, lineHeight, opacity: out,
        clipPath: `inset(0 ${(1 - t) * 100}% 0 0)`, transform: `translateY(${(1 - t) * 14}px)`,
        textShadow: metallic ? undefined : "0 4px 24px rgba(0,0,0,0.55)",
        ...metallicStyle, ...style,
      }}
    >
      {text}
    </div>
  );
};

/** Texto de apoio: fade + deslocamento de 20 px. */
export const Fade: React.FC<{
  text: React.ReactNode; from: number; until?: number; size?: number; weight?: 400 | 500 | 700 | 800;
  color?: string; align?: "left" | "center" | "right"; maxWidth?: number; italic?: boolean; style?: React.CSSProperties; upper?: boolean; tracking?: number;
}> = ({ text, from, until, size = 34, weight = 500, color = C.white, align = "center", maxWidth = 1300, italic = false, style, upper = false, tracking = 0.02 }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const out = until === undefined ? 1 : interpolate(frame, [until, until + 10], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  if (frame < from || out <= 0) return null;
  return (
    <div style={{
      fontFamily: FONT, fontWeight: weight, fontSize: size, color, textAlign: align, maxWidth, lineHeight: 1.35,
      opacity: t * out, transform: `translateY(${(1 - t) * 20}px)`, fontStyle: italic ? "italic" : "normal",
      textTransform: upper ? "uppercase" : "none", letterSpacing: `${tracking}em`,
      textShadow: "0 3px 18px rgba(0,0,0,0.6)", ...style,
    }}>
      {text}
    </div>
  );
};

/** Linha fina prata que se desenha (mesmo detalhe da vinheta sob "APRESENTA"). */
export const Rule: React.FC<{ from: number; width?: number; style?: React.CSSProperties }> = ({ from, width = 520, style }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  if (frame < from) return null;
  return <div style={{ height: 2, width: width * t, background: `linear-gradient(90deg, transparent, ${C.silver}, transparent)`, ...style }} />;
};

/** Escurecimento de entrada/saída de cena (fade de 8 frames). */
export const SceneFade: React.FC<{ durationInFrames: number; inFrames?: number; outFrames?: number }> = ({ durationInFrames, inFrames = 8, outFrames = 0 }) => {
  const frame = useCurrentFrame();
  const a = interpolate(frame, [0, inFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const b = outFrames > 0 ? interpolate(frame, [durationInFrames - outFrames, durationInFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
  const o = Math.max(a, b);
  if (o <= 0) return null;
  return <div style={{ position: "absolute", inset: 0, background: "#000", opacity: o, zIndex: 50 }} />;
};
