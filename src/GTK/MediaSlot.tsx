import React from "react";
import { Img, useVideoConfig } from "remotion";
import { Video } from "@remotion/media";
import { getMedia, mediaSrc } from "./mediaManifest";

type Props = {
  id: string;
  style?: React.CSSProperties;
  /** segundos a pular no início do vídeo */
  trimSeconds?: number;
  fit?: "cover" | "contain";
  loop?: boolean;
  /** conteúdo mostrado quando o slot não tem arquivo */
  fallback?: React.ReactNode;
};

/**
 * Renderiza a mídia de um slot do manifesto (foto ou vídeo). Se o slot estiver vazio,
 * mostra o `fallback` (normalmente uma ilustração SVG).
 */
export const MediaSlot: React.FC<Props> = ({
  id,
  style,
  trimSeconds = 0,
  fit = "cover",
  loop = true,
  fallback = null,
}) => {
  const { fps } = useVideoConfig();
  const media = getMedia(id);
  const src = mediaSrc(id);
  if (!media || !src) {
    return <>{fallback}</>;
  }
  const base: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: fit,
    display: "block",
    ...style,
  };
  if (media.kind === "image") {
    return <Img src={src} style={base} />;
  }
  return (
    <Video
      src={src}
      muted
      loop={loop}
      trimBefore={Math.round(trimSeconds * fps)}
      style={base}
      objectFit={fit}
    />
  );
};
