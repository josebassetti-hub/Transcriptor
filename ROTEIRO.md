# Roteiro — Vídeo institucional GTK Pré-Moldados (1 min 30 s)

Composição Remotion `GTKInstitutional` · 1920×1080 · 30 fps · 2.700 frames.
Estilo: motion graphics com fotos do catálogo Gervasi e vídeos da fábrica-modelo; cores GTK (marinho + amarelo)
e cores vivas dos equipamentos (amarelo e vermelho Gervasi).

## Cenas

| # | Tempo | Cena | Visual | Texto na tela |
|---|---|---|---|---|
| 1 | 0:00–0:06 | Abertura / marca | Fundo com a vibroprensa em operação (escurecido), partículas de pó, logo GTK montando-se bloco a bloco, tagline | GTK PRÉ-MOLDADOS · "Concreto que constrói o Norte Capixaba" |
| 2 | 0:06–0:16 | A empresa + localização | Mapa vetorial do ES com zoom até o norte capixaba, pino em 18°43'08.9"S 40°09'53.4"W (km 35 da BR-381), raio de ~100 km; contato de vendas no rodapé | Fundação 2026 · São Mateus – ES · BR-381, km 35 · Blocos, canaletas e pavers · NBR 6136 / 9781 · Vendas e Parcerias: Kauã Boldrini (27) 99978-3098 |
| 3 | 0:16–0:26 | Produtos | Três cards com ilustrações isométricas (bloco vazado, canaleta, pavers pigmentados) e foto de pátio de blocos | Blocos 9/14/19 · Canaletas · Pavers 6 cm 35 MPa / 8 cm 50 MPa |
| 4 | 0:26–0:48 | A linha de produção | Fundo com a XP em operação; 7 etapas em destaque com foto do catálogo: silo 90 t → central 4 cubas → misturador MXS-1000 → esteiras 6/12 m → vibroprensa XP350 (vídeo) → AM02/DM02 → paletizador ST800 | Linha automática Gervasi XP350 · ciclo < 15 s · 2.000 bandejas/turno · até 15 % menos cimento |
| 5 | 0:48–0:58 | Capacidade | Vídeo vertical do ciclo da vibroprensa + 4 contadores | 7.000 blocos/turno · 1,85 mi blocos/ano · 530 m² de paver/turno · 2× com o 2º turno |
| 6 | 0:58–1:08 | A planta em 3D | Sobrevoo do terreno de 25.000 m² (BR-381, acesso, área de ampliação hachurada) → mergulho no galpão (38×20 m + galpão de cura) com anexo de silo e central de agregados; equipamentos acendem em sequência com foto/vídeo aplicado e rótulo | Terreno 25.000 m² · Galpão ≈ 1.500 m² · Silo 90 t · Cura e expedição · Área para ampliações |
| 7 | 1:08–1:18 | Investimento | Contador "R$ 5 milhões" em fundo amarelo; três chips (equipamentos, galpão e obras, infraestrutura) sem valores | INVESTIMENTO TOTAL · R$ 5 milhões |
| 8 | 1:18–1:24 | Empregos | Grade de pessoas preenchendo: 12 diretos (amarelo) e ~36 indiretos (cinza); total 48 | 12 empregos diretos · ~36 indiretos · 48 postos de trabalho na região (estimativa) |
| 9 | 1:24–1:30 | Encerramento + contato | Logo vertical, card amarelo de contato, razão social/CNPJ/endereço | Vendas e Parcerias · Kauã Boldrini · (27) 99978-3098 |

Transições: fade de 12 frames entre cenas.

## Locução (para gravar — ~150 palavras, cabe em 90 s)

1. **Abertura (0:00)** — "GTK Pré-Moldados. Uma nova indústria nasce no coração do norte do Espírito Santo."
2. **Empresa (0:06)** — "Instalada no km 35 da rodovia Miguel Curry Carneiro, entre São Mateus e Nova Venécia, a GTK será a primeira fábrica automática de blocos e pisos intertravados do interior norte-capixaba."
3. **Produtos (0:16)** — "Blocos de vedação e estruturais, canaletas e pavers de alta resistência, com qualidade de norma para obras, revendas e prefeituras."
4. **Linha (0:26)** — "O coração da fábrica é a linha automática Gervasi XP350: dosagem, mistura, vibroprensagem, cura e paletização em fluxo contínuo, com supervisório em tempo real."
5. **Capacidade (0:48)** — "São mais de sete mil blocos por turno, quase dois milhões por ano, com capacidade de dobrar sem novo investimento."
6. **Planta (0:58)** — "Em um terreno de vinte e cinco mil metros quadrados, o galpão industrial abriga a linha em fluxo contínuo, pátio de cura e estoque, com área reservada para as próximas ampliações."
7. **Investimento (1:08)** — "Um investimento total de cinco milhões de reais em equipamentos, obras e infraestrutura."
8. **Empregos (1:18)** — "Doze empregos diretos e cerca de trinta e seis indiretos, movimentando pedreiras, transporte, revendas e a construção civil da região."
9. **Encerramento (1:24)** — "GTK Pré-Moldados. Construindo o futuro do norte capixaba. Vendas e parcerias: fale com Kauã Boldrini."

Para incluir a locução: coloque `public/gtk/audio/locucao.mp3` e adicione um `<Audio>` de `@remotion/media` em `src/GTK/audio/SoundTrack.tsx` (reduza `master` da trilha para ~0,6 quando houver voz).

## Som (v2)

Três camadas, montadas em `src/GTK/audio/SoundTrack.tsx` a partir de `src/GTK/audio/soundMap.ts`:

- **Trilha** `public/gtk/audio/trilha.mp3` — sintetizada por `scripts/gen-audio.py` (Python puro): drone em Ré menor na abertura, pulso a 95 BPM com hi-hat e sub-baixo a partir da cena 2, kick e arpejo da cena 4 em diante, clímax (pad em duas oitavas, kick em todas as batidas) nas cenas 6–7, alívio na cena 8 e acorde final em Ré maior com fade. Progressão Dm – Bb – F – C.
- **Ambiente** — som real da fábrica-modelo extraído dos vídeos (`amb-*.mp3`): galpão ao fundo nas cenas 1, 6 e 9; vibroprensa em operação na cena 4; ciclo da prensa na cena 5. Volumes entre 5 % e 16 %.
- **Efeitos** (WAV gerados pelo mesmo script), sincronizados frame a frame:

| Cena | Efeitos |
|---|---|
| 1 Marca | 3 impactos de bloco de concreto no encaixe do logo, riser + whoosh na linha amarela, brilho na tagline |
| 2 Empresa | whoosh longo no zoom do mapa, thud do pino, ping do raio, 4 ticks nas linhas de dados |
| 3 Produtos | 3 thuds nos cards |
| 4 Linha | whoosh + clique a cada etapa; "shunk" hidráulico na vibroprensa |
| 5 Capacidade | rajada de ticks nos contadores + ding em cada total |
| 6 Planta 3D | whoosh aéreo no sobrevoo, riser e sub-drop no mergulho, 7 "power-on" (hum + clique) nos equipamentos, dings nos rótulos |
| 7 Investimento | impacto cinematográfico no número, ticks acelerando, ding grave, pops nos chips; a trilha "respira" antes do impacto |
| 8 Empregos | pops por pessoa, dings nos totais, acorde grave no 48 |
| 9 Encerramento | impactos do logo, pop do card de contato, ding, fade da trilha |

Para trocar a trilha por uma música licenciada: substitua `public/gtk/audio/trilha.mp3` por um arquivo de 90 s (ou mais) e ajuste `musicVolume` em `soundMap.ts` se quiser outra curva. Para regenerar os sons: `python3 scripts/gen-audio.py`.

## Premissas dos números

- **Investimento total R$ 5 milhões**: valor informado pelo cliente. O Estudo de Mercado (ago/2026) estima CAPEX de R$ 6,6–8,2 milhões; o vídeo usa o valor do cliente e não mostra preço por equipamento.
- **Empregos**: o estudo prevê 5–7 pessoas por turno na produção (custeio com 6). Estimativa do vídeo para 1 turno: 6 produção + 1 encarregado/manutenção + 1 qualidade + 2 comercial/administrativo + 2 expedição/motorista = **12 diretos** (18–20 com 2º turno). **Indiretos ≈ 36** (multiplicador ~3× sobre os diretos, típico de indústria de materiais de construção: pedreira, cimento, transporte, pallets, revendas, obras). Os números são editáveis no Remotion Studio (props `directJobs`, `indirectJobs`, `investmentBRL`).
- **Capacidade**: dados nominais da proposta Gervasi (bloco 14×19×39: 7.020/turno; paver H6: ~530 m²/turno; 22 dias/mês).
- **Planta 3D**: adaptação do layout Gervasi "São Francisco Ind. Com. REV03" (2 linhas XP550) para uma linha XP350; terreno de 25.000 m² informado pelo cliente; galpão ≈ 1.500 m² cobertos conforme o estudo.
- **Localização**: 18°43'08.9"S 40°09'53.4"W (informada pelo cliente); mapa vetorial simplificado, não é imagem de satélite.

## Como editar

- Textos e números: `src/GTK/data.ts`.
- Cores e fonte: `src/GTK/theme.ts`.
- Mídias (fotos/vídeos): `public/gtk/media/` + `src/GTK/mediaManifest.ts` (ver `public/gtk/media/README.md`).
- Posições da planta 3D (metros): `src/GTK/plant3d/PlantLayout.ts`; câmera: `src/GTK/scenes/Scene06Plant.tsx`.
- Render: `npx remotion render GTKInstitutional out/gtk-institucional.mp4`; logo: `npx remotion still GTKLogoHorizontal out/logo.png`.
