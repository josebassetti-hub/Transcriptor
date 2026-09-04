import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile, continueRender, delayRender } from "remotion";
import { scenes } from "./data";
import { VINHETA_FRAMES, CONTENT_FRAMES, fontsReady } from "./theme";
import { Letterbox } from "./ui/Letterbox";
import { SceneFade } from "./ui/Text";
import { S1Gancho } from "./scenes/S1Gancho";
import { S2Dor } from "./scenes/S2Dor";
import { S3Solucao } from "./scenes/S3Solucao";
import { S4Produtos } from "./scenes/S4Produtos";
import { S5Grupo } from "./scenes/S5Grupo";
import { S6Obras } from "./scenes/S6Obras";
import { S7Parceria } from "./scenes/S7Parceria";
import { S8Final } from "./scenes/S8Final";

const components = [S1Gancho, S2Dor, S3Solucao, S4Produtos, S5Grupo, S6Obras, S7Parceria, S8Final];

export const Video: React.FC = () => {
  const [handle] = useState(() => delayRender("fontes Montserrat"));
  useEffect(() => {
    fontsReady.then(() => continueRender(handle)).catch(() => continueRender(handle));
  }, [handle]);

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {/* Vinheta pronta, intacta na imagem; o som é todo do score único */}
      <Sequence from={0} durationInFrames={VINHETA_FRAMES} layout="none">
        <OffthreadVideo src={staticFile("footage/vinheta_apresenta.mp4")} muted style={{ width: "100%", height: "100%" }} />
      </Sequence>

      {/* Conteúdo: 8 cenas do scenes.json */}
      <Sequence from={VINHETA_FRAMES} durationInFrames={CONTENT_FRAMES} layout="none">
        {scenes.map((sc, i) => {
          const Comp = components[i];
          return (
            <Sequence key={sc.id} from={sc.startFrame} durationInFrames={sc.durationFrames} layout="none">
              <Comp sc={sc} />
              <SceneFade durationInFrames={sc.durationFrames} inFrames={i === 0 ? 20 : 8} />
            </Sequence>
          );
        })}
      </Sequence>

      {/* Desenho de som completo (vinheta + conteúdo), gerado por audio/build_score.py */}
      <Audio src={staticFile("audio/score.wav")} />

      <Letterbox />
    </AbsoluteFill>
  );
};
