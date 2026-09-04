import React, { useEffect, useState } from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, interpolate, continueRender, delayRender } from "remotion";
import { scenes } from "./data";
import { VINHETA_FRAMES, CONTENT_FRAMES, fontsReady, FONT, C } from "./theme";
import { Letterbox } from "./ui/Letterbox";
import { SceneFade } from "./ui/Text";
import { Sfx, Trilha } from "./Sfx";
import { S1Gancho } from "./scenes/S1Gancho";
import { S2Dor } from "./scenes/S2Dor";
import { S3Solucao } from "./scenes/S3Solucao";
import { S4Produtos } from "./scenes/S4Produtos";
import { S5Grupo } from "./scenes/S5Grupo";
import { S6Obras } from "./scenes/S6Obras";
import { S7Parceria } from "./scenes/S7Parceria";
import { S8Final } from "./scenes/S8Final";

const components = [S1Gancho, S2Dor, S3Solucao, S4Produtos, S5Grupo, S6Obras, S7Parceria, S8Final];

export type VideoProps = { preview: boolean };

export const Video: React.FC<VideoProps> = ({ preview }) => {
  const [handle] = useState(() => delayRender("fontes Montserrat"));
  useEffect(() => {
    fontsReady.then(() => continueRender(handle)).catch(() => continueRender(handle));
  }, [handle]);

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {/* Vinheta pronta, intacta, com o áudio original e fade de 1 s no fim */}
      <Sequence from={0} durationInFrames={VINHETA_FRAMES} layout="none">
        <OffthreadVideo
          src={staticFile("footage/vinheta_apresenta.mp4")}
          volume={(f) => interpolate(f, [VINHETA_FRAMES - 25, VINHETA_FRAMES], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          style={{ width: "100%", height: "100%" }}
        />
      </Sequence>

      {/* Conteúdo: 8 cenas do scenes.json, uma trilha e os efeitos */}
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
        <Trilha frames={CONTENT_FRAMES} />
        <Sfx />
      </Sequence>

      <Letterbox />

      {preview ? (
        <div style={{ position: "absolute", top: 30, right: 40, zIndex: 200, fontFamily: FONT, fontWeight: 700, fontSize: 22, color: C.amber, letterSpacing: "0.2em", opacity: 0.8 }}>
          PRÉVIA · TRILHA PROVISÓRIA
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
