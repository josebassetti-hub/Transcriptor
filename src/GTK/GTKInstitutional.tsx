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
import { SCENES, TRANSITION } from "./timing";
import { SoundTrack } from "./audio/SoundTrack";

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

export { SCENES, TRANSITION, TOTAL_FRAMES } from "./timing";

export const GTKInstitutional: React.FC<GTKProps> = (props) => {
  return (
    <AbsoluteFill style={{ background: colors.navyDeep }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={SCENES.brand} name="01 Marca">
          <Scene01Brand />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
        <TransitionSeries.Sequence durationInFrames={SCENES.company} name="02 Empresa">
          <Scene02Company />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
        <TransitionSeries.Sequence durationInFrames={SCENES.products} name="03 Produtos">
          <Scene03Products />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
        <TransitionSeries.Sequence durationInFrames={SCENES.line} name="04 Linha">
          <Scene04Line />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
        <TransitionSeries.Sequence durationInFrames={SCENES.capacity} name="05 Capacidade">
          <Scene05Capacity />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
        <TransitionSeries.Sequence durationInFrames={SCENES.plant} name="06 Planta 3D">
          <Scene06Plant />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
        <TransitionSeries.Sequence durationInFrames={SCENES.investment} name="07 Investimento">
          <Scene07Investment investmentBRL={props.investmentBRL} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
        <TransitionSeries.Sequence durationInFrames={SCENES.jobs} name="08 Empregos">
          <Scene08Jobs directJobs={props.directJobs} indirectJobs={props.indirectJobs} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
        <TransitionSeries.Sequence durationInFrames={SCENES.outro} name="09 Encerramento">
          <Scene09Outro contactName={props.contactName} contactRole={props.contactRole} contactPhone={props.contactPhone} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <SoundTrack />
    </AbsoluteFill>
  );
};
