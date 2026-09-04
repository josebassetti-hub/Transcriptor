import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { theme } from "../theme";

/** Fundo contínuo (fora dos cortes): gradiente vivo, feixes de luz e grade em perspectiva. */
export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const x1 = 25 + 12 * Math.sin(t * 0.35);
  const y1 = 30 + 10 * Math.cos(t * 0.27);
  const x2 = 80 - 10 * Math.sin(t * 0.22);
  const y2 = 75 + 8 * Math.sin(t * 0.31);
  const beamX = interpolate(frame, [0, 1800], [-40, 140]);
  const gridY = (frame * 1.6) % 90;
  return (
    <AbsoluteFill style={{ background: `linear-gradient(150deg, ${theme.bg2} 0%, ${theme.bg} 55%, #04091A 100%)` }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(1100px 700px at ${x1}% ${y1}%, rgba(46,127,192,0.35), transparent 65%),
                       radial-gradient(900px 600px at ${x2}% ${y2}%, rgba(31,47,107,0.7), transparent 65%)`,
        }}
      />
      {/* grade em perspectiva no chão, correndo em direção à câmera */}
      <div
        style={{
          position: "absolute",
          left: "-50%",
          right: "-50%",
          bottom: -200,
          height: 700,
          transform: "perspective(900px) rotateX(64deg)",
          transformOrigin: "50% 100%",
          backgroundImage: `linear-gradient(${theme.line} 2px, transparent 2px), linear-gradient(90deg, ${theme.line} 2px, transparent 2px)`,
          backgroundSize: "90px 90px",
          backgroundPosition: `0px ${gridY}px`,
          maskImage: "linear-gradient(to top, rgba(0,0,0,0.9), transparent 90%)",
          WebkitMaskImage: "linear-gradient(to top, rgba(0,0,0,0.9), transparent 90%)",
        }}
      />
      {/* feixe de luz diagonal cruzando o quadro */}
      <div
        style={{
          position: "absolute",
          top: -400,
          bottom: -400,
          left: `${beamX}%`,
          width: 420,
          transform: "rotate(18deg)",
          background: "linear-gradient(90deg, transparent, rgba(95,179,232,0.10), rgba(255,255,255,0.06), rgba(95,179,232,0.10), transparent)",
        }}
      />
    </AbsoluteFill>
  );
};

/** Partículas flutuando (deterministas). */
export const Particles: React.FC<{ count?: number; speed?: number; seed?: string }> = ({ count = 70, speed = 1, seed = "p" }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: count }).map((_, i) => {
        const x = random(`${seed}x${i}`) * 100;
        const y0 = random(`${seed}y${i}`) * 120;
        const s = 2 + random(`${seed}s${i}`) * 5;
        const v = (0.4 + random(`${seed}v${i}`) * 1.2) * speed;
        const y = ((y0 - (frame * v) / 12) % 120 + 120) % 120 - 10;
        const o = 0.15 + random(`${seed}o${i}`) * 0.5;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: s,
              height: s,
              borderRadius: s,
              background: theme.blueLight,
              opacity: o,
              boxShadow: `0 0 ${s * 3}px ${theme.glow}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** Grão de filme + vinheta, por cima de tudo. */
export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.09, mixBlendMode: "overlay" }}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 60} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.55) 100%)" }} />
    </AbsoluteFill>
  );
};

/** Anel de choque que expande a partir do centro (usado nos "hits"). */
export const Shockwave: React.FC<{ at: number; color?: string; size?: number }> = ({ at, color = theme.blueLight, size = 1600 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  if (p <= 0 || p >= 1) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: size * p,
        height: size * p,
        marginLeft: (-size * p) / 2,
        marginTop: (-size * p) / 2,
        borderRadius: "50%",
        border: `${6 * (1 - p)}px solid ${color}`,
        opacity: 1 - p,
        boxShadow: `0 0 60px ${theme.glow}`,
      }}
    />
  );
};

/** Flash branco curto no corte. */
export const Flash: React.FC<{ at: number; strength?: number }> = ({ at, strength = 0.5 }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame - at, [0, 2, 12], [0, strength, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ background: "#fff", opacity: o, pointerEvents: "none" }} />;
};

/** Linha ascendente (eco da seta do logo) desenhada com brilho, e barras crescendo. */
export const RisingLine: React.FC<{ at: number; width?: number; height?: number; style?: React.CSSProperties }> = ({ at, width = 1500, height = 620, style }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - at, [0, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pts = [
    [0, 560],
    [220, 470],
    [420, 520],
    [640, 330],
    [860, 400],
    [1120, 150],
    [1500, 20],
  ];
  const d = pts.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x} ${y}`).join(" ");
  const len = 2200;
  return (
    <svg width={width} height={height} viewBox="0 0 1500 620" style={{ overflow: "visible", ...style }}>
      <defs>
        <linearGradient id="rl" x1="0" x2="1">
          <stop offset="0" stopColor={theme.blue} />
          <stop offset="1" stopColor={theme.blueLight} />
        </linearGradient>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="10" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const bp = interpolate(frame - at - 10 - i * 4, [0, 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const h = (120 + i * 70) * bp;
        return <rect key={i} x={180 + i * 210} y={600 - h} width="90" height={h} rx="6" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.14)" />;
      })}
      <path d={d} fill="none" stroke="url(#rl)" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - p)} filter="url(#glow)" />
      <path d={d} fill="none" stroke="#fff" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - p)} opacity="0.7" />
      <g opacity={p > 0.97 ? 1 : 0}>
        <path d="M1400 20 L1500 20 L1500 120" fill="none" stroke={theme.blueLight} strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" filter="url(#glow)" />
      </g>
    </svg>
  );
};
