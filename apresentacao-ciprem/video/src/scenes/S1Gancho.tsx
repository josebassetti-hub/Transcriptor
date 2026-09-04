import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";
import { Scene } from "../data";
import { sec, C, FONT } from "../theme";
import { Clip } from "../ui/Clip";
import { Safe } from "../ui/Layout";
import { Reveal } from "../ui/Text";

/** Título palavra por palavra (12 frames por palavra), como o reveal da vinheta. */
const Words: React.FC<{ text: string; from: number; size: number; step?: number }> = ({ text, from, size, step = 12 }) => {
  const words = text.split(" ");
  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: `0 ${size * 0.35}px`, maxWidth: 1500 }}>
      {words.map((w, i) => (
        <Reveal key={i} text={w} from={from + i * step} size={size} duration={14} tracking={0.14} style={{ display: "inline-block" }} />
      ))}
    </div>
  );
};

export const S1Gancho: React.FC<{ sc: Scene }> = ({ sc }) => {
  const frame = useCurrentFrame();
  const f = sc.footage;
  const subFrom = sec(sc.subtitle_in_s! - sc.start_s);
  const pop = interpolate(frame, [subFrom, subFrom + 8], [1.06, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill>
      <Clip file={f.arquivo} inS={f.in_s!} outS={f.out_s!} displayFrames={sc.durationFrames} darken={0.25} gradient="center" />
      <Safe justify="center" style={{ gap: 44 }}>
        <Words text={sc.title} from={sec(sc.title_in_s - sc.start_s)} size={72} />
        {frame >= subFrom ? (
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 104, color: C.amber, letterSpacing: "0.2em", textTransform: "uppercase", transform: `scale(${pop})`, textShadow: "0 6px 30px rgba(0,0,0,0.6)" }}>
            {sc.subtitle}
          </div>
        ) : null}
      </Safe>
    </AbsoluteFill>
  );
};
