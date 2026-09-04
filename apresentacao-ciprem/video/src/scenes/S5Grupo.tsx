import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";
import { Scene } from "../data";
import { sec, C, FONT } from "../theme";
import { ClipSequence } from "../ui/Clip";
import { Safe } from "../ui/Layout";
import { Reveal, Fade } from "../ui/Text";

const Bullet: React.FC<{ text: string; from: number }> = ({ text, from }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  if (frame < from) return null;
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 20, opacity: t, transform: `translateX(${(1 - t) * 24}px)` }}>
      <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 32, color: C.white, textAlign: "right", maxWidth: 900, lineHeight: 1.3, textShadow: "0 3px 16px rgba(0,0,0,0.6)" }}>{text}</div>
      <div style={{ width: 40 * t, height: 4, background: C.amber, flex: "none" }} />
    </div>
  );
};

export const S5Grupo: React.FC<{ sc: Scene }> = ({ sc }) => {
  const cuts = sc.footage.cortes!;
  return (
    <AbsoluteFill>
      <ClipSequence cuts={cuts} totalFrames={sc.durationFrames} gradient="right" />
      <Safe justify="flex-start" align="flex-end" padY={70} style={{ gap: 18 }}>
        <Reveal text={sc.title} from={sec(sc.title_in_s - sc.start_s)} size={60} metallic align="right" duration={22} />
        <Fade text={sc.subtitle} from={sec(sc.subtitle_in_s! - sc.start_s)} size={36} color={C.silver} align="right" maxWidth={900} />
        <div style={{ display: "flex", flexDirection: "column", gap: 20, marginTop: 30 }}>
          {sc.extra!.map((e) => (
            <Bullet key={e.text} text={e.text} from={sec(e.in_s - sc.start_s)} />
          ))}
        </div>
      </Safe>
    </AbsoluteFill>
  );
};
