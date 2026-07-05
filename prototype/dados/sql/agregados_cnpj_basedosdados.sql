-- ============================================================================
-- Consultas v3 (metodologia: docs/metodologia-v3.md)
-- Rode UMA de cada vez no BigQuery e cole/exporte o resultado:
--   A4 -> dados/cnpj_agregados_demo.csv
--         (cnae,uf,regime,porte,faixa_idade,qtd_empresas,qtd_estabelecimentos)
--         [substitui a A3: idade agora é a da MATRIZ = idade da empresa]
--   D  -> dados/cnpj_redes_demo.csv (cnae,uf,faixa_unidades,qtd_empresas,qtd_estabelecimentos)
--   B3 -> dados/cnpj_dinamica_demo.csv (ano,regime,porte,aberturas,fechamentos)
--   E  -> dados/cnpj_atividades_demo.csv (cnae,empresas_principal,empresas_somente_secundaria)
--   G  -> dados/rais_regiao_demo.csv (ano,sigla_uf,vinculos)
--
-- Regime tributário: MEI e Simples são públicos (tabela simples); Lucro
-- Presumido x Lucro Real é sigilo fiscal -> agrupados como FORA_SIMPLES.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- CONSULTA A4 — como a A3, mas a faixa de idade é a da EMPRESA (estabelecimento
-- matriz), não a de cada estabelecimento: fecha a limitação "matriz e filiais
-- de idades distintas podem cair em faixas diferentes".
-- ---------------------------------------------------------------------------
WITH ultima AS (
  SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
),
estab AS (
  SELECT e.cnpj_basico, e.cnae_fiscal_principal AS cnae7, e.sigla_uf,
         e.data_inicio_atividade
  FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
  WHERE e.data = ultima.d
    AND e.situacao_cadastral IN ('02', '2')
    AND e.cnae_fiscal_principal IN ('9602501', '9602502')
    AND e.sigla_uf = 'SP'
),
matriz AS (
  SELECT m.cnpj_basico, MIN(m.data_inicio_atividade) AS inicio_empresa
  FROM `basedosdados.br_me_cnpj.estabelecimentos` m, ultima
  WHERE m.data = ultima.d
    AND CAST(m.identificador_matriz_filial AS STRING) = '1'
    AND m.cnpj_basico IN (SELECT cnpj_basico FROM estab)
  GROUP BY m.cnpj_basico
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
  GROUP BY s.cnpj_basico
),
com_idade AS (
  SELECT estab.cnpj_basico, estab.cnae7, estab.sigla_uf,
         DATE_DIFF(CURRENT_DATE(),
                   COALESCE(matriz.inicio_empresa, estab.data_inicio_atividade),
                   YEAR) AS idade
  FROM estab
  LEFT JOIN matriz USING (cnpj_basico)
)
SELECT
  CASE com_idade.cnae7 WHEN '9602501' THEN '9602-5/01' WHEN '9602502' THEN '9602-5/02' END AS cnae,
  com_idade.sigla_uf AS uf,
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
  CASE WHEN com_idade.idade < 2 THEN '0-2' WHEN com_idade.idade < 5 THEN '2-5'
       WHEN com_idade.idade < 10 THEN '5-10' ELSE '10+' END AS faixa_idade,
  COUNT(DISTINCT com_idade.cnpj_basico) AS qtd_empresas,
  COUNT(*) AS qtd_estabelecimentos
FROM com_idade
LEFT JOIN emp USING (cnpj_basico)
LEFT JOIN tributo USING (cnpj_basico)
GROUP BY 1, 2, 3, 4, 5
ORDER BY 1, 3, 4, 5;

-- ---------------------------------------------------------------------------
-- CONSULTA G — RAIS: vínculos formais da subclasse por UF (peso regional)
-- Participação de SP = vinculos de SP ÷ soma de todas as UFs. Se der erro de
-- coluna, troque cnae_2_subclasse pelos 5 dígitos: cnae_2 IN ('96025').
-- ---------------------------------------------------------------------------
-- SELECT ano, sigla_uf, SUM(quantidade_vinculos_ativos) AS vinculos
-- FROM `basedosdados.br_me_rais.microdados_estabelecimentos`
-- WHERE cnae_2_subclasse IN ('9602501', '9602502')
--   AND ano = (SELECT MAX(ano)
--              FROM `basedosdados.br_me_rais.microdados_estabelecimentos`)
-- GROUP BY ano, sigla_uf
-- ORDER BY vinculos DESC;

-- ---------------------------------------------------------------------------
-- CONSULTA A3 (SUPERSEDIDA pela A4 — mantida por referência: idade era a do
-- estabelecimento, não a da empresa)
-- ---------------------------------------------------------------------------
-- WITH ultima AS (
--   SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
-- ),
-- estab AS (
--   SELECT e.cnpj_basico, e.cnae_fiscal_principal AS cnae7, e.sigla_uf,
--          DATE_DIFF(CURRENT_DATE(), e.data_inicio_atividade, YEAR) AS idade
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
--   WHERE e.data = ultima.d
--     AND e.situacao_cadastral IN ('02', '2')
--     AND e.cnae_fiscal_principal IN ('9602501', '9602502')
--     AND e.sigla_uf = 'SP'
-- )
-- SELECT ... (mesma estrutura da A4, com estab.idade no lugar de com_idade.idade);

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
