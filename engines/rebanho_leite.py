"""Motor de bovinocultura de leite — receitas, custos e produção do rebanho.

Fonte das regras: relatório-exemplo da ferramenta do professor
(knowledge/curso/relatorio-bovinocultura-leite.md) + preços do gado confirmados por
triangulação com o orçamento (knowledge/curso/orcamento-deposito.md). Cada fórmula tem
selo de confiança do protocolo:
  CONFIRMADO  = reproduz os números do exemplo ao centavo;
  PROVÁVEL    = hipótese que bate no exemplo mas com regra deduzida, confirmar nos vídeos.

A EVOLUÇÃO do rebanho (transições entre categorias ano a ano, com arredondamentos) ainda
NÃO está modelada — depende dos vídeos (ver test xfail). Por ora o motor recebe a
composição anual como entrada e calcula produção/receita/custo.
"""
from dataclasses import dataclass, field

# Preços do exemplo do curso (CONFIRMADO por triangulação orçamento×receitas; os valores
# são parâmetro do projeto real — cotar por região na operação)
PRECOS_PADRAO = {
    "matriz": 3_570.0,     # vaca (85% da arroba do boi a R$300 × 14@ — leitura provável)
    "garrota": 2_730.0,
    "garrote": 2_100.0,
    "bezerro": 1_500.0,
    "bezerra": 1_500.0,
    "novilha": 0.0,        # sem venda no exemplo; preço a definir por cotação
    "novilho": 0.0,
    "touro": 0.0,
}
PRECO_LEITE_PADRAO = 2.30          # R$/litro (CONFIRMADO no exemplo)
SALARIO_MINIMO_PADRAO = 1_518.0    # vigente na data do curso
FATOR_MAO_DE_OBRA = 0.26           # R$/cabeça/ano = 26% do SM (PROVÁVEL: 394,68 no exemplo)


@dataclass
class IndicadoresLeite:
    """Indicadores técnicos (defaults = exemplo do curso, anos 1–12)."""
    paricao: float = 0.70
    producao_leite_dia: float = 12.0     # L/vaca em lactação/dia
    periodo_ordenha_dias: int = 270
    relacao_touro_vaca: int = 30
    mortalidade_bezerros: float = 0.06
    mortalidade_garrotes: float = 0.03
    mortalidade_adultos: float = 0.02
    preco_leite: float = PRECO_LEITE_PADRAO
    precos: dict = field(default_factory=lambda: dict(PRECOS_PADRAO))
    salario_minimo: float = SALARIO_MINIMO_PADRAO


def vacas_em_lactacao(matrizes: int, ind: IndicadoresLeite) -> int:
    """CONFIRMADO (anos 2+ do exemplo): lactantes = round(matrizes × parição).
    round half-up: 35,7→36 (ano 2 ✓); 33,6→34 (ano 3 ✓); 36,4→36 (ano 5 ✓)."""
    import math
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
    return round(total_cabecas * ind.salario_minimo * FATOR_MAO_DE_OBRA, 2)


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
