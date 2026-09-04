import React from "react";
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { z } from "zod";
import { Scene01Brand } from "./scenes/Scene01Brand";
import { Scene02Company } from "./scenes/Scene02Company";
import { Scene03Products } from "./scenes/Scene03Products";
import { Scene04Line } from "./scenes/Scene04Line";
import { Scene05Capacity } from "./scenes/Scene05Capacity";
import { Scene06Plant } from "./scenes/Scene06Plant";
import { Scene07Investment } from "./scenes/Scene07Investment";
import { Scene08Jobs } from "./scenes/Scene08Jobs";
import { Scene09Outro } from "./scenes/Scene09Outro";
import { contact } from "./data";
import { colors } from "./theme";

export const gtkSchema = z.object({
  investmentBRL: z.number().min(0),
  directJobs: z.number().int().min(0),
  indirectJobs: z.number().int().min(0),
  contactName: z.string(),
  contactRole: z.string(),
  contactPhone: z.string(),
});

export type GTKProps = z.infer<typeof gtkSchema>;

export const gtkDefaultProps: GTKProps = {
  investmentBRL: 5_000_000,
  directJobs: 12,
  indirectJobs: 36,
  contactName: contact.name,
  contactRole: contact.role,
  contactPhone: contact.phone,
};

// Duração de cada cena (frames a 30 fps). Transições de 12 frames sobrepõem as cenas:
// soma = 2796, total da composição = 2796 - 8*12 = 2700 (90 s).
export const SCENES = {
  brand: 192,
  company: 312,
  products: 312,
  line: 672,
  capacity: 312,
  plant: 312,
  investment: 312,
  jobs: 192,
  outro: 180,
};
export const TRANSITION = 12;
export const TOTAL_FRAMES = Object.values(SCENES).reduce((a, b) => a + b, 0) - TRANSITION * (Object.keys(SCENES).length - 1);

const T: React.FC = () => <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />;

export const GTKInstitutional: React.FC<GTKProps> = (props) => {
  return (
    <AbsoluteFill style={{ background: colors.navyDeep }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={SCENES.brand} name="01 Marca">
          <Scene01Brand />
        </TransitionSeries.Sequence>
        <T />
        <TransitionSeries.Sequence durationInFrames={SCENES.company} name="02 Empresa">
          <Scene02Company />
        </TransitionSeries.Sequence>
        <T />
        <TransitionSeries.Sequence durationInFrames={SCENES.products} name="03 Produtos">
          <Scene03Products />
        </TransitionSeries.Sequence>
        <T />
        <TransitionSeries.Sequence durationInFrames={SCENES.line} name="04 Linha">
          <Scene04Line />
        </TransitionSeries.Sequence>
        <T />
        <TransitionSeries.Sequence durationInFrames={SCENES.capacity} name="05 Capacidade">
          <Scene05Capacity />
        </TransitionSeries.Sequence>
        <T />
        <TransitionSeries.Sequence durationInFrames={SCENES.plant} name="06 Planta 3D">
          <Scene06Plant />
        </TransitionSeries.Sequence>
        <T />
        <TransitionSeries.Sequence durationInFrames={SCENES.investment} name="07 Investimento">
          <Scene07Investment investmentBRL={props.investmentBRL} />
        </TransitionSeries.Sequence>
        <T />
        <TransitionSeries.Sequence durationInFrames={SCENES.jobs} name="08 Empregos">
          <Scene08Jobs directJobs={props.directJobs} indirectJobs={props.indirectJobs} />
        </TransitionSeries.Sequence>
        <T />
        <TransitionSeries.Sequence durationInFrames={SCENES.outro} name="09 Encerramento">
          <Scene09Outro contactName={props.contactName} contactRole={props.contactRole} contactPhone={props.contactPhone} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
