#!/usr/bin/env python3
"""Extrai o texto visível de cada quadro (OCR) para reforçar a leitura visual.

Usa o tesseract via CLI (instalado pelo setup.sh; opcional). O resultado
serve de índice pesquisável — nomes de menus, campos e valores pequenos que
podem ficar ilegíveis no JPEG — e complementa (não substitui) a leitura dos
quadros com a ferramenta Read.

Gera <outdir>/frames/frames_text.json: [{"frame", "time", "role", "text"}].

Uso:
  python3 ocr_frames.py --outdir saida/ [--lang por+eng]
  (rodar depois do extract_frames.py, no mesmo --outdir)
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", required=True, help="mesmo outdir do extract_frames.py")
    ap.add_argument("--lang", default="por+eng", help="idiomas do tesseract")
    args = ap.parse_args()

    if not shutil.which("tesseract"):
        print("AVISO: tesseract não instalado — pulando OCR (o aprendizado segue "
              "só com a leitura visual dos quadros). Rode setup.sh para instalar.",
              file=sys.stderr)
        return 0

    frames_dir = Path(args.outdir) / "frames"
    index_file = frames_dir / "frames_index.json"
    if not index_file.exists():
        print(f"ERRO: {index_file} não existe — rode extract_frames.py antes.",
              file=sys.stderr)
        return 1

    index = json.loads(index_file.read_text(encoding="utf-8"))
    lang = args.lang
    results = []
    failures = 0
    for entry in index:
        img = frames_dir / entry["frame"]
        proc = subprocess.run(
            ["tesseract", str(img), "stdout", "-l", lang, "--psm", "3"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 and "language" in proc.stderr.lower() and lang != "eng":
            # traineddata do idioma ausente: cai para inglês e segue
            print(f"AVISO: tesseract sem o idioma '{lang}' — usando 'eng' "
                  "(instale tesseract-ocr-por para melhor OCR em português).",
                  file=sys.stderr)
            lang = "eng"
            proc = subprocess.run(
                ["tesseract", str(img), "stdout", "-l", lang, "--psm", "3"],
                capture_output=True, text=True,
            )
        if proc.returncode != 0:
            failures += 1
        text = " ".join(proc.stdout.split()) if proc.returncode == 0 else ""
        results.append({**entry, "text": text})

    out = frames_dir / "frames_text.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    com_texto = sum(1 for r in results if r["text"])
    print(f"[ocr] {com_texto}/{len(results)} quadros com texto -> {out}")
    if results and failures == len(results):
        print("ERRO: o tesseract falhou em todos os quadros — OCR indisponível "
              "(veja os avisos acima).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
