-- Gera os agregados de CNPJ usados pelo produto a partir da Base dos Dados
-- (datalake público no BigQuery: https://basedosdados.org).
--
-- Em produção, este é o "atalho" do MVP: roda mensalmente e o resultado
-- (poucos milhões de linhas) é carregado no Postgres/Supabase na tabela
-- agg_empresas. Quando custo/controle justificarem, substituir pelo ETL
-- próprio sobre os dumps abertos da RFB (dadosabertos.rfb.gov.br/CNPJ/).
--
-- Tabelas de referência na Base dos Dados:
--   basedosdados.br_me_cnpj.estabelecimentos  (situação, CNAE, município, datas)
--   basedosdados.br_me_cnpj.empresas          (porte, natureza jurídica, capital)

WITH estab AS (
  SELECT
    e.cnae_fiscal_principal AS cnae,
    e.sigla_uf              AS uf,
    e.id_municipio,
    emp.porte,
    DATE_DIFF(CURRENT_DATE(), e.data_inicio_atividade, YEAR) AS idade_anos
  FROM `basedosdados.br_me_cnpj.estabelecimentos` e
  JOIN `basedosdados.br_me_cnpj.empresas` emp
    USING (cnpj_basico)
  WHERE e.situacao_cadastral = '2'                  -- 2 = ativa
    AND e.cnae_fiscal_principal IN ('9602501', '9602502')  -- parametrizar por setor
)
SELECT
  cnae,
  uf,
  id_municipio,
  porte,
  CASE
    WHEN idade_anos < 2  THEN '0-2'
    WHEN idade_anos < 5  THEN '2-5'
    WHEN idade_anos < 10 THEN '5-10'
    ELSE '10+'
  END AS faixa_idade,
  COUNT(*) AS qtd_ativas
FROM estab
GROUP BY 1, 2, 3, 4, 5;

-- Dinâmica (aberturas e fechamentos por ano) para a seção de tendências:
-- SELECT EXTRACT(YEAR FROM data_inicio_atividade) AS ano, COUNT(*) AS aberturas ...
-- SELECT EXTRACT(YEAR FROM data_situacao_cadastral) AS ano, COUNT(*) AS fechamentos
--   WHERE situacao_cadastral IN ('4','8') ...   -- 4 = inapta, 8 = baixada
