# Proposta FNE · Simulador BNB v2

Simulador de financiamento BNB/FNE com **camada de apresentação comercial** — desenhado a partir de
pesquisa sobre as práticas das melhores instituições financeiras do mundo (arquitetura de proposta
estilo consultoria, economia comportamental aplicada a crédito, UX de simuladores fintech) e sobre a
tributação brasileira por regime (Simples Nacional, Lucro Presumido, Lucro Real e incentivo SUDENE).

**Arquivo único, zero dependências, funciona offline** — abre direto do WhatsApp no celular.

## Arquivos

| Arquivo | O que é |
|---|---|
| `index.html` | O app completo (simulação técnica + apresentação + parâmetros) |
| `original/Simulador_BNB_1.html` | Versão original intacta — baseline de regressão do motor |
| `README.md` | Este guia |
| `src/`, `remotion.config.ts`, `package.json` | Projeto Remotion (template Hello World) — ver seção abaixo |
| `.agents/skills/` | Agent Skills oficiais do Remotion (`npx skills add remotion-dev/skills`) |

## Projeto Remotion (vídeo)

Projeto criado com `npx create-video@latest --hello-world`. Requer Node 18+.

```console
npm install        # instala dependências
npm run dev        # abre o Remotion Studio em http://localhost:3000
npx remotion render HelloWorld out/video.mp4   # renderiza a composição
npm run lint       # eslint + tsc
```

Composições registradas em `src/Root.tsx`:

- `GTKInstitutional` — vídeo institucional da GTK Pré-Moldados (90 s). Roteiro, locução e premissas em `ROTEIRO.md`;
  código em `src/GTK/`; mídias em `public/gtk/media/`.
- `GTK-Cenas/*` — cada cena isolada, para edição no Studio.
- `GTK-Logo/*` — logomarca em PNG (`npx remotion still GTKLogoHorizontal out/logo.png`).
- `HelloWorld` e `OnlyLogo` — template original. Guia do template em `REMOTION.md`.

## Os três modos

1. **🛠 Simulação técnica** — o wizard original preservado (dados da operação, prazos, esquema de
   desembolso, custos do CET) com o motor **validado 100% contra a planilha oficial do BNB**
   (dias úteis/252, feriados 2017–2060, carência, bônus de adimplência, CET por XIRR).
2. **🎯 Apresentação** — 5 telas para conduzir com o cliente:
   - *Enquadramento*: "sua empresa se enquadra no FNE" + régua de custo do dinheiro (ancoragem);
   - *Números*: parcela em destaque, R$/dia, custo total, CET na tela, bônus como conquista a proteger,
     cascata do custo líquido (juros − bônus − economia de IR);
   - *Dois Mundos*: pagar à vista (descapitalizar) × financiar mantendo o caixa aplicado — calculado
     mês a mês sobre o cronograma real, com o efeito tributário do regime do cliente e break-even;
   - *Pacotes & Comparativo*: 3 opções (Essencial/Recomendado★/Expansão), tabela-semáforo FNE ×
     Pronampe × BNDES × banco × caixa próprio, boxes SUDENE e depreciação;
   - *Página de decisão*: resumo executivo (SCQA), payback/TIR/VPL, cenários conservador/provável/
     otimista, sensibilidade ("E se?"), custo de esperar, próximos passos, impressão e link/QR.
3. **⚙️ Perfil & Parâmetros** — perfil tributário do cliente, números de mercado (todos editáveis,
   com data-base visível), módulos opcionais e **autoteste**.

## Estratégia tributária embutida (data-base 02/07/2026)

| Regime | Juros do FNE | Rendimento da aplicação | Break-even (CDI 14,15%) |
|---|---|---|---|
| Lucro Real | dedutíveis — escudo 34% (24% abaixo do adicional) | ~37,1% (34% + PIS/COFINS 4,65%) | financiar se taxa < **13,49%** |
| Lucro Real + SUDENE | escudo 34% até as receitas financeiras; excedente 17,1% (novo) / 15,25% (até 2025) | ~37,1% (benefício NÃO alcança aplicações) | idem |
| Lucro Presumido | sem dedução (mas o empréstimo não gera tributo) | 24–34% (adição integral à base) | < **9,3–10,8%** |
| Simples Nacional | sem dedução; DAS inalterado | IRRF definitivo 22,5%→15% | < **12,0%** |

O módulo *Dois Mundos* aplica essas regras automaticamente conforme o regime selecionado.
A depreciação (Lucro Real) entra no payback do projeto — não na comparação financiar × à vista,
pois o ativo existe nos dois cenários.

## Compartilhar com o cliente

- **Copiar link**: o estado (empresa, operação, perfil) vai codificado no `#d=` da URL — quem abre
  o link vê a simulação pré-preenchida.
- **QR na proposta impressa**: gerado localmente (encoder próprio, sem bibliotecas). Para o QR
  apontar para uma página real, hospede o arquivo — ex.: GitHub Pages neste repositório
  (Settings → Pages → branch) e o `index.html` já responde na raiz.
- **Imprimir/PDF**: botão na tela 5 gera a proposta A4 (capa personalizada, página de decisão com
  campo de assinatura, números, dois mundos, comparativo e premissas).

## Rotina de atualização anual (⚙️ Parâmetros)

1. Taxas FNE do ano: Programação FNE vigente / Resolução CMN de encargos (sai normalmente em julho)
   — as taxas da operação continuam sendo digitadas no modo técnico, como na planilha;
2. CDI, Selic, IPCA, TLP/BNDES, Pronampe, média de crédito PJ (séries do BCB);
3. Orçamento FNE do ano e % para portes prioritários;
4. Ajustar a **data-base** (aparece em todas as telas e na proposta impressa);
5. Rodar o **autoteste** (Parâmetros → Rodar autoteste): regressão do motor contra os valores
   validados + fórmulas fiscais + sanidade do Dois Mundos + QR.

## Notas de método

- O motor `runSim()` é **byte-idêntico** ao da versão original validada; a camada nova apenas o consome.
- Valores dourados da regressão (cenário-padrão): juros c/ bônus R$ 6.881.903,91 · CET 10,407309% /
  8,929488% a.a. · 120 prestações · 1ª parcela R$ 213.801,51 (05/04/2028).
- Simplificações documentadas nos disclaimers: rendimento composto à taxa anual líquida; desembolsos
  nas datas de alocação; IOF (quando ativado) pelo teto de 365 dias.
- Legislação refletida: Lei 10.177/2001 (bônus 15%/25% semiárido), MP 2.199-14 + Lei 14.753/2023 +
  LC 224/2025 (SUDENE 75%→67,5%, protocolos até 2028), Dec. 8.426/2015 (PIS/COFINS 4,65%),
  IN RFB 1.585/2015 (IRRF antecipação/definitivo), LC 123/2006 (Simples), Dec. 12.499/2025 (IOF).

> **Aviso**: estudo indicativo — não é oferta de crédito nem aconselhamento tributário. Condições
> finais são definidas pelo Banco do Nordeste na análise da proposta; efeitos fiscais devem ser
> validados com o contador do cliente.
