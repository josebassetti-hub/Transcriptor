import { SCENES, TRANSITION } from "../timing";

/** Frame absoluto em que cada cena começa (as transições de 12 frames sobrepõem as cenas). */
const order = ["brand", "company", "products", "line", "capacity", "plant", "investment", "jobs", "outro"] as const;
export type SceneKey = (typeof order)[number];

export const sceneStart: Record<SceneKey, number> = (() => {
  const out = {} as Record<SceneKey, number>;
  let acc = 0;
  order.forEach((k, i) => {
    out[k] = acc - (i > 0 ? TRANSITION * i : 0);
    acc += SCENES[k];
  });
  return out;
})();

export type Cue = {
  /** arquivo em public/gtk/audio/ */
  file: string;
  /** frame absoluto */
  frame: number;
  volume: number;
  playbackRate?: number;
};

const at = (scene: SceneKey, local: number) => sceneStart[scene] + local;

const cues: Cue[] = [];
const cue = (scene: SceneKey, local: number, file: string, volume: number, playbackRate?: number) =>
  cues.push({ file, frame: at(scene, local), volume, playbackRate });

// 1 · Marca — impactos de bloco no encaixe do logo, riser e whoosh na linha, brilho na tagline
cue("brand", 6, "impact-concreto.wav", 0.9);
cue("brand", 12, "impact-concreto.wav", 0.8, 0.94);
cue("brand", 20, "impact-concreto.wav", 1.0, 0.88);
cue("brand", 40, "riser.wav", 0.5);
cue("brand", 60, "whoosh-curto.wav", 0.6);
cue("brand", 70, "shimmer.wav", 0.45);

// 2 · Empresa — zoom do mapa, pino, raio, ticks das linhas
cue("company", 20, "whoosh-longo.wav", 0.55);
cue("company", 100, "thud.wav", 0.9);
cue("company", 120, "ding.wav", 0.35, 1.2);
[26, 32, 38, 44].forEach((f) => cue("company", f, "tick.wav", 0.5));

// 3 · Produtos — cards pousando
[22, 34, 46].forEach((f, i) => cue("products", f, "thud.wav", 0.7, 1 + i * 0.05));

// 4 · Linha — whoosh + clique por etapa, "shunk" hidráulico na vibroprensa
for (let k = 0; k < 7; k++) {
  const f = 42 + k * 90;
  cue("line", f, "whoosh-curto.wav", 0.55, 1.1);
  cue("line", f + 4, "tick.wav", 0.6, 0.8);
  if (k === 4) cue("line", f + 10, "shunk.wav", 0.9);
}

// 5 · Capacidade — rajada de ticks nos contadores + ding ao final de cada
[30, 42, 54, 66].forEach((s, i) => {
  for (let t = 0; t < 36; t += 3) cue("capacity", s + t, "tick.wav", 0.28 + (t / 36) * 0.2, 1 + t / 60);
  cue("capacity", s + 58, "ding.wav", 0.55, 1 + i * 0.12);
});

// 6 · Planta 3D — sobrevoo, mergulho, equipamentos acendendo
cue("plant", 0, "whoosh-aereo.wav", 0.5);
cue("plant", 118, "riser.wav", 0.55);
cue("plant", 150, "subdrop.wav", 0.9);
for (let k = 0; k < 7; k++) cue("plant", 150 + k * 24, "power-on.wav", 0.7, 0.95 + k * 0.03);
for (let k = 0; k < 6; k++) cue("plant", 158 + k * 24, "ding.wav", 0.28, 1.4);

// 7 · Investimento — impacto no número, ticks acelerando, ding grave, pops nos chips
cue("investment", 10, "impact-cine.wav", 1.0);
for (let t = 14; t < 84; t += 4) cue("investment", t, "tick.wav", 0.3 + ((t - 14) / 70) * 0.3, 0.9 + (t - 14) / 100);
cue("investment", 86, "ding-grave.wav", 0.8);
[90, 102, 114].forEach((f) => cue("investment", f, "pop.wav", 0.6));

// 8 · Empregos — pops por pessoa, dings nos totais, acorde no 48
for (let i = 0; i < 12; i++) cue("jobs", 20 + i * 2, "pop.wav", 0.35, 1 + (i % 3) * 0.08);
for (let i = 0; i < 36; i++) cue("jobs", 60 + i, "pop.wav", 0.16, 1.2 + (i % 4) * 0.06);
cue("jobs", 50, "ding.wav", 0.5);
cue("jobs", 100, "ding.wav", 0.5, 0.9);
cue("jobs", 112, "ding-grave.wav", 0.7);

// 9 · Encerramento — impactos do logo, pop do contato
cue("outro", 0, "impact-concreto.wav", 0.8);
cue("outro", 6, "impact-concreto.wav", 0.7, 0.94);
cue("outro", 14, "impact-cine.wav", 0.9);
cue("outro", 40, "pop.wav", 0.7, 0.8);
cue("outro", 44, "ding.wav", 0.45);

export const sfxCues: Cue[] = cues.sort((a, b) => a.frame - b.frame);

/** Trechos de som ambiente real da fábrica (áudio extraído dos vídeos). */
export const ambientCues: { file: string; from: number; durationInFrames: number; trimSeconds: number; volume: number }[] = [
  { file: "amb-fabrica-tour.mp3", from: at("brand", 0), durationInFrames: SCENES.brand, trimSeconds: 30, volume: 0.06 },
  { file: "amb-xp350-operacao.mp3", from: at("line", 0), durationInFrames: SCENES.line, trimSeconds: 18, volume: 0.14 },
  { file: "amb-xp350-ciclo.mp3", from: at("capacity", 0), durationInFrames: SCENES.capacity, trimSeconds: 3, volume: 0.16 },
  { file: "amb-fabrica-tour.mp3", from: at("plant", 0), durationInFrames: SCENES.plant, trimSeconds: 60, volume: 0.07 },
  { file: "amb-fabrica-tour.mp3", from: at("outro", 0), durationInFrames: SCENES.outro, trimSeconds: 90, volume: 0.05 },
];

/** Curva de volume da trilha (0–1) por frame absoluto: respiração antes do número do investimento e fade final. */
export const musicVolume = (frame: number): number => {
  const inv = sceneStart.investment;
  if (frame >= inv - 6 && frame < inv + 10) return 0.55; // respiração antes do impacto
  if (frame >= sceneStart.jobs && frame < sceneStart.outro) return 0.8;
  return 0.95;
};
