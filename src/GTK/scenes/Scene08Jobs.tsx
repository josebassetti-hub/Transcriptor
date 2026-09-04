import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { colors, fonts, SAFE } from "../theme";
import { Body, Headline, Kicker } from "../ui/Text";
import { CountUp } from "../ui/CountUp";
import { PersonGrid } from "../ui/PersonGrid";

export const Scene08Jobs: React.FC<{ directJobs: number; indirectJobs: number }> = ({ directJobs, indirectJobs }) => {
  const frame = useCurrentFrame();
  const total = directJobs + indirectJobs;
  const totalIn = interpolate(frame, [110, 130], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: `linear-gradient(135deg, ${colors.navy} 0%, ${colors.navyDeep} 100%)` }}>
      <div style={{ position: "absolute", left: SAFE.x, top: SAFE.y, width: 820, display: "flex", flexDirection: "column", gap: 22 }}>
        <Kicker start={2}>Geração de empregos</Kicker>
        <Headline start={6} size={74}>
          Renda e trabalho no interior norte-capixaba
        </Headline>
        <Body start={14} size={34}>
          Produção, manutenção, qualidade, comercial e expedição na fábrica; pedreiras, cimento, transporte, pallets, revendas e obras na cadeia.
        </Body>
        <div
          style={{
            marginTop: 20,
            padding: "22px 30px",
            background: "rgba(247,181,0,0.12)",
            border: `2px solid ${colors.yellow}`,
            borderRadius: 18,
            opacity: totalIn,
            translate: `0px ${(1 - totalIn) * 20}px`,
            fontFamily: fonts.body,
            color: colors.white,
          }}
        >
          <span style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 64, color: colors.yellow }}>
            <CountUp to={total} startFrame={110} durationInFrames={40} />
          </span>
          <span style={{ fontSize: 34, fontWeight: 700, marginLeft: 16 }}>postos de trabalho na região</span>
          <div style={{ fontSize: 24, color: colors.concreteLight, marginTop: 6 }}>estimativa com base no quadro da planta e no efeito na cadeia de fornecedores</div>
        </div>
      </div>

      <div style={{ position: "absolute", left: 1040, top: SAFE.y, width: 760, display: "flex", flexDirection: "column", gap: 34 }}>
        <div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 18, fontFamily: fonts.body, color: colors.white }}>
            <span style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 96, color: colors.yellow, lineHeight: 1 }}>
              <CountUp to={directJobs} startFrame={20} durationInFrames={30} />
            </span>
            <span style={{ fontSize: 40, fontWeight: 700 }}>empregos diretos</span>
          </div>
          <div style={{ marginTop: 14 }}>
            <PersonGrid count={directJobs} columns={12} size={52} start={20} perItem={2} />
          </div>
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 18, fontFamily: fonts.body, color: colors.white }}>
            <span style={{ fontFamily: fonts.heading, fontWeight: 900, fontSize: 96, color: colors.concreteLight, lineHeight: 1 }}>
              <CountUp to={indirectJobs} startFrame={60} durationInFrames={40} prefix="~" />
            </span>
            <span style={{ fontSize: 40, fontWeight: 700 }}>empregos indiretos</span>
          </div>
          <div style={{ marginTop: 14 }}>
            <PersonGrid count={indirectJobs} columns={12} size={52} start={60} perItem={1} color={colors.concreteLight} dim />
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
