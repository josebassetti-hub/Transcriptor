# Vídeo comercial CIPREM (Remotion)

Uma única composição, `CipremEvento`, que gera **um único MP4**: vinheta pronta (18,2 s) +
90 s de conteúdo em 8 cenas lidas de `../scenes.json`. 1920x1080, 25 fps, barras
cinematográficas de 110 px.

## Mídia (não versionada)

Colocar em `public/footage/` (arquivos reais, não links simbólicos):

- `vinheta_apresenta.mp4` — abertura "Grupo São Vicente apresenta" (a imagem é usada; o som não)
- `novo_investimento.mp4`, `mineracao_1.mp4`, `mineracao_2.mp4` — clipes do Drive

Som: `public/audio/score.wav` é gerado por `audio/build_score.py` (numpy + scipy). Ele contém
todo o desenho de som do vídeo, do primeiro ao último quadro: trilha sintetizada estilo
trailer, efeitos e silêncios de impacto, planejados segundo a segundo. Os clipes de vídeo
ficam mudos.

```bash
python audio/build_score.py          # escreve public/audio/score.wav e imprime o RMS por segundo
```

Para trocar por uma trilha real: gerar o score sem o stem `music` (ou baixar seu ganho no
script) e somar a faixa licenciada com os pontos de sincronia da tabela do roteiro.

## Comandos

```bash
npm install
npm run compositions          # confere: CipremEvento, 2706 quadros
npm run render:preview        # 960x540, rápido, para conferir
npm run render                # 1080p final em out/ciprem-evento.mp4
```

Neste ambiente o Chrome do Remotion é o `headless_shell` do Playwright, passado por
`--browser-executable` nos scripts. Em outra máquina, remover essa flag.

## Onde mudar o quê

- Textos, tempos de entrada e cortes dos clipes: `../scenes.json` (depois rodar
  `node ../build_roteiro.js` para atualizar o roteiro em Word/Markdown).
- Cores, fonte, barras: `src/theme.ts` (lê do JSON).
- Som (instantes dos hits, risers, percussão, harmonia): `audio/build_score.py`.
- Layout de cada cena: `src/scenes/S1..S8`.
- Cena 8: trocar `[WhatsApp comercial] | [Instagram] | [site]` no JSON pelos contatos reais e,
  se houver logo da CIPREM, substituir o texto "CIPREM" por uma `<Img>` em `S8Final.tsx` e
  `S3Solucao.tsx`.

Licença: o Remotion exige licença de empresa para uso comercial acima de 3 pessoas.
