"""Testes da base operacional de coeficientes (schema, lookup, append-only)."""
import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engines import coeficientes  # noqa: E402

SELOS_VALIDOS = {"CONFIRMADO", "PROVAVEL", "INCERTO"}


def test_schema_de_todas_as_entradas():
    base = coeficientes.carregar()
    assert base, "base operacional vazia"
    for cid, e in base.items():
        assert isinstance(e["valor"], (int, float)), cid
        for campo in ("unidade_canonica", "abrangencia", "fonte", "selo", "vigencia"):
            assert campo in e, f"{cid} sem campo {campo}"
        assert e["selo"] in SELOS_VALIDOS, f"{cid}: selo inválido {e['selo']}"
        assert "data_base" in e["vigencia"], cid
        assert isinstance(e.get("historico", []), list), cid


def test_obter_devolve_coeficiente_completo():
    c = coeficientes.obter("leite.preco_litro")
    assert c.valor == 2.30 and c.unidade == "R$/L" and c.selo == "CONFIRMADO"
    assert "recotar" in c.abrangencia  # cotação exige recotação por caso


def test_obter_inexistente_orienta_anti_escopo():
    with pytest.raises(KeyError, match="anti-escopo"):
        coeficientes.obter("cafe.coeficiente_que_nao_existe")


def test_atualizar_e_append_only(tmp_path):
    copia = tmp_path / "coef.json"
    shutil.copy(coeficientes.CAMINHO_PADRAO, copia)
    coeficientes.atualizar("leite.preco_litro", 2.55,
                           "cotação CEPEA fictícia (teste)", "2026-07-06",
                           caminho=str(copia))
    dados = json.load(open(copia, encoding="utf-8"))
    e = dados["leite.preco_litro"]
    assert e["valor"] == 2.55
    assert e["historico"][0]["valor"] == 2.30  # valor antigo preservado no topo do histórico
    # e o arquivo ORIGINAL não foi tocado
    assert coeficientes.obter("leite.preco_litro").valor == 2.30


def test_invariantes_de_generalizacao_do_motor_leite():
    """Fórmulas devem se comportar bem FORA dos números do exemplo (generalização)."""
    from engines.rebanho_leite import (IndicadoresLeite, custo_mao_de_obra,
                                       leite_litros_ano, vacas_em_lactacao)
    fixture = Path(__file__).resolve().parent / "fixtures" / "exemplo-professor-leite.json"
    ind = IndicadoresLeite.de_json(str(fixture))
    # lactantes nunca excede matrizes; leite cresce com matrizes; custo é linear em cabeças
    for matrizes in (1, 10, 33, 52, 200):
        assert vacas_em_lactacao(matrizes, ind) <= matrizes
    assert leite_litros_ano(100, ind) > leite_litros_ano(50, ind)
    assert custo_mao_de_obra(230, ind) == round(2 * custo_mao_de_obra(115, ind), 2)
