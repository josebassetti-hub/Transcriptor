import React from "react";
import { PX_PER_M, type Box } from "./PlantLayout";

/** Escurece/clareia uma cor hex por um fator (−1..1) */
export const shade = (hex: string, f: number) => {
  const n = parseInt(hex.replace("#", ""), 16);
  const ch = (v: number) => {
    const t = f < 0 ? v * (1 + f) : v + (255 - v) * f;
    return Math.max(0, Math.min(255, Math.round(t)));
  };
  const r = ch((n >> 16) & 255);
  const g = ch((n >> 8) & 255);
  const b = ch(n & 255);
  return `rgb(${r},${g},${b})`;
};

type FaceProps = {
  ax: number;
  ay: number;
  bx: number;
  by: number;
  z: number;
  h: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
};

/**
 * Face vertical apoiada na aresta A→B (metros) a partir da altura z, com altura h.
 * A normal aponta para a esquerda do sentido A→B (regra: front = aresta de (0,d) a (w,d)).
 */
export const WallFace: React.FC<FaceProps> = ({ ax, ay, bx, by, z, h, style, children }) => {
  const L = Math.hypot(bx - ax, by - ay) * PX_PER_M;
  const phi = (Math.atan2(by - ay, bx - ax) * 180) / Math.PI;
  const H = h * PX_PER_M;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: L,
        height: H,
        transformOrigin: "0 100%",
        transform: `translate3d(${ax * PX_PER_M}px, ${ay * PX_PER_M - H}px, ${z * PX_PER_M}px) rotateZ(${phi}deg) rotateX(-90deg)`,
        backfaceVisibility: "visible",
        overflow: "hidden",
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Face horizontal (plano do chão) no retângulo dado, à altura z. */
export const FloorFace: React.FC<{
  x: number;
  y: number;
  w: number;
  d: number;
  z: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}> = ({ x, y, w, d, z, style, children }) => (
  <div
    style={{
      position: "absolute",
      left: x * PX_PER_M,
      top: y * PX_PER_M,
      width: w * PX_PER_M,
      height: d * PX_PER_M,
      transform: `translateZ(${z * PX_PER_M}px)`,
      backfaceVisibility: "visible",
      overflow: "hidden",
      ...style,
    }}
  >
    {children}
  </div>
);

type Box3DProps = {
  box: Box;
  color: string;
  /** face frontal (voltada para +y) pode receber conteúdo, ex.: vídeo */
  front?: React.ReactNode;
  topStyle?: React.CSSProperties;
  opacity?: number;
  /** cor da faixa de destaque no topo (ex.: tremonha amarela) */
  accent?: string;
};

/** Caixa com 5 faces visíveis (sem fundo). */
export const Box3D: React.FC<Box3DProps> = ({ box, color, front, topStyle, opacity = 1, accent }) => {
  const { x, y, w, d, h } = box;
  const z = box.z ?? 0;
  const faceStyle = (f: number): React.CSSProperties => ({ background: shade(color, f), opacity });
  return (
    <>
      {/* frente (y = d) */}
      <WallFace ax={x} ay={y + d} bx={x + w} by={y + d} z={z} h={h} style={faceStyle(0.02)}>
        {front}
      </WallFace>
      {/* direita (x = w) */}
      <WallFace ax={x + w} ay={y + d} bx={x + w} by={y} z={z} h={h} style={faceStyle(-0.28)} />
      {/* esquerda (x = 0) */}
      <WallFace ax={x} ay={y} bx={x} by={y + d} z={z} h={h} style={faceStyle(-0.12)} />
      {/* fundo (y = 0) */}
      <WallFace ax={x + w} ay={y} bx={x} by={y} z={z} h={h} style={faceStyle(-0.35)} />
      {/* topo */}
      <FloorFace x={x} y={y} w={w} d={d} z={z + h} style={{ background: shade(accent ?? color, 0.18), opacity, ...topStyle }} />
    </>
  );
};

/** Prisma poligonal regular (silo). */
export const Cylinder3D: React.FC<{ box: Box; color: string; accent?: string; sides?: number; opacity?: number }> = ({
  box,
  color,
  accent,
  sides = 12,
  opacity = 1,
}) => {
  const cx = box.x + box.w / 2;
  const cy = box.y + box.d / 2;
  const r = box.w / 2;
  const z = box.z ?? 0;
  const pts = Array.from({ length: sides }, (_, i) => {
    const a = (i / sides) * Math.PI * 2;
    return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
  });
  return (
    <>
      {pts.map((p, i) => {
        const q = pts[(i + 1) % sides];
        const light = 0.5 * Math.sin(((i + 0.5) / sides) * Math.PI * 2 + Math.PI / 2);
        const isLadder = accent && i === Math.floor(sides * 0.7);
        return (
          <WallFace
            key={i}
            ax={q.x}
            ay={q.y}
            bx={p.x}
            by={p.y}
            z={z}
            h={box.h}
            style={{ background: isLadder ? accent : shade(color, light * 0.4 - 0.1), opacity }}
          />
        );
      })}
      <FloorFace
        x={cx - r}
        y={cy - r}
        w={2 * r}
        d={2 * r}
        z={z + box.h}
        style={{ background: shade(color, 0.25), borderRadius: "50%", opacity }}
      />
    </>
  );
};
