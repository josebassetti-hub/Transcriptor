# AUDITORIA DE FONTES — Estudo de Mercado GTK Pré-Moldados

**Data da auditoria:** 16/08/2026 (atualizada na revisão v3 — mix por absorção, teto EPP e capacidade efetiva) · **Escopo:** as 146 referências do estudo, os parâmetros sem fonte pública (premissas) e a consistência aritmética interna.

**Legenda de status:**
- ✅ **Confirmada** — o dado citado foi verificado em mais de um resultado de busca ou em documento primário (proposta comercial, SINAPI-ES, legislação);
- 🟡 **Snippet** — o dado consta do resultado indexado da busca (título/resumo da própria fonte oficial); a URL permite conferência direta em um clique. *(A política de rede do ambiente de elaboração bloqueou a abertura direta das páginas; nenhum dado foi redigido sem constar do material indexado.)*
- 📌 **Premissa declarada** — parâmetro sem fonte pública, explicitamente rotulado como premissa no texto, com sensibilidade apresentada;
- 🔁 **Corrigida na auditoria** — a afirmação original foi ajustada nesta revisão (detalhe na coluna Observação).

## 1. Resultado geral

| Categoria | Qtde | Situação |
|---|---|---|
| Referências confirmadas (✅) | 42 | dados centrais: capacidades (proposta), populações Censo 2022, SINAPI-ES 06/2026, Sudene/LC 185, obras SM e Jaguaré, cimento nacional, indústria ES 1S2026, LC 123/EPP, Anexo II do Simples, dias úteis 2027, feriados municipais, benchmarks OEE |
| Referências em snippet (🟡) | 104 | majoritariamente cadastros de empresas (CNPJ/Econodata), notícias oficiais estaduais e diretórios — URLs conferíveis |
| Premissas declaradas (📌) | 12 | listadas na seção 3, todas com sensibilidade ou faixa |
| Afirmações corrigidas na auditoria (🔁) | 16 | listadas na seção 4 |
| Referências reprovadas e removidas | 0 (2 realocadas) | [22] deixou de apoiar "crescimento setorial/orçamento MCMV" e passou a apoiar apenas ordem de grandeza de CAPEX; [61] deixou de apoiar número e passou a contexto |

## 2. Verificação das 30 afirmações que o analista confere primeiro

| # | Afirmação no estudo | Ref(s) | Status | Observação |
|---|---|---|---|---|
| 1 | XP350 produz 7.020 blocos 14/turno 8h (90%) | proposta | ✅ | documento contratual Gervasi REV00, p.3 — anexo do projeto |
| 2 | Troca de molde 15–20 min | proposta | ✅ | p.2 (~15 min) e p.6 (até 20 min, bolsas de ar) |
| 3 | Paver H6 ≈530 m²/turno; ~74 m²/h derivado | proposta | ✅/📌 | dígitos comprimidos no PDF; derivação declarada no §3.3 |
| 4 | São Mateus 123.750 hab (Censo 2022) | [4][5] | ✅ | IBGE via 2 veículos independentes |
| 5 | Nova Venécia 49.065; Jaguaré 28.931; demais populações | [6][7] | ✅ | Censo 2022 (lista completa conferida) |
| 6 | Eixo SM–NV = 64–67 km (Miguel Curry Carneiro) | [1][2][3] | ✅ | quilometragem + CEPs por trecho |
| 7 | Planta no km 35, entre Nova Verona (km 20–37) e Nestor Gomes (km 37+) | [2][3] | ✅ | base oficial de CEP por faixa de km |
| 8 | Cluster de fabricantes no km 28–35 (Pre Santos, EO Pereira, Blocos Gama, ITT, Megalaje) | [73][74][75][76][77] | 🟡 | cadastros/diretórios com endereço e CNPJ; conferível |
| 9 | 3 fabricantes com Selo ABCP no ES, todos em Aracruz/Serra | [53][58][59][60] | ✅ | busca do selo + sites dos 3 |
| 10 | Fábrica prisional Linhares ~1.000 blocos/dia | [86] | 🟡 | notícia oficial SEJUS |
| 11 | Cerâmica ES ~50 milhões peças/mês | [89] | 🟡 | reportagem setorial ES Brasil |
| 12 | Cimento: 64,7 Mt vendas (+3,9%) e 64,8 Mt consumo (+4,1%) em 2024; 67 Mt em 2025 (+3,7%) | [18][19][20] | ✅ | 3 fontes independentes; redação distingue vendas × consumo aparente |
| 13 | Consumo per capita ~280 kg/hab/ano | [138] | ✅ | número publicado (não mais derivação própria) — 🔁 |
| 14 | BlocoBrasil: capacidade ~100 mi blocos/mês (pesquisa mar/2013) | [21] | ✅ | agora datada no texto — 🔁 |
| 15 | MCMV-ES: 18,06 mil UH contratadas 2023–25 (R$ 2,62 bi); ~3,8 mil concluídas/ano | [24][25] | ✅ | Secom/Gov. Federal |
| 16 | Déficit habitacional São Mateus ~3 mil moradias | [62] | 🟡 | TC Online (título literal) |
| 17 | Convênio SM: 26 ruas, R$ 7 mi, >32 mil m², 10 km meio-fio, recursos SERD | [67][135] | ✅ | reconfirmado em 2ª busca; detalhes oficiais |
| 18 | Jaguaré: 13 ruas em blocos, R$ 4,3 mi (Fundo Cidades), pacote R$ 23 mi | [28] | ✅ | reconfirmado em 2ª busca |
| 19 | SEAG fornece blocos e meios-fios no Calçamento Rural | [136] | ✅ | página oficial do programa — achado da auditoria |
| 20 | Caminhos do Campo: +476 km anunciados; R$ 257,4 mi no biênio (reportagem) | [137][72] | 🟡 | 476 km em página SEAG; 257,4 mi atribuído à reportagem no texto |
| 21 | São Gabriel da Palha R$ 4,1 mi em blocos; Boa Esperança 22,9 mil m² | [70][71] | 🟡 | notícias oficiais estaduais/municipais |
| 22 | Indústria ES +20,2% (1S2026, PIM-PF/IBGE; BR +1,5%) | [40][131] | ✅ | período agora explícito — 🔁 |
| 23 | Seacrest: US$ 699 mi investidos; ~R$ 1 bi/ano; meta 2027 | [38][39] | 🟡 | imprensa regional/econômica com números consistentes entre si |
| 24 | Marcopolo São Mateus: R$ 260 mi, +500 empregos | [42] | 🟡 | Em Dia ES/A Gazeta |
| 25 | FNE 2026: R$ 52,6 bi; ES R$ 1,3 bi; indústria prioritária | [123][124][125] | ✅ | Sudene + BNB oficiais |
| 26 | Sudene inclui 31 municípios do ES (LC 185/2021), todos os 9 da área de influência | [132][133][130] | ✅ | IBGE + legislação — 🔁 (era "28") |
| 27 | SINAPI-ES 06/2026: bloco 14 estrutural fbk6 R$ 4,80 … paver e=6 R$ 69,97–88,39/m² | [11] | ✅ | base oficial Caixa (SINAPI-ES, ref. 06/2026, sem desoneração) processada localmente |
| 28 | Cimento a granel R$ 350–550/t (nacional 2025) | [93] | 🟡 | referência indicativa; estudo manda cotar localmente |
| 29 | Tarifa EDP-ES +15,53% (2025/26); subestação simplificada até 300 kVA | [14][15][13] | ✅ | ANEEL (notícia + REH 3.508) e norma EDP |
| 30 | Mortalidade da ind. de transformação: 27,3% em 5 anos | [126][127] | ✅ | Sebrae/Agência Brasil |

## 3. Premissas técnicas declaradas (sem fonte pública — rotuladas no texto)

| Premissa | Valor adotado | Sensibilidade/justificativa | Onde |
|---|---|---|---|
| Fração do cimento destinada a artefatos vibroprensados | 8–15% (central 12%) | resultado varia 3,4–6,4 mi blocos-eq; método é só validação cruzada | §5.3 Método A |
| Novas UH/ano na área de influência | 700–1.000 | derivada de crescimento censitário + MCMV + déficit + loteamentos | §5.3 Método B |
| Blocos por UH | 2.200–3.000 | 12,5 blocos/m² [90] × paredes de casa 50–70 m² + muros | §5.3 / Apêndice A |
| Anualização do pipeline público | pacotes ÷ 2–3 anos | evita dupla contagem; obras sem data ficam fora da soma | §5.3 / §8.1 |
| Consumo de cimento por bloco 14 vedação | 1,00 kg | ref. de mercado ~1,05 [17]; vibrocompactação economiza até 15% | §13.2 |
| Preços-alvo de venda GTK | tabela §6.4 | 10–25% abaixo da mediana SINAPI-ES; validar com 5 cotações locais | §6.4 |
| Mix de vendas (% do mercado em valor) | ved. 45% (36+9), estrutural+compl. 30% (26+4), paver 25% | paver derivado do SAM (24–33%→25%); horas da planta alocadas na proporção do mercado | §5.4 |
| Carga tributária sobre a receita | 15% | cobre Simples Anexo II no topo (15,0% [140]) e L. Presumido típico; regime a definir com contador (upside) | §13.2 |
| MC média do mix | 30% | derivada: 31,2% (planilha, aba Mix e Plano); adotado valor menor | §13.2/§13.4 |
| Cascata de capacidade efetiva | 249 dias úteis − paradas = ~210 dias efetivos (OEE ~76%) | calendário [141][142]; manutenção [145][146]; benchmark OEE [143][144]; não planejadas 6% e refugo 2% como premissas | §3.7 |
| Custos fixos mensais | R$ 52 mil | decomposição item a item no §13.3 | §13.3 |
| Serviço da dívida FNE | ~R$ 46–50 mil/mês | recomendação: ~R$ 4,0–4,5 mi em 12 anos (DSCR ≥1,35); substituir pela simulação BNB | §13.4 |

## 4. Correções aplicadas nesta auditoria (transparência total)

1. **Base única de receita**: as tabelas §5.4 e §13.4 usavam bases divergentes; ambas agora derivam da receita plena de R$ 7,24 mi (mix na planilha/Apêndice A). Receitas por cenário recalculadas (ex.: 60% = R$ 4,3 mi, antes "4,6"; 95% = R$ 6,9 mi, antes "7,0").
2. **Ponto de equilíbrio operacional**: de "≈29%" para **≈25% da capacidade de 1 turno** (R$ 149 mil/mês ÷ R$ 7,24 mi ÷ 12 = 24,6%).
3. **Equilíbrio com dívida**: consolidado em **R$ 320 mil/mês ≈ 53%** (SAC ~R$ 60 mil/mês pós-carência).
4. **EBITDA de regime**: de "R$ 1,3–1,5 mi" para **R$ 1,3–1,4 mi** (75–80% × 7,24 × 35% − 0,62).
5. **Shares do SAM**: ano 1 de "13–19%" para **12–20%**; anos 1–2 "13–28%" → **12–27%**; regime "25–36%" → **22–36%**.
6. **Física do frete**: truck de 13–14 t carrega ~1.090–1.180 blocos (não 1.700–2.000); frete/bloco no 1º anel R$ 0,36–0,49 e da Grande Vitória R$ 1,30–1,90 (carreta) — vantagem de 3–5×, antes superestimada.
7. **Sudene**: de "28" para **31 municípios do ES (LC nº 185/2021)**, com fonte legal e lista incluindo os 9 municípios da área de influência.
8. **Consumo per capita de cimento**: substituída derivação própria (~318 kg) pelo número publicado (**~280 kg/hab/ano**), reduzindo o Método A para 42,8 mil t/ano na área.
9. **Método A** reclassificado como validação cruzada com premissa declarada (8–15%) — antes o percentual aparecia apoiado em referência que não o publica.
10. **BlocoBrasil** datada (pesquisa de março/2013) e tratada como referência histórica.
11. **Indústria ES +20,2%** com período e pesquisa explícitos (1S2026, PIM-PF/IBGE) e segunda fonte.
12. **Custo variável**: padronizado R$ 1,85 industrial / R$ 2,28 total (o "R$ 1,90" remanescente é meta operacional, rotulada como meta); obras de Pedro Canário/Pinheiros marcadas como histórico fora da soma anual; citação [22] realocada para custo de implantação; MCMV 8–11 mi blocos/ano qualificado como teto de premissa.

13. **Mix por absorção de mercado (v3)**: o mix anterior (40/20/15/10/15% dos dias de produção) era premissa qualitativa; substituído pelo método em 3 passos — capacidade máxima por produto → horas alocadas na proporção do valor que cada família representa no mercado (45% vedação, 30% estrutural+complementos, 25% paver) → escala única até o teto. A participação de cada produto na receita anual agora é mostrada separadamente (§5.4).
14. **Teto de receita EPP (v3)**: plano-base limitado a R$ 4.791.000/ano (< R$ 4,8 mi da LC 123 [139]) — decisão de conservadorismo e enquadramento de porte (independe do regime tributário); vende-se menos do que se fabrica.
15. **Carga tributária (v3)**: premissa anterior de 8,5% (faixa inicial do Simples) era indefensável no teto da faixa; corrigida para 15% com comparação Simples Anexo II × Lucro Presumido (folha enxuta) no §13.2 — MC média passou de 35% para 30% (derivada 31,2%) e todos os indicadores foram refeitos (BE R$ 173 mil/mês; EBITDA regime R$ 813 mil; DSCR por estrutura de dívida; payback ~9 anos).
16. **Capacidade efetiva (v3)**: a utilização passou a ser medida contra ~210 dias efetivos/ano (cascata §3.7: 252 dias úteis nacionais − 3 feriados locais − manutenção preventiva 16 − trocas 2 − revisão anual 3 − não planejadas 6% − refugo 2%; OEE implícito 76%) — o plano no teto usa 83% da capacidade efetiva (e 66% da nominal), respondendo à diligência sobre feriados e paradas obrigatórias.

## 5. Numeração completa das referências

A lista integral com instituição, descrição e URL de cada uma das 146 referências está em `fontes.md` e na seção 16 do estudo. Nesta auditoria, **todas** foram checadas quanto a: (i) a afirmação do texto corresponder ao conteúdo indexado da fonte; (ii) especificidade da URL (página do dado, não domínio genérico); (iii) uso não decorativo (cada citação alimenta uma conclusão, premissa ou mitigador). As duas únicas citações cuja função mudou ([22] e [61]) estão descritas na seção 1.

## 6. Limitações remanescentes (para diligência da implantação)

1. Preços locais de venda e de insumos: calibrar com 5 cotações telefônicas (contatos no cap. 6/7) — os valores atuais são tabelas referenciais oficiais + faixas nacionais.
2. Valores dos editais CE 001/2025 e CE 005/2025 de São Mateus: consultar PNCP/portal de transparência municipal.
3. Datas das obras de Pedro Canário e Pinheiros: confirmar em diligência (já fora da soma de demanda).
4. Confirmar por telefone a venda a granel da Mizu Vitória e o frete até a planta.
5. As fórmulas da planilha calculam ao abrir no Excel/Google Sheets; o recálculo automatizado do ambiente de elaboração estava indisponível — todos os resultados foram conferidos por recomputação independente em Python (Apêndice A).
