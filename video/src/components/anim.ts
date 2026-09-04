import { Easing, interpolate, spring } from "remotion";

/** Progresso 0→1 com mola, sem hook (pode ser usado dentro de map). */
export const springAt = (frame: number, fps: number, delay: number, cfg?: { damping?: number; stiffness?: number; mass?: number }) =>
  spring({ frame: frame - delay, fps, config: { damping: cfg?.damping ?? 200, stiffness: cfg?.stiffness ?? 90, mass: cfg?.mass ?? 0.9 } });

/** Entrada "slam": escala grande + blur → nítido. Usado para tipografia cinética. */
export const slamIn = (frame: number, delay: number, dur = 9): React.CSSProperties => {
  const p = interpolate(frame - delay, [0, dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return {
    opacity: p,
    transform: `scale(${1.55 - 0.55 * p})`,
    filter: `blur(${(1 - p) * 18}px)`,
  };
};

/** Saída rápida: sobe e desfoca. */
export const slamOut = (frame: number, at: number, dur = 8): React.CSSProperties => {
  const p = interpolate(frame - at, [0, dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
  return {
    opacity: 1 - p,
    transform: `translateY(${-90 * p}px) scale(${1 + 0.15 * p})`,
    filter: `blur(${p * 14}px)`,
  };
};

/** Entrada suave de baixo para cima. */
export const riseIn = (frame: number, delay: number, dur = 14, dist = 40): React.CSSProperties => {
  const p = interpolate(frame - delay, [0, dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return { opacity: p, transform: `translateY(${(1 - p) * dist}px)` };
};

export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
