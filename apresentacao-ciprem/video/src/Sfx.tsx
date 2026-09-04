import React from "react";
import { Audio, Sequence, staticFile, interpolate } from "remotion";
import { scenes } from "./data";
import { sec } from "./theme";

type Ev = { t: number; file: "hit_big" | "hit_mid" | "whoosh" | "tick"; vol?: number };

/** Eventos de efeitos em segundos do CONTEÚDO (0 = início da cena 1), conforme o roteiro. */
const events: Ev[] = [
  { t: 5.5, file: "hit_big" },        // "ATÉ AGORA."
  { t: 8.5, file: "whoosh" },         // título da dor
  { t: 16, file: "hit_big", vol: 1 }, // CIPREM (maior do vídeo)
  { t: 21, file: "hit_mid" },         // "Brita produzida aqui"
  { t: 26, file: "whoosh" },
  { t: 42, file: "whoosh" }, { t: 44.8, file: "whoosh" }, { t: 47.6, file: "whoosh" }, { t: 50.4, file: "whoosh" }, { t: 53.2, file: "whoosh" },
  { t: 56, file: "whoosh" },
  { t: 62.5, file: "hit_mid" },       // "Quem constrói aqui"
  { t: 66, file: "whoosh" },
  { t: 69, file: "whoosh", vol: 0.5 }, { t: 72, file: "whoosh", vol: 0.5 }, { t: 75, file: "whoosh", vol: 0.5 },
  { t: 80, file: "hit_big", vol: 1 }, // hit final
  ...scenes[3].products!.map<Ev>((p) => ({ t: p.in_s, file: "tick", vol: 0.6 })),
];

const gain: Record<Ev["file"], number> = { hit_big: 0.9, hit_mid: 0.7, whoosh: 0.45, tick: 0.5 };

export const Sfx: React.FC = () => (
  <>
    {events.map((e, i) => (
      <Sequence key={i} from={sec(e.t)} layout="none">
        <Audio src={staticFile(`audio/sfx/${e.file}.wav`)} volume={(e.vol ?? 1) * gain[e.file]} />
      </Sequence>
    ))}
  </>
);

/** Trilha única do conteúdo, com entrada suave e fade final. */
export const Trilha: React.FC<{ frames: number }> = ({ frames }) => (
  <Audio
    src={staticFile("audio/trilha.mp3")}
    volume={(f) => interpolate(f, [0, 25, frames - 30, frames], [0, 0.85, 0.85, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
  />
);
