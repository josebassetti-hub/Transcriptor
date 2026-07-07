# Fontes de cotação de mercado (preços para projetos reais)

Regra: preço de projeto real é SEMPRE recotado — os valores dos exemplos do professor são
referência didática (ver abrangência em `coeficientes-tecnicos.json`). Toda cotação usada
num projeto carrega: fonte, URL/print, data e região.

## Fontes conhecidas até agora

| Fonte | O que cota | Como usar | Status |
|---|---|---|---|
| Site de cotações usado pelo professor | (a identificar nos vídeos) | HTML salvo no Drive: "Site para pesquisar algumas cotacoes.html"; há `cepea.png` nos assets — forte indício de CEPEA/ESALQ | pendente Fase 2 |
| CEPEA/ESALQ (cepea.esalq.usp.br) | boi gordo, bezerro, leite, café, grãos | indicadores diários/mensais por praça | usar quando confirmado |
| CONAB (conab.gov.br) | custos de produção, preços agropecuários | planilhas oficiais por UF | alternativa oficial |
| Agrolink / Scot Consultoria | reposição de gado por praça | conferência secundária | opcional |
| Cotação local (cooperativa/frigorífico/laticínio da região do cliente) | preço efetivamente praticado | pedir ao usuário/cliente | preferida pelo banco quando documentada |

## Processo de cotação num projeto real
1. Identificar os itens com `validade` vencida ou abrangência ≠ região do cliente.
2. Cotar em ≥1 fonte oficial + (se possível) 1 local; registrar as duas.
3. Atualizar `coeficientes-tecnicos.json` via `engines/coeficientes.atualizar()` —
   append-only (o valor antigo desce para o histórico, nunca some).
4. Divergência grande entre fontes (>15%) → decisão humana registrada no caso.
