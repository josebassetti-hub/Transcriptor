# Protocolo de pesquisa normativa

Quando o instrutor cita uma norma (lei, decreto, medida provisória, resolução,
portaria, instrução normativa, circular, súmula, NBR, edital, manual oficial),
ele quase sempre resume. O trabalho aqui é buscar o texto oficial, confirmar
que é o documento certo e acoplar o detalhe ao aprendizado — a skill gerada
fica muito melhor citando o artigo exato do que repetindo o resumo falado.

## 1. Detectar citações

Durante a leitura do transcript e dos quadros (inclusive `frames_text.json` —
normas costumam aparecer na tela em títulos de sistema, PDFs abertos e
rodapés), anote cada menção com:

- tipo + número + ano (ex.: Lei 14.133/2021; Resolução CMN 4.883/2020)
- órgão emissor, quando dito ou visível
- **o que o instrutor afirmou sobre a norma** (é contra isso que o texto
  oficial será conferido)
- timestamp da menção

Atenção à transcrição de números falados: "lei quatorze mil cento e trinta e
três" = 14.133; "resolução quarenta e oito oitenta e três" = 4.883. Em caso de
dúvida sobre o número transcrito, a pesquisa do passo 2 resolve (o resultado
tem que bater com o assunto do vídeo).

## 2. Pesquisar o documento

Use WebSearch com o identificador exato e o contexto:

- `Lei 14.133/2021 licitações planalto`
- `Resolução CMN 4.883 FNE site:bcb.gov.br`
- `Instrução Normativa RFB 2.055 restituição site:gov.br`

Citação vaga sem número ("a lei de licitações", "a norma do Banco Central")
só pode ser resolvida se o contexto tornar a identificação inequívoca (assunto
+ órgão + data). Se restar qualquer dúvida entre duas normas possíveis, NÃO
escolha por conta própria — leve a ambiguidade para a etapa de revisão com o
usuário.

## 3. Validar a fonte (hierarquia de confiança)

Somente fonte oficial serve como fonte de registro:

| Tipo de norma | Fonte oficial |
|---|---|
| Leis, decretos, MPs federais | `planalto.gov.br` (texto consolidado, com alterações) ou `normas.leg.br` |
| Resoluções, portarias, INs federais | `in.gov.br` (DOU) ou site do órgão emissor em `gov.br` (ex.: `bcb.gov.br` para CMN/Bacen, `gov.br/receitafederal`, `bnb.gov.br` para normas do FNE) |
| Normas estaduais/municipais | Diário oficial e portais `.gov.br`/`.leg.br` do próprio ente |
| Jurisprudência/súmulas | Tribunais em `.jus.br` |

Agregadores (JusBrasil, blogs jurídicos, sites de contabilidade) podem ajudar
a LOCALIZAR a norma e entender o contexto, mas nunca são a fonte final — o
texto incorporado ao aprendizado tem que vir do domínio oficial.

Prefira sempre o **texto consolidado/compilado** (que incorpora alterações
posteriores) ao texto original de publicação, e registre qual dos dois é.

## 4. Confirmar que é O documento

Antes de incorporar, confira contra as anotações do passo 1:

- [ ] número + ano + órgão emissor batem com a citação
- [ ] a ementa trata do assunto que o instrutor mencionou
- [ ] a norma está vigente (não revogada; se alterada, usar o consolidado)
- [ ] o trecho que o instrutor resumiu de fato existe no texto

Se o texto oficial **divergir** do que foi falado (prazo diferente, artigo
renumerado, norma revogada por outra), a divergência é um achado valioso:
registre-a e apresente na revisão — o documento oficial prevalece no conteúdo
da skill, mas com nota explicando o que o instrutor disse.

## 5. Baixar e destilar

- Baixe o texto com WebFetch da URL oficial.
- **Texto integral** → `aprendizados/<video>/normas/<identificador>.md`, com
  cabeçalho: nome completo, ementa, URL oficial, data de acesso, se é texto
  consolidado ou original.
- **Extrato relevante** → `references/normas/<identificador>.md` da skill
  gerada: apenas os artigos/incisos que tocam o procedimento ensinado, cada um
  com sua referência exata (art., §, inciso). Divulgação progressiva: o corpo
  do SKILL.md gerado cita a norma e aponta para o extrato — nunca cole lei
  inteira no corpo.
- Nos passos da skill gerada, ancore a regra na fonte: "o limite de R$ X vem
  do art. 75, I, da Lei 14.133/2021 (ver references/normas/lei-14133-2021.md)".

## 6. Limitações e fallbacks

- **Norma paga (NBR/ABNT e similares)**: o texto é licenciado — NÃO baixe de
  fonte pirata. Registre a citação, o que o instrutor disse, e onde adquirir
  (abntcatalogo.com.br); peça ao usuário o PDF se ele tiver licença e
  incorpore a partir dele.
- **Domínio oficial bloqueado pela política de rede** (WebFetch retorna
  403/erro de proxy): não tente contornar. Registre a citação + URL oficial
  como lacuna e informe o usuário na revisão: ele pode liberar o domínio na
  configuração de rede do ambiente (ex.: planalto.gov.br, normas.leg.br,
  in.gov.br, bcb.gov.br, bnb.gov.br, www.gov.br) ou anexar o PDF/HTML da
  norma na conversa.
- **Norma não encontrada em fonte oficial**: pode ser norma interna da
  empresa (manual, política interna) — nesse caso peça o documento ao
  usuário; documentos internos não estão na internet.

## 7. Na revisão com o usuário

Apresente a lista completa: normas encontradas e incorporadas (com fonte),
divergências entre fala e texto oficial, citações ambíguas não resolvidas e
normas inacessíveis (pagas/bloqueadas/internas) aguardando documento.
