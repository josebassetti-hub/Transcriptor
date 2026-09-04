import { interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";

/** Entrada suave: opacidade 0→1 e deslocamento vertical, a partir de `delay` frames. */
export const useEnter = (delay: number, opts?: { dist?: number; damping?: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - delay,
    fps,
    config: { damping: opts?.damping ?? 200, stiffness: 90, mass: 0.9 },
  });
  const opacity = interpolate(frame - delay, [0, 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const y = (1 - p) * (opts?.dist ?? 36);
  return { opacity, transform: `translateY(${y}px)`, progress: p };
};

/** Opacidade da cena: fade-in nos primeiros `inF` frames e fade-out nos últimos `outF`. */
export const useSceneFade = (duration: number, inF = 12, outF = 12) => {
  const frame = useCurrentFrame();
  return interpolate(
    frame,
    [0, inF, duration - outF, duration],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) },
  );
};
