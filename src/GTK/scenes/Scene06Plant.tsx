import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts, SAFE } from "../theme";
import { site } from "../data";
import { FactBar, Kicker } from "../ui/Text";
import { Plant3D, type CameraKeyframe } from "../plant3d/Plant3D";

// Sobrevoo: terreno inteiro -> mergulho no galpão -> percorre a linha
const camera: CameraKeyframe[] = [
  { frame: 0, px: 125, py: 60, rx: 52, rz: -18, scale: 0.62 },
  { frame: 70, px: 118, py: 55, rx: 56, rz: -24, scale: 0.72 },
  { frame: 150, px: 84, py: 40, rx: 60, rz: -34, scale: 2.4 },
  { frame: 230, px: 76, py: 38, rx: 62, rz: -8, scale: 2.9 },
  { frame: 311, px: 70, py: 39, rx: 60, rz: 12, scale: 2.7 },
];

export const Scene06Plant: React.FC = () => {
  const frame = useCurrentFrame();
  const overview = interpolate(frame, [20, 40, 120, 140], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const detail = interpolate(frame, [160, 185], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: `radial-gradient(1400px 900px at 50% 40%, #16324F 0%, ${colors.navyDeep} 70%, #030A14 100%)` }}>
      <Plant3D camera={camera} lightFrom={150} lightEvery={24} roofFadeAt={[120, 165]} labelOpacity={detail} />
      {/* faixa superior para legibilidade do título */}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(3,10,20,0.85) 0%, rgba(3,10,20,0.45) 18%, rgba(3,10,20,0) 34%)" }} />

      <div style={{ position: "absolute", left: SAFE.x, top: SAFE.y - 20 }}>
        <Kicker start={2}>A planta industrial</Kicker>
        <div style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 60, color: colors.white, marginTop: 12, textShadow: "0 4px 24px rgba(0,0,0,0.6)" }}>
          Implantação no km 35 da BR-381
        </div>
      </div>

      {/* legendas do terreno */}
      <div style={{ position: "absolute", right: SAFE.x, top: SAFE.y - 10, display: "flex", flexDirection: "column", gap: 14, opacity: overview }}>
        {[site.terrainLabel, site.shedLabel, site.expansionLabel].map((t, i) => (
          <div
            key={t}
            style={{
              padding: "14px 24px",
              background: "rgba(7,26,51,0.85)",
              border: `2px solid ${colors.yellow}`,
              borderRadius: 12,
              fontFamily: fonts.body,
              fontWeight: 700,
              fontSize: 32,
              color: i === 0 ? colors.yellow : colors.white,
            }}
          >
            {t}
          </div>
        ))}
      </div>

      <div style={{ position: "absolute", right: SAFE.x, top: SAFE.y - 10, opacity: detail, textAlign: "right" }}>
        <div style={{ fontFamily: fonts.body, fontWeight: 700, fontSize: 30, letterSpacing: 4, color: colors.yellow }}>LINHA GERVASI XP350</div>
        <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 26, color: colors.concreteLight, marginTop: 6 }}>layout de referência Gervasi, adaptado a uma linha</div>
      </div>

      <div style={{ position: "absolute", left: SAFE.x, bottom: 40 }}>
        <FactBar items={["Terreno 25.000 m²", "Galpão ≈ 1.500 m²", "Silo 90 t", "Cura e expedição", "Área para ampliações"]} start={30} size={30} />
      </div>
    </AbsoluteFill>
  );
};
