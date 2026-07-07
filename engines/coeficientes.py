"""Acesso à base operacional de coeficientes técnicos (knowledge/coeficientes-tecnicos.json).

Regras (plano v2.1):
  - APPEND-ONLY: atualizar um valor = mover o atual para 'historico' e gravar o novo por
    cima com nova vigência (função `atualizar`), nunca apagar.
  - Todo uso informa se o contexto do projeto está DENTRO da abrangência declarada;
    uso fora de abrangência deve ser bloqueado pelo agente Revisor sem aval humano.
  - Fixtures congelados dos exemplos do professor (tests/fixtures/) NÃO passam por aqui.
"""
import json
import os
from dataclasses import dataclass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_PADRAO = os.path.join(RAIZ, "knowledge", "coeficientes-tecnicos.json")


@dataclass
class Coeficiente:
    id: str
    valor: float
    unidade: str
    abrangencia: str
    selo: str
    data_base: str
    validade: str
    fonte: str


def carregar(caminho: str = CAMINHO_PADRAO) -> dict:
    dados = json.load(open(caminho, encoding="utf-8"))
    dados.pop("_schema", None)
    return dados


def obter(coef_id: str, base: dict = None) -> Coeficiente:
    base = base if base is not None else carregar()
    if coef_id not in base:
        raise KeyError(
            f"Coeficiente '{coef_id}' não existe na base operacional. Se o curso não o "
            f"cobre (ver knowledge/anti-escopo.md), pesquisar fonte externa com selo e "
            f"aprovação do usuário antes de usar.")
    e = base[coef_id]
    return Coeficiente(
        id=coef_id, valor=e["valor"], unidade=e["unidade_canonica"],
        abrangencia=e["abrangencia"], selo=e["selo"],
        data_base=e["vigencia"]["data_base"], validade=e["vigencia"]["validade"],
        fonte=str(e["fonte"]),
    )


def atualizar(coef_id: str, novo_valor: float, nova_fonte: str, data_base: str,
              caminho: str = CAMINHO_PADRAO) -> None:
    """Atualização append-only: valor atual desce para o histórico."""
    dados = json.load(open(caminho, encoding="utf-8"))
    if coef_id not in dados:
        raise KeyError(coef_id)
    e = dados[coef_id]
    e.setdefault("historico", []).insert(0, {
        "valor": e["valor"], "fonte": e["fonte"], "vigencia": e["vigencia"],
    })
    e["valor"] = novo_valor
    e["fonte"] = nova_fonte
    e["vigencia"] = {"data_base": data_base, "validade": e["vigencia"].get("validade")}
    json.dump(dados, open(caminho, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
