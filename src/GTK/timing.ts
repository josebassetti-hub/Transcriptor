// Duração de cada cena (frames a 30 fps). Transições de 12 frames sobrepõem as cenas:
// soma = 2796, total da composição = 2796 - 8*12 = 2700 (90 s).
export const SCENES = {
  brand: 192,
  company: 312,
  products: 312,
  line: 672,
  capacity: 312,
  plant: 312,
  investment: 312,
  jobs: 192,
  outro: 180,
};
export const TRANSITION = 12;
export const TOTAL_FRAMES = Object.values(SCENES).reduce((a, b) => a + b, 0) - TRANSITION * (Object.keys(SCENES).length - 1);
