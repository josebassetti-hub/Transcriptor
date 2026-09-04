# Vídeo institucional — Projet Consultoria & Investimentos

**Formato:** 1920×1080 (16:9), 30 fps, 60 s, sem locução, trilha instrumental.
**Uso:** abertura de reuniões presenciais com empresários que buscam financiamento e incentivos fiscais.
**Público:** empresas que querem financiamento (BNB/FNE) e incentivos fiscais (SUDENE, INVEST-ES, municipais).

## Storyboard

| # | Cena | Tempo | Texto em tela | Animação |
|---|------|-------|---------------|----------|
| 1 | Abertura | 0–5 s | Logo Projet · "Estruturação de projetos e incentivos fiscais" · "DESDE 2011" | Logo surge com leve escala; linha azul se estende; textos entram de baixo |
| 2 | O desafio | 5–13 s | "Investir exige capital." / "Acessar crédito de longo prazo exige método." · Expansão · Modernização · Capital de giro estrutural | Frases em sequência; três ícones desenhados por traço animado |
| 3 | Estruturação de projetos | 13–26 s | "Estruturação de projetos" · "Financiamento BNB · FNE" · 01 Diagnóstico → 02 Cadastro e carta-consulta → 03 Projeto econômico-financeiro → 04 Defesa e aprovação → 05 Contratação e liberação | Trilho azul avança; cada etapa "acende" com pop e legenda |
| 4 | Incentivos fiscais | 26–38 s | "Incentivos fiscais que reduzem o custo de crescer" · SUDENE **67,5%** de redução do IRPJ · REINVESTIMENTO **27%** do IRPJ reinvestido · INVEST-ES ICMS e incentivos estaduais e municipais · rodapé "Percentuais conforme Lei Complementar 224/2025" | Três cartões sobem; contadores animam até o valor |
| 5 | Por que a Projet | 38–48 s | Enquadramento otimizado · Projeto defensável · Defesa junto ao banco · Acompanhamento completo (cada um com uma linha de apoio) | Grade 2×2; check azul desenhado em cada cartão |
| 6 | Números | 48–54 s | "DESDE 2011" · **+1.000** · "operações aprovadas" | Contador sobe de 0 a 1.000 |
| 7 | Encerramento | 54–60 s | Logo · "Do projeto à liberação do crédito." · (27) 98142-8090 · (27) 3727-3251 | Fade-in do logo; trilha em fade-out nos últimos 4 s |

## Fontes dos textos

- Metodologia em 5 etapas e diferenciais: proposta comercial da Projet ("Proposta Comercial — Captação de Recursos Financeiros", Notion).
- Percentuais SUDENE (67,5% de redução do IRPJ; 27% de reinvestimento): Lei Complementar 224/2025, vigente a partir de 1º/01/2026 para o IRPJ. Verifique novamente antes de usar o vídeo em 2027 ou se houver nova alteração legal.
- Ano de fundação e número de operações: informados pela Projet.

## Como alterar e gerar de novo

Todos os textos, telefones, números e tempos de cena estão em `src/content.ts`. As cores estão em `src/theme.ts`.

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

Para trocar o logo, substitua `public/logo.png` (PNG com fundo transparente). O arquivo original enviado está em `public/logo.jpg`; a versão transparente foi gerada removendo o branco com o script inline documentado no histórico do projeto (sharp).

## Trilha

`public/trilha.wav` é um instrumental sintetizado (progressão D – Bm – G – A, 72 bpm, pad + arpejo + baixo), gerado por `scripts/gerar_trilha.py` sem dependências externas e livre de direitos autorais. Pode ser substituída por qualquer MP3/WAV licenciado: basta trocar o arquivo e o nome em `src/Video.tsx`.

## Licença do Remotion

O Remotion é gratuito para pessoas físicas e empresas com até 3 funcionários. Acima disso é necessária a licença de empresa (remotion.pro).
