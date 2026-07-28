# COBERTURA — Cadernos Técnicos DER-ES no Orçamentista

> Auditoria fechada. Registra **exatamente** o que está incorporado, o que falta, **por que** falta
> e **como completar** no futuro. Gerado a partir da tabela Abr/2026 (1.340 serviços) e dos
> 66 cadernos ingeridos (`data/cadernos/*.json` → `data/regras-medicao.json`).

**Estado:** 832 regras de medição · 827 cruzam com a tabela (**62%**) · **71%** dos itens usados
pelo mapa de padrões (o que o app efetivamente orça).

## O que cada regra faz no sistema

Cada regra traz do Caderno Técnico o **critério de medição** (como se mede) e os **serviços
incluídos no preço** (o que já está embutido, evitando dupla contagem). O app exibe o critério na
aba 📝 Memorial; o motor usa as regras de ouro derivadas delas (ver `METODOLOGIA.md`).
**Importante:** a ausência de regra **não impede orçar** — o preço vem da tabela e a quantidade das
fórmulas/NBR; apenas o texto do critério fica marcado como "caderno ainda não ingerido".

## Cobertura por capítulo

| Cap. | Nome | Com regra | Total | % |
|---|---|---:|---:|---:|
| 01 | Serviços preliminares | 64 | 81 | 79% |
| 02 | Instalação do canteiro de obras | 0 | 39 | 0% |
| 03 | Movimento de terra | 17 | 17 | **100%** |
| 04 | Estruturas | 47 | 47 | **100%** |
| 05 | Paredes e painéis | 20 | 20 | **100%** |
| 06 | Esquadrias de madeira | 47 | 47 | **100%** |
| 07 | Esquadrias metálicas | 0 | 12 | 0% |
| 08 | Vidros e espelhos | 0 | 6 | 0% |
| 09 | Cobertura | 25 | 26 | 96% |
| 10 | Impermeabilização | 0 | 7 | 0% |
| 11 | Tetos e forros | 6 | 6 | **100%** |
| 12 | Revestimento de paredes | 15 | 16 | 94% |
| 13 | Pisos internos e externos | 37 | 37 | **100%** |
| 14 | Instalações hidro-sanitárias | 55 | 100 | 55% |
| 15 | Instalações elétricas | 158 | 290 | 54% |
| 16 | Outras instalações | 99 | 175 | 57% |
| 17 | Aparelhos hidro-sanitários | 105 | 122 | 86% |
| 18 | Aparelhos elétricos | 40 | 41 | 98% |
| 19 | Pintura | 28 | 33 | 85% |
| 20 | Serviços complementares externos | 60 | 63 | 95% |
| 21 | Serviços complementares internos | 4 | 10 | 40% |
| 22 · 31 · 99 | Apoio, encargos, serviços auxiliares | 0 | 145 | 0% |

Os capítulos que compõem o esqueleto de uma residência (03, 04, 05, 06, 09, 11, 12, 13, 18, 19, 20)
estão **completos ou quase**.

## O que falta — e por quê

### A) Subcapítulos sem caderno na pasta de origem (474 itens)
Não é perda de dados nem falha de extração: **não existe PDF desses subcapítulos** no acervo
enviado. Prioridade para quem for buscá-los no site do DER-ES:

**Alta (toda obra residencial usa):**
`14.07` Pontos hidro-sanitários (14) · `15.18` Pontos elétricos NR-10 (17) · `14.01` Fossas/filtros (4) ·
`14.02` Entrada de água (4) · `14.21` Caixas de PVC/ralos/sifões (16) · `15.17` Padrão de entrada
ESCELSA (13) · `15.19` Quadros c/ barramento (5) · `15.01` Padrão de entrada (2) · `14.09` Tubulação
de ligação de caixas (6)

**Capítulos inteiros:**
`07.11` Grades e portões · `07.17` Esquadrias metálicas · `07.18` Revisões · `08.01` Vidros ·
`08.02` Espelhos · `10.01` Imperm. caixas d'água · `10.02` Imperm. lajes/baldrames · `10.03` Imperm.
fossas · `02.03` Tapumes/barracões · `02.07`/`02.08` Canteiro

**Conforme o tipo de obra:**
`15.08` Instalações aparentes (34) · `15.07` Envelopamento · `15.09` Composições intermediárias ·
`16.01` Telefone · `16.03` Pára-raios · `16.07` Depósito de gás · `16.10` Climatização · `21.03` Diversos internos

**Administrativos (raramente orçados):**
`01.05` Locação · `01.08` Mensalistas · `18.04` Postes · `22.08` Veículo · `31.08` EPI ·
`31.09` Ferramentas · `15.22` Montagem TTA/PTTA (38) · `99.01`/`99.02` Serviços auxiliares (121)

### B) Cadernos ingeridos 100%, mas que não documentam todos os códigos (39 itens)
A tabela de preços (Abr/2026) é **mais recente que os cadernos** (2023–2025): o DER-ES adicionou
serviços à tabela sem publicar as fichas. Não há o que recuperar.

| Subcap. | Tenho | Códigos sem ficha no caderno |
|---|---|---|
| 17.05 Outros aparelhos | 19/35 | 170507–170512… |
| 15.14 Fios e cabos | 29/36 | 151441–151447 (cabos não halogenados) |
| 20.07 Quadra de esportes | 17/20 | 200703, 200704, 200725 |
| 15.06 · 19.01 · 19.06 | −2 cada | espalhados |
| 09.03 · 12.02 · 14.15 · 15.03 · 16.06 · 17.06 · 19.04 | −1 cada | espalhados |

Curiosidade inversa: `15.20` tem **25 fichas para 24 códigos** — o caderno traz 152044, que não
consta da tabela de preços.

## Verificação de integridade (auditoria de truncamento)

Todos os 66 cadernos foram auditados por dois critérios independentes:

1. **Densidade (MB por ficha)** — calibrada por 9 arquivos reenviados divididos e confirmados
   íntegros (faixa 0,18–0,53 MB/ficha). **Nenhum arquivo ficou fora da faixa** (os acima de 0,65 são
   PDFs de ficha única, onde a capa infla a razão, e todos cobrem 1/1 do seu subcapítulo).
2. **Padrão das lacunas** — se um arquivo tivesse sido cortado, os códigos faltantes estariam
   **todos no fim** do subcapítulo. Só o `15.14` apresentou esse padrão, e a inspeção do texto
   confirmou que o PDF **termina na Bibliografia** — não houve corte.

**Validação cruzada:** três cadernos lidos na primeira extração (`1703`, `Etapa 19 Pintura`,
`20.07`) foram reenviados depois e bateram **exatamente** (50, 28 e 17 fichas) — o método de
extração inicial não perdeu conteúdo.

**Conclusão: nenhum truncamento silencioso.** Não há conteúdo perdido dentro dos arquivos recebidos.

## Limites de transporte encontrados (para referência futura)

| Via | Limite prático |
|---|---|
| Conector do Google Drive (download bruto) | ~3,5 MB por arquivo |
| Leitura de texto do Drive | ~156 mil caracteres (corta cadernos longos) |
| **Anexo no chat** | **~10 MB — sem limite de conteúdo, lê 100% via pdftotext** |

**Receita que funcionou** para os 6 cadernos grandes: dividir no Pré-Visualização (⌘P → intervalo de
páginas → PDF → Salvar como PDF) em partes < 10 MB e anexar no chat.

## Como incorporar um caderno novo

```bash
# 1. anexar o PDF no chat (dividido em partes < 10 MB se necessário)
# 2. extrair, gerar o JSON no schema de data/cadernos/ e então:
python3 tools/merge_regras.py data/cadernos   # consolida + valida contra a base
python3 tools/embed_data.py                   # re-embute no orcamentista.html
python3 tools/build_skill.py                  # re-sincroniza e regera o zip da skill
# 3. abrir o app → ⚙️ Parâmetros → Rodar autoteste (deve dar 11/11)
```

O schema de cada JSON de caderno está em `data/cadernos/*.json`:
`{arquivo, caderno, truncado, fichas:{codigo:{d,u,caderno,atualizacao,aplicacao,incluidos,criterio,normas[]}}}`
