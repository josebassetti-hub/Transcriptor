import React from "react";
import { colors } from "../theme";
import type { EquipmentId } from "../data";

const Y = colors.yellow;
const R = colors.red;
const S = colors.steel;
const D = colors.steelDark;

/** Ilustrações simplificadas (fallback) dos equipamentos nas cores do catálogo Gervasi. viewBox 0 0 320 240 */
export const EquipmentIcon: React.FC<{ id: EquipmentId; width?: number }> = ({ id, width = 320 }) => {
  const h = (width * 240) / 320;
  const body: Record<EquipmentId, React.ReactNode> = {
    silo: (
      <>
        <rect x="120" y="20" width="80" height="150" rx="10" fill={S} />
        <polygon points="120,170 200,170 160,215" fill={D} />
        <rect x="110" y="30" width="12" height="150" fill={Y} />
        <rect x="140" y="215" width="6" height="25" fill={D} />
        <rect x="174" y="215" width="6" height="25" fill={D} />
        <rect x="150" y="6" width="20" height="16" fill={Y} />
      </>
    ),
    central: (
      <>
        {[0, 1, 2, 3].map((i) => (
          <g key={i} transform={`translate(${20 + i * 72} 40)`}>
            <polygon points="0,0 64,0 64,60 32,110 0,60" fill={S} />
            <rect x="0" y="0" width="64" height="16" fill={D} />
          </g>
        ))}
        <rect x="14" y="150" width="292" height="26" fill={Y} />
        <rect x="24" y="176" width="10" height="60" fill={D} />
        <rect x="286" y="176" width="10" height="60" fill={D} />
        <rect x="150" y="176" width="10" height="60" fill={D} />
      </>
    ),
    misturador: (
      <>
        <rect x="80" y="70" width="160" height="110" rx="14" fill={R} />
        <polygon points="120,20 200,20 220,70 100,70" fill={Y} />
        <circle cx="60" cy="140" r="26" fill={D} />
        <circle cx="60" cy="140" r="12" fill="#2F6FBF" />
        <rect x="90" y="180" width="14" height="50" fill={D} />
        <rect x="216" y="180" width="14" height="50" fill={D} />
      </>
    ),
    esteiras: (
      <>
        <polygon points="20,190 300,90 300,110 20,210" fill={D} />
        <polygon points="20,186 300,86 300,92 20,192" fill={Y} />
        <rect x="60" y="205" width="10" height="30" fill={D} />
        <rect x="200" y="140" width="10" height="95" fill={D} />
        <rect x="280" y="112" width="10" height="123" fill={D} />
      </>
    ),
    vibroprensa: (
      <>
        <rect x="70" y="30" width="180" height="180" rx="8" fill={S} />
        <rect x="90" y="50" width="140" height="60" fill={R} />
        <polygon points="110,6 210,6 220,50 100,50" fill={Y} />
        <rect x="100" y="120" width="120" height="40" fill={D} />
        {[0, 1, 2, 3].map((i) => (
          <rect key={i} x={106 + i * 30} y="124" width="22" height="32" fill="#E8E9EC" />
        ))}
        <rect x="70" y="180" width="180" height="14" fill={Y} />
        <rect x="20" y="200" width="280" height="12" fill={D} />
      </>
    ),
    elevador: (
      <>
        <rect x="70" y="20" width="180" height="200" fill={S} />
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <rect key={i} x="82" y={34 + i * 30} width="156" height="12" fill={R} />
        ))}
        <rect x="60" y="20" width="12" height="200" fill={Y} />
        <rect x="248" y="20" width="12" height="200" fill={Y} />
        <rect x="130" y="4" width="60" height="18" fill={Y} />
      </>
    ),
    paletizador: (
      <>
        <rect x="40" y="60" width="14" height="170" fill={Y} />
        <rect x="266" y="60" width="14" height="170" fill={Y} />
        <rect x="30" y="48" width="260" height="18" fill={R} />
        <rect x="120" y="66" width="80" height="50" fill={S} />
        <rect x="100" y="150" width="120" height="50" fill="#C9CFD8" />
        <rect x="96" y="200" width="128" height="14" fill="#8A6A3A" />
        <rect x="20" y="222" width="280" height="10" fill={D} />
      </>
    ),
  };
  return (
    <svg width={width} height={h} viewBox="0 0 320 240">
      {body[id]}
    </svg>
  );
};
