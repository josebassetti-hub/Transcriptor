import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";
import { FPS, WIDTH, HEIGHT, TOTAL_FRAMES } from "./theme";

/** Uma única composição: vinheta (18.22 s) + 90 s de conteúdo = um único MP4. */
export const Root: React.FC = () => (
  <Composition
    id="CipremEvento"
    component={Video}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
    defaultProps={{ preview: true }}
  />
);
