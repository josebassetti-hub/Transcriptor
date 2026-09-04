import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";
import { Scene } from "../data";
import { sec, C, FONT } from "../theme";
import { Clip } from "../ui/Clip";
import { Safe } from "../ui/Layout";
import { Reveal, withAccent } from "../ui/Text";

const Chip: React.FC<{ text: string; from: number; until: number }> = ({ text, from, until }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const out = interpolate(frame, [until, until + 10], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  if (frame < from || out <= 0) return null;
  return (
    <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 26, color: C.white, letterSpacing: "0.06em", textTransform: "uppercase", whiteSpace: "nowrap", padding: "14px 28px", border: `1px solid ${C.silverDark}`, background: `${C.navy}b3`, opacity: t * out, transform: `translateY(${(1 - t) * 16 - (1 - out) * 30}px)` }}>
      {text}
    </div>
  );
};

export const S6Obras: React.FC<{ sc: Scene }> = ({ sc }) => {
  const f = sc.footage;
  const t0 = sec(sc.title_in_s - sc.start_s);
  const t1 = sec(sc.subtitle_in_s! - sc.start_s);
  const key = sc.extra![0];
  const tk = sec(key.in_s - sc.start_s);
  const chips = sc.subtitle!.split("|").map((s) => s.trim());
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Clip file={f.arquivo} inS={f.in_s!} outS={f.out_s!} displayFrames={sc.durationFrames} darken={0.3} gradient="center" zoom={1.04} />
      <Safe justify="center" style={{ gap: 40 }}>
        <Reveal text={sc.title} from={t0} until={tk} size={62} maxWidth={1500} duration={26} />
        <div style={{ display: "flex", gap: 22, justifyContent: "center" }}>
          {chips.map((c, i) => (
            <Chip key={c} text={c} from={t1 + i * 10} until={tk} />
          ))}
        </div>
      </Safe>
      {frame >= tk ? (
        <Safe justify="center">
          <Reveal text={withAccent(key.text)} from={tk + 8} size={76} maxWidth={1500} duration={26} />
        </Safe>
      ) : null}
    </AbsoluteFill>
  );
};
