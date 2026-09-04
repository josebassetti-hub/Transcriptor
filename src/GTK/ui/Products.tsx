import React from "react";
import { colors } from "../theme";

/**
 * Ilustrações isométricas dos produtos (SVG). Cores de concreto com sombra em 3 faces.
 * Todas usam viewBox 0 0 300 220.
 */
const top = "#D9DEE6";
const left = "#AEB6C2";
const right = "#8D97A6";
const hole = "#5B6472";

export const BlockIso: React.FC<{ size?: number }> = ({ size = 300 }) => (
  <svg width={size} height={(size * 220) / 300} viewBox="0 0 300 220">
    {/* bloco vazado 14x19x39 em isometria */}
    <polygon points="40,100 150,45 260,100 150,155" fill={top} />
    <polygon points="40,100 150,155 150,215 40,160" fill={left} />
    <polygon points="150,155 260,100 260,160 150,215" fill={right} />
    {/* furos */}
    <polygon points="72,100 128,72 168,92 112,120" fill={hole} />
    <polygon points="132,124 188,96 228,116 172,144" fill={hole} />
    <polygon points="72,100 112,120 112,134 72,114" fill="#3F4753" />
    <polygon points="132,124 172,144 172,158 132,138" fill="#3F4753" />
  </svg>
);

export const ChannelIso: React.FC<{ size?: number }> = ({ size = 300 }) => (
  <svg width={size} height={(size * 220) / 300} viewBox="0 0 300 220">
    {/* canaleta U */}
    <polygon points="40,100 150,45 260,100 150,155" fill={top} />
    <polygon points="40,100 150,155 150,215 40,160" fill={left} />
    <polygon points="150,155 260,100 260,160 150,215" fill={right} />
    {/* calha */}
    <polygon points="66,100 176,45 214,64 104,119" fill={hole} />
    <polygon points="104,119 214,64 214,90 104,145" fill="#3F4753" />
    <polygon points="66,100 104,119 104,145 66,126" fill="#4B5461" />
  </svg>
);

export const PaverIso: React.FC<{ size?: number }> = ({ size = 300 }) => {
  // pavers retangulares 10x20 intertravados, alguns pigmentados
  const cells: { x: number; y: number; c: string }[] = [];
  const pal = ["#C9CFD8", "#C9CFD8", "#B94A3C", "#C9CFD8", "#D7A24A", "#C9CFD8"];
  let k = 0;
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      cells.push({ x: c, y: r, c: pal[(k++ * 7) % pal.length] });
    }
  }
  const dx = 28;
  const dy = 14;
  return (
    <svg width={size} height={(size * 220) / 300} viewBox="0 0 300 220">
      {cells.map(({ x, y, c }, i) => {
        const ox = 150 + (x - y) * dx;
        const oy = 60 + (x + y) * dy;
        return (
          <g key={i}>
            <polygon points={`${ox},${oy} ${ox + dx},${oy + dy} ${ox},${oy + 2 * dy} ${ox - dx},${oy + dy}`} fill={c} />
            <polygon points={`${ox - dx},${oy + dy} ${ox},${oy + 2 * dy} ${ox},${oy + 2 * dy + 12} ${ox - dx},${oy + dy + 12}`} fill="#8D97A6" />
            <polygon points={`${ox},${oy + 2 * dy} ${ox + dx},${oy + dy} ${ox + dx},${oy + dy + 12} ${ox},${oy + 2 * dy + 12}`} fill="#707A89" />
          </g>
        );
      })}
    </svg>
  );
};

export const ProductIllustration: React.FC<{ id: string; size?: number }> = ({ id, size }) => {
  if (id === "bloco") return <BlockIso size={size} />;
  if (id === "canaleta") return <ChannelIso size={size} />;
  return <PaverIso size={size} />;
};

export const productAccent = colors.yellow;
