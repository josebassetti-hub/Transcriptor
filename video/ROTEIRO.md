# Vídeo institucional — Projet Consultoria & Investimentos

**Formato:** 1920×1080 (16:9), 30 fps, 60 s, sem locução, trilha instrumental.
**Uso:** abertura de reuniões presenciais com empresários que buscam financiamento e incentivos fiscais.
**Público:** empresas que querem financiamento (BNB/FNE) e incentivos fiscais (SUDENE, INVEST-ES, municipais).

## Linguagem

Ritmo de propaganda, não de apresentação: câmera em movimento contínuo (push-in, pan, viagem lateral), cortes e wipes sincronizados com a trilha (100 bpm, um tempo = 18 quadros), tipografia cinética (palavras que "batem" na tela com escala e desfoque), ondas de choque e flashes nos hits, partículas, grão de filme e vinheta.

## Storyboard

| # | Cena | Tempo | Texto em tela | Movimento |
|---|------|-------|---------------|-----------|
| 1 | Abertura fria | 0,0–4,8 s | "TODA EMPRESA QUER" · **CRESCER.** | A linha ascendente do logo se desenha com brilho, barras sobem; a palavra bate no 3º tempo com onda de choque e flash. Corte: wipe da esquerda. |
| 2 | O que a Projet faz | 4,8–10,8 s | "DESDE 2011" · "A PROJET ESTRUTURA" · **FINANCIAMENTOS** · **+** · **INCENTIVOS FISCAIS** · "para a sua empresa crescer pagando menos" | Os dois pilares batem na tela no 1º e no 3º tempo; frase de apoio sobe no 6º. Corte: slide de baixo. |
| 3 | Capítulo 01 · Financiamento | 10,8–22,8 s | Abertura: "01" fantasma · **Financiamento** · selo "BNB · FNE". Hits: **JUROS REDUZIDOS** (custo menor para investir) · **PRAZOS LONGOS** (para pagar com folga) · **CARÊNCIA** (para começar a pagar depois) | Impacto na trilha na abertura; um hit a cada 6 tempos, cada um com escala+desfoque, onda de choque e flash; barras ascendentes respiram ao fundo. Corte: wipe diagonal. |
| 4 | Capítulo 02 · Incentivos fiscais | 22,8–36,0 s | Abertura: "02" fantasma · **Incentivos fiscais** · "pague menos imposto para crescer". Hits: SUDENE **67,5%** de redução do IRPJ · REINVESTIMENTO **27%** do IRPJ reinvestido · INVEST-ES **ICMS** e incentivos estaduais e municipais · rodapé "Percentuais conforme Lei Complementar 224/2025" | Impacto na abertura; contadores sobem até o valor; raios de luz giram ao fundo. Corte: slide da direita. |
| 5 | Por que a Projet | 36,0–43,2 s | Enquadramento otimizado · Projeto defensável · Defesa junto ao banco · Acompanhamento completo | Cartões voam da direita em 3D e se encaixam a cada tempo; check desenhado. Corte: slide da esquerda. |
| 6 | Números | 43,2–50,4 s | "DESDE 2011" · **+1.000** · "operações aprovadas" | Contador sobe em 4 tempos; barras crescem como no logo; riser na trilha; onda e flash ao completar. Corte: wipe de baixo para a tela clara. |
| 7 | Final claro | 50,4–60,0 s | Logo original (sem moldura) · "Do projeto à liberação do crédito." · (27) 98142-8090 · (27) 3727-3251 | Impacto na trilha; fundo branco/azul-claro com brilhos suaves; logo entra com mola e varredura de luz; frase em azul-marinho e telefones em azul sobem; fade-out. |

## Fontes dos textos

- Metodologia em 5 etapas e diferenciais: proposta comercial da Projet ("Proposta Comercial — Captação de Recursos Financeiros", Notion).
- Percentuais SUDENE (67,5% de redução do IRPJ; 27% de reinvestimento): Lei Complementar 224/2025, vigente a partir de 1º/01/2026 para o IRPJ. Verifique novamente antes de usar o vídeo em 2027 ou se houver nova alteração legal.
- Ano de fundação e número de operações: informados pela Projet.

## Como alterar e gerar de novo

Todos os textos, telefones, números e durações de cena estão em `src/content.ts` (durações em quadros, múltiplas de 18 para cair no tempo da música). As cores estão em `src/theme.ts`. As transições entre cenas estão em `src/Video.tsx`.

```bash
cd video
npm install
# trilha (já gerada em public/trilha.wav; rode só se quiser regenerar)
python3 scripts/gerar_trilha.py public/trilha.wav
# render final
REMOTION_BROWSER=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell npm run render
# em máquina local com Chrome instalado basta: npx remotion render Projet out/projet-institucional.mp4
# pré-visualizar no navegador
npm run studio
```

Para trocar o logo, substitua `public/logo.png` (PNG com fundo transparente; é usado direto sobre a tela final clara). O arquivo original enviado está em `public/logo.jpg`; a versão transparente foi gerada removendo o branco com o script inline documentado no histórico do projeto (sharp).

## Trilha

`public/trilha.wav` é um instrumental sintetizado (progressão D – Bm – G – A, 100 bpm, pad + arpejo + baixo + bumbo/chimbal, riser antes do final, impactos nas aberturas de capítulo e no logo), gerado por `scripts/gerar_trilha.py` sem dependências externas e livre de direitos autorais. Pode ser substituída por qualquer MP3/WAV licenciado: basta trocar o arquivo e o nome em `src/Video.tsx`.

## Licença do Remotion

O Remotion é gratuito para pessoas físicas e empresas com até 3 funcionários. Acima disso é necessária a licença de empresa (remotion.pro).
