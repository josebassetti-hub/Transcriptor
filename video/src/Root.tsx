import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";
import { FPS, HEIGHT, TOTAL_FRAMES, WIDTH } from "./content";

export const Root: React.FC = () => (
  <Composition
    id="Projet"
    component={Video}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
