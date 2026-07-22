# Modo curso — vários vídeos, uma skill consolidada

Use este protocolo quando o material for um curso/treinamento com várias
aulas (horas de vídeo), não um único procedimento gravado. O princípio: cada
vídeo é processado sozinho (o disco e o contexto não comportam tudo de uma
vez), mas o **aprendizado acumula** numa memória do curso — e a consolidação
final transforma essa memória nas skills definitivas.

## Limites práticos (para informar o usuário)

Não há limite rígido de duração ou tamanho por vídeo. Os limites reais:

- **Disco da sessão**: processar UM vídeo por vez e apagar os brutos depois.
- **Tempo de transcrição** (por hora de vídeo, nos 4 CPUs típicos):
  `small` ≈ 8–15 min; `medium`/`large-v3-turbo` ≈ 30–60 min. Um curso de 22 h
  leva de ~4 h (small) a ~15–20 h (turbo) só de transcrição — divida o
  trabalho em várias sessões usando o checkpoint (abaixo).
- **Contexto de leitura**: vídeos são assistidos em segmentos de ~10–15 min
  (o fluxo normal já faz isso).
- **Upload**: arquivos grandes chegam melhor pelo Google Drive (atenção ao
  limite de payload das ferramentas MCP para arquivos de centenas de MB — se
  o download falhar, peça link direto ou upload); a aula não precisa ser
  recortada pelo usuário — divida aqui sem reencodar:
  `ffmpeg -i aula.mp4 -c copy -f segment -segment_time 1500 -reset_timestamps 1 parte%02d.mp4`
  (corta em keyframes: as partes saem com duração aproximada, não exata —
  normal e inofensivo).

## 1. Inventário e ordem

Tudo de `aprendizados/` fica na **raiz do projeto** (persiste entre sessões)
— NUNCA no scratchpad, que é apagado quando a sessão termina; a retomada do
curso depende disso.

1. Liste todos os materiais (pasta do Drive ou uploads) com nome e duração —
   **vídeos E manuais/PDFs** do curso (manuais entram com `"tipo": "manual"`
   e são processados pelo modo-manual, em geral após as aulas do mesmo tema).
2. Proponha a ordem pela numeração dos arquivos ("Aula 01", "Módulo 2.1"...).
3. **Confirme a ordem com o usuário antes de começar** — ambiguidade de
   ordem nunca se resolve por palpite.
4. Crie `aprendizados/<curso>/progresso.json`:

```json
{
  "curso": "nome do curso",
  "videos": [
    {"arquivo": "aula-01.mp4", "modulo": "01", "status": "pendente",
     "continuidade": null}
  ]
}
```

O checkpoint permite retomar em outra sessão sem repetir nada: ao entrar no
modo curso, leia o progresso.json primeiro e continue do próximo `pendente`.

## 2. Processar um vídeo por vez

Para cada vídeo, na ordem confirmada:

1. Baixe APENAS este vídeo para o scratchpad.
2. Rode o pipeline normal do SKILL.md (transcrever + quadros + OCR +
   assistir + pesquisa normativa), **lendo antes a memória do curso** (item 3)
   para assistir a aula com o contexto das anteriores.
3. Salve em `aprendizados/<curso>/modulos/NN-<nome>/`: as notas estruturadas
   da aula (o que ensina, passos, decisões, citações) + transcript + telas-chave.
4. Atualize a memória do curso e o progresso.json (status `concluido`).
5. **Apague o vídeo, o áudio e os quadros brutos** antes do próximo — só as
   notas e telas-chave ficam.
6. **Checkpoint**: os arquivos em `aprendizados/` (raiz do projeto) SÃO o
   checkpoint. Se o diretório for um repositório git E o usuário tiver
   concordado com commits, faça commit após cada módulo (proteção extra);
   sem git ou sem acordo, apenas mantenha os arquivos — nunca commite por
   conta própria. Se a sessão cair no meio de 22 h de curso, nada se perde.
   Atualize também `aprendizados/ferramentas/<programa>.md` (conhecimento
   acumulado por ferramenta — ver SKILL.md, etapa 5) a cada aula.

## 3. Memória do curso

`aprendizados/<curso>/memoria-do-curso.md` — atualizada após CADA aula:

```markdown
# Memória — [curso]
## Procedimentos ensinados até aqui
[um bloco por procedimento: nome, módulos que o ensinam, estado (completo/em andamento)]
## Glossário
[termos, sistemas, siglas que o instrutor usa — com o significado dado por ele]
## Regras e decisões acumuladas
[critérios narrados, com o módulo de origem]
## Referências cruzadas e correções
["módulo 07 ALTERA o ensinado no módulo 02: ..."]
## Dúvidas em aberto
[o que ainda não ficou claro — aulas futuras podem responder]
```

## 4. Detecção de continuidade

Ao assistir cada aula, decida explicitamente: **continua um procedimento da
memória ou inicia assunto novo?** Quatro sinais, nesta ordem:

1. **Numeração dos arquivos** — a ordem confirmada no inventário.
2. **Fala do instrutor** — "na aula passada...", "continuando de onde
   paramos", "como vimos no módulo anterior" ⇒ continuação; "agora vamos
   para outro assunto", "novo módulo" ⇒ assunto novo.
3. **Estado da tela** — a aula abre no MESMO sistema/tela/documento em que a
   anterior terminou (compare o primeiro quadro com a última tela-chave do
   módulo anterior) ⇒ continuação; sistema novo ou slide de título ⇒ novo.
4. **Comparação com a memória** — o conteúdo encaixa em qual procedimento já
   listado? Se em nenhum, é novo.

Grave o veredito nas notas do módulo e no progresso.json
(`"continuidade": "continua modulo-03"` ou `"novo_procedimento"`). Se uma
aula CONTRADIZ uma anterior (tela mudou, regra atualizada), vale o ensinado
por último — registre a correção na memória e avise na revisão final.

## 5. Consolidação final

Com todos os vídeos processados, sintetize a partir da memória + notas:

- O curso ensina **um procedimento grande**? → UMA skill, com o passo a passo
  consolidado no SKILL.md e o detalhe de cada etapa em `references/` (um
  arquivo por módulo/etapa — divulgação progressiva).
- Ensina **vários procedimentos distintos**? → uma skill por procedimento
  (regra "uma skill = uma tarefa") + uma **skill mestre do curso**, cuja
  description cobre o tema geral e cujo corpo descreve o mapa do curso e
  aponta qual skill usar para cada serviço.
- Em ambos os casos: rascunho revisado com o usuário (apresente o mapa de
  procedimentos e as correções entre aulas), validação em exemplo novo, SOP
  geral do curso em `aprendizados/<curso>/SOP-curso.md`.

## Recomendações para o usuário

- Mantenha os arquivos como o curso já divide (aulas de 5–40 min são o
  formato ideal — não precisa juntar nem recortar).
- Envie por Google Drive (uma pasta com todas as aulas numeradas).
- Comece uma sessão dizendo "continue o curso X" — o progresso.json faz a
  retomada automática.
