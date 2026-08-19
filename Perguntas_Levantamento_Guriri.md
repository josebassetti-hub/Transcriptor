# Reconciliação do Levantamento_Pavimentacao_Guriri.xlsx (19/08/2026)

> Texto pronto para colar no chat que produziu o levantamento.

---

Preciso reconciliar quatro pontos da planilha `Levantamento_Pavimentacao_Guriri.xlsx` que você
gerou em 19/08/2026. Ela vai anexada a um pacote de financiamento bancário e passou por auditoria
independente; os itens abaixo são os que a auditoria não conseguiu fechar lendo só a planilha.
Não estou questionando o trabalho — quero registrar a resposta correta antes que o analista do
banco pergunte.

## BLOCO 1 — A contagem de pontos: 637 declarados × 496 rastreáveis

O cabeçalho da aba `Resumo Geral` declara **637 pontos** (517 no Street View + 120 em satélite), e
a coluna `Pontos auditados` do resumo soma exatamente 637.

Mas ao descer às 21 abas de loteamento e somar a coluna `Pontos auditados` via a via, o total é
**496**. O mesmo 496 aparece por um caminho independente: somando os números escritos na coluna
`Origem da classificação` (`N ponto(s): X SV + Y satélite`), dá **462 SV + 34 satélite = 496**.

Faltam **141 pontos** — e a diferença entre as partições também não bate: declarado 517/120,
rastreável 462/34. O buraco é de 55 pontos no Street View e **86 dos 120 pontos de satélite**.

### Onde a diferença está, loteamento a loteamento

| Nº | Loteamento | Declarado (resumo) | Soma via a via | Gap | Metragem só de planta |
|---|---|---|---|---|---|
| 80 | Soma Cevolani (Golden Guriri) | 32 | **0** | 32 | 4.952 m (100%) |
| 35 | Verão Vermelho | 37 | 9 | 28 | 7.830 m |
| 27 | Residencial Mar Aberto | 33 | 8 | 25 | 4.108 m |
| 9 | Bosque da Praia | 27 | 3 | 24 | 35.450 m (97%) |
| 78 | João de Barro (COHAJOBA) | 14 | **0** | 14 | 1.490 m (100%) |
| 84 | Pontal de Guriri II | 14 | **0** | 14 | 1.073 m (100%) |
| 7 | Balneário de Guriri | 58 | 54 | 4 | 0 m |
| | **Os outros 14 loteamentos** | | | **0** | 0 m (exceto o nº 42) |
| | **TOTAL** | **637** | **496** | **141** | 56.979 m |

### O padrão, e as duas exceções que o quebram

- **14 dos 21 loteamentos fecham exatamente** — declarado = soma via a via, diferença zero. Todos
  os 14 têm metragem só de planta igual a zero.
- **6 dos 7 loteamentos com metragem só de planta > 0 têm gap**, e os gaps somam 137.
- **Exceção A:** o nº 42 (Residencial Bom Jesus) tem 2.076 m só de planta e mesmo assim fecha em
  zero (70 = 70). Por que esse é diferente dos outros seis?
- **Exceção B:** o nº 7 (Balneário de Guriri) tem zero metragem de planta e ainda assim sobram 4
  pontos (58 declarados × 54 via a via). De onde vêm esses 4?

### Minha hipótese — confirme ou corrija

Os 141 pontos foram efetivamente verificados, mas gastos nas vias **só de planta**: você olhou o
ponto, concluiu que ali não há traçado que permita classificar a via individualmente, e por isso a
linha ficou com `0` em `Pontos auditados` e `sem ponto próprio — taxa a...` na origem. O ponto foi
consumido mas não creditado à via. Isso explicaria também por que 86 dos 120 pontos de satélite
sumiram: satélite é justamente o recurso usado onde o Street View não cobre, que é onde estão as
vias de planta.

### Perguntas do Bloco 1

1. **Os 141 pontos foram realmente verificados?** Se sim, a hipótese acima está certa, ou eles
   foram gastos de outra forma?
2. **Você consegue reemitir a planilha com esses 141 lançados nas linhas de via a que pertencem** —
   ainda que a via continue classificada como "sem ponto próprio" para efeito de taxa? Bastaria a
   coluna `Pontos auditados` passar a refletir os pontos gastos, com a origem dizendo o que se
   conseguiu (ou não) concluir ali.
3. Se **não** foram verificados um a um — isto é, se os 637 do cabeçalho incluem pontos planejados,
   estimados ou herdados de uma versão anterior — diga isso explicitamente. Eu ajusto o número no
   pacote para 496 em definitivo e paro de citar 637. **Prefiro a resposta honesta a um número
   alto.**
4. **O nº 42 e o nº 7** (as duas exceções acima): o que os distingue?
5. **A partição 517 SV / 120 satélite** do cabeçalho: ela vale para os 637 ou foi calculada sobre
   outra base? Pergunto porque a rastreável é 462/34, e a proporção é bem diferente.

Um detalhe correlato: o cabeçalho diz "1 ponto a cada ~350 m de via". Com 637 pontos sobre
193.374,8 m dá **1 a cada 304 m**; com 496, **1 a cada 390 m**. Nenhum dos dois é 350. Qual era a
regra real de espaçamento?

## BLOCO 2 — Duas linhas que se contradizem sozinhas

**2.1 — João de Barro (nº 78).** A observação de passeio da aba diz, textualmente: *"sem cobertura
de Street View no loteamento — mantida a estimativa anterior por satélite/analogia; NÃO verificado
ponto a ponto"*. Mas o `Resumo Geral` credita **14 pontos auditados** ao loteamento, e o cabeçalho
da própria aba diz "Auditoria completa: 14 pontos verificados neste loteamento". As duas frases
estão na mesma aba e dizem o contrário uma da outra. Qual vale?

**2.2 — Soma Cevolani / Golden Guriri (nº 80).** É a linha mais estranha do levantamento:

- 4.952 m, 8 vias, **100% de metragem só de planta** (nenhuma medida em imagem);
- confiança declarada **baixa**;
- **zero pontos próprios** em todas as 8 vias, com `sem ponto próprio` escrito em cada linha;
- e ainda assim lançado como **100% pavimentado**, falta a pavimentar = 0;
- ao mesmo tempo, a planilha afirma que 87% dessas mesmas vias não têm calçada, gerando
  17.232,96 m² de passeio faltante;
- e o resumo lhe atribui **32 pontos auditados** — a maior densidade de todo o levantamento
  (1 ponto a cada 155 m), sobre justamente as vias que ninguém mediu.

**Em que evidência se apoia o "100% pavimentado"?** Foi imagem de satélite recente, matéria de
entrega do loteamento, planta aprovada com pavimentação executada, ou inferência? Isso importa
porque é a única linha do inventário em que a incerteza reduz o volume: se a hipótese cair, a
falta a pavimentar **sobe** 4.952 m (39.616 m²). Uma resposta que confirme com fonte me deixa
mantê-la; uma que não confirme também serve, e nesse caso eu a movo para "a confirmar".

## BLOCO 3 — A largura das vias

Toda a conversão de metros para metros quadrados do levantamento — e portanto todo o volume de
material do estudo — repousa em **dois escalares**: 8 m de largura de pista e 4 m² de calçada por
metro de via. Procurei coluna de largura nas 22 abas e não existe nenhuma; o único registro é a
nota "largura média de pista adotada: 8 m (premissa)".

A sensibilidade é grande: a **7 m** o potencial de material cai **13%**; a **6 m**, cai **25%**.
E há sinal contrário dentro da própria planilha — a aba do Soma Cevolani descreve a Avenida
Copacabana como *"avenida coletora 25 m com canteiro/ciclovia"*.

1. De onde saíram os 8 m? Medição em imagem, padrão da Prefeitura, norma de loteamento, quadro de
   área das plantas, ou arbitragem?
2. As plantas dos loteamentos trazem **caixa de via / largura de leito carroçável**? Se trazem,
   dá para extrair a largura por loteamento — ou ao menos separar as coletoras das locais? Uma
   coluna de largura por via, mesmo aproximada, é a informação que mais aumentaria a confiança
   deste levantamento.
3. Os 4 m² de calçada por metro de via (2 lados × 2 m): mesma pergunta — origem e possibilidade
   de abrir por loteamento.

## BLOCO 4 — A premissa de "% de passeio existente"

O cálculo do passeio faltante usa, por loteamento, um **percentual escalar** (coluna `% passeio
existente` do resumo), na fórmula `(extensão − vias não abertas) × (1 − % passeio)`. A coluna
`% passeio` via a via, dentro de cada aba, **não entra na conta** — ela é decorativa.

Na maioria dos loteamentos a diferença é de arredondamento (1% a 9%), mas em três casos não é:

| Nº | Loteamento | Premissa usada | Média ponderada da coluna via a via | Razão |
|---|---|---|---|---|
| 27 | Residencial Mar Aberto | 0,02 | 0,0936 | **4,7×** |
| 35 | Verão Vermelho | 0,06 | 0,0806 | 1,34× |
| 9 | Bosque da Praia | 0,05 | 0,0000 | premissa maior que o medido |

E em **três abas — nº 78, 80 e 84 — a coluna `% passeio` está preenchida com "—" em todas as
vias**, sem nenhum lastro, e ainda assim a premissa vale 0,05 / 0,13 / 0,28, gerando
24.731,2 m² de calçada faltante.

1. A premissa escalar é a boa (por ser uma amostragem própria de pontos de passeio, mais confiável
   que a coluna via a via), ou a coluna via a via é a boa e a premissa ficou desatualizada?
2. O caso do Mar Aberto (0,02 contra 0,094) parece erro de digitação — 0,02 em vez de 0,09?
   Confirma?
3. Nas abas 78, 80 e 84, de onde saíram 0,05 / 0,13 / 0,28 se nenhuma via tem % preenchido?

## Como responder

O que me ajuda de verdade, em ordem:

1. **Uma planilha reemitida** com os 141 pontos lançados nas linhas de via e, se possível, uma
   coluna de largura por via. É o melhor desfecho.
2. Se não der, **um texto curto respondendo item a item**, dizendo em cada um se o número atual
   se sustenta ou não. Vale mais uma resposta que derruba um número do que uma que o mantém sem
   base — o pacote já registra correções contra nós e não tem problema em registrar mais uma.
3. Em qualquer caso, diga **quais dos 637 pontos você consegue reproduzir hoje** (coordenada, data
   da imagem, classificação), nem que seja por amostra. É o que um analista pediria.
