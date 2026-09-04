/**
 * Layout da planta em metros (origem no canto superior-esquerdo do terreno; x para a direita, y para baixo).
 * Adaptado do desenho Gervasi "LAYOUT SAO FRANCISCO IND. COM. - REV03" (2 linhas XP550) para uma linha XP350:
 * anexo lateral com silo + central de agregados, linha na metade próxima do anexo, cura na metade oposta.
 */
export const PX_PER_M = 8;

export const terrain = { w: 250, d: 100 }; // 25.000 m²

// Galpão 38 x 20 m (≈ 760 m² cobertos) + área de cura/pátio coberta ao lado = ~1.500 m² cobertos
export const shed = { x: 60, y: 32, w: 38, d: 20, h: 7.5 };
// Galpão de cura/estoque contíguo (mesma cobertura, prolongando o galpão)
export const shedCure = { x: 98, y: 32, w: 38, d: 20, h: 7.5 };
// Anexo externo de 4,8 m de largura ao longo do galpão (silo, central de agregados, rosca)
export const annex = { x: 60, y: 26.5, w: 38, d: 4.8 };
// Pátio de expedição / estoque de pallets
export const yard = { x: 138, y: 30, w: 40, d: 24 };
// Área de expansão (restante do terreno)
export const expansion = { x: 60, y: 60, w: 120, d: 32 };
// Acesso e rodovia BR-381 (na borda inferior do terreno)
export const road = { y: 100, d: 8 };
export const access = { x: 40, y: 56, w: 8, d: 44 };

export type Box = { x: number; y: number; w: number; d: number; h: number; z?: number };

export type EquipmentPlacement = {
  id: string;
  label: string;
  /** slot de mídia aplicado na face frontal (opcional) */
  media?: string;
  /** cor principal */
  color: string;
  /** cor de detalhe */
  accent?: string;
  box: Box;
  /** ordem de "acender" no sobrevoo */
  order: number;
  kind?: "box" | "cylinder" | "hopper" | "rack";
};

const Y = "#F7B500";
const R = "#D6232B";
const S = "#B8BEC7";

export const equipmentPlacements: EquipmentPlacement[] = [
  { id: "silo", label: "Silo de cimento 90 t", color: S, accent: Y, kind: "cylinder", order: 1,
    box: { x: 62, y: 27.4, w: 3, d: 3, h: 12 } },
  { id: "rosca", label: "Rosca 7 m", color: S, kind: "box", order: 1,
    box: { x: 65, y: 28.4, w: 7, d: 0.6, h: 0.6, z: 2.6 } },
  { id: "central", label: "Central de agregados 4 cubas", color: S, accent: Y, kind: "hopper", order: 2,
    box: { x: 73, y: 27, w: 12, d: 3.5, h: 4.5 } },
  { id: "esteira-agregados", label: "Esteira 12 m", color: Y, kind: "box", order: 3,
    box: { x: 75, y: 33, w: 12, d: 0.9, h: 0.5, z: 1.4 } },
  { id: "misturador", label: "Misturador MXS-1000", color: R, accent: Y, kind: "box", order: 3,
    box: { x: 87.5, y: 33.5, w: 2.8, d: 2.6, h: 2.4, z: 2.4 } },
  { id: "misturador-base", label: "", color: S, kind: "box", order: 3,
    box: { x: 87.5, y: 33.5, w: 2.8, d: 2.6, h: 2.4 } },
  { id: "esteira-6", label: "Esteira 6 m", color: Y, kind: "box", order: 4,
    box: { x: 84.5, y: 37.5, w: 6, d: 0.9, h: 0.5, z: 1.2 } },
  { id: "vibroprensa", label: "Vibroprensa XP350", media: "video:xp350-ciclo", color: R, accent: Y, kind: "box", order: 5,
    box: { x: 79.5, y: 36.5, w: 3.2, d: 3, h: 3.9 } },
  { id: "cabine", label: "Cabine de comando", color: "#E9ECF1", kind: "box", order: 5,
    box: { x: 80, y: 45, w: 3.4, d: 2.9, h: 2.7 } },
  { id: "transportador-bandejas", label: "Transportador de bandejas", color: S, kind: "box", order: 6,
    box: { x: 70, y: 37.6, w: 9.5, d: 0.8, h: 0.9 } },
  { id: "elevador", label: "Acumulador AM02 / DM02", media: "cat:elevador-2", color: R, accent: Y, kind: "box", order: 6,
    box: { x: 67.5, y: 36.6, w: 2.4, d: 2.6, h: 5.2 } },
  { id: "paletizador", label: "Paletizador ST800", media: "cat:paletizador-2", color: Y, accent: R, kind: "box", order: 7,
    box: { x: 62, y: 39.5, w: 4.2, d: 3.4, h: 3.6 } },
  { id: "esteira-pallets", label: "Esteira de pallets", color: S, kind: "box", order: 7,
    box: { x: 62.5, y: 43.5, w: 1.2, d: 6, h: 0.5 } },
];

/** Estantes de cura (multigarfos) no galpão de cura: 3 fileiras x 6 blocos */
export const curingRacks: Box[] = (() => {
  const out: Box[] = [];
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 6; c++) {
      out.push({ x: 100 + c * 6, y: 33.5 + r * 6, w: 5, d: 4.6, h: 3.2 });
    }
  }
  return out;
})();

/** Pallets de blocos no pátio */
export const yardPallets: Box[] = (() => {
  const out: Box[] = [];
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 8; c++) {
      if ((r * 8 + c) % 5 === 3) continue;
      out.push({ x: 141 + c * 4.3, y: 33 + r * 5, w: 1.2, d: 1.2, h: 1.4 + ((r + c) % 3) * 0.3 });
    }
  }
  return out;
})();

export const shedColumns: Box[] = (() => {
  const out: Box[] = [];
  const total = { x: shed.x, y: shed.y, w: shed.w + shedCure.w, d: shed.d, h: shed.h };
  for (let i = 0; i <= 12; i++) {
    const x = total.x + (i * total.w) / 12;
    out.push({ x: x - 0.2, y: total.y - 0.2, w: 0.4, d: 0.4, h: total.h });
    out.push({ x: x - 0.2, y: total.y + total.d - 0.2, w: 0.4, d: 0.4, h: total.h });
  }
  return out;
})();
