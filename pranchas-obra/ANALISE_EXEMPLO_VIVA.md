# Análise do exemplo VIVA — Orçamento ↔ Caderno de Plantas

> Par de referência analisado em 15/07/2026: `Planta_Reforma__Viva.pdf` (13 pranchas A4) +
> `Planilha_Orcamentaria_Viva_Cronograma_9meses_170626.xlsx`. Este documento é o **manual de
> estilo** para gerar cadernos de plantas de outras obras a partir da respectiva planilha
> orçamentária, com o kit em `template/`.

## 1. O que é o par de documentos

Dossiê de financiamento bancário de reforma (padrão de banco de fomento — mesma família do
formato BNB/FNE): o engenheiro levanta na obra o que precisa ser feito e produz a **planilha
orçamentária analítica** (formato exigido pelo banco: BDI 0 em administração direta, bases
DER-ES/SINAPI, ART/RRT do orçamentista); a arquiteta produz o **caderno de plantas** que mostra,
por disciplina, *onde* cada serviço orçado será executado. O banco confere a coerência entre os
dois.

- **Obra**: reforma de 345 m² — 2º andar (132 m²) e 5º andar (213 m²), Rua Marechal Deodoro da
  Fonseca 108, Centro, Baixo Guandu/ES.
- **Cliente**: VIVA CUIDADOS EM SAÚDE LTDA (estabelecimento de saúde).
- **Orçamentista**: Eng° Claudio Fernandes Quintela, CREA MG-060909/D — ART 0820260061476.
- **Autora do projeto**: Michelle Cecato, CAU A42167-7.
- **Total**: R$ 690.816,93 (≈ R$ 2.002/m²) · prazo 9 meses (mai/26–jan/27).

## 2. Planilha orçamentária (XLSX, 3 abas)

| Aba | Conteúdo |
|---|---|
| `Manual` | Instruções oficiais de preenchimento do template do banco |
| `Cliente` | O orçamento analítico em si (cabeçalho, declaração, itens, assinaturas) |
| `Cronograma` | Cronograma físico-financeiro mensal com etapas e curva acumulada |

Colunas do orçamento analítico: `ITEM · BASE REFERÊNCIA · DATA BASE · CÓDIGO · DISCRIMINAÇÃO ·
UNID · QUANT · PREÇO UNIT (S/ BDI) · PREÇO TOTAL · OBS`. Hierarquia: `1` obra → `1.n` grupo →
`1.n.m` subgrupo → `1.n.m.k` serviço.

### Grupos de serviço (nível `1.n`)

| Grupo | Valor (R$) | % | Principais serviços |
|---|---:|---:|---|
| 1.1 Pisos internos e externos | 84.843,50 | 12,3 | contrapiso 280 m², porcelanato 60x60 280 m², vinílico 150 m², rodapé granito 158,5 m |
| 1.2 Tetos e forros | 34.099,20 | 4,9 | forro fibra mineral 360 m² |
| 1.3 Revestimento de paredes | 11.985,00 | 1,7 | cerâmica 10x10 100 m² (áreas molhadas) |
| 1.4 Instalações hidrossanitárias | 44.783,11 | 6,5 | 113 pontos, tubos PVC 215 m, rede esgoto 110 m |
| 1.5 Aparelhos hidrossanitários | 34.825,86 | 5,0 | 10 lavatórios, 7 bacias (1 PNE), bancadas granito 18,3 m², barras NBR 9050 |
| 1.6 Instalações elétricas | 81.592,20 | 11,8 | eletrodutos 1.150 m, cabos 5.100 m, disjuntores/DR/DPS |
| 1.7 Aparelhos elétricos | 28.711,38 | 4,2 | 90 luminárias LED + 30 emergência, 110 tomadas, 106 interruptores, 40 TV |
| 1.8 Outras instalações | 24.178,97 | 3,5 | rede lógica cat5e 850 m + 40 RJ45, telefonia 500 m + 30 RJ11 |
| 1.9 Esquadrias de madeira | 30.303,30 | 4,4 | 22 portas + 22 marcos (0,70 e 0,80 × 2,10) |
| 1.10 Esquadrias metálicas | 248.229,49 | **35,9** | **pele de vidro laminado 15 mm 90 m²**, vidro temperado 10 mm 90 m², portas de vidro |
| 1.11 Pintura | 30.790,36 | 4,5 | massa+látex 360 m² paredes/forros, esmalte 161 m² madeira |
| 1.12 Serviços complementares | 8.442,00 | 1,2 | limpeza geral e de pisos |
| 1.13 Administração local | 28.032,56 | 4,1 | engenheiro pleno + mestre, 116 h cada |

### Cronograma (9 meses, 3 etapas de 3 meses)

Etapa 01 R$ 260.178,81 · Etapa 02 R$ 300.480,74 · Etapa 03 R$ 130.157,38. Sequência executiva:
infra hidráulica/elétrica primeiro (meses 1–4), esquadrias metálicas/pele de vidro (2–5), pisos
(2–3 e 5–7), forro (5–6), revestimentos (4–5), pintura (6–7), aparelhos hidro (7–8) e elétricos
(8–9), limpeza (8–9), administração linear (1–9). Pico de desembolso no mês 5 (19%).

## 3. Caderno de plantas (PDF, 13 pranchas A4 retrato)

| Pág | Prancha | Pavimento | Nº |
|---|---|---|---|
| 1 | Capa (dados da obra + relação de documentos) | — | — |
| 2 | Planta Baixa | 5º | 1/6 |
| 3 | Iluminação | 5º | 2/6 |
| 4 | Paginação de Piso | 5º | 3/6 |
| 5 | Móveis/Marcenaria | 5º | 4/6 |
| 6 | Móveis/Marcenaria (**duplicada** — deveria ser Planta da Reforma 5/6) | 5º | 4/6 |
| 7 | Pontos Elétricos (esc. 1/25) | 5º | 6/6 |
| 8 | Planta Baixa | 2º | 1/6 |
| 9 | Paginação de Piso | 2º | 2/6 |
| 10 | Iluminação | 2º | 3/6 |
| 11 | Móveis/Marcenaria | 2º | 4/6 |
| 12 | **Planta Obra** (anotações da reforma) | 2º | 5/6 |
| 13 | Pontos Elétricos (esc. 1/25) | 2º | 6/6 |

### Anatomia da prancha (replicada em `template/prancha.html`)

- Moldura preta com canto superior direito arredondado (~24 mm).
- Desenho na metade superior; título em caixa alta espaçada com **balão** (círculo) à esquerda e
  sublinhado; `ESC: 1/100` abaixo (elétrica 1/25).
- Quadro **LEGENDA** à direita, acima do carimbo; na Planta Obra há também quadro **GERAL** com a
  lista de serviços do pavimento.
- **Carimbo**: célula esquerda da responsável (nome manuscrito + CAU + "Arquitetura·Interiores");
  à direita: `PROJETO DE REFORMA` → `CLIENTE | AUTOR DO PROJETO` (com assinaturas digitais
  gov.br) → nomes → `ENDEREÇO` → `DATA | ÁREA | PRANCHA n/6`.

### Convenções visuais observadas

- **Azul**: esquadrias de vidro / pele de vidro nas fachadas (item 1.10).
- **Vermelho**: pequeno trecho de intervenção junto à escada (2º) e acesso (5º).
- **Malha quadriculada**: paginação de piso — desenhada **por baixo** das paredes (aparece nos
  vãos das paredes duplas); legenda indica o material.
- **Iluminação**: malha de forro + símbolos coloridos (painel LED 28x28W rosa, plafon amarelo,
  painel 22x22W, spot ✳) — correspondem a 1.2 (forro) + 1.7 (luminárias).
- **Pontos elétricos**: triângulos/círculos vermelhos com simbologia de alturas (tomada baixa
  h=30, média h=115, alta/TV h=180, interruptores h=110, interfone h=80, rede h=30).
- **Planta Obra**: setas com anotações por ambiente ("WC – revestimento até 110 cm e pintura,
  instalação de louças sanitárias") + quadro GERAL (pele de vidro, pisos, revestimentos de
  banheiros/copa/DML, rodapé).

## 4. Mapeamento orçamento → pranchas (a "gramática")

| Grupo do orçamento | Prancha onde aparece | Como aparece |
|---|---|---|
| 1.1 Pisos | Paginação de Piso | malha + legenda do material; rodapé citado na Planta Obra |
| 1.2 Forros | Iluminação | malha de forro sob os símbolos |
| 1.3 Revestimentos | Planta Obra | anotação nos ambientes molhados ("revestimento até 110 cm") |
| 1.4/1.5 Hidrossanitário | Planta Obra (+ Planta Baixa) | anotação "instalação de louças sanitárias"; louças desenhadas |
| 1.6 Instalações elétricas | Pontos Elétricos | eletrodutos/circuitos implícitos nos pontos com alturas |
| 1.7 Aparelhos elétricos | Iluminação + Pontos Elétricos | luminárias na Iluminação; tomadas/interruptores nos Pontos |
| 1.8 Rede lógica/telefone | Pontos Elétricos | símbolo "rede (internet e telefone)" |
| 1.9 Portas de madeira | Planta Baixa / Planta Obra | portas com giro desenhadas |
| 1.10 Esquadrias metálicas / vidro | todas (linha azul) + quadro GERAL | pele de vidro nas fachadas |
| 1.11 Pintura | Planta Obra | anotações "e pintura" |
| 1.12/1.13 Limpeza e administração | — | serviços gerais, sem prancha |
| *(sem item no orçamento)* | Móveis/Marcenaria | layout de uso — **móveis não entram** na planilha do banco (nota 1 do template) |

### ⚠️ Incoerências detectadas no exemplo (evitar na próxima obra)

1. **Piso**: legenda das pranchas diz `PORCELANATO 90X90`; o orçamento (1.1.2.1) especifica
   `porcelanato 60x60 cm Portobello`. É exatamente o tipo de divergência que análise bancária
   aponta.
2. **PDF montado com página duplicada**: a prancha 5/6 do 5º andar (Planta da Reforma) não está
   no PDF — a 4/6 aparece duas vezes.
3. **Escala**: as pranchas dizem `1/100`, mas o desenho impresso está em ≈1:125 (malha de 90 cm
   medida em 20,4 pt). Na obra nova: calcular a escala real de impressão e, se possível,
   acrescentar barra gráfica.

## 5. Pipeline para a nova obra (quando chegarem orçamento + projeto)

1. **Orçamento**: extrair grupos `1.n`, quantidades e descrições (openpyxl) → definir a lista de
   pranchas: uma por grupo com expressão espacial + Planta Baixa + capa (+ Planta Obra com o
   quadro GERAL amarrando os demais grupos).
2. **Projeto**: extrair a planta baixa de cada pavimento como SVG vetorial
   (`pdftocairo -svg -f <pág> -l <pág>`), medir o recorte e a escala real
   (raster 72 dpi → 1 px = 1 pt).
3. **Camadas temáticas**: para cada prancha, gerar fragmento SVG (malhas por baixo; símbolos de
   `template/simbologia.svg` e anotações por cima), com quantidades/especificações citando o item
   do orçamento na legenda.
4. **Montagem**: um JSON por prancha → `python3 template/montar.py prancha.json` →
   `template/gerar_pdf.sh -o caderno.pdf capa.html *.html`.
5. **QA de coerência (o que o banco confere)**: todo grupo do orçamento aparece em ≥1 prancha;
   materiais/dimensões das legendas idênticos às discriminações da planilha; áreas do carimbo
   batem com a descrição da obra; sem divergências tipo item 4 acima.
6. Entregar PDFs + fontes; marca "reprodução digital" até haver prancha assinada por RT.

## 6. Prova de conceito (`poc/`)

Reproduzimos a prancha **2/6 — Paginação Piso 2º Andar** a partir da planta baixa (pág. 8) do
PDF original + malha 90x90 gerada por código (`grade-piso.svg`), montada com o template e
convertida em PDF A4. Comparação lado a lado validou: moldura, título com balão, malha sob as
paredes, pele de vidro azul, legenda e carimbo. Diferenças intencionais: nomes de ambientes
visíveis (herdados da planta baixa), campos de assinatura vazios e marca "reprodução digital" no
rodapé.

Reproduzir: `python3 template/montar.py poc/prancha-paginacao.json && template/gerar_pdf.sh
poc/paginacao-piso-2andar.html`.

## 7. O que pedir junto com a nova obra

- [ ] Planilha orçamentária XLSX (mesmo formato de banco).
- [ ] Projeto em PDF **vetorial** com planta baixa legível de cada pavimento (se for scan/foto, o
      redesenho é manual e menos fiel).
- [ ] Dados do carimbo: cliente/CNPJ, endereço, área por pavimento, data, responsável técnico e
      registro (ou deixo placeholders).
- [ ] Se houver: relação de ambientes por pavimento e observações do engenheiro (o que é
      demolição × construção nova).
