-- ============================================================================
-- Consultas do 2º setor-piloto: OFICINAS (CNAE 4520-0/01,02,03 — SP)
-- Mesmo fluxo do piloto de estética: rode UMA por vez no BigQuery e cole o
-- resultado no chat. Destinos:
--   A4 -> dados/oficinas_agregados_demo.csv
--   B3 -> dados/oficinas_dinamica_demo.csv
--   D  -> dados/oficinas_redes_demo.csv
--   E  -> dados/oficinas_atividades_demo.csv
--   G  -> dados/oficinas_rais_demo.csv
--   H  -> dados/oficinas_frota_demo.csv  (driver de demanda: frota SENATRAN)
-- As consultas A4/B3/D/E são as de agregados_cnpj_basedosdados.sql com os
-- CNAEs trocados por ('4520001','4520002','4520003') — versões completas
-- abaixo, prontas para colar.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- CONSULTA H — FROTA (SENATRAN via Base dos Dados): frota de SP por tipo,
-- na referência mais recente. Se der erro de esquema, cole a mensagem no chat.
-- ---------------------------------------------------------------------------
WITH ultimo AS (
  SELECT MAX(ano) AS ano FROM `basedosdados.br_denatran_frota.municipio_tipo`
)
SELECT f.ano, MAX(f.mes) AS mes, f.tipo_veiculo,
       SUM(f.quantidade) AS quantidade
FROM `basedosdados.br_denatran_frota.municipio_tipo` f, ultimo
WHERE f.sigla_uf = 'SP'
  AND f.ano = ultimo.ano
  AND f.mes = (SELECT MAX(mes)
               FROM `basedosdados.br_denatran_frota.municipio_tipo` m, ultimo
               WHERE m.ano = ultimo.ano)
GROUP BY f.ano, f.tipo_veiculo
ORDER BY quantidade DESC;

-- ---------------------------------------------------------------------------
-- CONSULTA A4 — empresas/estabelecimentos por CNAE x regime x porte x idade
-- (idade da EMPRESA = estabelecimento matriz)
-- ---------------------------------------------------------------------------
-- WITH ultima AS (
--   SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
-- ),
-- estab AS (
--   SELECT e.cnpj_basico, e.cnae_fiscal_principal AS cnae7, e.sigla_uf,
--          e.data_inicio_atividade
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
--   WHERE e.data = ultima.d
--     AND e.situacao_cadastral IN ('02', '2')
--     AND e.cnae_fiscal_principal IN ('4520001', '4520002', '4520003')
--     AND e.sigla_uf = 'SP'
-- ),
-- matriz AS (
--   SELECT m.cnpj_basico, MIN(m.data_inicio_atividade) AS inicio_empresa
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` m, ultima
--   WHERE m.data = ultima.d
--     AND CAST(m.identificador_matriz_filial AS STRING) = '1'
--     AND m.cnpj_basico IN (SELECT cnpj_basico FROM estab)
--   GROUP BY m.cnpj_basico
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
--   GROUP BY s.cnpj_basico
-- ),
-- com_idade AS (
--   SELECT estab.cnpj_basico, estab.cnae7, estab.sigla_uf,
--          DATE_DIFF(CURRENT_DATE(),
--                    COALESCE(matriz.inicio_empresa, estab.data_inicio_atividade),
--                    YEAR) AS idade
--   FROM estab
--   LEFT JOIN matriz USING (cnpj_basico)
-- )
-- SELECT
--   CASE com_idade.cnae7
--     WHEN '4520001' THEN '4520-0/01' WHEN '4520002' THEN '4520-0/02'
--     WHEN '4520003' THEN '4520-0/03' END AS cnae,
--   com_idade.sigla_uf AS uf,
--   CASE WHEN COALESCE(tributo.eh_mei, FALSE) THEN 'MEI'
--        WHEN COALESCE(tributo.eh_simples, FALSE) THEN 'SIMPLES'
--        ELSE 'FORA_SIMPLES' END AS regime,
--   CASE WHEN COALESCE(tributo.eh_mei, FALSE) THEN 'MEI'
--        WHEN emp.porte IN ('01', '1') THEN 'ME'
--        WHEN emp.porte IN ('03', '3') THEN 'EPP'
--        ELSE 'DEMAIS' END AS porte,
--   CASE WHEN com_idade.idade < 2 THEN '0-2' WHEN com_idade.idade < 5 THEN '2-5'
--        WHEN com_idade.idade < 10 THEN '5-10' ELSE '10+' END AS faixa_idade,
--   COUNT(DISTINCT com_idade.cnpj_basico) AS qtd_empresas,
--   COUNT(*) AS qtd_estabelecimentos
-- FROM com_idade
-- LEFT JOIN emp USING (cnpj_basico)
-- LEFT JOIN tributo USING (cnpj_basico)
-- GROUP BY 1, 2, 3, 4, 5
-- ORDER BY 1, 3, 4, 5;

-- ---------------------------------------------------------------------------
-- CONSULTA B3 — aberturas x fechamentos por ano x regime x porte
-- (copie a B3 de agregados_cnpj_basedosdados.sql trocando a lista de CNAEs
--  por ('4520001', '4520002', '4520003'))
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- CONSULTA D — redes/filiais na região
-- (copie a D de agregados_cnpj_basedosdados.sql trocando a lista de CNAEs)
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- CONSULTA E — concorrência por atividade (principal x só-secundária)
-- (copie a E de agregados_cnpj_basedosdados.sql trocando a lista de CNAEs)
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- CONSULTA G — RAIS: vínculos da subclasse por UF (peso regional)
-- ---------------------------------------------------------------------------
-- SELECT ano, sigla_uf, SUM(quantidade_vinculos_ativos) AS vinculos
-- FROM `basedosdados.br_me_rais.microdados_estabelecimentos`
-- WHERE cnae_2_subclasse IN ('4520001', '4520002', '4520003')
--   AND ano = 2024
-- GROUP BY ano, sigla_uf
-- ORDER BY vinculos DESC;

-- ---------------------------------------------------------------------------
-- CONSULTA F — PNAD: informalidade da ocupação (mecânicos = COD 7231)
-- (copie a F de pnad_informalidade_basedosdados.sql trocando as ocupações
--  {5141, 5142} por {7231} — mecânicos e reparadores de veículos a motor)
-- ---------------------------------------------------------------------------
