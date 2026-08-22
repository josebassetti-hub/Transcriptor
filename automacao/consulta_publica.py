#!/usr/bin/env python3
"""
Consulta pública de CNPJ — SEM login, SEM senha, SEM gov.br.

Cobre a maior parte do que se usa num dossiê de prospecção: razão social,
nome fantasia, natureza jurídica, capital social, CNAE principal e secundários,
quadro societário (QSA), endereço, situação cadastral, porte, data de abertura.

Fontes (ambas públicas e gratuitas, derivadas dos Dados Abertos da Receita Federal):
  1. BrasilAPI   — https://brasilapi.com.br/api/cnpj/v1/{cnpj}
  2. MinhaReceita — https://minhareceita.org/{cnpj}   (fallback automático)

O que ESTAS fontes NÃO trazem (só a Junta Comercial tem, e exige login):
  NIRE, número/data dos arquivamentos, ficha cadastral completa,
  certidão simplificada, imagem digitalizada do contrato social.

Uso:
    python3 consulta_publica.py 12345678000199
    python3 consulta_publica.py --lista cnpjs.txt --csv saida/empresas.csv
    python3 consulta_publica.py --lista cnpjs.txt --json saida/empresas.json

Zero dependências — só a biblioteca padrão do Python 3.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

TIMEOUT = 30
PAUSA_PADRAO = 1.5  # segundos entre requisições — respeita o rate limit das APIs
UA = "consulta-publica-cnpj/1.0 (uso proprio; contato via repositorio)"

FONTES = [
    ("BrasilAPI", "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"),
    ("MinhaReceita", "https://minhareceita.org/{cnpj}"),
]


def so_digitos(texto):
    return re.sub(r"\D", "", texto or "")


def valida_cnpj(cnpj):
    """Valida os dois dígitos verificadores. Evita gastar requisição com lixo."""
    c = so_digitos(cnpj)
    if len(c) != 14 or c == c[0] * 14:
        return False
    for tamanho in (12, 13):
        pesos = list(range(tamanho - 7, 1, -1)) + list(range(9, 1, -1))
        soma = sum(int(d) * p for d, p in zip(c[:tamanho], pesos))
        resto = soma % 11
        digito = 0 if resto < 2 else 11 - resto
        if int(c[tamanho]) != digito:
            return False
    return True


def formata_cnpj(cnpj):
    c = so_digitos(cnpj)
    if len(c) != 14:
        return cnpj
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"


def busca_em(url, cnpj):
    req = urllib.request.Request(url.format(cnpj=cnpj), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def consulta(cnpj):
    """Tenta cada fonte em ordem. Retorna (dados, nome_da_fonte) ou levanta a última falha."""
    c = so_digitos(cnpj)
    ultimo_erro = None
    for nome, url in FONTES:
        try:
            return busca_em(url, c), nome
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise LookupError(f"CNPJ {formata_cnpj(c)} não encontrado na Receita Federal")
            ultimo_erro = f"{nome}: HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            ultimo_erro = f"{nome}: {e}"
        time.sleep(1)
    raise RuntimeError(f"Todas as fontes falharam. Última: {ultimo_erro}")


def _primeiro(dados, *chaves):
    """As duas APIs usam nomes de campo diferentes para a mesma coisa."""
    for k in chaves:
        v = dados.get(k)
        if v not in (None, "", []):
            return v
    return ""


def normaliza(dados, fonte):
    """Achata a resposta num dicionário estável, independente da fonte."""
    socios = _primeiro(dados, "qsa", "socios") or []
    nomes_socios = [
        _primeiro(s, "nome_socio", "nome", "nome_representante_legal") for s in socios
    ]

    secundarios = _primeiro(dados, "cnaes_secundarios", "cnae_fiscal_secundaria") or []
    lista_secundarios = [
        f"{_primeiro(x, 'codigo', 'code')} - {_primeiro(x, 'descricao', 'text')}"
        for x in secundarios
        if isinstance(x, dict)
    ]

    return {
        "cnpj": formata_cnpj(_primeiro(dados, "cnpj", "estabelecimento")),
        "razao_social": _primeiro(dados, "razao_social", "nome_empresarial", "nome"),
        "nome_fantasia": _primeiro(dados, "nome_fantasia", "fantasia"),
        "situacao": _primeiro(dados, "descricao_situacao_cadastral", "situacao"),
        "data_situacao": _primeiro(dados, "data_situacao_cadastral", "data_situacao"),
        "data_abertura": _primeiro(dados, "data_inicio_atividade", "abertura"),
        "porte": _primeiro(dados, "porte", "descricao_porte"),
        "natureza_juridica": _primeiro(dados, "natureza_juridica"),
        "capital_social": _primeiro(dados, "capital_social"),
        "cnae_principal": (
            f"{_primeiro(dados, 'cnae_fiscal')} - {_primeiro(dados, 'cnae_fiscal_descricao')}"
        ).strip(" -"),
        "cnaes_secundarios": " | ".join(lista_secundarios),
        "logradouro": (
            f"{_primeiro(dados, 'descricao_tipo_de_logradouro')} "
            f"{_primeiro(dados, 'logradouro')}, {_primeiro(dados, 'numero')}"
        ).strip(),
        "bairro": _primeiro(dados, "bairro"),
        "municipio": _primeiro(dados, "municipio"),
        "uf": _primeiro(dados, "uf"),
        "cep": _primeiro(dados, "cep"),
        "telefone": _primeiro(dados, "ddd_telefone_1", "telefone"),
        "email": _primeiro(dados, "email"),
        "socios": " | ".join(n for n in nomes_socios if n),
        "qtd_socios": len(socios),
        "fonte": fonte,
    }


def carrega_lista(caminho):
    """Lê CNPJs de um arquivo texto (um por linha; ignora vazios e linhas com #)."""
    with open(caminho, encoding="utf-8") as f:
        return [
            linha.strip()
            for linha in f
            if linha.strip() and not linha.lstrip().startswith("#")
        ]


def grava_csv(registros, caminho):
    if not registros:
        return
    os.makedirs(os.path.dirname(os.path.abspath(caminho)) or ".", exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=list(registros[0].keys()), delimiter=";")
        escritor.writeheader()
        escritor.writerows(registros)


def grava_json(registros, caminho):
    os.makedirs(os.path.dirname(os.path.abspath(caminho)) or ".", exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)


def main():
    p = argparse.ArgumentParser(
        description="Consulta pública de CNPJ (sem login gov.br).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("cnpj", nargs="*", help="um ou mais CNPJs")
    p.add_argument("--lista", help="arquivo texto com um CNPJ por linha")
    p.add_argument("--csv", help="grava o resultado em CSV (separador ';', abre no Excel)")
    p.add_argument("--json", help="grava o resultado em JSON")
    p.add_argument(
        "--pausa",
        type=float,
        default=PAUSA_PADRAO,
        help=f"segundos entre consultas (padrão {PAUSA_PADRAO})",
    )
    args = p.parse_args()

    alvos = list(args.cnpj)
    if args.lista:
        alvos += carrega_lista(args.lista)
    if not alvos:
        p.error("informe ao menos um CNPJ ou use --lista")

    registros, falhas = [], []
    for i, bruto in enumerate(alvos, 1):
        c = so_digitos(bruto)
        if not valida_cnpj(c):
            falhas.append((bruto, "CNPJ inválido (dígito verificador)"))
            print(f"[{i}/{len(alvos)}] {bruto}: inválido", file=sys.stderr)
            continue
        try:
            dados, fonte = consulta(c)
            reg = normaliza(dados, fonte)
            registros.append(reg)
            print(f"[{i}/{len(alvos)}] {formata_cnpj(c)}  {reg['razao_social']}  ({fonte})")
        except (LookupError, RuntimeError) as e:
            falhas.append((bruto, str(e)))
            print(f"[{i}/{len(alvos)}] {formata_cnpj(c)}: {e}", file=sys.stderr)
        if i < len(alvos):
            time.sleep(args.pausa)

    if args.csv:
        grava_csv(registros, args.csv)
        print(f"\nCSV gravado: {args.csv}")
    if args.json:
        grava_json(registros, args.json)
        print(f"JSON gravado: {args.json}")
    if not args.csv and not args.json and len(registros) == 1:
        print()
        print(json.dumps(registros[0], ensure_ascii=False, indent=2))

    print(f"\n{len(registros)} consultado(s), {len(falhas)} falha(s).")
    for bruto, motivo in falhas:
        print(f"  ! {bruto}: {motivo}")
    return 1 if falhas and not registros else 0


if __name__ == "__main__":
    sys.exit(main())
