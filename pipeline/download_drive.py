#!/usr/bin/env python3
"""Baixa arquivos grandes do Google Drive (Rota A).

Pré-requisitos (ação do usuário, uma vez):
  1. Política de rede do ambiente permitindo: drive.google.com,
     drive.usercontent.google.com, *.googleapis.com
  2. Arquivos (ou a pasta) compartilhados como "qualquer pessoa com o link – leitor".

Uso:
  python3 pipeline/download_drive.py                # baixa os vídeos do curso
  python3 pipeline/download_drive.py ID destino.ext # baixa um arquivo específico

Lida com a página de confirmação "arquivo grande demais para verificação de vírus"
do Drive e retoma downloads interrompidos (HTTP Range).
"""
import os
import re
import sys
import time

import requests

VIDEOS = {
    # fileId: nome de destino
    "1J2FsUxvcQwOZc5dU38PuBN1adbEwTOo0": "2.mov",
    "1dLqzlFCOqGm17qaWAw-cHuqzT3EowVur": "3.mov",
    "1MTbh_m6LJiJFp0ws4zO81RCSkzqNPEZS": "4.mov",
    "1ZRd6gq5e_CgB9uNznz-GOGM_DeED3F8_": "5.mov",
    # 1.mov: adicionar o fileId quando confirmado no inventário
}

# Binários médios que não passam pelo conector MCP (limite ~70KB)
BINARIOS = {
    "1ylbMcTX7bzgOJpk_xU7O15CuxF2gvNSi": "Automatizador para Projetistas V1.4.xlsm",
    "1ED5KYsL_jQ7oKftrmNkWWrsv-yYRcKPF": "Exemplo investimento rural.INVRUR",
    "1WFTMradbIqLDI2MDX-x4tS6f6NROoX0G": "Exemplo recria e engorda.CUSTEIOPECUARIO",
    "1PijXUJpwWMEV7fJuodBkxveV8OKDPOvW": "Exemplo com racao.CUSTEIOPECUARIO",
    "1VQsWa0Q0ywf50bs-a3Nmcsxxrlcl8gu4": "planilha investimento rural-curso.INVRUR",
    "1B_Ja9V9D32aLauBHiW0BgAwcpvMcPcXu": "Check List Externo - Rural V3.2.zip",
    "1k-vPICe4GVdZxgpO5gNbdLunhzTQZDmY": "Ferramenta para Coordenadas Geodesicas.xlsm",
    "1FRDJRz8Y9yxBHwM527o7pEDN9NkwlY7R": "Credito Rural - Apresentacao.pdf",
    "14rDhloRBMKw6jvfN-ZUzTXKTXi-lS5cm": "Tutorial de Configuracao do Excel.pdf",
    "1PqeB6QScDlWStqd_SUybgD8_3hNsB_cy": "Custos e despesas.pdf",
    "17Q2BonU8AB_hAQb8XMCBppvNNt2rkNOI": "Evolucao rebanho de leite.pdf",
    "1Tui4Rwhi9Py_-RupxAlFsZhFFBvs5yBm": "Capacidade de pagamento.pdf",
}

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_VIDEOS = os.path.join(RAIZ, "materiais", "videos")
DIR_BRUTOS = os.path.join(RAIZ, "materiais", "brutos")


def baixar(file_id: str, destino: str, tentativas: int = 4) -> bool:
    """Baixa via gdown (principal, com resume); fallback manual se indisponível."""
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    try:
        import gdown
        for tentativa in range(1, tentativas + 1):
            try:
                saida = gdown.download(id=file_id, output=destino,
                                       quiet=False, resume=True)
                if saida and os.path.exists(destino):
                    print(f"  OK (gdown): {os.path.basename(destino)} "
                          f"({os.path.getsize(destino) >> 20} MB)")
                    return True
            except Exception as e:
                espera = 2 ** tentativa
                print(f"  gdown tentativa {tentativa}/{tentativas}: {e} — {espera}s")
                time.sleep(espera)
        print("  gdown esgotou tentativas; tentando downloader manual...")
    except ImportError:
        print("  gdown não instalado; usando downloader manual.")
    return _baixar_manual(file_id, destino, tentativas)


def _baixar_manual(file_id: str, destino: str, tentativas: int = 4) -> bool:
    """Fallback: baixa driblando a tela de confirmação na mão."""
    url = "https://drive.usercontent.google.com/download"
    params = {"id": file_id, "export": "download", "confirm": "t"}
    sessao = requests.Session()
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    temp = destino + ".part"

    for tentativa in range(1, tentativas + 1):
        try:
            ja_baixado = os.path.getsize(temp) if os.path.exists(temp) else 0
            headers = {"Range": f"bytes={ja_baixado}-"} if ja_baixado else {}
            r = sessao.get(url, params=params, headers=headers, stream=True, timeout=60)

            ctype = r.headers.get("Content-Type", "")
            if "text/html" in ctype:
                # Página de confirmação — extrai token/uuid do formulário
                html = r.text
                form = dict(re.findall(r'name="(\w+)" value="([^"]*)"', html))
                if not form:
                    print(f"  ERRO: Drive devolveu HTML sem formulário — o arquivo "
                          f"está compartilhado por link? ({file_id})")
                    return False
                r = sessao.get(url, params={**params, **form}, headers=headers,
                               stream=True, timeout=60)

            r.raise_for_status()
            modo = "ab" if ja_baixado else "wb"
            total = int(r.headers.get("Content-Length", 0)) + ja_baixado
            baixado = ja_baixado
            marco = time.time()
            with open(temp, modo) as f:
                for pedaco in r.iter_content(chunk_size=1 << 20):
                    f.write(pedaco)
                    baixado += len(pedaco)
                    if time.time() - marco > 15:
                        pct = f"{100*baixado/total:.0f}%" if total else f"{baixado>>20}MB"
                        print(f"  ... {os.path.basename(destino)}: {pct}", flush=True)
                        marco = time.time()
            os.replace(temp, destino)
            print(f"  OK: {os.path.basename(destino)} ({baixado >> 20} MB)")
            return True
        except Exception as e:
            espera = 2 ** tentativa
            print(f"  tentativa {tentativa}/{tentativas} falhou: {e} — "
                  f"aguardando {espera}s", flush=True)
            time.sleep(espera)
    return False


def main() -> int:
    if len(sys.argv) == 3:
        return 0 if baixar(sys.argv[1], sys.argv[2]) else 1

    falhas = []
    print("== Binários médios ==")
    for fid, nome in BINARIOS.items():
        destino = os.path.join(DIR_BRUTOS, nome)
        if os.path.exists(destino):
            print(f"  já existe: {nome}")
            continue
        if not baixar(fid, destino):
            falhas.append(nome)

    print("== Vídeos ==")
    for fid, nome in VIDEOS.items():
        destino = os.path.join(DIR_VIDEOS, nome)
        if os.path.exists(destino):
            print(f"  já existe: {nome}")
            continue
        if not baixar(fid, destino):
            falhas.append(nome)

    if falhas:
        print(f"\nFALHARAM ({len(falhas)}): {falhas}")
        print("Causas prováveis: rede ainda bloqueada (403 CONNECT) ou arquivo sem "
              "compartilhamento por link.")
        return 1
    print("\nTudo baixado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
