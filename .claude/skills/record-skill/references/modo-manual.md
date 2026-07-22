# Modo manual — aprender por documentos

Manuais, apostilas, documentação de sistema e prints também são material de
aprendizado — sozinhos ou complementando vídeos. O produto final é o mesmo do
fluxo de vídeo: SOP + skill gerada + conhecimento acumulado por ferramenta.

## 1. Fontes aceitas e como ler

| Fonte | Como ler |
|---|---|
| PDF com texto | Ferramenta Read (por intervalos de páginas; manuais grandes em capítulos) |
| PDF escaneado (imagem) | Skill `pdf` (OCR) quando disponível; senão, avisar o usuário da limitação |
| DOCX | Skill `docx`/conversão; em último caso pedir exportação em PDF |
| Prints de tela | Read (imagem) + `ocr_frames.py` se forem muitos |
| HTML/TXT | Read direto |

Manuais grandes: leia por capítulos e faça notas incrementais (mesma lógica
dos segmentos de vídeo) — nunca tente segurar o manual inteiro de uma vez.

## 2. Aprender SÓ do manual (sem vídeo)

1. **Mapear**: sumário/estrutura → quais procedimentos o manual ensina, em
   quais capítulos. Manuais costumam ensinar VÁRIOS serviços — cada um segue
   a regra "uma skill = uma tarefa" (com skill mestre se forem muitos, como
   no modo curso).
2. **Extrair por procedimento**: passos, campos e parâmetros (tabelas do
   manual valem ouro — copie-as fielmente), pré-requisitos, exceções e
   mensagens de erro documentadas.
3. **Sintetizar** pelo fluxo normal (SOP + skill + revisão + validação), com
   uma regra de honestidade extra: **passos aprendidos só de manual são
   marcados "não demonstrado em tela"** nas notas, e a skill gerada avisa que
   a interface real pode divergir do manual (manuais desatualizam). Na
   primeira execução real, a skill deve confirmar as telas antes de confiar.
4. Atualizar `aprendizados/ferramentas/<programa>.md` com tudo que o manual
   ensina sobre a ferramenta (campos, variáveis, funções) — mesmo o que não
   virou skill ainda: é conhecimento acumulado para os próximos serviços.

## 3. Manual COMPLEMENTANDO vídeo (o melhor dos dois)

Papéis diferentes e complementares:

- **Vídeo = prática**: a ordem real dos passos, onde clicar, os macetes e
  correções do instrutor, o que ele confere antes de prosseguir.
- **Manual = oficial**: a lista COMPLETA de parâmetros e campos (o vídeo
  costuma mostrar só os usados no exemplo), exceções, limites, tabelas.

Na síntese, cruze passo a passo (mesma mecânica da pesquisa normativa):

1. Cada passo do vídeo é conferido contra o capítulo correspondente do
   manual; o que o manual detalha a mais entra na skill como aprofundamento
   ("o vídeo preencheu 4 campos; o manual documenta os 11 — ver referência").
2. **Divergência** (tela do vídeo ≠ manual, procedimento diferente): registre
   e apresente na revisão — em regra vale o VÍDEO para "como fazer" (é a
   interface real demonstrada) e o MANUAL para parâmetros/regras, mas o
   usuário decide nos casos ambíguos.
3. Trechos relevantes do manual entram nas `references/` da skill gerada,
   citados por capítulo/página; o SOP ganha a coluna de fonte (vídeo, manual
   ou ambos) na base normativa/passos.

## 4. Integração com o modo curso

Manuais entram no inventário do curso como fontes (campo `tipo: "manual"` no
progresso.json) e são processados na posição que fizer sentido (em geral,
depois das aulas que cobrem o mesmo tema, para o cruzamento). A memória do
curso registra a origem de cada aprendizado (vídeo vs manual).

## 5. Revisão e validação

Iguais ao fluxo de vídeo: rascunho apresentado ao usuário (com a lista de
divergências vídeo×manual e os passos "não demonstrados em tela"), validação
em exemplo novo, empacotamento .skill.
