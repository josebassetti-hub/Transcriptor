#!/usr/bin/env python3
"""Diagnóstico das fontes públicas — rode NA SUA MÁQUINA (rede aberta).

  cd prototype
  python3 testar_fontes.py

O script:
  1. Testa a conexão com o Banco Central (SGS) e o IBGE (API de agregados v3);
  2. Descobre, direto da API do IBGE, os metadados das tabelas candidatas do
     setor (PAS 2577 — receita por atividade; CEMPRE 6449 — nº de empresas por
     classe CNAE): variáveis, períodos e classificações disponíveis;
  3. Grava tudo em saida/descoberta_fontes.json — use esse arquivo para
     preencher o bloco `topdown.agregado_sidra` do JSON do setor (ou envie a
     saída no chat para eu configurar).

Se aparecer erro de certificado SSL (comum no Python do macOS):
  - Python instalado da python.org: rode /Applications/Python 3.x/Install Certificates.command
  - Ou instale certifi: python3 -m pip install certifi
"""

import json
import ssl
import sys
import urllib.request
from pathlib import Path

SAIDA = Path(__file__).resolve().parent / "saida"

TESTES_CONEXAO = [
    ("Banco Central — SGS (Selic)",
     "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"),
    ("IBGE — API de agregados v3 (catálogo)",
     "https://servicodados.ibge.gov.br/api/v3/agregados?assunto=131"),
]

# Tabelas SIDRA candidatas para o setor-piloto (descobertas na pesquisa):
#   2577 — PAS: receita operacional líquida, nº de empresas etc., por atividade CNAE 2.0
#   6449 — CEMPRE: empresas por seção/divisão/grupo/CLASSE da CNAE 2.0 (série até 2021)
#    993 — CEMPRE: empresas por seção CNAE, faixas de pessoal, ano de fundação
TABELAS_CANDIDATAS = [2577, 6449, 993]

META_URL = "https://servicodados.ibge.gov.br/api/v3/agregados/{id}/metadados"


def baixar(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "prototipo-pesquisa-mercado/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    resultado = {"conexao": {}, "tabelas": {}}
    falhas = 0

    print("== 1. Teste de conexão ==")
    for nome, url in TESTES_CONEXAO:
        try:
            baixar(url)
            print(f"  [OK]    {nome}")
            resultado["conexao"][nome] = "ok"
        except ssl.SSLError as exc:
            falhas += 1
            print(f"  [SSL]   {nome}: {exc}")
            print("          -> problema de certificado do Python; veja o cabeçalho deste script.")
            resultado["conexao"][nome] = f"erro ssl: {exc}"
        except Exception as exc:
            falhas += 1
            print(f"  [ERRO]  {nome}: {exc}")
            resultado["conexao"][nome] = f"erro: {exc}"

    print("\n== 2. Metadados das tabelas candidatas (IBGE) ==")
    for tid in TABELAS_CANDIDATAS:
        try:
            meta = baixar(META_URL.format(id=tid))
            variaveis = [
                {"id": v["id"], "nome": v["nome"], "unidade": v.get("unidade")}
                for v in meta.get("variaveis", [])
            ]
            classificacoes = [
                {
                    "id": c["id"],
                    "nome": c["nome"],
                    "exemplos_categorias": [
                        {"id": cat["id"], "nome": cat["nome"]}
                        for cat in c.get("categorias", [])[:8]
                    ],
                }
                for c in meta.get("classificacoes", [])
            ]
            resultado["tabelas"][tid] = {
                "nome": meta.get("nome"),
                "periodo": meta.get("periodicidade", {}),
                "niveis_territoriais": meta.get("nivelTerritorial", {}),
                "variaveis": variaveis,
                "classificacoes": classificacoes,
            }
            print(f"  [OK]    Tabela {tid}: {meta.get('nome','')[:90]}")
            for v in variaveis[:6]:
                print(f"          variavel {v['id']}: {v['nome'][:80]}")
        except Exception as exc:
            falhas += 1
            print(f"  [ERRO]  Tabela {tid}: {exc}")
            resultado["tabelas"][tid] = f"erro: {exc}"

    SAIDA.mkdir(exist_ok=True)
    destino = SAIDA / "descoberta_fontes.json"
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResultado completo salvo em: {destino}")
    if falhas:
        print(f"{falhas} teste(s) falharam — envie a saída acima no chat para diagnóstico.")
        sys.exit(1)
    print("Tudo OK — envie o arquivo descoberta_fontes.json (ou a saída acima) no chat "
          "para configurarmos as tabelas reais no JSON do setor.")


if __name__ == "__main__":
    main()
