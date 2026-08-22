#!/usr/bin/env python3
"""
JUCEES em lote — login MANUAL feito por você, repetição automatizada pelo script.

O PRINCÍPIO: sua senha gov.br nunca é digitada no código, nunca vai para um
arquivo, nunca passa por uma IA. Você loga com os próprios dedos, uma vez, numa
janela de navegador de verdade. O Chromium guarda os cookies num perfil local
(pasta ./perfil-jucees). O script reaproveita essa sessão e faz só a parte
repetitiva: abrir a consulta, digitar o CNPJ, salvar o resultado.

Isso NÃO burla o CAPTCHA nem o 2FA do gov.br — pelo contrário, depende de você
resolvê-los, como um usuário normal. O que se automatiza é o trabalho braçal
depois da porta aberta, dentro da sua própria conta.

FLUXO (três comandos, nessa ordem):

  1) python3 jucees_lote.py login
     Abre o navegador. Você loga no gov.br à mão. A sessão fica salva no perfil.

  2) python3 jucees_lote.py gravar
     Abre o gravador do Playwright. Você faz UMA consulta clicando normalmente e
     o Playwright imprime os seletores. Copie-os para config.json. Só na 1ª vez.

  3) python3 jucees_lote.py consultar --lista cnpjs.txt
     Percorre a lista reaproveitando a sessão e salva cada resultado em saida/.

Requer:  pip install playwright  &&  playwright install chromium

ANTES DE USAR, leia o README.md desta pasta: há limites de Termo de Uso do
gov.br que valem para qualquer automação, inclusive esta.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
PERFIL = os.path.join(AQUI, "perfil-jucees")
CONFIG = os.path.join(AQUI, "config.json")
SAIDA = os.path.join(AQUI, "saida")

# Se a navegação cair em qualquer um destes hosts, a sessão expirou.
HOSTS_LOGIN = ("sso.acesso.gov.br", "acesso.gov.br", "login.gov.br")

CONFIG_EXEMPLO = {
    "_comentario": (
        "Preencha 'url_consulta' e os seletores rodando `python3 jucees_lote.py gravar`. "
        "Os seletores mudam quando a JUCEES atualiza o site — se o script parar de achar "
        "o campo, rode 'gravar' de novo e atualize aqui."
    ),
    "url_consulta": "https://jucees.es.gov.br/",
    "seletor_campo_cnpj": "",
    "seletor_botao_pesquisar": "",
    "seletor_resultado": "",
    "pausa_entre_consultas": 5,
    "timeout_ms": 30000,
}


def carrega_config():
    if not os.path.exists(CONFIG):
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump(CONFIG_EXEMPLO, f, ensure_ascii=False, indent=2)
        print(f"Criei {CONFIG} com o modelo. Preencha os seletores e rode de novo.")
        print("Para descobrir os seletores: python3 jucees_lote.py gravar")
        sys.exit(1)
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def exige_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print("Playwright não instalado. Rode:", file=sys.stderr)
        print("    pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)


def abre_contexto(p, headless=False):
    """Contexto persistente: os cookies do login manual sobrevivem entre execuções."""
    return p.chromium.launch_persistent_context(
        PERFIL,
        headless=headless,
        viewport={"width": 1400, "height": 900},
        accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"],
    )


def na_tela_de_login(page):
    return any(h in (page.url or "") for h in HOSTS_LOGIN)


def cmd_login(args):
    """Passo 1: você loga à mão. O script só segura a janela aberta e confirma."""
    from playwright.sync_api import sync_playwright

    cfg = carrega_config() if os.path.exists(CONFIG) else CONFIG_EXEMPLO
    with sync_playwright() as p:
        ctx = abre_contexto(p, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(cfg["url_consulta"], wait_until="domcontentloaded")

        print("=" * 68)
        print(" Faça o login no gov.br NESTA JANELA, com suas próprias mãos.")
        print(" Resolva o CAPTCHA e o 2FA normalmente. Não digite sua senha")
        print(" em nenhum outro lugar — nem no terminal, nem num arquivo, nem")
        print(" numa conversa com IA.")
        print()
        print(" Quando estiver logado e na tela de Consulta Empresa,")
        print(" volte aqui e aperte ENTER para salvar a sessão.")
        print("=" * 68)
        input()

        if na_tela_de_login(page):
            print("Ainda estou vendo a tela de login. A sessão pode não ter sido salva.")
        else:
            print(f"Sessão salva no perfil: {PERFIL}")
            print("Agora rode:  python3 jucees_lote.py consultar --lista cnpjs.txt")
        ctx.close()
    return 0


def cmd_gravar(args):
    """Passo 2: descobre os seletores gravando uma consulta feita à mão."""
    cfg = carrega_config() if os.path.exists(CONFIG) else CONFIG_EXEMPLO
    print("Abrindo o gravador do Playwright.")
    print("Faça UMA consulta clicando normalmente; o código gerado mostra os seletores.")
    print("Copie-os para config.json e feche a janela.\n")
    return subprocess.call([
        sys.executable, "-m", "playwright", "codegen",
        "--target", "python",
        "--browser", "chromium",
        cfg["url_consulta"],
    ])


def carrega_lista(caminho):
    with open(caminho, encoding="utf-8") as f:
        return [
            re.sub(r"\D", "", l)
            for l in f
            if l.strip() and not l.lstrip().startswith("#")
        ]


def cmd_consultar(args):
    """Passo 3: o trabalho repetitivo, reaproveitando a sessão do passo 1."""
    from playwright.sync_api import TimeoutError as PWTimeout
    from playwright.sync_api import sync_playwright

    cfg = carrega_config()
    faltando = [
        k for k in ("seletor_campo_cnpj", "seletor_botao_pesquisar") if not cfg.get(k)
    ]
    if faltando:
        print(f"config.json incompleto: {', '.join(faltando)}", file=sys.stderr)
        print("Rode:  python3 jucees_lote.py gravar", file=sys.stderr)
        return 1

    if not os.path.isdir(PERFIL):
        print("Nenhuma sessão salva. Rode primeiro: python3 jucees_lote.py login", file=sys.stderr)
        return 1

    alvos = list(args.cnpj)
    if args.lista:
        alvos += carrega_lista(args.lista)
    if not alvos:
        print("Informe CNPJs ou use --lista", file=sys.stderr)
        return 1

    carimbo = datetime.now().strftime("%Y-%m-%d_%H%M")
    destino = os.path.join(SAIDA, carimbo)
    os.makedirs(destino, exist_ok=True)
    pausa = args.pausa if args.pausa is not None else cfg.get("pausa_entre_consultas", 5)
    timeout = cfg.get("timeout_ms", 30000)

    ok, erros = [], []
    with sync_playwright() as p:
        ctx = abre_contexto(p, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        for i, cnpj in enumerate(alvos, 1):
            rotulo = f"[{i}/{len(alvos)}] {cnpj}"
            try:
                page.goto(cfg["url_consulta"], wait_until="domcontentloaded", timeout=timeout)

                if na_tela_de_login(page):
                    print(f"\n{rotulo}: a sessão expirou.")
                    print("Refaça o login NESTA JANELA e aperte ENTER para continuar.")
                    input()
                    if na_tela_de_login(page):
                        print("Continua na tela de login. Interrompendo.", file=sys.stderr)
                        break
                    page.goto(cfg["url_consulta"], wait_until="domcontentloaded", timeout=timeout)

                page.fill(cfg["seletor_campo_cnpj"], cnpj, timeout=timeout)
                page.click(cfg["seletor_botao_pesquisar"], timeout=timeout)

                if cfg.get("seletor_resultado"):
                    page.wait_for_selector(cfg["seletor_resultado"], timeout=timeout)
                else:
                    page.wait_for_load_state("networkidle", timeout=timeout)

                base = os.path.join(destino, cnpj)
                page.screenshot(path=f"{base}.png", full_page=True)
                with open(f"{base}.html", "w", encoding="utf-8") as f:
                    f.write(page.content())

                ok.append(cnpj)
                print(f"{rotulo}: salvo em {base}.png / .html")

            except PWTimeout:
                erros.append((cnpj, "timeout — seletor não encontrado ou página lenta"))
                print(f"{rotulo}: timeout", file=sys.stderr)
            except Exception as e:  # noqa: BLE001 — um CNPJ ruim não pode derrubar o lote
                erros.append((cnpj, str(e)))
                print(f"{rotulo}: {e}", file=sys.stderr)

            if i < len(alvos):
                time.sleep(pausa)  # não martele o servidor público

        ctx.close()

    print(f"\n{len(ok)} consultado(s), {len(erros)} falha(s). Saída: {destino}")
    for cnpj, motivo in erros:
        print(f"  ! {cnpj}: {motivo}")
    return 0


def main():
    p = argparse.ArgumentParser(
        description="JUCEES em lote — login manual, repetição automatizada.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("login", help="passo 1: abrir navegador para você logar à mão")
    sub.add_parser("gravar", help="passo 2: descobrir os seletores do site")

    c = sub.add_parser("consultar", help="passo 3: rodar a lista de CNPJs")
    c.add_argument("cnpj", nargs="*")
    c.add_argument("--lista", help="arquivo com um CNPJ por linha")
    c.add_argument("--pausa", type=float, default=None, help="segundos entre consultas")

    args = p.parse_args()
    exige_playwright()
    return {"login": cmd_login, "gravar": cmd_gravar, "consultar": cmd_consultar}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
