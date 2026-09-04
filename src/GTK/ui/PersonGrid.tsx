import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { colors } from "../theme";

const Person: React.FC<{ color: string; size: number; opacity?: number }> = ({ color, size, opacity = 1 }) => (
  <svg width={size} height={size * 1.25} viewBox="0 0 40 50" style={{ opacity }}>
    <circle cx="20" cy="11" r="9" fill={color} />
    <path d="M4 48c0-12 6-19 16-19s16 7 16 19v2H4v-2Z" fill={color} />
  </svg>
);

/** Grade de pessoas que vai sendo preenchida ao longo do tempo. */
export const PersonGrid: React.FC<{
  count: number;
  columns: number;
  color?: string;
  size?: number;
  start?: number;
  perItem?: number;
  gap?: number;
  dim?: boolean;
}> = ({ count, columns, color = colors.yellow, size = 44, start = 0, perItem = 2, gap = 10, dim = false }) => {
  const frame = useCurrentFrame();
  const items = Array.from({ length: count }, (_, i) => i);
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${columns}, ${size}px)`,
        gap,
      }}
    >
      {items.map((i) => {
        const s = start + i * perItem;
        const scale = interpolate(frame, [s, s + 12], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.spring({ damping: 200 }),
          output: "perceptual-scale",
        });
        return (
          <div key={i} style={{ scale, transformOrigin: "50% 100%" }}>
            <Person color={color} size={size} opacity={dim ? 0.55 : 1} />
          </div>
        );
      })}
    </div>
  );
};
