import React from "react";
import { AbsoluteFill } from "remotion";
import { Counter } from "../components/Counter";
import { useEnter, useSceneFade } from "../components/anim";
import { EMPRESA, SCENES } from "../content";
import { font, theme } from "../theme";

export const Numeros: React.FC = () => {
  const fade = useSceneFade(SCENES.numeros.duration);
  const a = useEnter(6);
  const b = useEnter(40, { dist: 50 });
  const c = useEnter(70);
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center", justifyContent: "center", fontFamily: font.family, textAlign: "center" }}>
      <div style={{ ...a, fontSize: 36, fontWeight: 600, color: theme.blueLight, letterSpacing: 6, textTransform: "uppercase" }}>
        {EMPRESA.desde}
      </div>
      <div style={{ ...b, fontSize: 250, fontWeight: 800, color: theme.white, letterSpacing: -8, lineHeight: 1, marginTop: 30 }}>
        <Counter to={EMPRESA.operacoes} delay={40} duration={70} prefix="+" />
      </div>
      <div style={{ ...c, fontSize: 48, fontWeight: 500, color: theme.muted, marginTop: 20 }}>{EMPRESA.operacoesLabel}</div>
    </AbsoluteFill>
  );
};
