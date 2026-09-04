import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { Title } from "../components/Title";
import { Card } from "../components/Card";
import { Counter } from "../components/Counter";
import { useEnter, useSceneFade } from "../components/anim";
import { INCENTIVOS, SCENES } from "../content";
import { font, theme } from "../theme";

export const Incentivos: React.FC = () => {
  const frame = useCurrentFrame();
  const fade = useSceneFade(SCENES.incentivos.duration);
  const foot = interpolate(frame, [200, 220], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: fade, padding: "110px 140px", fontFamily: font.family }}>
      <Title text={INCENTIVOS.titulo} sub={INCENTIVOS.subtitulo} />
      <div style={{ display: "flex", gap: 44, marginTop: 120 }}>
        {INCENTIVOS.cards.map((c, i) => {
          const e = useEnter(40 + i * 18, { dist: 60 });
          return (
            <Card key={c.rotulo} style={{ ...e, flex: 1, minHeight: 470, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div style={{ fontSize: 26, fontWeight: 700, color: theme.blueLight, letterSpacing: 3 }}>{c.rotulo}</div>
              <div>
                {c.valor !== null ? (
                  <div style={{ fontSize: 150, fontWeight: 800, color: theme.white, letterSpacing: -4, lineHeight: 1 }}>
                    <Counter to={c.valor} delay={52 + i * 18} duration={50} decimals={c.valor % 1 === 0 ? 0 : 1} suffix={c.sufixo} />
                  </div>
                ) : (
                  <div style={{ fontSize: 96, fontWeight: 800, color: theme.white, letterSpacing: -2, lineHeight: 1.05 }}>ICMS</div>
                )}
                <div style={{ fontSize: 32, color: theme.muted, marginTop: 20, lineHeight: 1.25 }}>{c.desc}</div>
              </div>
            </Card>
          );
        })}
      </div>
      <div style={{ opacity: foot, marginTop: 44, fontSize: 24, color: theme.muted }}>{INCENTIVOS.rodape}</div>
    </AbsoluteFill>
  );
};
