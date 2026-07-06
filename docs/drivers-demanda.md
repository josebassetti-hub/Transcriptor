# Drivers de demanda por arquétipo de setor — metodologia

**A pergunta que abre qualquer estudo:** quem compra, e o que dimensiona esse consumo na
região? Pessoas para salões; frota para oficinas; empresas (e âncoras) para galpões
logísticos. Antes de contar a oferta (CNPJs), o estudo precisa dimensionar a BASE de
demanda — este documento sistematiza como, para qualquer CNAE, com dados públicos.

**Benchmark de mercado:** é o padrão da indústria — a Statista chama de *driver-based
projection* (alocar mercado por variáveis que CAUSAM a demanda), a IBISWorld publica
*demand determinants* em cada relatório setorial, e o benchmark comercial brasileiro
([IPC Maps](https://www.ipcbr.com/), potencial de consumo em 22 categorias × 5.570
municípios) é construído exatamente assim: população × renda por classe × estrutura de
gasto por categoria, sobre dados públicos (IBGE/MTE).

## A fórmula universal

```
Demanda regional = BASE contável   ×   PENETRAÇÃO / FREQUÊNCIA   ×   VALOR
                   (quem pode          (quantos usam, quanto         (gasto médio,
                    comprar, na         usam)                         com fonte)
                    região)
```

Cada termo com fonte pública citada e selo de proveniência; o que não tiver dado vira
premissa declarada com racional — a regra de sempre.

O protótipo JÁ aplica a fórmula para um caso: a âncora de demanda do piloto de estética
é `domicílios (Censo 2022, tab. 4712) × despesa média mensal familiar com o setor
(POF 2017-2018, tab. 6715) × 12 × IPCA` — o arquétipo 1 abaixo, funcionando ao vivo.

## Os 8 arquétipos

| # | Arquétipo | Setores típicos (divisões CNAE) | BASE (driver) | Fontes públicas |
|---|---|---|---|---|
| 1 | **B2C População/Domicílios** | beleza (96), padarias/alimentação (10/47/56), vestuário (47), pet (75/47) | domicílios e população, por faixa de renda | Censo 2022 (SIDRA 4712), PNAD-C rendimento, POF despesa por categoria (SIDRA 6715) |
| 2 | **B2C Frota** | oficinas e reparação (45.2), autopeças (45.3), lava-rápido, seguros auto | frota por município × tipo × **idade** (frota velha = mais manutenção) | [SENATRAN](https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/estatisticas-frota-de-veiculos-senatran) mensal: UF × município × ano de fabricação × modelo; [Base dos Dados](https://basedosdados.org/dataset/61d592ca-5aec-4f66-b8eb-f7b894a29b66) no BigQuery |
| 3 | **B2C Saúde** | clínicas (86), laboratórios, odontologia | população por faixa etária + beneficiários de plano (mercado privado = quem tem plano ou paga particular) | Censo/projeções IBGE; ANS dados abertos (beneficiários por município/faixa); CNES (oferta instalada) |
| 4 | **B2C Educação** | escolas (85), cursos livres, idiomas | população em idade escolar + matrículas existentes | Censo; INEP (censo escolar, sinopses estatísticas) |
| 5 | **B2B Tecido empresarial** | contabilidade (69), TI (62), marketing (73), coworking/galpões (68/52) | nº de empresas por porte/CNAE na região + FLUXO de novas empresas + ÂNCORAS (maiores empregadores) + massa salarial | base CNPJ/BigQuery (já dominada no piloto), RAIS (vínculos e maiores empregadores — consulta G provou o caminho), Mapa de Empresas (fluxo) |
| 6 | **B2B Agro** | insumos (46.83), máquinas (46.61/28), revendas, armazéns rurais | área plantada e valor da produção + rebanho | PAM (SIDRA 1612/5457), PPM (SIDRA 3939), Censo Agro — mesma API de agregados já usada |
| 7 | **Fluxo/Turismo** | hotéis (55), restaurantes turísticos (56), eventos (82.3/90) | passageiros/visitantes + leitos + população flutuante | ANAC dados abertos (passageiros por aeroporto), CADASTUR; ocupação hoteleira (FOHB) = parceria, declarar |
| 8 | **B2G/Institucional** | obras públicas (41/42), serviços a governo | orçamento executado por função + licitações da região | SICONFI/Tesouro (execução municipal), PNCP dados abertos (licitações) |

### Regras de uso

1. **Todo setor recebe um arquétipo default pela divisão CNAE** (biblioteca curada e
   versionada em `prototype/drivers/arquetipos.json`), com 1–3 drivers. O analista pode
   sobrescrever no JSON do setor — ex.: restaurante de bairro é arquétipo 1; restaurante
   em polo turístico soma o 7.
2. **Setores mistos somam arquétipos** (galpão logístico = 5 como principal + fluxo de
   importações/âncoras; clínica popular = 3 com recorte de renda do 1).
3. **A conversão é sempre declarada**: qual taxa de penetração/frequência foi usada e de
   onde veio (POF para gasto B2C; benchmarks setoriais citáveis para B2B; premissa
   declarada quando não houver dado).
4. **O driver abre o relatório** (seção "Quem compra"), com a base regional, sua evolução
   e a comparação com o Brasil — e alimenta a âncora de demanda da triangulação.
5. **Sinal de âncora (arquétipo 5)**: a chegada/presença de grandes players (maiores
   empregadores da RAIS, novas plantas) entra como leitura qualitativa com fonte, não
   como número inventado.

## Prova no protótipo

- **Arquétipo 1 (estética/SP)**: ao vivo desde o piloto — 16.224.248 domicílios (Censo
  2022) × R$ 38/mês (POF 2017-2018) × 12 × IPCA 1,55 = R$ 11,6 bi/ano.
- **Arquétipo 2 (oficinas/SP, 2º piloto)**: frota SENATRAN por município e ano de
  fabricação (idade da frota como multiplicador de manutenção) × gasto médio com
  manutenção de veículos (POF, grupo transporte) — consultas preparadas em
  `prototype/dados/sql/consultas_oficinas_sp.sql`.

## O que NÃO fazer (armadilhas mapeadas)

- Usar população total quando o driver é um recorte (frota, empresas, faixa etária) —
  superestima e não explica nada.
- Importar "índices de potencial" comerciais sem licença — IPC Maps é benchmark citável
  de metodologia, não fonte de dados da ferramenta.
- Inventar taxa de penetração: sem dado, publicar como premissa declarada + sensibilidade.
- Confundir estoque com fluxo no arquétipo 5: galpão logístico responde a fluxo de
  empresas/carga; contabilidade responde a estoque de empresas.

---

*Pesquisa 06/07/2026. Relacionados: `pesquisa-mercado-ferramentas-analise.md` (seção 4),
`plano-fechamento-lacunas.md` (lacunas 3–4), `metodologia-v3.md`.*
