# Metodologia v3 — regimes tributários, unidades de contagem, redes e multi-CNAE

Evoluções pedidas na revisão do relatório-piloto e como cada uma é tratada com
dados públicos.

## 1. Regime tributário: o que é público e o que não é

| Grupo | Fonte pública | Identificável por empresa? |
|---|---|---|
| **MEI** | `br_me_cnpj.simples` (opção pelo MEI) | ✅ sim |
| **Simples Nacional** | `br_me_cnpj.simples` (opção pelo Simples) | ✅ sim |
| **Lucro Presumido** | declaração de IRPJ — **sigilo fiscal** | ❌ não |
| **Lucro Real** | declaração de IRPJ — **sigilo fiscal** | ❌ não |

O estudo reporta 3 grupos: **MEI / Simples / Fora do Simples** (Presumido +
Real, indistinguíveis publicamente). Proxy declarado no relatório: fora do
Simples com porte DEMAIS tende a Lucro Real (obrigatório acima de R$ 78 mi de
receita e para setores específicos); ME/EPP fora do Simples tende a Presumido.
A classificação usa a situação vigente na tabela `simples` (opção sem exclusão).

## 2. Unidades de contagem: empresa × estabelecimento × rede

Cada unidade responde a uma pergunta diferente — o relatório usa as três:

| Unidade | O que mede | Pergunta que responde |
|---|---|---|
| **Estabelecimento** (CNPJ completo, matriz ou filial) **na região** | Pontos de atendimento no mercado local — filial de rede de fora da região **conta** | "Qual a cobertura/oferta instalada no mercado estudado?" |
| **Empresa** (`cnpj_basico` distinto) | Decisores/CNPJs-raiz | "Quantos players/clientes potenciais existem?" |
| **Rede** (empresas por nº de estabelecimentos na região: 1 / 2–5 / 6+) | Concentração e "força" dos players | "O mercado é pulverizado ou dominado por redes? Qual o porte real de quem compete?" |

Para estudo de viabilidade, a distribuição por faixa de unidades é o dado de
força competitiva: um mercado com 95% de empresas de 1 unidade é muito diferente
de um com 30% dos estabelecimentos pertencentes a redes 6+.

## 3. Dinâmica (aberturas/fechamentos) por regime e porte

A consulta B3 abre o fluxo anual em **ano × regime (MEI/Simples/Fora) × porte
(MEI/ME/EPP/DEMAIS)**, para aberturas e para fechamentos/inaptidões. Leituras
que isso habilita no relatório:

- “Quem está nascendo”: composição das aberturas (tipicamente dominada por MEI).
- “Quem está morrendo, e de que tamanho”: fechamentos por porte — mortalidade de
  MEI é churn de cauda; fechamento de EPP/DEMAIS é sinal competitivo relevante.
- Ressalvas mantidas: baixas do último ano sofrem atraso de registro; o porte
  registrado pode estar defasado em relação ao faturamento real.

## 4. Multi-CNAE com mix de receita (projeção de receita e share por atividade)

Cenário: o cliente fatura 40% na atividade do CNAE principal e 15% em cada um de
4 CNAEs secundários. Método adotado:

1. **Cada atividade é um mercado próprio.** Para cada CNAE i do estudo:
   - `SAM_i` = SAM da atividade na região (top-down da atividade ou premissa
     `participacao_sam_i` sobre o SAM total do estudo, declarada);
   - **concorrência da atividade** = empresas que exercem o CNAE i como
     principal **ou** secundário (deduplicadas por `cnpj_basico` — sem dupla
     contagem), pois quem faz a atividade "por tabela" também compete nela.
2. **Projeção de receita** = soma ponderada pelo mix do cliente:
   `receita_alvo_i = receita_total_alvo × peso_i` (pesos 0,40/0,15/0,15/0,15/0,15).
3. **Share implícito por atividade** = `receita_alvo_i / SAM_i` — o teste de
   realismo do plano: se o mix exigir 20% de share numa atividade e 0,3% em
   outra, o relatório expõe onde o plano é agressivo.

O share, portanto, **não é global**: é por atividade, contra o conjunto de
concorrentes daquela atividade. No produto, cada atividade do JSON do setor
carrega `{cnae, descricao, peso_receita, participacao_sam}` e a consulta E
fornece a contagem de concorrentes por atividade (principal + só-secundária).
