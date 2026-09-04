import raw from "../../scenes.json";

export type Cut = { arquivo: string; in_s: number; out_s: number; descricao: string };
export type Footage = {
  arquivo: string;
  in_s: number | null;
  out_s: number | null;
  cortes?: Cut[];
  descricao: string;
  tratamento: string;
  alternativa?: string;
};
export type Extra = { text: string; in_s: number; style: string };
export type Product = { nome: string; uso: string; in_s: number };
export type Card = { para: string; oferta: string; in_s: number };
export type Scene = {
  id: number;
  nome: string;
  startFrame: number;
  durationFrames: number;
  start_s: number;
  end_s: number;
  footage: Footage;
  title: string;
  title_in_s: number;
  subtitle: string | null;
  subtitle_in_s?: number;
  extra?: Extra[];
  products?: Product[];
  cards?: Card[];
  animation: string;
  sfx: string;
  musicCue: string;
};

export const scenes = raw.scenes as unknown as Scene[];
export const meta = raw.meta;

/** Caminho do arquivo de vídeo em public/footage a partir do nome curto usado no JSON. */
export const footageFile = (name: string) => `footage/${name}.mp4`;
