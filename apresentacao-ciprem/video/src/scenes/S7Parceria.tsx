import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";
import { Scene } from "../data";
import { sec, C, FONT } from "../theme";
import { ClipSequence } from "../ui/Clip";
import { Reveal } from "../ui/Text";
import { LETTERBOX } from "../theme";

const Card: React.FC<{ para: string; oferta: string; from: number }> = ({ para, oferta, from }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  if (frame < from) return null;
  return (
    <div style={{ flex: 1, background: `${C.navy}cc`, border: `1px solid ${C.silverDark}`, padding: "38px 40px", opacity: t, transform: `translateY(${(1 - t) * 60}px)`, display: "flex", flexDirection: "column", gap: 18, minHeight: 250 }}>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 26, color: C.amber, letterSpacing: "0.2em", textTransform: "uppercase" }}>{para}</div>
      <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 32, color: C.white, lineHeight: 1.35 }}>{oferta}</div>
    </div>
  );
};

export const S7Parceria: React.FC<{ sc: Scene }> = ({ sc }) => {
  const frame = useCurrentFrame();
  const cuts = sc.footage.cortes!;
  const t0 = sec(sc.title_in_s - sc.start_s);
  const tUp = t0 + sec(2.5);
  const m = interpolate(frame, [tUp, tUp + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const ty = -230 * m;
  const scale = 1 - 0.25 * m;
  return (
    <AbsoluteFill>
      <ClipSequence cuts={cuts} totalFrames={sc.durationFrames} weights={[5, 4, 5]} darken={0.3} gradient="center" />
      <div style={{ position: "absolute", top: LETTERBOX, bottom: LETTERBOX, left: 0, right: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ transform: `translateY(${ty}px) scale(${scale})` }}>
          <Reveal text={<>VAMOS CONSTRUIR<br />SÃO MATEUS JUNTOS.</>} from={t0} size={74} maxWidth={1500} duration={26} />
        </div>
      </div>
      <div style={{ position: "absolute", left: 120, right: 120, bottom: LETTERBOX + 90, display: "flex", gap: 28 }}>
        {sc.cards!.map((c) => (
          <Card key={c.para} para={c.para} oferta={c.oferta} from={sec(c.in_s - sc.start_s)} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
