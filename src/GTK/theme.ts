import { staticFile } from "remotion";
import { loadFont } from "@remotion/fonts";

// Montserrat (fonte variável, pesos 100–900) empacotada em public/fonts para não depender da internet no render.
loadFont({
  family: "Montserrat",
  url: staticFile("fonts/Montserrat-Variable.woff2"),
  weight: "100 900",
  format: "woff2",
});

export const fonts = {
  heading: `Montserrat, "Arial Black", Arial, sans-serif`,
  body: `Montserrat, Arial, Helvetica, sans-serif`,
};

// Paleta: identidade GTK (marinho + amarelo) e cores vivas do catálogo Gervasi nos equipamentos.
export const colors = {
  navy: "#0B2545",
  navyDeep: "#071A33",
  navy2: "#13315C",
  yellow: "#F7B500",
  yellowDark: "#D99A00",
  red: "#D6232B",
  redDark: "#A5181E",
  steel: "#B8BEC7",
  steelDark: "#6F7785",
  concrete: "#8D99AE",
  concreteLight: "#C9CFD8",
  white: "#F5F7FA",
  ink: "#0A0F1A",
  grass: "#5E7F4C",
  grassDark: "#4C6A3D",
  asphalt: "#3A3F47",
  floor: "#D5D8DD",
};

// Área segura para 1920x1080 (regra: 80/100 px em 1080 de largura, escalada).
export const SAFE = { x: 140, y: 110 };

export const VIDEO = { width: 1920, height: 1080, fps: 30 };
