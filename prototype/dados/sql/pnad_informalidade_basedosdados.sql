-- ============================================================================
-- CONSULTA F — informalidade do setor via PNAD Contínua (labor input method)
-- Resultado -> dados/pnad_informalidade_demo.csv
--   (uf, ano, trimestre, categoria, trabalhadores, rendimento_medio_mensal)
--
-- Ocupações COD: 5141 = cabeleireiros; 5142 = especialistas em tratamento de
-- beleza e afins (manicures, esteticistas). V4019: empreendimento tem CNPJ
-- (1=sim, 2=não) — perguntada a conta própria/empregadores desde o 4T2015.
-- Nomes de coluna podem variar entre versões do datalake (v4010 minúsculo
-- etc.); se der erro de nome, confira a aba Esquema e me envie a mensagem.
-- ============================================================================
WITH ultimo AS (
  SELECT MAX(ano * 10 + trimestre) AS ref
  FROM `basedosdados.br_ibge_pnadc.microdados`
),
setor AS (
  SELECT
    m.sigla_uf AS uf,
    m.ano,
    m.trimestre,
    CASE
      -- conta própria (V4012=6) ou empregador (V4012=5) COM CNPJ, ou
      -- empregado com carteira (V4012=3): FORMAL; resto: INFORMAL
      WHEN SAFE_CAST(m.V4019 AS INT64) = 1 THEN 'FORMAL'
      WHEN SAFE_CAST(m.V4012 AS INT64) = 3 THEN 'FORMAL'
      ELSE 'INFORMAL'
    END AS categoria,
    SAFE_CAST(m.V1028 AS FLOAT64) AS peso,
    SAFE_CAST(m.VD4016 AS FLOAT64) AS rendimento
  FROM `basedosdados.br_ibge_pnadc.microdados` m, ultimo
  WHERE m.ano * 10 + m.trimestre = ultimo.ref
    AND m.sigla_uf = 'SP'
    AND SAFE_CAST(m.V4010 AS INT64) IN (5141, 5142)
)
SELECT
  uf, ano, trimestre, categoria,
  ROUND(SUM(peso)) AS trabalhadores,
  ROUND(SUM(peso * rendimento) / NULLIF(SUM(IF(rendimento IS NOT NULL, peso, 0)), 0), 2)
    AS rendimento_medio_mensal
FROM setor
GROUP BY 1, 2, 3, 4
ORDER BY 4;
