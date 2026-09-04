# Mídias do vídeo institucional GTK

Arquivos referenciados por `src/GTK/mediaManifest.ts`.

| Slot | Arquivo | Situação |
|---|---|---|
| video:fabrica-tour | fabrica-tour.mp4 (480×848, 140 s) | ok |
| video:xp350-operacao | xp350-operacao.mp4 (848×480, 43 s) | ok |
| video:xp350-ciclo | xp350-ciclo.mp4 (478×850, 44 s) | ok |
| video:fabrica-b-roll-3 | fabrica-b-roll-3.mp4 | **faltando** (vídeo do Drive, comprimir < 100 MB) |
| video:fabrica-b-roll-4 | fabrica-b-roll-4.mp4 | **faltando** (vídeo do Drive, comprimir < 100 MB) |
| image:satelite | satelite.jpg | opcional (print do Google Earth em 18°43'08.9"S 40°09'53.4"W) |
| cat:* | catalogo/*.jpg | gerados por `scripts/extract-catalog.py` |
| layout:* | layout/sao-francisco-p*.png | páginas do layout Gervasi de referência |

Para preencher um slot faltante: copie o arquivo com o nome indicado para esta pasta e
edite a entrada correspondente em `mediaManifest.ts` (troque `null` pelo objeto com `file`).
