-- ============================================================================
-- Agregados de CNPJ via Base dos Dados (BigQuery) — 2 consultas, A e B.
-- Cada uma produz EXATAMENTE o esquema do CSV correspondente do protótipo:
--   A -> dados/cnpj_agregados_demo.csv  (cnae,uf,porte,faixa_idade,qtd_ativas)
--   B -> dados/cnpj_dinamica_demo.csv   (ano,aberturas,fechamentos)
-- Rode uma de cada vez, exporte como CSV e substitua o conteúdo dos arquivos.
--
-- Antes de rodar, confira a estimativa de dados processados no canto superior
-- direito do editor do BigQuery (deve ficar em poucos GB — dentro do nível
-- gratuito de 1 TB/mês). Para espiar as tabelas sem custo, use a aba
-- "Visualizar" (Preview) da tabela, NUNCA um "SELECT *".
--
-- Observações de esquema (podem variar entre versões do datalake):
--   * As tabelas são particionadas pela coluna `data` (data da extração da
--     RFB); o filtro `data = ultima.d` pega só a extração mais recente.
--     Se a sua versão não tiver essa coluna, remova as referências a `ultima`.
--   * situacao_cadastral: '02'/'2' = ativa; '04'/'4' = inapta; '08'/'8' = baixada.
--   * porte (tabela empresas): '01' = ME, '03' = EPP, '05'/demais = DEMAIS.
--   * MEI vem da tabela `simples` (coluna opcao_mei).
-- Em caso de erro de nome de coluna, copie a mensagem e as colunas mostradas
-- na aba "Esquema" da tabela — o ajuste é pontual.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- CONSULTA A — agregado por CNAE x UF x porte x faixa de idade
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
  SELECT s.cnpj_basico, s.opcao_mei
  FROM `basedosdados.br_me_cnpj.simples` s, ultima
  WHERE s.data = ultima.d
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
  COUNT(*) AS qtd_ativas
FROM estab
LEFT JOIN emp USING (cnpj_basico)
LEFT JOIN mei USING (cnpj_basico)
GROUP BY 1, 2, 3, 4
ORDER BY 1, 3, 4;

-- ---------------------------------------------------------------------------
-- CONSULTA B — aberturas e fechamentos por ano (rode separadamente)
-- ---------------------------------------------------------------------------
-- WITH ultima AS (
--   SELECT MAX(data) AS d FROM `basedosdados.br_me_cnpj.estabelecimentos`
-- ),
-- base AS (
--   SELECT e.data_inicio_atividade, e.data_situacao_cadastral, e.situacao_cadastral
--   FROM `basedosdados.br_me_cnpj.estabelecimentos` e, ultima
--   WHERE e.data = ultima.d
--     AND e.cnae_fiscal_principal IN ('9602501', '9602502')
--     AND e.sigla_uf = 'SP'
-- ),
-- ab AS (
--   SELECT EXTRACT(YEAR FROM data_inicio_atividade) AS ano, COUNT(*) AS aberturas
--   FROM base GROUP BY 1
-- ),
-- fe AS (
--   SELECT EXTRACT(YEAR FROM data_situacao_cadastral) AS ano, COUNT(*) AS fechamentos
--   FROM base
--   WHERE situacao_cadastral IN ('04', '4', '08', '8')
--   GROUP BY 1
-- )
-- SELECT ano,
--        COALESCE(ab.aberturas, 0) AS aberturas,
--        COALESCE(fe.fechamentos, 0) AS fechamentos
-- FROM ab FULL JOIN fe USING (ano)
-- WHERE ano BETWEEN 2021 AND EXTRACT(YEAR FROM CURRENT_DATE()) - 1
-- ORDER BY ano;
