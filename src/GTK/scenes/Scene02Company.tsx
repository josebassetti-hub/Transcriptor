import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts, SAFE } from "../theme";
import { company, contact, marketCities } from "../data";
import { Body, ContactFooter, Headline, Kicker } from "../ui/Text";
import { Logo } from "../Logo";

// Contorno simplificado do Espírito Santo (lon, lat)
const ES: [number, number][] = [
  [-40.95, -17.92], [-40.6, -17.95], [-40.2, -18.05], [-39.9, -18.1], [-39.72, -18.3], [-39.7, -18.55],
  [-39.75, -18.75], [-39.85, -19.05], [-39.95, -19.4], [-40.15, -19.7], [-40.25, -20.0], [-40.28, -20.32],
  [-40.6, -20.6], [-40.75, -20.85], [-40.95, -21.05], [-41.05, -21.3], [-41.3, -21.2], [-41.5, -21.05],
  [-41.85, -20.85], [-41.87, -20.5], [-41.7, -20.2], [-41.55, -19.9], [-41.3, -19.55], [-41.2, -19.1],
  [-41.05, -18.8], [-40.95, -18.45], [-41.1, -18.15],
];
const BR101: [number, number][] = [[-39.9, -18.08], [-39.86, -18.5], [-39.9, -18.75], [-40.0, -19.0], [-40.05, -19.4], [-40.2, -19.9], [-40.3, -20.3], [-40.65, -20.65], [-41.0, -21.25]];
const BR381: [number, number][] = [[-39.86, -18.72], [-40.0, -18.7], [-40.16483, -18.71914], [-40.3, -18.72], [-40.4, -18.71]];

const LAT0 = -19.6;
const LON0 = -40.8;
const K = 230; // px por grau
const proj = (lon: number, lat: number) => ({
  x: (lon - LON0) * K * Math.cos((LAT0 * Math.PI) / 180),
  y: -(lat - LAT0) * K,
});
const path = (pts: [number, number][]) => pts.map(([lo, la], i) => `${i ? "L" : "M"}${proj(lo, la).x.toFixed(1)} ${proj(lo, la).y.toFixed(1)}`).join(" ");

const MAP_W = 800;
const MAP_H = 860;

export const Scene02Company: React.FC = () => {
  const frame = useCurrentFrame();
  const ease = Easing.bezier(0.45, 0, 0.2, 1);
  const zoom = interpolate(frame, [20, 110], [1, 3.4], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const plant = proj(company.lon, company.lat);
  const center = proj(-40.8, -19.6);
  const tx = interpolate(frame, [20, 110], [0, -(plant.x - center.x)], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const ty = interpolate(frame, [20, 110], [0, -(plant.y - center.y)], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const pin = interpolate(frame, [100, 122], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.spring({ damping: 200 }) });
  const radius = interpolate(frame, [120, 175], [0, 100 * (K / 111)], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const cities = interpolate(frame, [125, 150], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const mapIn = interpolate(frame, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const coordIn = interpolate(frame, [130, 150], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: `linear-gradient(120deg, ${colors.navyDeep} 0%, ${colors.navy} 60%, ${colors.navy2} 100%)` }}>
      {/* texto */}
      <div style={{ position: "absolute", left: SAFE.x, top: SAFE.y - 20, width: 800, display: "flex", flexDirection: "column", gap: 22 }}>
        <div style={{ marginBottom: 6 }}>
          <Logo variant="horizontal" height={84} />
        </div>
        <Kicker start={4}>A empresa</Kicker>
        <Headline start={8} size={62}>
          Nova indústria de concreto no norte do Espírito Santo
        </Headline>
        <Body start={16} size={32}>
          {company.claim}.
        </Body>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 4 }}>
          {[
            ["Fundação", company.founded],
            ["Sede", `${company.city} · BR-381, km 35`],
            ["Produtos", "Blocos · Canaletas · Pavers"],
            ["Normas", "NBR 6136 · NBR 9781"],
          ].map(([k, v], i) => (
            <Row key={k} k={k} v={v} start={26 + i * 6} />
          ))}
        </div>
      </div>

      {/* mapa */}
      <div
        style={{
          position: "absolute",
          left: 1920 - SAFE.x - MAP_W,
          top: 60,
          width: MAP_W,
          height: MAP_H,
          borderRadius: 26,
          overflow: "hidden",
          background: "rgba(7,26,51,0.55)",
          border: "2px solid rgba(255,255,255,0.12)",
          boxShadow: "0 30px 70px rgba(0,0,0,0.4)",
          opacity: mapIn,
        }}
      >
        <svg width={MAP_W} height={MAP_H} viewBox={`${-MAP_W / 2} ${-MAP_H / 2} ${MAP_W} ${MAP_H}`}>
          <g transform={`scale(${zoom}) translate(${tx} ${ty}) translate(${-center.x} ${-center.y})`}>
            <path d={path(ES) + " Z"} fill="#1B4478" stroke={colors.concreteLight} strokeWidth={2 / zoom} />
            <path d={path(BR101)} fill="none" stroke="#9AA6BA" strokeWidth={3 / zoom} strokeDasharray={`${8 / zoom} ${5 / zoom}`} />
            <path d={path(BR381)} fill="none" stroke={colors.yellow} strokeWidth={4 / zoom} />
            {/* raio de atendimento ~100 km */}
            <circle cx={plant.x} cy={plant.y} r={radius} fill="rgba(247,181,0,0.10)" stroke={colors.yellow} strokeWidth={2 / zoom} strokeDasharray={`${6 / zoom} ${6 / zoom}`} />
            {marketCities.map((c) => {
              const p = proj(c.lon, c.lat);
              const big = c.major || c.capital;
              return (
                <g key={c.name} opacity={c.capital ? 1 : cities}>
                  <circle cx={p.x} cy={p.y} r={(big ? 5 : 3.2) / zoom} fill={c.capital ? colors.concreteLight : colors.white} />
                  <text
                    x={p.x + 8 / zoom}
                    y={p.y + 4 / zoom}
                    fontFamily={fonts.body}
                    fontWeight={big ? 800 : 600}
                    fontSize={(big ? 15 : 12) / zoom}
                    fill={colors.white}
                  >
                    {c.name}
                  </text>
                </g>
              );
            })}
            {/* pino da GTK */}
            <g transform={`translate(${plant.x} ${plant.y}) scale(${pin / zoom})`}>
              <circle r={26} fill="rgba(247,181,0,0.25)" />
              <path d="M0 -44 C -20 -44 -28 -28 -28 -18 C -28 0 0 22 0 22 C 0 22 28 0 28 -18 C 28 -28 20 -44 0 -44 Z" fill={colors.yellow} stroke={colors.navyDeep} strokeWidth={3} />
              <circle cy={-20} r={9} fill={colors.navyDeep} />
            </g>
          </g>
          <text x={-MAP_W / 2 + 26} y={-MAP_H / 2 + 44} fontFamily={fonts.body} fontWeight={700} fontSize={24} letterSpacing={4} fill={colors.yellow}>
            ESPÍRITO SANTO · NORTE CAPIXABA
          </text>
        </svg>
        {/* coordenadas */}
        <div
          style={{
            position: "absolute",
            left: 26,
            right: 26,
            bottom: 26,
            padding: "14px 22px",
            background: "rgba(7,26,51,0.9)",
            border: `2px solid ${colors.yellow}`,
            borderRadius: 12,
            fontFamily: fonts.body,
            color: colors.white,
            opacity: coordIn,
          }}
        >
          <div style={{ display: "flex", gap: 14, alignItems: "center", fontWeight: 700, fontSize: 30 }}>
            <span style={{ color: colors.yellow }}>GTK</span> {company.gps}
          </div>
          <div style={{ fontSize: 22, color: colors.concreteLight, marginTop: 4 }}>raio de entrega ≈ 100 km · 9 municípios · ~230 mil habitantes</div>
        </div>
      </div>

      <ContactFooter role={contact.role} name={contact.name} phone={contact.phone} start={40} />
    </AbsoluteFill>
  );
};

const Row: React.FC<{ k: string; v: string; start: number }> = ({ k, v, start }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [start, start + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ display: "flex", gap: 18, alignItems: "baseline", opacity: o, translate: `${(1 - o) * -20}px 0px`, fontFamily: fonts.body }}>
      <span style={{ width: 190, flexShrink: 0, fontSize: 24, fontWeight: 700, letterSpacing: 3, textTransform: "uppercase", color: colors.yellow }}>{k}</span>
      <span style={{ fontSize: 32, fontWeight: 500, color: colors.white }}>{v}</span>
    </div>
  );
};
