import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import { Background } from "./components/Background";
import { SCENES } from "./content";
import { Abertura } from "./scenes/Abertura";
import { Desafio } from "./scenes/Desafio";
import { Estruturacao } from "./scenes/Estruturacao";
import { Incentivos } from "./scenes/Incentivos";
import { Diferenciais } from "./scenes/Diferenciais";
import { Numeros } from "./scenes/Numeros";
import { Encerramento } from "./scenes/Encerramento";

const scenes: Array<[keyof typeof SCENES, React.FC]> = [
  ["abertura", Abertura],
  ["desafio", Desafio],
  ["estruturacao", Estruturacao],
  ["incentivos", Incentivos],
  ["diferenciais", Diferenciais],
  ["numeros", Numeros],
  ["encerramento", Encerramento],
];

export const Video: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <Audio src={staticFile("trilha.wav")} volume={0.9} />
    {scenes.map(([key, Scene]) => (
      <Sequence key={key} from={SCENES[key].from} durationInFrames={SCENES[key].duration} name={key}>
        <Scene />
      </Sequence>
    ))}
  </AbsoluteFill>
);
