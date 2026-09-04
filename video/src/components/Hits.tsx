import React from "react";
import { useCurrentFrame } from "remotion";
import { Counter } from "./Counter";
import { Shockwave, Flash } from "./Fx";
import { riseIn, slamIn, slamOut } from "./anim";
import { BEAT } from "../content";
import { font, theme } from "../theme";

export type Hit = {
  rotulo: string;
  valor?: number;
  sufixo?: string;
  texto?: string;
  desc: string;
};

/**
 * Sequência de "hits": a cada `step` frames entra um rótulo, um número/texto gigante e uma linha de apoio,
 * com onda de choque e flash. `offset` é o frame do primeiro hit dentro da cena.
 */
export const Hits: React.FC<{ hits: Hit[]; offset?: number; step?: number; sceneDuration: number }> = ({ hits, offset = 0, step = BEAT * 6, sceneDuration }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {hits.map((h, i) => {
        const at = offset + i * step;
        const out = i < hits.length - 1 ? at + step - 6 : sceneDuration + 40;
        if (frame < at || frame > out + 12) return null;
        const outS = frame >= out ? slamOut(frame, out) : {};
        const isNumber = typeof h.valor === "number";
        const big = h.texto ?? "";
        const fontSize = isNumber ? 400 : big.length > 10 ? 190 : 300;
        return (
          <div key={h.rotulo + i} style={{ position: "absolute", inset: 0, fontFamily: font.family, ...outS }}>
            <div style={{ position: "absolute", left: 0, right: 0, top: 250, textAlign: "center", ...riseIn(frame, at + 4, 10, 20) }}>
              <div style={{ fontSize: 40, fontWeight: 700, color: theme.blueLight, letterSpacing: 10 }}>{h.rotulo}</div>
            </div>
            <div style={{ position: "absolute", left: 0, right: 0, top: isNumber ? 320 : 360, textAlign: "center", ...slamIn(frame, at, 10) }}>
              <div style={{ fontSize, fontWeight: 900, color: theme.white, letterSpacing: isNumber ? -18 : -8, lineHeight: 1, textShadow: `0 0 90px ${theme.glow}`, whiteSpace: "nowrap" }}>
                {isNumber ? (
                  <Counter to={h.valor!} from={h.valor! * 0.6} delay={at} duration={26} decimals={h.valor! % 1 === 0 ? 0 : 1} suffix={h.sufixo ?? ""} />
                ) : (
                  big
                )}
              </div>
            </div>
            <div style={{ position: "absolute", left: 0, right: 0, top: 760, textAlign: "center", ...riseIn(frame, at + 10, 12, 30) }}>
              <div style={{ fontSize: 54, fontWeight: 500, color: theme.white }}>{h.desc}</div>
            </div>
          </div>
        );
      })}
      {hits.map((_, i) => (
        <React.Fragment key={i}>
          <Shockwave at={offset + i * step} size={1800} />
          <Flash at={offset + i * step} strength={0.3} />
        </React.Fragment>
      ))}
    </>
  );
};
