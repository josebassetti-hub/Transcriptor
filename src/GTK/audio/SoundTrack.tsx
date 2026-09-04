import React from "react";
import { Sequence, interpolate, staticFile, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import { ambientCues, musicVolume, sfxCues } from "./soundMap";

const audio = (file: string) => staticFile(`gtk/audio/${file}`);

/**
 * Camadas de som do vídeo: trilha contínua, ambientes reais da fábrica e efeitos sincronizados.
 * Montado fora do TransitionSeries para que os cross-fades de vídeo não cortem o áudio.
 */
export const SoundTrack: React.FC<{ master?: number }> = ({ master = 1 }) => {
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <>
      <Audio
        src={audio("trilha.mp3")}
        volume={(f) =>
          master *
          musicVolume(f) *
          interpolate(f, [0, 20, durationInFrames - 45, durationInFrames - 1], [0, 1, 1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })
        }
      />
      {ambientCues.map((a, i) => (
        <Sequence key={`amb${i}`} from={a.from} durationInFrames={a.durationInFrames} name={`Ambiente ${a.file}`}>
          <Audio
            src={audio(a.file)}
            trimBefore={Math.round(a.trimSeconds * fps)}
            volume={(f) =>
              master *
              a.volume *
              interpolate(f, [0, 20, a.durationInFrames - 20, a.durationInFrames - 1], [0, 1, 1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })
            }
          />
        </Sequence>
      ))}
      {sfxCues.map((c, i) => (
        <Sequence key={`sfx${i}`} from={c.frame} durationInFrames={5 * fps} name={`SFX ${c.file}`}>
          <Audio src={audio(c.file)} volume={() => master * c.volume} playbackRate={c.playbackRate ?? 1} />
        </Sequence>
      ))}
    </>
  );
};
