import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { theme } from "../theme";

/** Fundo azul-marinho com gradiente, brilhos suaves em movimento lento e grade discreta. */
export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const x1 = 30 + 6 * Math.sin(t * 0.25);
  const y1 = 25 + 5 * Math.cos(t * 0.2);
  const x2 = 78 - 5 * Math.sin(t * 0.18);
  const y2 = 80 + 4 * Math.sin(t * 0.22);
  const gridShift = interpolate(frame, [0, 1800], [0, 120]);
  return (
    <AbsoluteFill style={{ background: `linear-gradient(160deg, ${theme.bg2} 0%, ${theme.bg} 60%)` }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(900px 600px at ${x1}% ${y1}%, rgba(46,127,192,0.28), transparent 70%),
                       radial-gradient(800px 500px at ${x2}% ${y2}%, rgba(31,47,107,0.55), transparent 70%)`,
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${theme.line} 1px, transparent 1px), linear-gradient(90deg, ${theme.line} 1px, transparent 1px)`,
          backgroundSize: "120px 120px",
          backgroundPosition: `${gridShift}px ${gridShift * 0.5}px`,
          opacity: 0.35,
          maskImage: "radial-gradient(ellipse at center, black 30%, transparent 85%)",
          WebkitMaskImage: "radial-gradient(ellipse at center, black 30%, transparent 85%)",
        }}
      />
    </AbsoluteFill>
  );
};
