#!/usr/bin/env python3
"""Gera um vídeo sintético de teste para o extract_actions.py, com GABARITO.

Simula uma tela de sistema (janela, dois botões, um campo de texto) onde um
cursor de mouse se move, clica e digita — com feedback visual realista
(botão escurece ao clicar, caret piscando, texto surgindo letra a letra).
Nada de marcadores artificiais: o extrator precisa achar tudo só pelos pixels.

Saídas:
  video_acoes_teste.mp4   (1280x720, 10 fps, ~22 s, sem áudio)
  acoes_verdade.json      (gabarito: cliques, digitação, trajetória-chave)
"""

import json
from pathlib import Path

import cv2
import numpy as np

W, H, FPS = 1280, 720, 10
DUR = 22.0

# --- elementos da "tela" -----------------------------------------------------
BTN1 = (820, 160, 240, 64)    # x, y, w, h  — "Emitir Guia"
BTN2 = (820, 460, 240, 64)    # "Gerar Boleto"
FIELD = (300, 340, 420, 52)   # campo de texto
TEXTO_DIGITADO = "12.345.678/0001-99"

# --- roteiro do cursor: (t_seg, x, y) — interpolação com easing --------------
WAYPOINTS = [
    (0.0, 200, 620), (2.0, 200, 620), (4.5, 940, 192), (5.6, 940, 192),
    (8.0, 510, 366), (9.0, 510, 366), (15.5, 510, 366), (18.0, 940, 492),
    (19.0, 940, 492), (21.5, 300, 650),
]
CLIQUES = [  # (t, x, y, alvo)
    (5.0, 940, 192, "botao Emitir Guia"),
    (8.5, 510, 366, "campo CNPJ"),
    (18.5, 940, 492, "botao Gerar Boleto"),
]
DIGITACAO = {"t_ini": 9.5, "t_fim": 14.5, "texto": TEXTO_DIGITADO, "campo": FIELD}


def pos_cursor(t: float):
    if t <= WAYPOINTS[0][0]:
        return WAYPOINTS[0][1], WAYPOINTS[0][2]
    for (t0, x0, y0), (t1, x1, y1) in zip(WAYPOINTS, WAYPOINTS[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / max(t1 - t0, 1e-6)
            f = f * f * (3 - 2 * f)  # smoothstep (aceleração natural)
            return int(x0 + (x1 - x0) * f), int(y0 + (y1 - y0) * f)
    return WAYPOINTS[-1][1], WAYPOINTS[-1][2]


def draw_cursor(img, x, y):
    """Seta padrão estilo Windows: preenchimento branco, contorno preto."""
    pts = np.array([[0, 0], [0, 16], [4, 12], [7, 19], [10, 18], [7, 11],
                    [12, 11]], np.int32) + [x, y]
    cv2.fillPoly(img, [pts], (255, 255, 255))
    cv2.polylines(img, [pts], True, (0, 0, 0), 1, cv2.LINE_AA)


def draw_button(img, rect, label, pressed=False):
    x, y, w, h = rect
    cor = (170, 120, 60) if not pressed else (110, 75, 35)
    cv2.rectangle(img, (x, y), (x + w, y + h), cor, -1)
    cv2.rectangle(img, (x, y), (x + w, y + h), (60, 40, 20), 2)
    cv2.putText(img, label, (x + 18, y + h // 2 + 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)


def frame_at(t: float) -> np.ndarray:
    img = np.full((H, W, 3), (46, 38, 32), np.uint8)          # fundo
    cv2.rectangle(img, (120, 80), (1160, 660), (243, 240, 236), -1)  # janela
    cv2.rectangle(img, (120, 80), (1160, 120), (196, 150, 96), -1)   # barra título
    cv2.putText(img, "Sistema de Guias - Prefeitura", (140, 108),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2, cv2.LINE_AA)

    press1 = any(0 <= t - c[0] < 0.4 and c[3].startswith("botao Emitir") for c in CLIQUES)
    press2 = any(0 <= t - c[0] < 0.4 and c[3].startswith("botao Gerar") for c in CLIQUES)
    draw_button(img, BTN1, "Emitir Guia", press1)
    draw_button(img, BTN2, "Gerar Boleto", press2)

    fx, fy, fw, fh = FIELD
    cv2.putText(img, "CNPJ da empresa:", (fx, fy - 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh), (255, 255, 255), -1)
    focado = t >= CLIQUES[1][0]
    cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh),
                  (200, 120, 40) if focado else (150, 150, 150), 2)

    d = DIGITACAO
    n = 0
    if t >= d["t_ini"]:
        n = min(len(d["texto"]),
                int(len(d["texto"]) * (t - d["t_ini"]) / (d["t_fim"] - d["t_ini"])))
    parcial = d["texto"][:n]
    if parcial:
        cv2.putText(img, parcial, (fx + 10, fy + fh - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2, cv2.LINE_AA)
    if focado and t <= d["t_fim"] + 2 and int(t * 2) % 2 == 0:  # caret piscando
        (tw, _), _ = cv2.getTextSize(parcial, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cx = fx + 12 + tw
        cv2.line(img, (cx, fy + 10), (cx, fy + fh - 10), (20, 20, 20), 2)

    draw_cursor(img, *pos_cursor(t))
    return img


def main():
    out = Path(__file__).resolve().parent
    vid = out / "video_acoes_teste.mp4"
    wr = cv2.VideoWriter(str(vid), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    n_frames = int(DUR * FPS)
    for i in range(n_frames):
        wr.write(frame_at(i / FPS))
    wr.release()

    gabarito = {
        "video": vid.name, "fps": FPS, "duracao": DUR,
        "cliques": [{"t": t, "x": x, "y": y, "alvo": a} for t, x, y, a in CLIQUES],
        "digitacao": DIGITACAO,
        "waypoints": [{"t": t, "x": x, "y": y} for t, x, y in WAYPOINTS],
    }
    (out / "acoes_verdade.json").write_text(
        json.dumps(gabarito, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"gerado: {vid} ({n_frames} quadros) + acoes_verdade.json")


if __name__ == "__main__":
    main()
