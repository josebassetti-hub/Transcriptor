import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts, SAFE } from "../theme";
import { capacity } from "../data";
import { Body, Headline, Kicker } from "../ui/Text";
import { CountUp } from "../ui/CountUp";
import { MediaSlot } from "../MediaSlot";

export const Scene05Capacity: React.FC = () => {
  const frame = useCurrentFrame();
  const phone = interpolate(frame, [0, 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.16, 1, 0.3, 1) });
  return (
    <AbsoluteFill style={{ background: `linear-gradient(135deg, ${colors.navyDeep} 0%, ${colors.navy} 100%)` }}>
      {/* vídeo vertical do ciclo em moldura */}
      <div
        style={{
          position: "absolute",
          left: SAFE.x,
          top: 90,
          width: 500,
          height: 890,
          borderRadius: 28,
          overflow: "hidden",
          border: `4px solid ${colors.yellow}`,
          boxShadow: "0 30px 80px rgba(0,0,0,0.5)",
          opacity: phone,
          translate: `${(1 - phone) * -60}px 0px`,
        }}
      >
        <MediaSlot id="video:xp350-ciclo" trimSeconds={3} />
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "18px 24px", background: "linear-gradient(0deg, rgba(7,26,51,0.9), rgba(7,26,51,0))", fontFamily: fonts.body, fontWeight: 700, fontSize: 26, color: colors.white }}>
          Vibroprensa XP350 em operação
        </div>
      </div>

      <div style={{ position: "absolute", left: 740, top: SAFE.y, width: 1040, display: "flex", flexDirection: "column", gap: 18 }}>
        <Kicker start={4}>Capacidade instalada</Kicker>
        <Headline start={8} size={72}>
          Escala industrial desde o primeiro turno
        </Headline>
        <Body start={14} size={34}>
          Valores nominais do fabricante para bandeja 700×550 mm, turno de 8 h com 90 % de utilização.
        </Body>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28, marginTop: 20 }}>
          {capacity.map((c, i) => {
            const s = 30 + i * 12;
            const o = interpolate(frame, [s, s + 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div
                key={c.label}
                style={{
                  background: "rgba(255,255,255,0.06)",
                  border: "2px solid rgba(255,255,255,0.12)",
                  borderLeft: `10px solid ${colors.yellow}`,
                  borderRadius: 18,
                  padding: "22px 30px",
                  opacity: o,
                  translate: `0px ${(1 - o) * 30}px`,
                }}
              >
                <div style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 84, color: colors.yellow, lineHeight: 1 }}>
                  <CountUp to={c.value} startFrame={s} durationInFrames={60} decimals={c.decimals ?? 0} suffix={c.suffix} />
                </div>
                <div style={{ fontFamily: fonts.body, fontWeight: 700, fontSize: 36, color: colors.white, marginTop: 8 }}>{c.label}</div>
                <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 26, color: colors.concreteLight, marginTop: 4 }}>{c.note}</div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
