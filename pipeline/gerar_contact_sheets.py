#!/usr/bin/env python3
"""Gera contact sheets (folhas de contato) commitáveis a partir dos frames de um vídeo.

Plano v2.1, Adição 1: navegação visual da aula inteira dentro do git, sem precisar do
vídeo — grades de miniaturas com o timestamp de cada frame.

Uso:
  python3 pipeline/gerar_contact_sheets.py 2          # materiais/frames/2 → knowledge/frames/2-contatos/
  python3 pipeline/gerar_contact_sheets.py --todos

Saída: knowledge/frames/<video>-contatos/folha_NN.jpg (~24 miniaturas por folha).
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS, LINHAS = 4, 6                 # 24 miniaturas por folha
MINI_L, MINI_A = 320, 180           # tamanho da miniatura
ROTULO_A = 18                       # faixa do rótulo com o timestamp
MARGEM = 8


def rotulo_do_nome(caminho: str) -> str:
    # f_HHMMSS.CC_a.jpg → "HH:MM:SS a"
    base = os.path.basename(caminho)
    try:
        t, papel = base[2:8], base.rsplit("_", 1)[1].split(".")[0]
        return f"{t[0:2]}:{t[2:4]}:{t[4:6]} {papel}"
    except Exception:
        return base


def gerar(video: str) -> int:
    origem = os.path.join(RAIZ, "materiais", "frames", video)
    destino = os.path.join(RAIZ, "knowledge", "frames", f"{video}-contatos")
    frames = sorted(glob.glob(os.path.join(origem, "f_*.jpg")))
    if not frames:
        print(f"  {video}: nenhum frame em {origem}")
        return 0
    os.makedirs(destino, exist_ok=True)

    por_folha = COLS * LINHAS
    folhas = (len(frames) + por_folha - 1) // por_folha
    larg = COLS * (MINI_L + MARGEM) + MARGEM
    alt = LINHAS * (MINI_A + ROTULO_A + MARGEM) + MARGEM

    for nf in range(folhas):
        folha = Image.new("RGB", (larg, alt), (24, 26, 31))
        des = ImageDraw.Draw(folha)
        lote = frames[nf * por_folha:(nf + 1) * por_folha]
        for i, arq in enumerate(lote):
            col, lin = i % COLS, i // COLS
            x = MARGEM + col * (MINI_L + MARGEM)
            y = MARGEM + lin * (MINI_A + ROTULO_A + MARGEM)
            try:
                mini = Image.open(arq).convert("RGB").resize((MINI_L, MINI_A))
                folha.paste(mini, (x, y))
            except Exception as e:
                des.text((x + 4, y + 4), f"erro: {e}", fill=(255, 120, 120))
            des.text((x + 2, y + MINI_A + 3), rotulo_do_nome(arq), fill=(220, 224, 230))
        saida = os.path.join(destino, f"folha_{nf:02d}.jpg")
        folha.save(saida, quality=68, optimize=True)
    print(f"  {video}: {folhas} folha(s) com {len(frames)} frames → {destino}")
    return folhas


def main() -> int:
    if "--todos" in sys.argv:
        base = os.path.join(RAIZ, "materiais", "frames")
        videos = sorted(os.path.basename(d) for d in glob.glob(os.path.join(base, "*"))
                        if os.path.isdir(d))
    else:
        videos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not videos:
        print(__doc__)
        return 1
    for v in videos:
        gerar(v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
