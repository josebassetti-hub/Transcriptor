import React from "react";
import { AbsoluteFill, Freeze, OffthreadVideo, Sequence, staticFile } from "remotion";
import { FPS, C } from "../theme";
import { footageFile } from "../data";

type Gradient = "none" | "bottom" | "left" | "center" | "right";

type Props = {
  /** nome curto do clipe (novo_investimento, mineracao_1, ...) */
  file: string;
  inS: number;
  outS: number;
  /** quantos frames a cena precisa cobrir com este clipe */
  displayFrames: number;
  /** 0 = sem escurecer, 1 = navy total */
  darken?: number;
  gradient?: Gradient;
  /** taxa máxima permitida (1 = velocidade normal). Câmera lenta é calculada sozinha. */
  maxRate?: number;
  /** zoom leve (1.04 esconde as barras internas da vinheta) */
  zoom?: number;
};

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

/**
 * Corta um trecho de um clipe (sempre mudo) e cobre exatamente `displayFrames`:
 * - se o trecho é mais longo, corta no fim;
 * - se é mais curto, aplica câmera lenta até 0.5x e, se ainda faltar, congela o último quadro.
 */
export const Clip: React.FC<Props> = ({ file, inS, outS, displayFrames, darken = 0, gradient = "none", maxRate = 1, zoom = 1 }) => {
  const srcFrames = Math.round((outS - inS) * FPS);
  const rate = clamp(srcFrames / displayFrames, 0.5, maxRate);
  const covered = Math.min(displayFrames, Math.floor(srcFrames / rate));
  const startFrom = Math.round(inS * FPS);
  const endAt = startFrom + Math.ceil(covered * rate);
  const src = staticFile(footageFile(file));

  const overlays: React.CSSProperties[] = [];
  if (darken > 0) overlays.push({ background: C.navy, opacity: darken });
  if (gradient === "bottom") overlays.push({ background: `linear-gradient(180deg, transparent 45%, ${C.navy} 100%)`, opacity: 0.85 });
  if (gradient === "left") overlays.push({ background: `linear-gradient(90deg, ${C.navy} 0%, ${C.navy}cc 42%, transparent 70%)` });
  if (gradient === "right") overlays.push({ background: `linear-gradient(270deg, ${C.navy} 0%, ${C.navy}cc 42%, transparent 70%)` });
  if (gradient === "center") overlays.push({ background: `radial-gradient(ellipse at center, ${C.navy}b3 0%, ${C.navy}59 55%, transparent 100%)` });

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Sequence from={0} durationInFrames={covered} layout="none">
        <OffthreadVideo src={src} startFrom={startFrom} endAt={endAt} playbackRate={rate} muted style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})` }} />
      </Sequence>
      {covered < displayFrames ? (
        <Sequence from={covered} durationInFrames={displayFrames - covered} layout="none">
          <Freeze frame={0}>
            <OffthreadVideo src={src} startFrom={endAt - 1} endAt={endAt} muted style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})` }} />
          </Freeze>
        </Sequence>
      ) : null}
      {overlays.map((s, i) => (
        <AbsoluteFill key={i} style={s} />
      ))}
    </AbsoluteFill>
  );
};

/** Sequência de cortes que juntos cobrem `totalFrames`, dividindo o tempo igualmente (ou por `weights`). */
export const ClipSequence: React.FC<{
  cuts: Array<{ arquivo: string; in_s: number; out_s: number }>;
  totalFrames: number;
  weights?: number[];
  darken?: number;
  gradient?: Gradient;
  maxRate?: number;
}> = ({ cuts, totalFrames, weights, darken, gradient, maxRate }) => {
  const w = weights ?? cuts.map(() => 1);
  const sum = w.reduce((a, b) => a + b, 0);
  let from = 0;
  return (
    <AbsoluteFill>
      {cuts.map((c, i) => {
        const dur = i === cuts.length - 1 ? totalFrames - from : Math.round((totalFrames * w[i]) / sum);
        const el = (
          <Sequence key={i} from={from} durationInFrames={dur} layout="none">
            <Clip file={c.arquivo} inS={c.in_s} outS={c.out_s} displayFrames={dur} darken={darken} gradient={gradient} maxRate={maxRate} />
          </Sequence>
        );
        from += dur;
        return el;
      })}
    </AbsoluteFill>
  );
};
