"""Guarda LGPD: nenhum CPF/CNPJ real pode ser commitado em knowledge/.

Os extratores (visão/transcrição) tendem a reintroduzir dados pessoais dos exemplos do
professor. Dados completos ficam apenas em materiais/ (fora do git); em knowledge/ usa-se
pseudônimo (ex.: "CLIENTE-EXEMPLO A.P.M.").
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PADRAO_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b")
PADRAO_CNPJ = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")
# Números de 11 dígitos legítimos (nenhum por enquanto). fileIds do Drive têm letras, não caem.
EXCECOES = set()


def _arquivos_versionados():
    for pasta in ("knowledge", "templates", "engines", "pipeline", "tests"):
        base = RAIZ / pasta
        if base.exists():
            yield from (p for p in base.rglob("*") if p.is_file() and p.suffix in
                        {".md", ".json", ".py", ".txt", ".csv", ".html"})


def test_sem_cpf_ou_cnpj_em_arquivos_commitados():
    violacoes = []
    for arq in _arquivos_versionados():
        texto = arq.read_text(encoding="utf-8", errors="ignore")
        for m in PADRAO_CPF.finditer(texto):
            if m.group(0) not in EXCECOES:
                violacoes.append(f"{arq.relative_to(RAIZ)}: CPF-like '{m.group(0)}'")
        for m in PADRAO_CNPJ.finditer(texto):
            violacoes.append(f"{arq.relative_to(RAIZ)}: CNPJ-like '{m.group(0)}'")
    assert not violacoes, "Dados pessoais detectados (pseudonimize):\n" + "\n".join(violacoes)
