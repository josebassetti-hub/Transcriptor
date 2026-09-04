import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import data from "../../scenes.json";

export const FPS = data.meta.fps;
export const WIDTH = data.meta.width;
export const HEIGHT = data.meta.height;
export const LETTERBOX = data.meta.letterbox_px;
export const VINHETA_FRAMES = Math.round(data.meta.vinheta.duracao_s * FPS); // 456
export const CONTENT_FRAMES = data.meta.duracao_conteudo_frames; // 2250
export const TOTAL_FRAMES = VINHETA_FRAMES + CONTENT_FRAMES;

export const C = {
  navy: data.meta.paleta.navy_fundo,
  navyLight: data.meta.paleta.navy_claro,
  white: data.meta.paleta.branco,
  silver: data.meta.paleta.prata_clara,
  silverDark: data.meta.paleta.prata_escura,
  amber: data.meta.paleta.ambar_destaque,
};

export const FONT = "Montserrat";

const weights: Array<[string, string]> = [
  ["400", "fonts/montserrat-latin-400-normal.woff2"],
  ["500", "fonts/montserrat-latin-500-normal.woff2"],
  ["700", "fonts/montserrat-latin-700-normal.woff2"],
  ["800", "fonts/montserrat-latin-800-normal.woff2"],
];

export const fontsReady = Promise.all(
  weights.map(([weight, file]) =>
    loadFont({ family: FONT, url: staticFile(file), weight, format: "woff2" }),
  ),
);

export const sec = (s: number) => Math.round(s * FPS);
