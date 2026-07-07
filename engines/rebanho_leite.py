"""Motor de bovinocultura de leite — receitas, custos e produção do rebanho.

Fonte das regras: relatório-exemplo da ferramenta do professor
(knowledge/curso/relatorio-bovinocultura-leite.md) + preços do gado confirmados por
triangulação com o orçamento (knowledge/curso/orcamento-deposito.md). Cada fórmula tem
selo de confiança do protocolo:
  CONFIRMADO  = reproduz os números do exemplo ao centavo;
  PROVÁVEL    = hipótese que bate no exemplo mas com regra deduzida, confirmar nos vídeos.

SEPARAÇÃO DE COEFICIENTES (plano v2.1):
  - Este módulo guarda só as FÓRMULAS (gerais). Nenhum preço/índice fica em código.
  - Golden tests carregam o fixture CONGELADO tests/fixtures/exemplo-professor-leite.json.
  - Projetos reais carregam valores da base operacional via engines/coeficientes.py
    (append-only, com abrangência/vigência) — atualizar cotação lá NÃO altera os goldens.

A EVOLUÇÃO do rebanho (transições entre categorias ano a ano, com arredondamentos) ainda
NÃO está modelada — depende dos vídeos (ver test xfail). Por ora o motor recebe a
composição anual como entrada e calcula produção/receita/custo.
"""
import json
import math
from dataclasses import dataclass, field


@dataclass
class IndicadoresLeite:
    """Indicadores técnicos e preços de um projeto de leite (sem defaults embutidos —
    carregar de fixture congelado nos testes ou da base operacional em produção)."""
    paricao: float
    producao_leite_dia: float          # L/vaca em lactação/dia
    periodo_ordenha_dias: int
    relacao_touro_vaca: int
    mortalidade_bezerros: float
    mortalidade_garrotes: float
    mortalidade_adultos: float
    preco_leite: float                 # R$/L
    salario_minimo: float
    fator_mao_de_obra: float           # R$/cabeça/ano = fator × salário mínimo
    precos: dict = field(default_factory=dict)   # R$/cabeça por categoria

    @classmethod
    def de_json(cls, caminho: str) -> "IndicadoresLeite":
        dados = json.load(open(caminho, encoding="utf-8"))
        campos = {k: v for k, v in dados.items() if not k.startswith("_")}
        return cls(**campos)


def vacas_em_lactacao(matrizes: int, ind: IndicadoresLeite) -> int:
    """CONFIRMADO (anos 2+ do exemplo): lactantes = round(matrizes × parição).
    round half-up: 35,7→36 (ano 2 ✓); 33,6→34 (ano 3 ✓); 36,4→36 (ano 5 ✓)."""
    return int(math.floor(matrizes * ind.paricao + 0.5))


def leite_litros_ano(matrizes: int, ind: IndicadoresLeite) -> float:
    """CONFIRMADO: litros/ano = lactantes × L/dia × dias de ordenha.
    Ano 2 exemplo: 36 × 12 × 270 = 116.640 ✓"""
    return vacas_em_lactacao(matrizes, ind) * ind.producao_leite_dia * ind.periodo_ordenha_dias


def leite_litros_ano_transicao(matrizes_medias: float, ind: IndicadoresLeite) -> float:
    """PROVÁVEL (ano 1 do exemplo, rebanho em formação): usa a média de matrizes SEM
    arredondar lactantes. Exemplo: 35 × 0,7 × 12 × 270 = 79.380 ✓ (24,5 lactantes)."""
    return matrizes_medias * ind.paricao * ind.producao_leite_dia * ind.periodo_ordenha_dias


def custo_mao_de_obra(total_cabecas: int, ind: IndicadoresLeite) -> float:
    """CONFIRMADO no valor (R$ 394,68/cabeça/ano reproduz os 5 anos do exemplo ao
    centavo); PROVÁVEL na interpretação (394,68 = 26% × salário mínimo 1.518 — rótulo
    'SAL. PECUARIA - CABEÇA/OPER.=1518' no relatório)."""
    return round(total_cabecas * ind.salario_minimo * ind.fator_mao_de_obra, 2)


def receita_vendas(vendas_por_categoria: dict, ind: IndicadoresLeite) -> float:
    """CONFIRMADO: Σ cabeças vendidas × preço da categoria."""
    return round(sum(qtd * ind.precos.get(cat, 0.0)
                     for cat, qtd in vendas_por_categoria.items()), 2)


def receita_total_ano(litros_leite: float, vendas_por_categoria: dict,
                      ind: IndicadoresLeite) -> float:
    """CONFIRMADO: leite × preço + vendas de animais.
    Ano 1 exemplo: 79.380×2,30 + (3×3.570 + 3×2.730 + 18×1.500) = 228.474,00 ✓"""
    return round(litros_leite * ind.preco_leite
                 + receita_vendas(vendas_por_categoria, ind), 2)


def evoluir_rebanho(composicao_inicial: dict, ind: IndicadoresLeite, anos: int) -> list:
    """NÃO IMPLEMENTADO: a máquina de transição entre categorias (nascimentos →
    bezerros → garrotes → novilhas → matrizes, com mortalidade/vendas/arredondamentos
    exatos da ferramenta) depende da confirmação nos vídeos (Fase 2).
    Incógnitas documentadas: U.A. 40 vs 72 no Ano 1; indicadores mudam no Ano 13+."""
    raise NotImplementedError("Aguardando regras dos vídeos (Fase 2) — ver docstring")
