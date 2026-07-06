# Fábrica de Projetos de Crédito Rural BNB/FNE

## O que é este repositório

Sistema em construção que absorve a metodologia de um curso de elaboração de projetos de
crédito rural para o Banco do Nordeste (BNB/FNE) e a transforma em uma fábrica de projetos
operada por agentes: o usuário fornece os dados do cliente, os agentes calculam, preenchem
as planilhas e entregam o pacote pronto para revisão humana e protocolo no banco.

O plano completo e aprovado está em `knowledge/PLANO.md`. Leia-o antes de qualquer trabalho.
A extração de conhecimento dos vídeos segue OBRIGATORIAMENTE o `knowledge/PROTOCOLO-EXTRACAO.md`
(protocolo do usuário: pares antes/depois, 3 gavetas, escala de confiança, tabela-mestra,
carimbo de tempo em tudo, professor = fonte canônica).

## Idioma e usuário

- Todo o conteúdo, commits e conversas em **português (pt-BR)**.
- O usuário NÃO é programador — explique em linguagem simples, entregue coisas que funcionam
  sem configuração manual.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `index.html` | Simulador financeiro BNB/FNE já validado (motor `runSim()`, `xirr()`, dias úteis, CET, bônus adimplência). FONTE DA VERDADE financeira — reusar, não reinventar |
| `knowledge/` | Base de conhecimento derivada do curso (commitada) |
| `knowledge/curso/` | Destilações dos PDFs/planilhas didáticos |
| `knowledge/transcricoes/` | Transcrições das vídeo-aulas com timestamps |
| `knowledge/frames/` | Eventos extraídos dos frames dos vídeos ("min M: preenche célula X da aba Y") |
| `materiais/` | Arquivos brutos baixados do Drive — **fora do git** (.gitignore), direitos do professor |
| `pipeline/` | Scripts de ingestão: download do Drive, extração áudio/frames, transcrição |
| `engines/` | Motores de cálculo em Python (Fase 3): custeio pecuário, investimento, evolução de rebanho, capacidade de pagamento |
| `templates/` | Templates Excel/documentos para preenchimento |
| `tests/` | Golden tests contra os exemplos do professor |

## Fatos operacionais deste ambiente

- Conector Google Drive (MCP) disponível: `read_file_content` (PDF/XLSX→texto),
  `download_file_content` (base64, só serve para arquivos pequenos, limite ~70KB),
  `create_file` (upload de resultados). A conexão oscila — se cair, aguarde reconectar
  (ToolSearch) e retente.
- Vídeos do curso (`1.mov`–`5.mov`, 1–2,5GB cada) estão na pasta do Drive
  `1AFEY8E5dw_hJ6WVdcDCyk7S3JGLqDePn`; grandes demais para o conector. Rota A: usuário
  libera `drive.google.com`, `drive.usercontent.google.com`, `*.googleapis.com` na política
  de rede do ambiente e compartilha por link → `pipeline/download_drive.py`.
- Proxy bloqueia downloads do github.com (403 em raw); PyPI é direto (liberado).
  ffmpeg vem de `imageio-ffmpeg` (binário dentro do wheel) — NÃO usar static-ffmpeg.
- 4 CPUs, 15GB RAM, ~30GB disco. Transcrição: faster-whisper int8, modelo `small` como
  padrão (2-4x tempo real), `medium` só se a qualidade exigir.

## IDs dos arquivos-chave no Drive

| Arquivo | fileId |
|---|---|
| Automatizador para Projetistas V1.4 (XLSM 1,4MB) | `1ylbMcTX7bzgOJpk_xU7O15CuxF2gvNSi` |
| Crédito Rural - Apresentação.pdf (1,8MB) | `1FRDJRz8Y9yxBHwM527o7pEDN9NkwlY7R` |
| Exemplo investimento rural.INVRUR | `1ED5KYsL_jQ7oKftrmNkWWrsv-yYRcKPF` |
| Exemplo recria e engorda.CUSTEIOPECUARIO | `1WFTMradbIqLDI2MDX-x4tS6f6NROoX0G` |
| Exemplo com ração.CUSTEIOPECUARIO | `1PijXUJpwWMEV7fJuodBkxveV8OKDPOvW` |
| planilha investimento rural-curso.INVRUR | `1VQsWa0Q0ywf50bs-a3Nmcsxxrlcl8gu4` |
| Check List Externo - Rural V3.2.zip | `1B_Ja9V9D32aLauBHiW0BgAwcpvMcPcXu` |
| Capacidade de pagamento.pdf | `1Tui4Rwhi9Py_-RupxAlFsZhFFBvs5yBm` |
| Custos e despesas.pdf | `1PqeB6QScDlWStqd_SUybgD8_3hNsB_cy` |
| Evolução rebanho de leite.pdf | `17Q2BonU8AB_hAQb8XMCBppvNNt2rkNOI` |
| Vídeos 2–5 (.mov) | `1J2FsUxvcQwOZc5dU38PuBN1adbEwTOo0`, `1dLqzlFCOqGm17qaWAw-cHuqzT3EowVur`, `1MTbh_m6LJiJFp0ws4zO81RCSkzqNPEZS`, `1ZRd6gq5e_CgB9uNznz-GOGM_DeED3F8_` |

(Inventário completo com todos os IDs: `knowledge/inventario-drive.md`)

## Fatos do domínio já estabelecidos

- Os `.INVRUR`/`.CUSTEIOPECUARIO` são arquivos de salvamento da ferramenta
  **"Planilha Investimento Rural – Procedimento Simplificado"** do professor.
- Relatório de capacidade de pagamento: 12 anos de projeção, estrutura em
  `knowledge/curso/relatorio-capacidade-pagamento.md`; % de utilização sempre < 60%
  no exemplo (regra a confirmar nos vídeos).
- Ordem de validação dos motores: 1º custeio pecuário (2 exemplos golden), 2º investimento
  rural (café/benfeitorias), 3º evolução de rebanho de leite.

## Salvaguardas (design)

- Saída dos agentes = **minuta técnica**; revisão humana obrigatória antes do banco.
- NUNCA automatizar login/envio nos sistemas do BNB.
- Material bruto do curso não vai para o git nem é redistribuído.
- Todo número gerado deve ser rastreável: regra → vídeo+timestamp ou documento de origem.

## Git

- Branch de trabalho: `claude/rural-credit-automation-j4fn5s` (única — não criar outras).
- Commits em português descrevendo a fase (ex.: "Fase 0: ...").

## ESTADO ATUAL (2026-07-06) — leia isto primeiro em sessão nova

- ✅ Fase 0 (fundação), 0b (correções da revisão) e 3.1 (motores financeiro/leite/regras,
  15 testes verdes + 1 xfail) CONCLUÍDAS. Histórico LGPD-limpo (não reintroduzir CPFs).
- ⏳ PRÓXIMA AÇÃO = Fase 1 (Rota A). O usuário JÁ liberou os domínios na política de rede
  do ambiente (drive.google.com, drive.usercontent.google.com, *.googleapis.com,
  huggingface.co, cdn-lfs.huggingface.co, *.hf.co) e JÁ compartilhou a pasta do curso por
  link — mas a liberação só vale para sessões criadas DEPOIS dela (a sessão anterior ficou
  presa na política antiga).
- Sequência da Fase 1 (detalhes em knowledge/PLANO.md):
  1. Testar rede: `curl -sI https://drive.google.com` (esperar 3xx/200; 000 = ainda
     bloqueado → avisar o usuário para conferir a política e recriar a sessão).
  2. `pip install --user gdown faster-whisper imageio-ffmpeg openpyxl oletools pillow imagehash numpy pytest`
     (container novo não herda os pacotes da sessão anterior).
  3. Baixar BINÁRIOS primeiro: `python3 pipeline/download_drive.py` (baixa binários médios
     e vídeos; IDs já no script). Confirmar se existe `1.mov` na pasta compartilhada
     (usuário nunca respondeu; listar com gdown --folder se preciso).
  4. Dissecar binários (tarefa pendente): Automatizador XLSM via openpyxl+olevba; formato
     .INVRUR → knowledge/automatizador-estrutura.md; decide gate de escrita (plano v2).
  5. Piloto 2.mov: extrair_audio_frames.py → transcrever.py (blocos retomáveis, commit por
     bloco, lock) → auditoria do usuário (3 trechos + 5 pares de frames) → demais vídeos
     um a um (apagar .mov após gate de integridade).
  6. Durante jobs longos: send_later encadeado (~45 min) para commitar parciais e retomar
     se o processo morrer (lock em materiais/transcricao.lock).
- Fase 2 segue OBRIGATORIAMENTE knowledge/PROTOCOLO-EXTRACAO.md (síncrona, lotes de visão
  de 20–50 pares, manifesto JSONL, commit por lote).
