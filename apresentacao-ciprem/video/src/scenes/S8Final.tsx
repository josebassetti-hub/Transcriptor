import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Scene } from "../data";
import { sec, C, WIDTH, HEIGHT } from "../theme";
import { Safe } from "../ui/Layout";
import { Reveal, Fade, Rule } from "../ui/Text";

/** Fundo navy com partículas, no espírito da cartela do grupo. Determinístico (sem Math.random). */
const Particles: React.FC = () => {
  const frame = useCurrentFrame();
  const dots = useMemo(() => {
    const arr: Array<{ x: number; y: number; r: number; s: number; p: number }> = [];
    let seed = 7;
    const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
    for (let i = 0; i < 90; i++) arr.push({ x: rnd() * WIDTH, y: rnd() * HEIGHT, r: 1 + rnd() * 3, s: 0.2 + rnd() * 0.6, p: rnd() * Math.PI * 2 });
    return arr;
  }, []);
  return (
    <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0 }}>
      {dots.map((d, i) => {
        const y = (d.y - frame * d.s + HEIGHT) % HEIGHT;
        const o = 0.25 + 0.35 * Math.sin(frame * 0.05 + d.p);
        return <circle key={i} cx={d.x} cy={y} r={d.r} fill="#9fc4ff" opacity={o} />;
      })}
    </svg>
  );
};

export const S8Final: React.FC<{ sc: Scene }> = ({ sc }) => {
  const frame = useCurrentFrame();
  const t0 = sec(sc.title_in_s - sc.start_s);
  const t1 = sec(sc.subtitle_in_s! - sc.start_s);
  const [contatos, assinatura] = sc.extra!;
  const tc = sec(contatos.in_s - sc.start_s);
  const ta = sec(assinatura.in_s - sc.start_s);
  const fadeOut = interpolate(frame, [sc.durationFrames - 20, sc.durationFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const [cip, grupo] = sc.title.split("|").map((s) => s.trim());
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 45%, ${C.navyLight} 0%, ${C.navy} 55%, #000010 100%)` }}>
      <Particles />
      <Safe justify="center" style={{ gap: 26 }}>
        <Reveal text={cip} from={t0} size={150} metallic tracking={0.24} duration={22} />
        <Fade text={grupo} from={t0 + 12} size={30} color={C.silver} upper tracking={0.35} weight={500} />
        <Rule from={t1 - 10} width={700} style={{ marginTop: 10 }} />
        <Fade text={sc.subtitle} from={t1} size={40} maxWidth={1300} />
        {contatos.text.split("\n").map((linha, i) => (
          <Fade key={i} text={linha} from={tc + i * 10} size={28} color={C.silver} tracking={0.06} style={{ marginTop: i === 0 ? 18 : 4 }} />
        ))}
        <Fade text={assinatura.text} from={ta} size={32} color={C.silver} italic style={{ marginTop: 26 }} />
      </Safe>
      <AbsoluteFill style={{ background: "#000", opacity: fadeOut }} />
    </AbsoluteFill>
  );
};
