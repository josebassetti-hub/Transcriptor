# Ferramentas de Engenharia — Orçamentista DER-ES + Simulador BNB/FNE

Dois apps **de arquivo único, zero dependências, offline** — abrem direto do WhatsApp no celular:

| App | Arquivo | O que faz |
|---|---|---|
| 🏗️ **Orçamentista DER-ES** | `orcamentista.html` | Orçamento de obra por padrão de acabamento sobre a Tabela Referencial DER-ES (pontos + distâncias pela escala + memorial com premissas) |
| 🏦 **Simulador BNB/FNE** | `index.html` | Simulador de financiamento FNE com camada de apresentação comercial e estratégia tributária |

---

## 🏗️ Orçamentista DER-ES

Implementa a metodologia descrita em **`METODOLOGIA.md`**: você envia o projeto arquitetônico,
a IA (ou você) preenche a lista de ambientes e as distâncias medidas pela escala, e o app monta
o orçamento completo **sem perguntar item por item** — o padrão de acabamento
(popular/médio/alto) escolhe os itens da tabela automaticamente e toda estimativa vira
**premissa declarada no memorial**.

### As 5 abas

1. **📁 Projeto** — dados da obra (padrão, BDI, rede de esgoto, laje…), tabela de ambientes
   (tipo, área, perímetro, distância ao quadro elétrico e à prumada/caixa) e **planta com
   calibração de escala**: carregue a foto/print, clique nos 2 extremos de uma cota conhecida,
   informe os metros — depois meça qualquer distância clicando em 2 pontos e aplique direto
   no campo (quadro→medidor, esgoto externo, ambiente…).
2. **📋 Quantitativos** — cada grupo com a fórmula à vista (ex.: tomadas = mínimos NBR 5410
   por perímetro), quantidade e item DER **editáveis**, busca em toda a base (1.340 serviços)
   para itens extras (muro, portão, ar-condicionado…).
3. **💰 Orçamento** — planilha por capítulo DER com PU sem/com BDI, total, R$/m² e curva ABC.
4. **📝 Memorial** — premissas, lacunas e memória de cálculo item a item, com o **critério de
   medição do Caderno Técnico** quando o capítulo já foi ingerido.
5. **⚙️ Parâmetros** — parâmetros de estimativa editáveis (pé-direito, fatores de rota,
   raio coberto por ponto…), sobrescrita de preço por código e **autoteste** de regressão.

Compartilhe pelo **link/QR** (estado codificado no `#d=` da URL), exporte **JSON**
(`orcamento.json` — o formato que a IA gera ao analisar um projeto) ou **CSV** para Excel,
e imprima a proposta **A4** (capa, planilha, premissas, memória e campo de assinatura).

### O motor de estimativa (resumo)

- **Pontos**: a tabela DER-ES já precifica *pontos padrão* (14.07 hidro / 15.18 elétrica) com
  eletroduto e cabo do ramal embutidos (~5 m) — contar pontos resolve os ramais; os
  **aparelhos** (tomada, interruptor, luminária — cap. 18) são somados à parte.
- **Distâncias**: alimentador (quadro→medidor), ramais hidráulicos (prumada→ambiente) e
  coletores de esgoto (banheiro→caixas→rede) usam as distâncias **medidas pela escala** ×
  fator de percurso (1,15–1,25); sem medição, valem defaults declarados como premissa.
- **Estrutura sem projeto**: índices paramétricos (baldrame por metro de parede, 0,045 m³/m²
  de concreto, 85 kg aço/m³) — sinalizada como a maior incerteza (±20%).
- Regras completas em `data/indices-estimativa.json` (editável) e `METODOLOGIA.md`.

### Dados e atualização anual

```
fontes/  XLSX oficiais da Tabela DER-ES (serviços, composições, insumos)
data/    base-der-es.json · mapa-padroes.json · indices-estimativa.json ·
         regras-medicao.json · composicoes-resumo.json · insumos.json
tools/   build_base.py (XLSX→JSON) · parse_caderno.py (Caderno Técnico PDF→regras) ·
         embed_data.py (injeta os JSON no orcamentista.html) ·
         build_sinapi.py (SINAPI_Referência.xlsx → preços da UF) ·
         decompoe_sinapi.py (composição sem preço → MO oficial + material a cotar) ·
         gera_excel.py (orcamento.json → planilha .xlsx de 8 abas)
```

### Segunda tabela de referência: SINAPI

`data/base-sinapi-es.json` traz **8.402 composições + 4.278 insumos** com preço em Vitória/ES
(SINAPI 06/2026, **sem desoneração** — custo direto, BDI 0, mesma natureza da DER-ES, portanto
diretamente comparável). Serve para precificar o que a DER-ES não cobre (vidro temperado, forro
em fibra mineral, guarda-corpo na altura de norma) e para **cruzar preços** dos itens que as duas
tabelas têm.

```bash
python3 tools/build_sinapi.py SINAPI_Referencia_2026_06.xlsx --uf ES --out data/base-sinapi-es.json
```

O extrator lê as abas `ISD` (insumos) e `CSD` (composições), que trazem as 27 UFs lado a lado, e
recupera o código da composição de dentro da fórmula `=HYPERLINK(...)` — o Excel não grava o
resultado dessa fórmula em cache, e uma leitura ingênua devolveria `0` em todas as linhas.

**Composições publicadas sem preço.** Itens como pele de vidro (104099-104103), brises
(104940-104943) e fachada com placas insertadas (105938-105943) existem no SINAPI com a estrutura
completa, mas **sem custo em nenhuma das 27 UFs**: o IBGE não pesquisa o preço desses materiais.
`decompoe_sinapi.py` lê a aba `Analítico` e separa o que tem preço do que não tem, de modo que a
**mão de obra fica oficial** e só o material vai a cotação:

```bash
python3 tools/decompoe_sinapi.py SINAPI_Referencia_2026_06.xlsx 104099 104941 --uf ES
#  104099 fachada cortina stick → MO R$ 59,84/m² (vidraceiro + servente) | material 44970 a cotar
#  104941 brise de alumínio B57 → MO R$ 26,27/m² (serralheiro + auxiliar) | material 45096 a cotar
```

Resultado em `data/sinapi-decomposicoes.json`.

### Orçamento para agente financeiro (100% código de tabela)

Bancos de fomento (BNB/FNE e similares) **não aceitam item por cotação de mercado** — todo serviço
precisa de código de tabela referencial. Quando o projeto especifica acabamento sem equivalente
publicado (pele de vidro, brise, ACM, marcenaria, iluminação decorativa), o caminho é substituir
pelo serviço de tabela mais próximo **declarando o grau de similaridade**:

| Grau | Significado |
|---|---|
| **ALTO** | mesma função e mesmo sistema construtivo — troca sem impacto técnico relevante |
| **MÉDIO** | mesma função, material ou sistema diferente — exige aceite do projetista |
| **BAIXO** | só analogia funcional; o serviço de tabela **não** reproduz o especificado |

O `orcamento.json` aceita as chaves `itens_sinapi` (itens precificados pelo SINAPI, fora do motor
DER-ES) e `substituicoes` (item de projeto → serviços de tabela adotados, com grau e justificativa).
Havendo `substituicoes`, a aba 3 do Excel deixa de ser "complemento a cotar" e passa a ser o
comparativo, fechando com a **diferença de escopo** — o valor que o cliente terá de cobrir com
recursos próprios se executar os acabamentos como projetados. Exemplo real em
`data/exemplo-substituicoes.json`.

> Entregue as duas versões: a codificada, para o banco, e a de custo real, para o cliente. O
> memorial descritivo deve manter sempre a especificação de projeto.

Para entregar o orçamento em Excel formatado (capa/resumo com gráfico por capítulo, planilha por
capítulo, complemento a cotar, curva ABC, memorial com o critério de medição de cada item,
premissas/lacunas e a lista de ambientes):

```bash
python3 tools/gera_excel.py orcamento.json Orcamento.xlsx --refs data
```

Quando sair tabela nova (ou de outro estado/SINAPI no mesmo formato):

```bash
# 1. substituir os XLSX em fontes/
python3 tools/build_base.py          # regenera data/*.json e valida preços dourados
python3 tools/parse_caderno.py --dir cadernos/   # ingere novos Cadernos Técnicos (PDF)
python3 tools/embed_data.py          # re-embute tudo no orcamentista.html
# 2. abrir o app → ⚙️ Parâmetros → Rodar autoteste
```

Base atual: **DER-ES Edificações, Abril/2026** (LABOR/CT-UFES) — 1.340 serviços, Leis Sociais
157,27%, preços em **custo direto** (BDI 0 na tabela; o app aplica o BDI da obra).
Cadernos Técnicos ingeridos: **66 cadernos → 832 regras de medição** (critério + serviços incluídos
por código) — **827 dos 1.340 serviços da tabela (62%)** e **71% dos itens do mapa de padrões**.
Completos: capítulos **03, 04, 05, 06, 11, 13** (100%) e **09, 12, 18, 19, 20** (94–98%). JSONs por
caderno em `data/cadernos/`, consolidados por `tools/merge_regras.py`.

**Auditoria fechada** — nenhum truncamento silencioso (verificado por densidade MB/ficha e padrão de
lacunas, com validação cruzada de 3 cadernos reenviados). O que falta são subcapítulos **sem caderno
publicado no acervo** (02 canteiro, 07 esquadrias metálicas, 08 vidros, 10 impermeabilização, 14.07
pontos hidráulicos, 15.18 pontos elétricos, entre outros) e 39 códigos que a tabela Abr/2026 traz sem
ficha correspondente (tabela mais nova que os cadernos de 2023–2025).
**Nada disso impede orçar**: preço vem da tabela, quantidade vem das fórmulas/NBR — só o texto do
critério fica marcado como "caderno ainda não ingerido" no memorial.
👉 Auditoria completa, lista do que falta e receita de ingestão: **[`COBERTURA.md`](COBERTURA.md)**
(também visível no app em ⚙️ Parâmetros → 📚 Cobertura dos Cadernos Técnicos).

> **Aviso**: estudo indicativo por metodologia paramétrica. Não substitui orçamento executivo
> com projetos completos, nem dispensa responsável técnico.

### 🧩 Skill para o chat do Claude (`.claude/skills/orcamentista-der-es/`)

Todo o sistema também existe como **Agent Skill**: no chat do claude.ai (ou em qualquer sessão
do Claude Code neste repositório), você envia o projeto e o Claude produz **o mesmo orçamento do
app** — a skill embute **as duas bases de preços** (DER-ES e SINAPI-ES), o mapa de padrões, os 832
critérios de medição, o gerador de Excel e um **motor em Python idêntico ao do app**, validado
contra **dois orçamentos dourados**: residencial (custo direto R$ 175.142,06 na casa de 70 m²) e
comercial (academia de 1.886 m² — 109 itens DER-ES + 10 SINAPI, total R$ 5.876.422,49).

Além do orçamento residencial, a skill sabe: escolher **perfil estrutural comercial**, orçar
**cobertura metálica por peso**, buscar nas duas tabelas antes de declarar que um item não existe,
decompor composições SINAPI publicadas sem preço em **mão de obra oficial + material a cotar**, e
montar **orçamento 100% em código de tabela** para agente financeiro, com o grau de similaridade de
cada substituição e a diferença de escopo declarada.

**Instalar no claude.ai:** baixe `dist/orcamentista-der-es.zip` → claude.ai → Configurações →
Capacidades (Capabilities) → **Skills** → carregar o zip → ativar. Depois é só abrir um chat,
anexar a planta e pedir "faça o orçamento desta obra". Requer o recurso de execução de código
ativo (padrão nos planos pagos); sem ele a skill degrada para estimativa aproximada com aviso.

**Atualização anual:** após rodar `build_base.py`/`merge_regras.py`, rode
`python3 tools/build_skill.py` — ele re-sincroniza as referências, roda o autoteste dourado e
regenera o zip.

---

## 🏦 Simulador BNB/FNE (`index.html`)

Simulador de financiamento BNB/FNE com camada de apresentação comercial — pesquisa de práticas
de instituições financeiras, economia comportamental aplicada a crédito e tributação por regime
(Simples, Presumido, Real, SUDENE). Motor validado 100% contra a planilha oficial do BNB
(dias úteis/252, feriados 2017–2060, carência, bônus de adimplência, CET por XIRR).

- **🛠 Simulação técnica** — wizard original com o motor validado.
- **🎯 Apresentação** — 5 telas para conduzir com o cliente (enquadramento, números, dois
  mundos financiar × à vista com efeito tributário, pacotes/comparativo, página de decisão).
- **⚙️ Perfil & Parâmetros** — regime tributário, números de mercado editáveis, autoteste.

Detalhes de método, estratégia tributária embutida (data-base 02/07/2026) e rotina de
atualização anual: ver o cabeçalho do próprio `index.html` e `original/Simulador_BNB_1.html`
(baseline de regressão do motor).

> **Aviso**: estudo indicativo — não é oferta de crédito nem aconselhamento tributário.

---

## Compartilhar com o cliente (ambos os apps)

- **Copiar link**: estado codificado no `#d=` — quem abre vê tudo pré-preenchido.
- **QR** gerado localmente (encoder próprio, sem bibliotecas).
- **Imprimir/PDF**: proposta A4 com capa e assinatura.
- Para o QR apontar para página real: hospedar via GitHub Pages (Settings → Pages → branch).
