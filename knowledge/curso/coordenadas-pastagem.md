# Coordenadas de gleba (pastagem) — formato de georreferenciamento

Fonte: `Coordenadas pastagem.xlsx` (Drive) — extração completa. Par com `Pastagem.kml` e
`Pastagem.txt` (mesma gleba), e com a "Ferramenta para Coordenadas Geodésicas.xlsm".

## Formato

Lista de vértices do polígono da gleba em **graus decimais, latitude,longitude (WGS84)**:

```
-3.99915402342129, -41.9821525645567
-3.99980965063658, -41.9832766218176
-4.00006958238988, -41.9835522880600
-4.00115606716314, -41.9853202381695
-4.00211412702115, -41.9867370788531
-4.00342502209548, -41.9876083162075
-4.00643064319556, -41.9856819555344
-4.00432811124957, -41.9842346147274
-4.00458296850488, -41.9832527015664
-4.00497964962923, -41.9811862713342
```

10 vértices; região aproximada: norte do Piauí (lat ≈ −4,00, lon ≈ −41,98).

## Uso no produto

- O projeto para o banco exige as coordenadas das glebas (croqui/CAR); o professor usa
  Google Earth (KML/KMZ: `Pastagem.kml`, `Cerca.kmz`) + planilha de conversão.
- Motor futuro (`engines/`): ler KML/KMZ → extrair vértices → converter formato exigido
  pela ferramenta do banco (a "Ferramenta para Coordenadas Geodésicas.xlsm" faz conversões
  grau decimal ↔ GMS — dissecar quando o binário vier pela Rota A) → calcular área do
  polígono (conferência da área declarada).
