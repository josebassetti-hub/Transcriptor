# Regras de autoria para a skill gerada

Destilado das práticas oficiais da Anthropic (docs de Agent Skills best
practices e skill-creator). Aplique tudo isto ao escrever a skill que nasce
do vídeo.

## Estrutura

```
nome-do-procedimento/
├── SKILL.md          (obrigatório: frontmatter YAML + instruções)
├── scripts/          (opcional: código determinístico)
├── references/       (opcional: docs/prints carregados sob demanda)
└── assets/           (opcional: templates usados na saída)
```

Divulgação progressiva em três níveis: o par name+description fica sempre em
contexto; o corpo do SKILL.md só entra quando a skill dispara; os arquivos de
references/ só quando lidos. Portanto: corpo enxuto (<500 linhas, ideal bem
menos), detalhes pesados em references/ com no máximo **um nível** de
profundidade a partir do SKILL.md.

## Frontmatter

- **name**: minúsculas-com-hífens, <64 caracteres, de preferência no padrão
  ação/gerúndio (`emitindo-nota-fiscal`, `cadastro-cliente-sistema-x`).
  **Uma skill = uma tarefa** — se o vídeo ensina dois procedimentos
  independentes, gere duas skills.
- **description**: em terceira pessoa, ≤1024 caracteres, dizendo (1) o que a
  skill faz e (2) **quando disparar**, com frases-gatilho explícitas que o
  usuário realmente digitaria. Skills tendem a subdisparar, então seja
  "empurrado": liste variações, sinônimos e contextos, como fazem as demais
  skills deste repositório.

## Corpo

- Imperativo, direto, terminologia consistente (escolha um nome para cada
  tela/campo e use sempre o mesmo).
- Explique o **porquê** das regras em vez de empilhar MUSTs — o modelo segue
  melhor instruções que entende. As decisões narradas no vídeo ("faço X
  porque Y") viram exatamente isso.
- Inclua exemplos concretos de entrada/saída quando o procedimento tiver
  formatos definidos (nomes de arquivo, formato de resposta, template).
- Fluxos multi-etapa ganham checklist numerado; pontos de decisão viram
  condicionais explícitas ("Se aparecer X → siga o caminho A").
- Grau de liberdade proporcional à fragilidade: tarefa flexível → instruções
  em texto; sequência exata e crítica → passo a passo rígido ou script em
  scripts/.
- Só inclua contexto que o Claude não teria sozinho. Pergunte de cada frase:
  "o modelo realmente precisa disto?"
- Nada de informação volátil (datas de validade, versões) sem necessidade;
  descreva telas pelo texto visível, não por posição ("terceiro botão azul").

## Validação

Antes de dar a skill por pronta: 2–3 prompts de teste realistas (como um
usuário de verdade pediria, com contexto e detalhes) rodados em subagente com
a skill disponível. A skill deve disparar e guiar a tarefa corretamente.
