import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Camera } from "../components/Camera";
import { Chapter } from "../components/Chapter";
import { Hits } from "../components/Hits";
import { Particles } from "../components/Fx";
import { Kicker } from "../components/Kicker";
import { FINANCIAMENTO, SCENES } from "../content";
import { font, theme } from "../theme";

/** Capítulo 01: financiamento BNB/FNE. Abertura de capítulo e três benefícios em hits. */
export const Financiamento: React.FC = () => {
  const frame = useCurrentFrame();
  const bars = Array.from({ length: 9 });
  return (
    <AbsoluteFill style={{ fontFamily: font.family, overflow: "hidden" }}>
      <Camera duration={SCENES.financiamento} from={1.06} to={1} panX={20}>
        <Particles count={50} speed={1.1} seed="fi" />
        {/* barras ascendentes discretas ao fundo, eco do logo */}
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 520, display: "flex", alignItems: "flex-end", gap: 40, padding: "0 120px", opacity: 0.5 }}>
          {bars.map((_, i) => {
            const h = 80 + i * 45 + 20 * Math.sin(frame / 25 + i);
            return <div key={i} style={{ flex: 1, height: h, borderRadius: "8px 8px 0 0", background: "linear-gradient(180deg, rgba(95,179,232,0.22), rgba(46,127,192,0.03))", border: "1px solid rgba(255,255,255,0.08)", borderBottom: "none" }} />;
          })}
        </div>
      </Camera>
      <Chapter numero={FINANCIAMENTO.numero} titulo={FINANCIAMENTO.titulo} sub={FINANCIAMENTO.sub} duration={FINANCIAMENTO.abertura} pill />
      {frame >= FINANCIAMENTO.abertura ? <Kicker text={FINANCIAMENTO.kicker} delay={FINANCIAMENTO.abertura} /> : null}
      <Hits hits={FINANCIAMENTO.hits} offset={FINANCIAMENTO.abertura} sceneDuration={SCENES.financiamento} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 4, background: theme.line }} />
    </AbsoluteFill>
  );
};
