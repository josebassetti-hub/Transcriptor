"""Extrai recortes de fotos do catálogo Gervasi (PDF) para public/gtk/media/catalogo/.

Uso: python3 scripts/extract-catalog.py caminho/do/catalogo.pdf
Requer PyMuPDF (pip install pymupdf). Os recortes são frações da página (x0, y0, x1, y1).
"""
import sys, os
import pymupdf

CROPS = {
    # nome: (página 1-based, x0, y0, x1, y1) em frações da página
    "xp350":            (3,  0.00, 0.00, 0.43, 0.32),
    "xp350-detalhe":    (3,  0.46, 0.60, 0.70, 0.89),
    "central-agregados":(12, 0.08, 0.12, 0.66, 0.37),
    "esteira-balanca":  (12, 0.37, 0.60, 0.64, 0.70),
    "misturador":       (13, 0.06, 0.12, 0.65, 0.37),
    "carro-aereo":      (14, 0.06, 0.19, 0.49, 0.42),
    "silo":             (14, 0.52, 0.19, 0.95, 0.42),
    "rosca-cimento":    (14, 0.52, 0.53, 0.95, 0.73),
    "paletizador":      (15, 0.06, 0.10, 0.62, 0.34),
    "paletizador-2":    (15, 0.52, 0.71, 0.95, 0.93),
    "elevador-bandejas":(18, 0.06, 0.13, 0.50, 0.41),
    "elevador-2":       (18, 0.06, 0.79, 0.46, 0.93),
    "diagrama-linha":   (10, 0.10, 0.57, 0.95, 0.93),
    "produtos":         (19, 0.05, 0.15, 0.60, 0.33),
    "produtos-tipos":   (19, 0.05, 0.34, 0.60, 0.44),
}

def main(pdf, out="public/gtk/media/catalogo", dpi=150):
    doc = pymupdf.open(pdf)
    os.makedirs(out, exist_ok=True)
    for name, (page, x0, y0, x1, y1) in CROPS.items():
        p = doc[page - 1]
        r = p.rect
        clip = pymupdf.Rect(r.x0 + r.width * x0, r.y0 + r.height * y0,
                            r.x0 + r.width * x1, r.y0 + r.height * y1)
        pix = p.get_pixmap(dpi=dpi, clip=clip)
        pix.save(os.path.join(out, f"{name}.jpg"), jpg_quality=88)
        print(name, pix.width, pix.height)

if __name__ == "__main__":
    main(sys.argv[1])
