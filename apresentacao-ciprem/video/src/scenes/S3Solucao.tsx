import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";
import { Scene } from "../data";
import { sec, C } from "../theme";
import { Clip } from "../ui/Clip";
import { Safe } from "../ui/Layout";
import { Reveal, Fade, withAccent } from "../ui/Text";
import { BrandName } from "../ui/BrandName";

export const S3Solucao: React.FC<{ sc: Scene }> = ({ sc }) => {
  const frame = useCurrentFrame();
  const f = sc.footage;
  const t0 = sec(sc.title_in_s - sc.start_s);
  const t1 = sec(sc.subtitle_in_s! - sc.start_s);
  const key = sc.extra![0];
  const tk = sec(key.in_s - sc.start_s);
  // o nome encolhe do centro para o canto superior esquerdo em 20 frames a partir de tk
  const m = interpolate(frame, [tk, tk + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const scale = 1 - 0.62 * m;
  const tx = -520 * m;
  const ty = -290 * m;
  return (
    <AbsoluteFill>
      <Clip file={f.arquivo} inS={f.in_s!} outS={f.out_s!} displayFrames={sc.durationFrames} darken={0.22} gradient="center" />
      <Safe justify="center" style={{ gap: 24 }}>
        <div style={{ transform: `translate(${tx}px, ${ty}px) scale(${scale})`, transformOrigin: "center" }}>
          <BrandName name={sc.title} from={t0} sizeSmall={46} sizeBig={120} />
        </div>
        <Fade text={sc.subtitle} from={t1} until={tk} size={40} />
        {frame >= tk ? (
          <div style={{ position: "absolute", left: 0, right: 0, top: 0, bottom: 0, display: "flex", alignItems: "center", justifyContent: "center", padding: "0 120px" }}>
            <Reveal text={withAccent(key.text)} from={tk + 6} size={78} maxWidth={1500} duration={26} />
          </div>
        ) : null}
      </Safe>
      {/* linha de apoio permanente na base */}
      <Fade text="São Mateus / ES" from={t1 + 10} size={26} color={C.silverDark} upper tracking={0.3} style={{ position: "absolute", bottom: 150, left: 0, right: 0 }} />
    </AbsoluteFill>
  );
};
