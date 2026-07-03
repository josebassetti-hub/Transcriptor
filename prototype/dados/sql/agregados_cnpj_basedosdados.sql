-- ============================================================================
-- Consultas v2 (pós-auditoria: docs/auditoria-numeros-piloto.md)
-- Rode UMA de cada vez no BigQuery e cole/exporte o resultado:
--   A2 -> dados/cnpj_agregados_demo.csv  (cnae,uf,porte,faixa_idade,qtd_empresas,qtd_estabelecimentos)
--   C  -> nº para o campo icp.empresas_somente_cnae_secundario do JSON do setor
--   B2 -> dados/cnpj_dinamica_demo.csv   (ano,segmento,aberturas,fechamentos)
-- ============================================================================

-- ---------------------------------------------------------------------------
-- CONSULTA A2 — empresas E estabelecimentos por CNAE x porte x faixa de idade
-- (corrige a unidade: DISTINCT cnpj_basico conta EMPRESAS; filiais não inflam)
-- ---------------------------------------------------------------------------
WITH ultima AS (
  SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
),
estab AS (
  SELECT
    e.cnpj_basico,
    e.cnae_fiscal_principal AS cnae7,
    e.sigla_uf,
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
mei AS (
  SELECT s.cnpj_basico, MAX(s.opcao_mei) = 1 AS opcao_mei
  FROM `basedosdados.br_me_cnpj.simples` s
  GROUP BY 1
)
SELECT
  CASE estab.cnae7
    WHEN '9602501' THEN '9602-5/01'
    WHEN '9602502' THEN '9602-5/02'
  END AS cnae,
  estab.sigla_uf AS uf,
  CASE
    WHEN COALESCE(mei.opcao_mei, FALSE) THEN 'MEI'
    WHEN emp.porte IN ('01', '1') THEN 'ME'
    WHEN emp.porte IN ('03', '3') THEN 'EPP'
    ELSE 'DEMAIS'
  END AS porte,
  CASE
    WHEN estab.idade < 2 THEN '0-2'
    WHEN estab.idade < 5 THEN '2-5'
    WHEN estab.idade < 10 THEN '5-10'
    ELSE '10+'
  END AS faixa_idade,
  COUNT(DISTINCT estab.cnpj_basico) AS qtd_empresas,
  COUNT(*) AS qtd_estabelecimentos
FROM estab
LEFT JOIN emp USING (cnpj_basico)
LEFT JOIN mei USING (cnpj_basico)
GROUP BY 1, 2, 3, 4
ORDER BY 1, 3, 4;

-- ---------------------------------------------------------------------------
-- CONSULTA C — empresas com 9602-5 APENAS como CNAE secundário
-- (mede a subcontagem do filtro por CNAE principal; sem dupla contagem:
--  DISTINCT cnpj_basico e exclusão de quem já entra pelo principal)
-- ---------------------------------------------------------------------------
-- WITH ultima AS (
--   SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
-- ),
-- pelo_principal AS (
--   SELECT DISTINCT e.cnpj_basico
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
--   WHERE e.data = ultima.d
--     AND e.situacao_cadastral IN ('02', '2')
--     AND e.cnae_fiscal_principal IN ('9602501', '9602502')
--     AND e.sigla_uf = 'SP'
-- ),
-- pela_secundaria AS (
--   SELECT DISTINCT e.cnpj_basico
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
--   WHERE e.data = ultima.d
--     AND e.situacao_cadastral IN ('02', '2')
--     AND e.sigla_uf = 'SP'
--     AND REGEXP_CONTAINS(COALESCE(e.cnae_fiscal_secundaria, ''), r'960250[12]')
-- )
-- SELECT COUNT(*) AS empresas_somente_cnae_secundario
-- FROM pela_secundaria s
-- WHERE s.cnpj_basico NOT IN (SELECT cnpj_basico FROM pelo_principal);

-- ---------------------------------------------------------------------------
-- CONSULTA B2 — aberturas e fechamentos por ano, separados MEI x não-MEI
-- (a maior parte do fluxo de aberturas é MEI, que está fora do ICP — separar
--  evita a leitura enganosa de "66 mil clientes potenciais novos por ano")
-- ---------------------------------------------------------------------------
-- WITH ultima AS (
--   SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
-- ),
-- mei AS (
--   SELECT s.cnpj_basico, MAX(s.opcao_mei) = 1 AS opcao_mei
--   FROM `basedosdados.br_me_cnpj.simples` s
--   GROUP BY 1
-- ),
-- base AS (
--   SELECT
--     e.cnpj_basico, e.data_inicio_atividade,
--     e.data_situacao_cadastral, e.situacao_cadastral
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
--   WHERE e.data = ultima.d
--     AND e.cnae_fiscal_principal IN ('9602501', '9602502')
--     AND e.sigla_uf = 'SP'
-- ),
-- cls AS (
--   SELECT base.*,
--          IF(COALESCE(m.opcao_mei, FALSE), 'MEI', 'NAO_MEI') AS segmento
--   FROM base LEFT JOIN mei m USING (cnpj_basico)
-- ),
-- ab AS (
--   SELECT segmento, EXTRACT(YEAR FROM data_inicio_atividade) AS ano,
--          COUNT(*) AS aberturas
--   FROM cls GROUP BY 1, 2
-- ),
-- fe AS (
--   SELECT segmento, EXTRACT(YEAR FROM data_situacao_cadastral) AS ano,
--          COUNT(*) AS fechamentos
--   FROM cls
--   WHERE situacao_cadastral IN ('04', '4', '08', '8')
--   GROUP BY 1, 2
-- )
-- SELECT ano, segmento,
--        COALESCE(ab.aberturas, 0) AS aberturas,
--        COALESCE(fe.fechamentos, 0) AS fechamentos
-- FROM ab FULL JOIN fe USING (segmento, ano)
-- WHERE ano BETWEEN 2021 AND EXTRACT(YEAR FROM CURRENT_DATE()) - 1
-- ORDER BY ano, segmento;
