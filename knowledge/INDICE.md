# Índice da base de conhecimento — "que pergunta → qual arquivo"

Mapa de consulta para qualquer sessão/agente novo. Regra geral: **fonte na mão > memória**;
todo número tem selo (CONFIRMADO/PROVÁVEL/INCERTO) e origem (vídeo+mm:ss ou documento).

| Pergunta | Consulte | Observação |
|---|---|---|
| O que é este projeto? Qual o plano? | `PLANO.md` | plano v2 + adições v2.1 aprovados |
| Como extrair conhecimento dos vídeos? | `PROTOCOLO-EXTRACAO.md` | OBRIGATÓRIO na Fase 2 (pesquisa original: `protocolo-original.md`) |
| Onde está cada arquivo do Drive (fileIds)? | `inventario-drive.md` | inclui limites do conector |
| Qual o estado do pipeline por vídeo? | `status.json` | baixado→áudio→frames→blocos→visão |
| Que normas/manuais o professor cita? | `fontes-citadas.md` | Etapa 0 do protocolo; conferir vigência |
| O que o curso NÃO cobre? | `anti-escopo.md` | fora disso: pesquisar/cotar/perguntar, nunca extrapolar em silêncio |
| Valor de coeficiente técnico (produtividade, preço, índice) | `coeficientes-tecnicos.json` via `engines/coeficientes.py` | operacional, append-only; goldens usam `tests/fixtures/` |
| Regras de juros FNE / conservação / impostos | `engines/regras_fixas.py` + `curso/00-apresentacao-curso.md` | taxas mudam por resolução — conferir vigência |
| Como funciona o relatório de capacidade de pagamento? | `curso/relatorio-capacidade-pagamento.md` | 12 anos; % utilização < 60% (confirmar) |
| Estrutura de custos de um projeto | `curso/relatorio-custos-despesas.md` | regras 2,5% e 0,2% |
| Evolução de rebanho / indicadores de leite | `curso/relatorio-bovinocultura-leite.md` + `engines/rebanho_leite.py` | fórmulas com selo |
| Documentos que o cliente precisa | `curso/checklist-documental.md` | dossiê cadastro/imóvel/operação |
| Modelo de orçamento de benfeitoria | `curso/orcamento-deposito.md` | golden test |
| Georreferenciamento de glebas | `curso/coordenadas-pastagem.md` | KML/coordenadas |
| Transcrição de uma aula | `transcricoes/<video>.md` | ⚠️ = baixa confiança; blocos em `transcricoes/blocos/` |
| O que aconteceu na tela da aula N? | `frames/<video>-tabela-mestra.md` | espinha dorsal por vídeo |
| Ver as telas da aula sem abrir o vídeo | `frames/<video>-contatos/` | folhas de miniaturas com timestamps |
| Evidência de um item duvidoso | `frames/<video>-evidencias/` | pares antes/depois de PROVÁVEL/INCERTO |
| A extração foi completa/íntegra? | `frames/<video>-manifesto.jsonl` | cada frame com hash e motivo de descarte |
| Entendimentos livres do analista | `frames/<video>-notas.md` | toda nota com mm:ss + selo |
| O que foi descartado como conversa fiada? | `descartes.md` | recuperável, com tempo |
| Casos já resolvidos (professor + reais) | `casos/` | raciocínio por analogia; pseudonimizado |
| Onde cotar preços de mercado | `mercado/fontes-cotacao.md` | com data de cada cotação |
| Como decidir como o professor decide | `manual-metodologia/principios-decisorios.md` | heurísticas com citação (Fase 2) |
| Passo a passo completo da análise de vídeos (do bruto ao auditável) | `manual-metodologia/passo-a-passo-analista.md` | 29 passos em 6 etapas; roteiro da analista (Fase 1-2) |
| Qual modelo usar em cada etapa? | `PLANO.md` (Adendo v2.2) | leitura de números/síntese = topo de linha, nunca menos |
| Estrutura da ferramenta do professor | `automatizador-estrutura.md` | após dissecação (Fase 1) |
| Configurar Excel para as planilhas do professor | `curso/tutorial-configuracao-excel.md` | Excel legado/macros |

Arquivos ainda não criados aparecem na tabela como destino planejado — se não existir,
a fase correspondente ainda não rodou (ver `status.json` e `PLANO.md`).
