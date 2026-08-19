# Respostas à reconciliação do Levantamento_Pavimentacao_Guriri.xlsx

**Data:** 19/08/2026 · **Responde a:** as quatro frentes levantadas pela auditoria independente
**Acompanha:** `Levantamento_Pavimentacao_Guriri_v2.xlsx` (planilha reemitida)

Antes de entrar nos itens: **as cinco divergências apontadas procedem, todas.** Reproduzi cada
número da auditoria a partir dos dados brutos e todos batem — inclusive os 496, a partição
462/34 e a tabela de gaps loteamento a loteamento. Três eram falhas de exposição (dado correto,
mal apresentado) e duas eram números sem base que não deveriam ter sido publicados. A planilha v2
corrige as cinco. Onde a correção derruba um número, ela está marcada como tal.

---

## BLOCO 1 — A contagem de pontos

### 1. Os 141 pontos foram realmente verificados? Sim.

**A hipótese está quase certa, mas o mecanismo é outro.** Não é que se olhou o ponto e não havia
traçado. É o inverso: **havia traçado, o ponto foi aberto e classificado — mas a via em que ele
caiu não tem, no mapa, um nome que corresponda a alguma via da lista da planta.**

A malha de amostragem foi gerada sobre o traçado viário existente dentro do polígono de cada
loteamento. Quando o trecho tinha nome coincidente com a planta, o ponto foi creditado àquela
linha. Quando o trecho existia mas estava **sem nome no mapa, ou com nome que não consta da
planta**, o ponto recebeu um rótulo interno com asterisco (`*sem nome`) e passou a alimentar a
**taxa agregada do loteamento** — que é exatamente o que as linhas marcadas "sem ponto próprio —
taxa agregada da malha física auditada do loteamento" usam. O ponto foi verificado, entrou na
conta do loteamento e simplesmente não tinha a que linha ser creditado.

São exatamente 141, e reproduzem a sua tabela:

| Nº | Loteamento | Pontos na malha sem nome | Street View | Satélite |
|---|---|---|---|---|
| 80 | Soma Cevolani (Golden Guriri) | 32 | 2 | 30 |
| 35 | Verão Vermelho | 28 | 11 | 17 |
| 27 | Residencial Mar Aberto | 25 | 25 | 0 |
| 9 | Bosque da Praia | 24 | 9 | 15 |
| 78 | João de Barro (COHAJOBA) | 14 | 0 | 14 |
| 84 | Pontal de Guriri II | 14 | 4 | 10 |
| 7 | Balneário de Guriri | 4 | 4 | 0 |
| | **TOTAL** | **141** | **55** | **86** |

Os 55/86 fecham com o seu "buraco de 55 no Street View e 86 dos 120 de satélite". A correlação
que você notou com a metragem só de planta é real e tem causa comum: onde o loteamento foi
implantado com traçado diferente do projeto, os nomes da planta não aparecem no mapa — e isso
produz, ao mesmo tempo, metragem sem lastro medido e pontos sem via a que se ligar.

### 2. A planilha foi reemitida com os 141 lançados. Sim.

Na v2, cada aba de loteamento traz agora, no bloco de resumo, duas linhas explícitas —
*Pontos verificados em vias nomeadas* e *Pontos verificados na malha física sem nome no mapa* —
e o `Resumo Geral` ganhou três colunas: `Pontos em vias nomeadas` (496), `Pontos na malha física`
(141) e `Total de pontos` (637). **496 + 141 = 637 fecha na planilha, sem nota de rodapé.**

Fui além do pedido: a v2 tem uma aba nova, **`Pontos auditados`**, com **os 637 pontos, um por
linha** — ID, loteamento, via ou malha, latitude, longitude, fonte, data da imagem, superfície
classificada, se conta como pavimentada, calçada nas testadas, extensão representada e observação
do verificador. Isso responde também ao seu item 3 de "como responder": **todos os 637 são
reproduzíveis hoje, não uma amostra.**

### 3. Se não tivessem sido verificados, eu diria.

Não é o caso — mas registro o teste que faz a afirmação verificável: a coluna `Data da imagem` na
aba de pontos está preenchida para os 517 pontos de Street View e vazia para os 120 de satélite.
Um ponto herdado ou estimado não teria data de imagem nem coordenada. A distribuição das datas é
nov/2023 (292), mai/2026 (96), dez/2023 (92), fev/2012 (23), nov/2013 (8), nov/2025 (6).

**Você pode continuar citando 637** — desde que com a partição correta: 496 creditados a vias
nomeadas e 141 à malha física do loteamento. Se o analista preferir o número conservador,
**496 é o número de pontos que sustentam uma linha de via individualmente**, e é uma citação
igualmente honesta.

### 4. As duas exceções

**Nº 42 (Bom Jesus) fecha em zero** porque **todo** trecho com traçado dentro do polígono tem nome
que bate com a planta — zero pontos de malha sem nome. A metragem só de planta dele (2.076 m) são
duas vias nomeadas, Rua Porto Alegre (1.370 m) e Rua Porto Velho (706 m), que existem na planta,
não receberam ponto próprio e caíram na taxa agregada. Ou seja: no nº 42 a metragem sem lastro e
os pontos sem via **não coincidem**, e por isso a conta fecha.

**Nº 7 (Balneário) tem 4 pontos sobrando** e eles têm nome: os quatro estão sobre o **Calçadão de
Guriri**, a via de pedestres da orla (ids 612 a 615, imagens de mai/2026 e nov/2025, bloquete). O
calçadão existe no mapa e está dentro do polígono, mas **não é via de rolamento e não consta da
planta** — logo não tem linha a que ser creditado. Rigorosamente, esses 4 não deveriam contar como
pontos de auditoria de via; estão listados na aba de pontos com o prefixo `(malha)` para que você
possa descontá-los se quiser. Com esse desconto, o universo vira 633.

### 5. A partição 517/120 vale para os 637.

Vale, e é essa mesma: 517 Street View + 120 satélite **sobre os 637**. A partição rastreável que
você extraiu (462/34) é a dos 496 creditados a vias; a diferença é a partição dos 141 (55/86). A
proporção é mesmo bem diferente, e a razão é a que você deduziu: satélite é o recurso usado onde
o Street View não entra, que é justamente onde o traçado não tem nome. **86 dos 120 pontos de
satélite caem na malha sem nome — 72%.**

### O espaçamento: nem 304 nem 350

A regra real não foi "637 pontos distribuídos sobre 193.374 m". Foi, **por trecho contínuo de via
dentro do polígono**: `n = máximo(1; arredondar(comprimento ÷ 350 m))`, com remoção de pontos
duplicados a menos de 35 m um do outro. O `~350 m` do cabeçalho é o **alvo para trechos longos**,
não a média realizada — e o cabeçalho está impreciso ao sugerir o contrário.

O que a regra produz de fato: a extensão representada por ponto tem mediana de **267 m**,
quartis de 151 m e 346 m, e soma 154.239 m de traçado observado. **216 dos 637 pontos vêm de
trechos com menos de 175 m, que caíram na cláusula do mínimo de 1 ponto** — é isso que puxa a
média para baixo. Nenhum
ponto representa mais de 518 m. A redação correta, que está na v2, é: *"1 ponto a cada ~350 m de
trecho contínuo de via, com no mínimo 1 ponto por trecho"*.

---

## BLOCO 2 — As duas linhas contraditórias

### 2.1 João de Barro (nº 78): as duas frases são verdadeiras, sobre coisas diferentes — e o cabeçalho está mal escrito

Os **14 pontos existem e foram verificados**, todos por **satélite** — o João de Barro não tem
nenhuma cobertura de Street View. Os 14 deram saibro, e é daí que vem o 0% de pavimentação do
loteamento, que se sustenta.

Mas **satélite não permite ler calçada.** Por isso a observação de passeio diz "NÃO verificado
ponto a ponto": ela é verdadeira **sobre o passeio**. O cabeçalho "Auditoria completa: 14 pontos
verificados" é verdadeiro **sobre a pista** e não fazia essa distinção — é uma falha de redação
minha, não um conflito de dados.

**Qual vale:** ambas, com o escopo explícito. Na v2 o cabeçalho passou a discriminar pontos de
pista e base do passeio, e — este é o ponto que **derruba um número** — o **% de passeio do nº 78
deixou de ser 5% e passou a NÃO MEDIDO**. Aqueles 5% eram estimativa de uma versão anterior, sem
nenhuma leitura por trás, e não deveriam ter sobrevivido à auditoria. Com isso saem **1.102 m de via — 4.408 m²** (fator de 4,0 m²/m nesse loteamento) do total de
passeio faltante.

### 2.2 Soma Cevolani / Golden Guriri (nº 80): a pavimentação se sustenta; o passeio não

**Em que se apoia o "100% pavimentado":** em **imagem de satélite recente, em 30 pontos**, com
confiança alta declarada pelo verificador. O que ele registrou nesses pontos: pista cinza
homogênea com **meio-fio e sarjeta**, **faixas de pedestre pintadas** em vários cruzamentos e uma
**rotatória com sinalização horizontal**. Não é inferência a partir da planta nem matéria de
entrega — é leitura direta de imagem, e é reproduzível: os 30 pontos estão na aba `Pontos
auditados` com coordenada. Os outros 2 pontos do loteamento são de Street View e estão sobre a
**ES-010, na orla** — ou seja, no limite leste, não na malha interna.

Duas ressalvas honestas sobre essa linha, ambas agora visíveis na v2:

- A malha física observada nos 30 pontos de satélite soma **3.822 m**, contra **4.952 m** que a
  planta atribui ao loteamento — **77,2% da metragem tem grade correspondente observada**; o
  restante é projeto. A correspondência entre a grade observada e os **nomes** das 8 vias da
  planta nunca foi estabelecida — daí o "sem ponto próprio" em cada linha e o "100% de metragem
  só de planta". A **confiança baixa** declarada refere-se a isso, não à leitura do pavimento.
- **O "87% sem calçada" não se sustenta e foi retirado.** Ele vinha de **2 leituras — e as duas
  estão na ES-010**, fora da malha interna. Usar a orla para inferir a calçada das ruas internas
  de um residencial fechado não é defensável. Na v2 o nº 80 está como **NÃO MEDIDO** para passeio,
  o que **retira 18.276 m²** do inventário de calçada faltante (4.308 m de via × 4,2423 m²/m).

**Resumo para o pacote:** mantenha o 100% pavimentado (evidência: 30 pontos de satélite, cf. alta,
com sinalização pintada e meio-fio visíveis); mova para "a confirmar" a **correspondência
via-a-via e a metragem de 4.952 m**, que é de planta. Se a hipótese de pavimentação caísse, a
falta subiria 4.952 m — mas ela é a linha **mais bem observada** do inventário em número de
pontos por metro, e o que está frágil ali é o cadastro das vias, não o pavimento.

---

## BLOCO 3 — A largura das vias

### 1. De onde saíram os 8 m: arbitragem minha — mas as plantas a confirmam como caso modal

Sendo direto: **os 8 m foram uma premissa única que eu adotei, não uma extração das plantas.** A
planilha estava certa em chamá-la de premissa e errada em não abrir a base.

Ao conferir agora, o quadro é melhor do que a origem sugere. **As plantas trazem caixa de via, e
185 das 418 vias de planta a informam** (44%). A distribuição é fortemente concentrada:

| Caixa de via | Vias | | Caixa | Vias |
|---|---|---|---|---|
| **12,0 m** | **146** | | 20,0 m | 5 |
| 15,0 m | 12 | | 22,0 m | 3 |
| 11,0 m | 7 | | 25,0 m | 2 |
| 18,5 m | 2 | | 34,0 m | 1 |
| outras (6; 10; 16; 18,03; 19,6; 20,58; 23) | 7 | | | |

A caixa de 12 m domina — e **12 m de caixa com dois passeios de 2 m devolve exatamente 8 m de
leito carroçável**. Ou seja, a premissa e o fator de calçada de 4 m²/m que a planilha usou são
mutuamente consistentes e correspondem ao padrão real dominante do loteamento capixaba na ilha
(8 + 2 + 2 = 12). Isso não transforma arbitragem em medição, mas mostra que ela caiu no lugar
certo para a maioria das vias.

### 2. Sim, dá para abrir a largura por via — e está feito

A v2 traz, em cada aba, três colunas novas: **`Caixa de via — planta (m)`**, **`Origem da
largura`** e **`Largura de pista adotada (m)`**, e a coluna de m² passou a ser calculada
**via a via** (`falta × largura da via`), não mais por escalar. Onde a caixa veio do quadro da
planta, o valor está em negrito; onde foi preenchida por padrão, a célula está em amarelo.

Regra de conversão, declarada na própria planilha:

| Caixa de via | Largura de pista adotada | Dedução |
|---|---|---|
| até 15 m | caixa − 4,0 m | dois passeios de 2,0 m |
| 15 a 20 m | caixa − 5,0 m | dois passeios de 2,5 m |
| acima de 20 m | caixa − 8,0 m | dois passeios de 2,5 m + canteiro central de 3,0 m |

Vias sem largura na planta recebem a **mediana da própria planta**; plantas sem nenhuma largura
recebem 12,0 m (a moda da ilha), que devolve os mesmos 8,0 m de antes — a mudança nunca é
silenciosa.

**O efeito contraria a direção que a sua sensibilidade temia.** Com largura por via o volume
**sobe 7,1%**:

| | Falta pavimentar |
|---|---|
| Premissa única de 8 m | 1.135.968 m² |
| **Larguras da planta, via a via** | **1.216.547 m²** |
| Diferença | **+80.579 m² (+7,1%)** |

A alta se concentra onde a caixa é maior que 12 m: Mar Aberto (+37,5%), Flor Pan (+37,5%),
Bosque da Praia (+15,3%), Pontal de Guriri II (+14,8%), Vale do Amazonas (+13,1%), Albatrozes
(+6,4%) e Oitizeiro (+4,9%). O Verão Vermelho é o único que **cai** (−2,4%), por ter vias de 10 m
de caixa. **Doze loteamentos não mudam nada**, porque a caixa de 12 m já era o padrão deles; o
nº 80 também não muda, mas por outro motivo — a falta dele é zero, então não há o que converter.

Uma ressalva de alcance, para não vender a melhoria como maior do que é: das **437 vias do
inventário, 138 (32%) têm caixa efetivamente lida da planta**. As demais usam a mediana da própria
planta ou os 12 m padrão. A largura deixou de ser um escalar único para toda a ilha, mas ainda não
é medição via a via em dois terços dos casos — e a planilha marca em amarelo, uma a uma, quais são.

Sobre a **Avenida Copacabana** que você citou: ela está na planta com **25 m de caixa** e passou a
entrar na conta com **17 m de pista**, não 8. Era exatamente o tipo de via que a premissa única
subestimava.

### 3. Os 4 m² de calçada por metro: mesma origem, mesma correção

Vinham da mesma arbitragem (2 lados × 2 m) e agora derivam da caixa: **4 m²/m para caixa até 15 m
e 5 m²/m acima disso** (passeios de 2,5 m nas vias mais largas), aplicados como média ponderada
por loteamento. O efeito é pequeno: o passeio faltante passa de **566.492 m² para 576.888 m² (+1,835%)** antes
das retiradas do Bloco 4 — muito menos que na pista, porque a caixa de 12 m predomina.

---

## BLOCO 4 — A premissa de "% de passeio existente"

### 1. A premissa escalar é a boa. A coluna via a via é que é parcial.

Você está certo de que a coluna via a via **não entra na conta** — mas a conclusão de qual das
duas é a boa se inverte quando se sabe o que cada uma cobre. O **escalar é a média ponderada das
leituras de calçada de TODOS os pontos do loteamento**, inclusive os 141 da malha sem nome. A
**coluna via a via só enxerga os pontos creditados a vias nomeadas**. Nos loteamentos onde há
muitos pontos de malha, a coluna vê uma fração pequena e enviesada da amostra.

Recalculando os três casos que você isolou:

| Nº | Loteamento | Escalar publicado | Recálculo com todos os pontos | Só vias nomeadas | Só malha |
|---|---|---|---|---|---|
| 27 | Mar Aberto | 2% | **1,8%** (33 pontos) | 4,8% (8 pontos) | 0,0% (25 pontos) |
| 35 | Verão Vermelho | 6% | **5,7%** (19 pontos) | 4,7% (8) | 7,3% (11) |
| 9 | Bosque da Praia | 5% | **5,4%** (12 pontos) | 0,0% (3) | 7,7% (9) |

O escalar reproduz em todos os três. A diferença é composição de amostra, não erro de cálculo.

### 2. Mar Aberto: não é erro de digitação. Confirmo o 0,02.

O 2% sai de **33 pontos**; o número maior que você calculou sai de **8**. Os 25 pontos de malha do
Mar Aberto deram **todos** "nenhuma calçada" — e são justamente os que a coluna via a via não
mostra. O 0,02 é o número mais bem amostrado dos dois, e fica.

### 3. Abas 78, 80 e 84: dois dos três não tinham base, e foram retirados

Esta é a correção que mais derruba número no pacote:

| Nº | Valor publicado | Base real | Decisão na v2 |
|---|---|---|---|
| 78 | 0,05 | **nenhuma leitura** — sobrevivente de estimativa anterior | **NÃO MEDIDO** |
| 80 | 0,13 | **2 leituras, ambas na ES-010**, fora da malha interna | **NÃO MEDIDO** |
| 84 | 0,28 | 4 leituras de Street View, na malha do loteamento | **mantido**, confiança baixa |

Os três tinham a coluna via a via em "—" porque **todos os seus pontos são de malha sem nome** —
por isso não havia lastro visível na aba, embora no caso do 84 exista lastro real.

Com o 78 e o 80 fora, o passeio faltante da ilha cai de **141.623 m para 136.213 m de via**
(**−5.410 m**). Em m², a cadeia completa é: 566.492 m² na premissa antiga → **576.888 m²** ao
aplicar os fatores de calçada da planta → **−18.276 m²** (nº 80) **−4.408 m²** (nº 78) =
**554.203 m²**. (A soma dos valores já arredondados por loteamento dá 554.203; arredondando só no
fim dá 554.204 — 1 m² de resíduo.) Na v2 esses
dois aparecem como "não estimado", com a célula em amarelo e a base declarada em coluna própria —
nunca como um número.

---

## O que muda no pacote, em uma tabela

| Indicador | Versão de 19/08 | **v2 reconciliada** | Por quê |
|---|---|---|---|
| Extensão de vias | 193.373 m | 193.373 m | — |
| Pista pavimentada | 51.375 m (26,6%) | 51.375 m (26,6%) | — |
| Falta pavimentar (linear) | 141.996 m | 141.996 m | — |
| **Falta pavimentar (m²)** | 1.135.968 | **1.216.547** | larguras da planta, via a via (+7,1%) |
| **Passeio faltante (m de via)** | 141.623 | **136.213** | nº 78 e nº 80 sem base → NÃO MEDIDO |
| **Passeio faltante (m²)** | 566.492 | **554.203** | idem, com fator de calçada da planta |
| Pontos: rastreáveis / declarados | 496 / 637 | **637 / 637** | os 141 de malha agora reportados |

Nenhum dos números de pista mudou: a auditoria não encontrou erro na classificação, e sim na
**exposição** dela. O que mudou foi a conversão para m² (para cima) e o inventário de calçada
(para baixo, ao retirar o que não tinha base).

## Os dois pontos que eu levaria ao analista antes que ele pergunte

1. **29,5% da metragem (56.979 m) não tem traçado medido** — é metragem de planta. Isso responde
   por **456.036 m² — 37,5% do orçamento** (já com as larguras da planta; na premissa antiga de
   8 m eram 401.344 m²), dos quais **35.450 m estão no Bosque da Praia (nº 9)**, cuja
   malha observada soma apenas 4.849 m. É a maior incerteza do estudo, maior que a da largura, e
   está isolada em colunas próprias no `Resumo Geral`.
2. **"Passeio faltante (m de via)" não é metro linear de calçada.** São metros de via sem calçada
   completa nos dois lados. Quem licitar 136.213 m de calçada erra por um fator de 2.

*Todos os valores permanecem aproximados e derivados de imagem. Nada aqui substitui levantamento
de campo ou consulta à Prefeitura de São Mateus, que continuam recomendados antes de uso oficial.*
