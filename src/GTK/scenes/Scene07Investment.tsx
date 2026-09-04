import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts, SAFE } from "../theme";
import { Body, Kicker } from "../ui/Text";
import { CountUp } from "../ui/CountUp";
import { EquipmentIcon } from "../equipment/EquipmentIcon";

export const Scene07Investment: React.FC<{ investmentBRL: number }> = ({ investmentBRL }) => {
  const frame = useCurrentFrame();
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const big = interpolate(frame, [10, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const millions = investmentBRL / 1_000_000;
  const chips = [
    { label: "Equipamentos", sub: "Linha automática Gervasi XP350", icon: "vibroprensa" as const },
    { label: "Galpão e obras", sub: "Estrutura, piso industrial, cura e pátio", icon: "paletizador" as const },
    { label: "Infraestrutura", sub: "Energia MT, água, silo, moldes e startup", icon: "silo" as const },
  ];
  return (
    <AbsoluteFill style={{ background: `linear-gradient(160deg, ${colors.yellow} 0%, ${colors.yellowDark} 100%)` }}>
      {/* faixas diagonais decorativas */}
      <AbsoluteFill style={{ background: "repeating-linear-gradient(-30deg, rgba(11,37,69,0.06) 0 60px, rgba(11,37,69,0) 60px 140px)" }} />
      <div style={{ position: "absolute", left: SAFE.x, top: SAFE.y }}>
        <Kicker start={2} color={colors.navy}>
          Investimento
        </Kicker>
      </div>
      <div style={{ position: "absolute", left: SAFE.x, top: 300, opacity: big, translate: `0px ${(1 - big) * 40}px` }}>
        <div style={{ fontFamily: fonts.body, fontWeight: 700, fontSize: 44, letterSpacing: 6, color: colors.navy }}>INVESTIMENTO TOTAL</div>
        <div style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 250, lineHeight: 1, color: colors.navyDeep, letterSpacing: -4, marginTop: 6 }}>
          <span style={{ fontSize: 110, verticalAlign: "top", lineHeight: 2.1 }}>R$ </span>
          <CountUp to={millions} startFrame={14} durationInFrames={70} decimals={0} />
          <span style={{ fontSize: 120 }}> milhões</span>
        </div>
        <Body start={60} size={40} color={colors.navy}>
          em equipamentos, obras civis e infraestrutura da nova fábrica.
        </Body>
      </div>
      <div style={{ position: "absolute", left: SAFE.x, right: SAFE.x, bottom: 110, display: "flex", gap: 30 }}>
        {chips.map((c, i) => {
          const s = 90 + i * 12;
          const o = interpolate(frame, [s, s + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
          return (
            <div
              key={c.label}
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                gap: 22,
                padding: "20px 26px",
                background: colors.navyDeep,
                borderRadius: 18,
                opacity: o,
                translate: `0px ${(1 - o) * 30}px`,
              }}
            >
              <div style={{ width: 150, flexShrink: 0 }}>
                <EquipmentIcon id={c.icon} width={150} />
              </div>
              <div>
                <div style={{ fontFamily: fonts.heading, fontWeight: 800, fontSize: 36, color: colors.yellow }}>{c.label}</div>
                <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 26, color: colors.concreteLight, marginTop: 4 }}>{c.sub}</div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
