-- ============================================================================
-- Consultas v3 (metodologia: docs/metodologia-v3.md)
-- Rode UMA de cada vez no BigQuery e cole/exporte o resultado:
--   A3 -> dados/cnpj_agregados_demo.csv
--         (cnae,uf,regime,porte,faixa_idade,qtd_empresas,qtd_estabelecimentos)
--   D  -> dados/cnpj_redes_demo.csv (cnae,uf,faixa_unidades,qtd_empresas,qtd_estabelecimentos)
--   B3 -> dados/cnpj_dinamica_demo.csv (ano,regime,porte,aberturas,fechamentos)
--   E  -> dados/cnpj_atividades_demo.csv (cnae,empresas_principal,empresas_somente_secundaria)
--
-- Regime tributário: MEI e Simples são públicos (tabela simples); Lucro
-- Presumido x Lucro Real é sigilo fiscal -> agrupados como FORA_SIMPLES.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- CONSULTA A3 — empresas e estabelecimentos por CNAE x REGIME x porte x idade
-- ---------------------------------------------------------------------------
WITH ultima AS (
  SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
),
estab AS (
  SELECT e.cnpj_basico, e.cnae_fiscal_principal AS cnae7, e.sigla_uf,
         DATE_DIFF(CURRENT_DATE(), e.data_inicio_atividade, YEAR) AS idade
  FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
  WHERE e.data = ultima.d
    AND e.situacao_cadastral IN ('02', '2')
    AND e.cnae_fiscal_principal IN ('9602501', '9602502')
    AND e.sigla_uf = 'SP'
),
emp AS (
  SELECT emp.cnpj_basico, emp.porte
  FROM `basedosdados.br_me_cnpj.empresas` emp, ultima
  WHERE emp.data = ultima.d
),
tributo AS (
  SELECT s.cnpj_basico,
         MAX(s.opcao_mei) = 1 AS eh_mei,
         MAX(s.opcao_simples) = 1 AS eh_simples
  FROM `basedosdados.br_me_cnpj.simples` s
  GROUP BY 1
)
SELECT
  CASE estab.cnae7 WHEN '9602501' THEN '9602-5/01' WHEN '9602502' THEN '9602-5/02' END AS cnae,
  estab.sigla_uf AS uf,
  CASE
    WHEN COALESCE(tributo.eh_mei, FALSE) THEN 'MEI'
    WHEN COALESCE(tributo.eh_simples, FALSE) THEN 'SIMPLES'
    ELSE 'FORA_SIMPLES'
  END AS regime,
  CASE
    WHEN COALESCE(tributo.eh_mei, FALSE) THEN 'MEI'
    WHEN emp.porte IN ('01', '1') THEN 'ME'
    WHEN emp.porte IN ('03', '3') THEN 'EPP'
    ELSE 'DEMAIS'
  END AS porte,
  CASE WHEN estab.idade < 2 THEN '0-2' WHEN estab.idade < 5 THEN '2-5'
       WHEN estab.idade < 10 THEN '5-10' ELSE '10+' END AS faixa_idade,
  COUNT(DISTINCT estab.cnpj_basico) AS qtd_empresas,
  COUNT(*) AS qtd_estabelecimentos
FROM estab
LEFT JOIN emp USING (cnpj_basico)
LEFT JOIN tributo USING (cnpj_basico)
GROUP BY 1, 2, 3, 4, 5
ORDER BY 1, 3, 4, 5;

-- ---------------------------------------------------------------------------
-- CONSULTA D — redes: empresas por nº de estabelecimentos ativos NA REGIÃO
-- (filial na região conta, mesmo com sede fora — mede cobertura e "força")
-- ---------------------------------------------------------------------------
-- WITH ultima AS (
--   SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
-- ),
-- unidades AS (
--   SELECT e.cnpj_basico,
--          CASE e.cnae_fiscal_principal
--            WHEN '9602501' THEN '9602-5/01' WHEN '9602502' THEN '9602-5/02'
--          END AS cnae,
--          COUNT(*) AS n_unidades
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
--   WHERE e.data = ultima.d
--     AND e.situacao_cadastral IN ('02', '2')
--     AND e.cnae_fiscal_principal IN ('9602501', '9602502')
--     AND e.sigla_uf = 'SP'
--   GROUP BY 1, 2
-- )
-- SELECT cnae, 'SP' AS uf,
--        CASE WHEN n_unidades = 1 THEN '1'
--             WHEN n_unidades <= 5 THEN '2-5'
--             ELSE '6+' END AS faixa_unidades,
--        COUNT(*) AS qtd_empresas,
--        SUM(n_unidades) AS qtd_estabelecimentos
-- FROM unidades
-- GROUP BY 1, 2, 3
-- ORDER BY 1, 3;

-- ---------------------------------------------------------------------------
-- CONSULTA B3 — aberturas e fechamentos por ano x regime x porte
-- ---------------------------------------------------------------------------
-- WITH ultima AS (
--   SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
-- ),
-- emp AS (
--   SELECT emp.cnpj_basico, emp.porte
--   FROM `basedosdados.br_me_cnpj.empresas` emp, ultima
--   WHERE emp.data = ultima.d
-- ),
-- tributo AS (
--   SELECT s.cnpj_basico,
--          MAX(s.opcao_mei) = 1 AS eh_mei,
--          MAX(s.opcao_simples) = 1 AS eh_simples
--   FROM `basedosdados.br_me_cnpj.simples` s
--   GROUP BY 1
-- ),
-- base AS (
--   SELECT e.cnpj_basico, e.data_inicio_atividade, e.data_situacao_cadastral,
--          e.situacao_cadastral
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
--   WHERE e.data = ultima.d
--     AND e.cnae_fiscal_principal IN ('9602501', '9602502')
--     AND e.sigla_uf = 'SP'
-- ),
-- cls AS (
--   SELECT base.*,
--     CASE WHEN COALESCE(t.eh_mei, FALSE) THEN 'MEI'
--          WHEN COALESCE(t.eh_simples, FALSE) THEN 'SIMPLES'
--          ELSE 'FORA_SIMPLES' END AS regime,
--     CASE WHEN COALESCE(t.eh_mei, FALSE) THEN 'MEI'
--          WHEN emp.porte IN ('01', '1') THEN 'ME'
--          WHEN emp.porte IN ('03', '3') THEN 'EPP'
--          ELSE 'DEMAIS' END AS porte
--   FROM base
--   LEFT JOIN emp USING (cnpj_basico)
--   LEFT JOIN tributo t USING (cnpj_basico)
-- ),
-- ab AS (
--   SELECT regime, porte, EXTRACT(YEAR FROM data_inicio_atividade) AS ano,
--          COUNT(*) AS aberturas
--   FROM cls GROUP BY 1, 2, 3
-- ),
-- fe AS (
--   SELECT regime, porte, EXTRACT(YEAR FROM data_situacao_cadastral) AS ano,
--          COUNT(*) AS fechamentos
--   FROM cls
--   WHERE situacao_cadastral IN ('04', '4', '08', '8')
--   GROUP BY 1, 2, 3
-- )
-- SELECT ano, regime, porte,
--        COALESCE(ab.aberturas, 0) AS aberturas,
--        COALESCE(fe.fechamentos, 0) AS fechamentos
-- FROM ab FULL JOIN fe USING (regime, porte, ano)
-- WHERE ano BETWEEN 2021 AND EXTRACT(YEAR FROM CURRENT_DATE()) - 1
-- ORDER BY ano, regime, porte;

-- ---------------------------------------------------------------------------
-- CONSULTA E — concorrência por atividade (multi-CNAE, principal x secundária)
-- Ajuste a lista de CNAEs conforme as atividades do estudo.
-- ---------------------------------------------------------------------------
-- WITH ultima AS (
--   SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
-- ),
-- alvo AS (
--   SELECT cnae FROM UNNEST(['9602501', '9602502']) AS cnae
-- ),
-- princ AS (
--   SELECT a.cnae, COUNT(DISTINCT e.cnpj_basico) AS empresas_principal
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima, alvo a
--   WHERE e.data = ultima.d AND e.situacao_cadastral IN ('02', '2')
--     AND e.sigla_uf = 'SP' AND e.cnae_fiscal_principal = a.cnae
--   GROUP BY 1
-- ),
-- sec AS (
--   SELECT a.cnae, COUNT(DISTINCT e.cnpj_basico) AS empresas_somente_secundaria
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima, alvo a
--   WHERE e.data = ultima.d AND e.situacao_cadastral IN ('02', '2')
--     AND e.sigla_uf = 'SP'
--     AND REGEXP_CONTAINS(COALESCE(e.cnae_fiscal_secundaria, ''), a.cnae)
--     AND e.cnpj_basico NOT IN (
--       SELECT ep.cnpj_basico
--       FROM `basedosdados.br_me_cnpj.estabelecimentos` ep, ultima
--       WHERE ep.data = ultima.d AND ep.situacao_cadastral IN ('02', '2')
--         AND ep.sigla_uf = 'SP' AND ep.cnae_fiscal_principal = a.cnae
--     )
--   GROUP BY 1
-- )
-- SELECT
--   CASE a.cnae WHEN '9602501' THEN '9602-5/01' WHEN '9602502' THEN '9602-5/02'
--        ELSE a.cnae END AS cnae,
--   COALESCE(p.empresas_principal, 0) AS empresas_principal,
--   COALESCE(s.empresas_somente_secundaria, 0) AS empresas_somente_secundaria
-- FROM alvo a
-- LEFT JOIN princ p USING (cnae)
-- LEFT JOIN sec s USING (cnae)
-- ORDER BY 1;
