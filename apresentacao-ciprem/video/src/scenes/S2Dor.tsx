import React from "react";
import { AbsoluteFill } from "remotion";
import { Scene } from "../data";
import { sec, C } from "../theme";
import { Clip } from "../ui/Clip";
import { Safe } from "../ui/Layout";
import { Reveal, Fade, Rule } from "../ui/Text";

export const S2Dor: React.FC<{ sc: Scene }> = ({ sc }) => {
  const f = sc.footage;
  const t0 = sec(sc.title_in_s - sc.start_s);
  const t1 = sec(sc.subtitle_in_s! - sc.start_s);
  return (
    <AbsoluteFill>
      <Clip file={f.arquivo} inS={f.in_s!} outS={f.out_s!} displayFrames={sc.durationFrames} darken={0.3} gradient="center" />
      <Safe justify="center" style={{ gap: 30 }}>
        <Reveal text={sc.title} from={t0} size={58} maxWidth={1650} duration={26} />
        <Rule from={t1 - 12} />
        <Fade text={sc.subtitle} from={t1} size={40} color={C.silver} />
      </Safe>
    </AbsoluteFill>
  );
};
