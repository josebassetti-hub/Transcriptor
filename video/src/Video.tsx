import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/800.css";
import "@fontsource/inter/900.css";
import { Background, Grain } from "./components/Fx";
import { SCENES, TRANSITION } from "./content";
import { Abertura } from "./scenes/Abertura";
import { OQueFaz } from "./scenes/OQueFaz";
import { Financiamento } from "./scenes/Financiamento";
import { Incentivos } from "./scenes/Incentivos";
import { Porque } from "./scenes/Porque";
import { Numeros } from "./scenes/Numeros";
import { Final } from "./scenes/Final";

const T = TRANSITION;
const timing = linearTiming({ durationInFrames: T });

// Cada Sequence recebe +T para compensar a sobreposição da transição seguinte,
// assim o início de cada cena continua caindo exatamente no tempo da música.
export const Video: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <Audio src={staticFile("trilha.wav")} volume={0.95} />
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={SCENES.abertura + T}>
        <Abertura />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={wipe({ direction: "from-left" })} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENES.oquefaz + T}>
        <OQueFaz />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENES.financiamento + T}>
        <Financiamento />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={wipe({ direction: "from-top-left" })} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENES.incentivos + T}>
        <Incentivos />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENES.porque + T}>
        <Porque />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={slide({ direction: "from-left" })} timing={timing} />
      <TransitionSeries.Sequence durationInFrames={SCENES.numeros + T}>
        <Numeros />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={wipe({ direction: "from-bottom" })} timing={linearTiming({ durationInFrames: T })} />
      <TransitionSeries.Sequence durationInFrames={SCENES.final}>
        <Final />
      </TransitionSeries.Sequence>
    </TransitionSeries>
    <Grain />
  </AbsoluteFill>
);
