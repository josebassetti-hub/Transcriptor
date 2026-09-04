import { staticFile } from "remotion";

export type MediaEntry =
  | { kind: "video"; file: string; width: number; height: number; seconds: number }
  | { kind: "image"; file: string };

// Slot -> arquivo em public/. Slots com `null` ainda não têm arquivo (ver public/gtk/media/README.md).
export const mediaManifest: Record<string, MediaEntry | null> = {
  // Vídeos da fábrica-modelo (mesma linha Gervasi)
  "video:fabrica-tour": { kind: "video", file: "gtk/media/fabrica-tour.mp4", width: 480, height: 848, seconds: 140 },
  "video:xp350-operacao": { kind: "video", file: "gtk/media/xp350-operacao.mp4", width: 848, height: 480, seconds: 43 },
  "video:xp350-ciclo": { kind: "video", file: "gtk/media/xp350-ciclo.mp4", width: 478, height: 850, seconds: 44 },
  "video:fabrica-b-roll-3": null,
  "video:fabrica-b-roll-4": null,
  "image:satelite": null,

  // Recortes do catálogo Gervasi (scripts/extract-catalog.py)
  "cat:xp350": { kind: "image", file: "gtk/media/catalogo/xp350.jpg" },
  "cat:xp350-detalhe": { kind: "image", file: "gtk/media/catalogo/xp350-detalhe.jpg" },
  "cat:central-agregados": { kind: "image", file: "gtk/media/catalogo/central-agregados.jpg" },
  "cat:esteira-balanca": { kind: "image", file: "gtk/media/catalogo/esteira-balanca.jpg" },
  "cat:misturador": { kind: "image", file: "gtk/media/catalogo/misturador.jpg" },
  "cat:carro-aereo": { kind: "image", file: "gtk/media/catalogo/carro-aereo.jpg" },
  "cat:silo": { kind: "image", file: "gtk/media/catalogo/silo.jpg" },
  "cat:rosca-cimento": { kind: "image", file: "gtk/media/catalogo/rosca-cimento.jpg" },
  "cat:paletizador": { kind: "image", file: "gtk/media/catalogo/paletizador.jpg" },
  "cat:paletizador-2": { kind: "image", file: "gtk/media/catalogo/paletizador-2.jpg" },
  "cat:elevador-bandejas": { kind: "image", file: "gtk/media/catalogo/elevador-bandejas.jpg" },
  "cat:elevador-2": { kind: "image", file: "gtk/media/catalogo/elevador-2.jpg" },
  "cat:diagrama-linha": { kind: "image", file: "gtk/media/catalogo/diagrama-linha.jpg" },
  "cat:produtos": { kind: "image", file: "gtk/media/catalogo/produtos.jpg" },
  "cat:produtos-tipos": { kind: "image", file: "gtk/media/catalogo/produtos-tipos.jpg" },

  // Layout de referência (Gervasi, planta São Francisco)
  "layout:p1": { kind: "image", file: "gtk/media/layout/sao-francisco-p1.png" },
  "layout:p2": { kind: "image", file: "gtk/media/layout/sao-francisco-p2.png" },
};

export const getMedia = (id: string): MediaEntry | null => mediaManifest[id] ?? null;

export const mediaSrc = (id: string): string | null => {
  const m = getMedia(id);
  return m ? staticFile(m.file) : null;
};
