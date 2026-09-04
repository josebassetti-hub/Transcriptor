import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";
import { Scene } from "../data";
import { sec, C, FONT } from "../theme";
import { ClipSequence } from "../ui/Clip";
import { Safe } from "../ui/Layout";
import { Reveal, Fade } from "../ui/Text";

const Item: React.FC<{ nome: string; uso: string; from: number }> = ({ nome, uso, from }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  if (frame < from) return null;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 22, opacity: t, transform: `translateX(${(1 - t) * -24}px)` }}>
      <div style={{ width: 40 * t, height: 4, background: C.amber, flex: "none" }} />
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 50, color: C.white, letterSpacing: "0.08em", textTransform: "uppercase", whiteSpace: "nowrap", textShadow: "0 3px 16px rgba(0,0,0,0.6)" }}>{nome}</div>
      <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 28, color: C.silver, letterSpacing: "0.02em", whiteSpace: "nowrap", marginTop: 6 }}>{uso}</div>
    </div>
  );
};

export const S4Produtos: React.FC<{ sc: Scene }> = ({ sc }) => {
  const cuts = sc.footage.cortes!;
  return (
    <AbsoluteFill>
      <ClipSequence cuts={cuts} totalFrames={sc.durationFrames} gradient="left" maxRate={0.85} />
      <Safe justify="flex-start" align="flex-start" padY={40} style={{ gap: 26 }}>
        <Reveal text={sc.title} from={sec(sc.title_in_s - sc.start_s)} size={54} align="left" maxWidth={950} duration={24} />
        <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 6 }}>
          {sc.products!.map((p) => (
            <Item key={p.nome} nome={p.nome} uso={p.uso} from={sec(p.in_s - sc.start_s)} />
          ))}
        </div>
      </Safe>
      <Fade text={sc.subtitle} from={sec(sc.subtitle_in_s! - sc.start_s)} size={32} color={C.silver} align="left" maxWidth={1300} style={{ position: "absolute", left: 120, bottom: 140 }} />
    </AbsoluteFill>
  );
};
