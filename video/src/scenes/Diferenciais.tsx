import React from "react";
import { AbsoluteFill } from "remotion";
import { Title } from "../components/Title";
import { Card } from "../components/Card";
import { Check } from "../components/Check";
import { useEnter, useSceneFade } from "../components/anim";
import { DIFERENCIAIS, SCENES } from "../content";
import { font, theme } from "../theme";

export const Diferenciais: React.FC = () => {
  const fade = useSceneFade(SCENES.diferenciais.duration);
  return (
    <AbsoluteFill style={{ opacity: fade, padding: "110px 140px", fontFamily: font.family }}>
      <Title text={DIFERENCIAIS.titulo} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 44, marginTop: 110 }}>
        {DIFERENCIAIS.itens.map((it, i) => {
          const e = useEnter(30 + i * 16, { dist: 40 });
          return (
            <Card key={it.titulo} style={{ ...e, display: "flex", gap: 34, alignItems: "flex-start", padding: "52px 48px", minHeight: 250 }}>
              <Check delay={38 + i * 16} size={72} />
              <div>
                <div style={{ fontSize: 44, fontWeight: 700, color: theme.white, lineHeight: 1.1 }}>{it.titulo}</div>
                <div style={{ fontSize: 29, color: theme.muted, marginTop: 14, lineHeight: 1.3 }}>{it.desc}</div>
              </div>
            </Card>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
