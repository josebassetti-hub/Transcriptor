# METODOLOGIA — Orçamento automático de obra a partir de projetos (DER-ES)

> Roteiro que a IA (Claude) segue **a cada projeto recebido** para produzir um orçamento
> completo **sem perguntar item por item**. Toda decisão não coberta por projeto vira
> **premissa declarada** no memorial. Perguntas ao usuário: no máximo 1–3, só as de alto
> impacto (padrão de acabamento; incluir muro/canteiro; rede pública de esgoto?).
>
> Base de preços: `data/base-der-es.json` (Tabela DER-ES, custo direto, BDI 0).
> Regras de medição: `data/regras-medicao.json` (Cadernos Técnicos).
> Seleção por padrão: `data/mapa-padroes.json`. Heurísticas: `data/indices-estimativa.json`.
> Saída: `orcamento.json` (schema abaixo) carregado no `orcamentista.html`.

---

## FASE 0 — Inventário dos arquivos recebidos

1. Listar pranchas/arquivos e classificar por disciplina: **ARQ** (plantas baixas, cortes,
   fachadas, cobertura, situação), **EST**, **ELE**, **HID/SAN**, **outros** (PPCI, SPDA, gás).
2. Registrar no orçamento: `disciplinas_presentes` e `disciplinas_ausentes` — as ausentes
   acionam as heurísticas da FASE 4 e as premissas de `indices-estimativa.json → premissas_texto`.
3. Identificar: nº de pavimentos, área construída declarada (carimbo/tabela de áreas),
   localização (para nota sobre data-base/região da tabela).

## FASE 1 — Calibração de escala e medição

1. Escala declarada no carimbo (ex.: 1:50) **nunca é confiada às cegas** — PDFs são
   reimpressos/redimensionados. Calibrar por **cota conhecida**: escolher 2 cotas longas e
   independentes (ex.: comprimento total da edificação e largura de um ambiente),
   converter px→m e comparar. Divergência > 3% → recalibrar com terceira cota.
2. Toda medição pela escala usa a planta calibrada. Anotar no memorial:
   `escala calibrada por cotas X e Y, desvio Z%`.
3. Pé-direito: dos cortes; sem cortes → premissa `pe_direito_m` (2,80 m).

## FASE 2 — Take-off de arquitetura (sempre presente)

Por ambiente (nome, tipo, área, perímetro — medidos ou lidos da planta):
1. **Paredes**: comprimento × pé-direito, descontando vãos > 2 m² (critério usual de
   alvenaria; vãos menores não descontados — compensam vergas/enchimento). → `alvenaria`,
   `chapisco`, `reboco`/`emboco` conforme face seca/molhada.
2. **Esquadrias**: quadro de esquadrias quando houver; senão contagem em planta com
   dimensões padrão (porta 0,80×2,10; janela dormitório ≥ 1/6 da área do piso).
   → portas (folha+marco+alizar), janelas (m²), vidros, soleiras, peitoris.
3. **Pisos**: área interna por pavimento → lastro (térreo), regularização, acabamento
   (item pelo padrão), rodapé (ambientes secos).
4. **Forro**: médio/alto → gesso nos ambientes internos; popular → sem forro (premissa).
5. **Cobertura**: área de projeção da planta de cobertura × fator de inclinação+beiral
   (cerâmica 1,3 / fibrocimento 1,15) → estrutura de madeira + telhamento.
6. **Pintura**: faces rebocadas − áreas azulejadas; + forro quando houver; selador sempre,
   massa corrida médio/alto.

## FASE 3 — Instalações COM projeto complementar

Quando o projeto da disciplina existe, **contar o que está desenhado**:
- **ELE**: pontos por tipo (luz, tomadas, interruptores, TUEs), quadro(s), disjuntores do
  diagrama unifilar, medição dos alimentadores em planta. Itens 15.18 (pontos) **não incluem
  o aparelho** → somar 18.02 (tomadas/interruptores) e 18.01/18.10 (luminárias).
- **HID**: pontos por peça (14.07), tubulações por trecho e DN conforme isométrico/planta
  (14.14/14.15 água; 14.19 esgoto), registros (17.03), caixas (14.11/14.21).
- Conferir com os mínimos da FASE 4: se o projeto tiver MENOS pontos que o mínimo NBR,
  manter o projeto e ANOTAR a divergência no memorial.

## FASE 4 — Instalações SEM projeto complementar (heurísticas)

**Elétrica (NBR 5410 mínimos — `indices-estimativa.json → ambientes`):**
1. Pontos por ambiente: 1 luz no teto + interruptor (conjugado c/ tomada); tomadas =
   max(tug_min, ⌈perímetro / tug_por_perimetro⌉); banheiro: chuveiro elétrico (ponto
   dedicado 151805 + disjuntor bipolar 50A + aparelho).
2. **Localizar o quadro**: no desenho (se indicado) ou premissa: cozinha/circulação central.
   **Localizar o poste/medidor**: planta de situação; medir distância pela escala.
3. Alimentador: 3 × dist(quadro→medidor) × 1,2 em cabo 10 mm² + eletroduto 1".
4. Ambientes além de 8 m do quadro: cabo 2,5 mm² e eletroduto 3/4" extras por circuito
   (3 × excedente × 1,2) — o ponto padrão já embute ~5 m de infraestrutura.
5. Circuitos = ilum. (1/75 m²) + TUG (1/60 m²) + cozinha/AS dedicado + 1 por chuveiro
   + reserva → nº de disjuntores mono + quadro conforme nº de circuitos.
6. Padrão de entrada (15.17) por carga estimada: ≤ 5 kW mono; casas médias bifásico;
   alto/ar-condicionado trifásico.

**Hidráulica (NBR 5626):**
1. Pontos de AF por peça (lavatório, bacia c/ caixa, pia, tanque, chuveiro c/ registro
   de pressão). Registros de gaveta: 1 por ambiente molhado + geral.
2. **Localizar reservatório** (premissa: sobre banheiro/área de serviço) → prumadas:
   nº de colunas × (pé-direito + 2) × 2; ramais: dist(prumada→ambiente) medida ou 6 m,
   × 1,25. DN: barrilete/prumada 32 mm, ramais 25 mm (pontos já incluem sub-ramal 20/25).
3. Reservatório 500 L (popular) / 1000 L (médio/alto) + entrada d'água padrão CESAN.

**Esgoto (NBR 8160):**
1. Pontos: primário por bacia; secundário por pia/lavatório/tanque; ralos sifonados
   (1/banheiro + 1/AS); caixa de gordura na cozinha.
2. **Localizar a caixa de esgoto/inspeção existente ou a rede na rua** (planta de
   situação). Traçado: banheiros → caixas de inspeção → gordura (só cozinha) → rede/fossa.
   Medir cada trecho pela escala × 1,15; interno 100 mm (141909), externo enterrado
   140903 (já inclui escavação). Caixas: 1 por zona molhada + 1 a cada 12 m + 1 por
   mudança de direção.
3. Sem rede pública → fossa séptica + filtro anaeróbio (140102+140103) e premissa.

**Estrutura (índices paramétricos — maior incerteza, ±20%):**
- Baldrame: perímetro de paredes × 0,08 m³/m (+ fôrma 0,8 m²/m + escavação 0,24 m³/m).
- Pilares/cintas: área × 0,045 m³/m²; aço 85 kg/m³; fôrma 12 m²/m³; laje treliçada por m².
- Declarar sempre: "recomenda-se projeto estrutural para orçamento definitivo".

## FASE 5 — Seleção de itens e precificação

1. Para cada grupo do `mapa-padroes.json`: quantidade (regra) × item do padrão escolhido.
2. Conferir **critério de medição e serviços incluídos** em `regras-medicao.json` (quando o
   caderno do capítulo já foi ingerido) — evita dupla contagem (ex.: ponto elétrico já tem
   eletroduto do ramal; alvenaria já tem argamassa).
3. Itens fora do mapa (muro, portão, quadra, canteiro, ar-condicionado): adicionar
   manualmente da base pesquisando por descrição.
4. Preços = custo direto DER × (1 + BDI). BDI editável (default 25% residencial privado;
   obras públicas: BDI do órgão). Administração local/canteiro/limpeza conforme porte.

## FASE 6 — Saída (`orcamento.json`)

```json
{
 "obra": {"nome": "", "local": "", "area_m2": 0, "pavimentos": 1, "padrao": "medio",
          "bdi_pct": 25, "data_base": "Abril/2026", "disciplinas_ausentes": []},
 "ambientes": [{"nome": "Sala", "tipo": "sala", "area": 0, "perimetro": 0,
                "dist_quadro_m": null, "dist_prumada_m": null}],
 "medicoes": {"quadro_medidor_m": null, "esgoto_externo_m": null,
              "escala": {"cotas": [], "desvio_pct": 0}},
 "itens": [{"grupo": "piso", "c": "130233", "qtd": 0, "formula": "texto do cálculo",
            "premissa": "texto ou null", "manual": false}],
 "premissas": ["..."], "lacunas": ["..."]
}
```

1. Gerar o JSON, carregar no `orcamentista.html` (aba Projeto → Importar, ou embutir via
   link `#d=`), revisar as 5 abas, imprimir/compartilhar.
2. Memorial: cada item com fórmula, critério de medição citado e premissa. Lista de
   premissas e lacunas no topo. **Nunca entregar número sem origem rastreável.**

## Autocrítica antes de entregar (checklist)

- [ ] Total/m² dentro da faixa de sanidade (CUB-ES residencial: popular R$ 1,8–2,4 mil/m²,
      médio R$ 2,4–3,2 mil/m², alto > 3,2 mil/m² — ordem de grandeza, conferir data-base)?
- [ ] Elétrica 8–15% do total? Hidrossanitário 6–12%? Estrutura+alvenaria 30–45%?
- [ ] Nenhum grupo do mapa com quantidade zero sem justificativa?
- [ ] Premissas cobrem TODAS as disciplinas ausentes?
- [ ] Aparelhos (tomadas/interruptores/luminárias) somados aos pontos?
