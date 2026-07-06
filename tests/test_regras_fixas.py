"""Golden tests das regras fixas (knowledge/curso/relatorio-custos-despesas.md)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engines.regras_fixas import (  # noqa: E402
    conservacao_anual, impostos_terra_nua_anual, taxa_fne,
)


def test_conservacao_exemplo_do_curso():
    assert conservacao_anual(224_400) == 5_610.00


def test_impostos_terra_nua_exemplo_do_curso():
    assert impostos_terra_nua_anual(1_700_000) == 3_400.00


def test_tabela_juros_fne():
    inv_mini = taxa_fne("investimento", "mini_peq_peqmedio")
    assert inv_mini["taxa"] == 6.50 and inv_mini["taxa_bonus"] == 6.25
    assert taxa_fne("custeio", "grande")["fp"] == 1.0580553
