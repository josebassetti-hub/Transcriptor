"""Golden tests do motor de leite contra o relatório-exemplo do curso
(knowledge/curso/relatorio-bovinocultura-leite.md — números extraídos do PDF)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engines.rebanho_leite import (  # noqa: E402
    IndicadoresLeite, custo_mao_de_obra, evoluir_rebanho, leite_litros_ano,
    leite_litros_ano_transicao, receita_total_ano, vacas_em_lactacao,
)

IND = IndicadoresLeite()


def test_leite_anos_estaveis():
    assert leite_litros_ano(51, IND) == 116_640          # ano 2 (36 lactantes)
    assert leite_litros_ano(48, IND) == 110_160          # ano 3 (34 lactantes)
    assert leite_litros_ano(52, IND) == 116_640          # ano 5 (36 lactantes)


def test_lactantes_arredondamento():
    assert vacas_em_lactacao(51, IND) == 36              # 35,7 → 36
    assert vacas_em_lactacao(48, IND) == 34              # 33,6 → 34
    assert vacas_em_lactacao(52, IND) == 36              # 36,4 → 36


def test_leite_ano1_transicao():
    # PROVÁVEL: ano de formação usa média de matrizes (20→50) sem arredondar lactantes
    assert leite_litros_ano_transicao(35.0, IND) == 79_380


def test_custo_mao_de_obra_5_anos_do_exemplo():
    assert custo_mao_de_obra(67, IND) == 26_443.56       # ano 1
    assert custo_mao_de_obra(109, IND) == 43_020.12      # anos 2 e 3
    assert custo_mao_de_obra(113, IND) == 44_598.84      # ano 4
    assert custo_mao_de_obra(116, IND) == 45_782.88      # ano 5
    assert custo_mao_de_obra(115, IND) == 45_388.20      # anos 6+ (estável)


def test_receita_ano1():
    vendas = {"matriz": 3, "garrota": 3, "bezerro": 18}
    assert receita_total_ano(79_380, vendas, IND) == 228_474.00


def test_receita_ano2():
    vendas = {"matriz": 4, "garrota": 9, "garrote": 1, "bezerro": 18}
    assert receita_total_ano(116_640, vendas, IND) == 336_222.00


@pytest.mark.xfail(reason="Máquina de evolução do rebanho depende dos vídeos (Fase 2): "
                          "U.A. 40 vs 72 no Ano 1; arredondamentos das transições; "
                          "comportamento do Ano 13+", raises=NotImplementedError,
                   strict=True)
def test_evolucao_rebanho_pendente():
    composicao_atual = {"touro": 1, "matriz": 20, "novilha": 5, "garrota": 5,
                        "bezerra": 9, "bezerro": 9}
    evoluir_rebanho(composicao_atual, IND, anos=12)
