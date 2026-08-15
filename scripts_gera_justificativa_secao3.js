const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
} = require('docx');

const RED = 'C00000';
const GREY = '595959';
const FONT = 'Calibri';

// r(texto) = preto (mantido) | r(texto, 1) = vermelho (alterado nesta revisão)
function r(text, red) {
  return new TextRun({ text, color: red ? RED : '000000', font: FONT, size: 22 });
}
function para(runs, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { after: opts.after === undefined ? 180 : opts.after, line: 276 },
    indent: opts.indent,
    children: runs,
  });
}

const titulo = new Paragraph({
  spacing: { after: 160 },
  children: [new TextRun({ text: '3. JUSTIFICATIVA DO EMPREENDIMENTO', bold: true, font: FONT, size: 24 })],
});

const legenda = new Paragraph({
  spacing: { after: 300 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: 'BFBFBF', space: 8 } },
  children: [
    new TextRun({ text: 'Em ', italics: true, color: GREY, font: FONT, size: 18 }),
    new TextRun({ text: 'vermelho', italics: true, bold: true, color: RED, font: FONT, size: 18 }),
    new TextRun({
      text: ', os trechos alterados nesta revisão — por correção de dado verificado em fonte pública ou por ajuste ao mercado-base conservador do Estudo de Mercado anexo. Em preto, o texto mantido. A nota ao final relaciona o que foi suprimido e por quê.',
      italics: true, color: GREY, font: FONT, size: 18,
    }),
  ],
});

const corpo = [
  // --- P1: abertura (nova) ---
  para([
    r('Os fundamentos mercadológicos do empreendimento estão detalhados no Estudo de Mercado anexo (Projet Consultoria, junho de 2026, atualizado em agosto de 2026), cujos principais resultados são resumidos a seguir.', 1),
  ]),

  // --- P2: mercado-base ---
  para([
    r('São Mateus é o '),
    r('município-polo e o mais populoso da Microrregião Nordeste do Espírito Santo (regionalização estadual da Lei nº 9.768/2011)', 1),
    r(', com 134,4 mil habitantes — IBGE, estimativa 2025; 8º do Estado — e polo regional de comércio e serviços. '),
    r('O setor tem natureza essencialmente local: pelo baixo valor por tonelada, o raio econômico de comercialização raramente ultrapassa algumas dezenas de quilômetros, e excepcionalmente 150 km entre a fonte e o consumidor. Por isso, o', 1),
    r(' mercado-base do empreendimento — definido pelo raio econômico do frete e pela posição real dos concorrentes '),
    r('— foi delimitado de forma deliberadamente conservadora: restringe-se a São Mateus e Conceição da Barra, que somam 161.881 habitantes (IBGE, estimativa 2025 e Censo 2022), os dois municípios em que a varredura de concorrência não identificou nenhum produtor de brita instalado.', 1),
  ]),

  // --- P3: demanda ---
  para([
    r('A demanda corrente nesse mercado-base é estimada '),
    r('entre 235 e 275 mil toneladas/ano. A estimativa parte de um índice de consumo aparente de brita no Espírito Santo de 1,6 a 1,7 t/hab/ano — elaboração própria a partir das vendas declaradas à ANM no Relatório Anual de Lavra (RAL), convergente com o parâmetro setorial da ANEPAC para o Sudeste —, aplicado integralmente à sede (215–230 mil t/ano) e, por conservadorismo, pela metade em Conceição da Barra, município de perfil rural-litorâneo. Trata-se de estimativa de ordem de grandeza, e não de número contábil: a memória de cálculo e as premissas constam do Estudo anexo. A ordem de grandeza é corroborada por baixo pelo censo de clientes do próprio Estudo, que mapeia 44 compradores na área de influência, com cerca de 192 mil t/ano de consumo identificado e da ordem de 62 mil t/ano imediatamente capturáveis pela CIPREM.', 1),
  ]),

  // --- P4: praças fora da base ---
  para([
    r('As praças vizinhas de Jaguaré e Boa Esperança (~46 mil habitantes; 36–78 mil t/ano pela mesma métrica) foram mantidas fora da linha de base — a primeira por ter produtor instalado, a segunda por gravitar comercialmente para Nova Venécia — e permanecem, ao lado de', 1),
    r(' Pedro Canário e '),
    r('da franja norte do Estado (Montanha, Mucurici e Ponto Belo — ~53 mil habitantes, sem produtor de brita local), como potencial adicional de captura. Por conservadorismo, tais mercados não foram incorporados às projeções de receita do empreendimento.', 1),
  ]),

  // --- P5: oferta instalada ---
  para([
    r('A oferta instalada confirma a lacuna: '),
    r('a varredura município a município realizada em agosto de 2026 — em bases públicas de CNPJ, cadastros da ANM e fontes indexadas — não identificou nenhuma pedreira de britagem em atividade em São Mateus ou em Conceição da Barra. Em São Mateus, a presença concorrente é de natureza logístico-comercial: a Pedreira Mattar, sediada em Pinheiros (~70 km), mantém filial no município com CNAE de beneficiamento, sem atividade de extração associada. A operação de britagem mais próxima é a Mineração Usibrita, em Jaguaré (~40 km da sede), ainda em escala reduzida e situada fora do mercado-base. Os produtores de porte operam a partir de ~65 km — Nova Venécia e Pinheiros — e o maior deles a cerca de 100 km, em Rio Bananal', 1),
    r(', com parte do suprimento vindo do eixo Linhares–Aracruz (85–140 km). A jazida da CIPREM está a ~35 km da sede — e a ~25 km de Boa Esperança: em um produto cujo preço posto na obra é dominado pelo frete, é vantagem competitiva estrutural no maior polo de demanda da região — a operação substitui suprimento de longa distância por produção local.'),
  ]),

  // --- P6: obras públicas ---
  para([
    r('Além disso, o município de São Mateus vive um ciclo de investimentos públicos sem precedente na sua série histórica. '),
    r('A macrodrenagem e pavimentação de Guriri é um programa que o Governo do Estado estima em cerca de R$ 1 bilhão no conjunto das três etapas: a bacia 2 está em execução pelo Consórcio Guriri CT, com conclusão prevista para o fim de 2028; a bacia 1 teve edital publicado em março de 2026 (R$ 321,8 milhões, 13,5 km de galerias e ~125 mil m² de pavimentação); e a bacia 3 está prevista, ainda sem edital publicado. Somam-se o Contorno de São Mateus/ES-318, em execução desde novembro de 2024 (R$ 164 milhões, 24,26 km e duas pontes sobre o rio Mariricu, prazo de 35 meses), a duplicação da ES-315 entre a sede e Guriri (R$ 92,1 milhões, 12,06 km, conclusão contratual prevista para dezembro de 2026) e a antecipação, pela concessionária Ecovias Capixaba, de 21,6 km de terceiras faixas no trecho norte da BR-101 — entre os km 50,3 e 134,1, distribuídos por Conceição da Barra, São Mateus, Jaguaré, Sooretama e Linhares —, com cerca de 7 km previstos até fevereiro de 2027 e os 14,72 km restantes até dezembro de 2027, dentro dos 41 km planejados na concessão.', 1),
  ]),

  // --- P7: efeito das obras ---
  para([
    r('Essas frentes adicionam 70–100 mil t/ano de demanda extraordinária de brita durante a janela de obras — e destravam um potencial estrutural maior: a malha planejada de Guriri (11 avenidas e 31 ruas ao longo de ~8 km) permanece majoritariamente sem pavimentação definitiva, e sua pavimentação completa, viabilizada justamente pela macrodrenagem em curso, '),
    r('é dimensionada no Estudo anexo em 350 a 400 mil m² de pavimento — da ordem de 500 mil toneladas de agregados ao longo dos próximos anos —, das quais as projeções contabilizam, conservadoramente, apenas 75 a 90 mil t de brita da pavimentação remanescente.', 1),
    r(' As frentes demandam todo o portfólio do projeto: concreto estrutural (Britas 0 e 1) nas galerias e pontes, base e sub-base granular (BGS) nas rodovias, CBUQ (pedrisco) e assentamento de pavimento intertravado (pó de pedra) — padrão construtivo predominante na região.'),
  ]),

  // --- P8: setor privado ---
  para([
    r('No setor privado, operam na praça centrais de concreto de grupos consolidados ('),
    r('Polimix, na BR-101 km 71, e Pedramix', 1),
    r('), consumidoras contínuas de brita e areia industrial. O escoamento das frações finas — historicamente as de venda mais difícil em pedreiras entrantes — apoia-se no padrão construtivo predominante da região, o pavimento intertravado, que consome pó de pedra no assentamento e na fabricação dos blocos, e nas rotas técnicas de recomposição em brita graduada simples e de areia de brita. A Prefeitura — receita realizada de R$ 696,7 milhões em 2024 e '),
    r('classificação A na Capacidade de Pagamento (CAPAG) do Tesouro Nacional na avaliação vigente, ano-base 2025', 1),
    r(' — é compradora direta para pavimentação em blocos, meios-fios e drenagem.'),
  ]),

  // --- P9: porto ---
  para([
    r('Há ainda potencial adicional não contabilizado nas projeções: o Terminal Portuário de Urussuquara (Petrocity), '),
    r('cujo processo de Licença Prévia tramita no IBAMA desde 2021, com EIA/Rima e audiência pública realizada em 2023', 1),
    r(', demandaria enrocamento e concreto em volume de outra ordem de grandeza caso as obras se confirmem. '),
    r('Até a última informação pública disponível a licença não havia sido emitida, razão pela qual o terminal é tratado como potencial, e não como premissa.', 1),
  ]),

  // --- P10: síntese ---
  para([
    r('Em síntese, ', 1),
    r('mesmo sob a definição mais conservadora de mercado — linha de base restrita a São Mateus e Conceição da Barra, com as praças disputadas de Jaguaré e Boa Esperança deixadas de fora e sem contar as obras —, a demanda corrente, de 235 a 275 mil t/ano, já supera o platô de produção do projeto, de 216 mil t/ano (82% do teto licenciado), que corresponde a 78–91% dessa demanda: a receita de regime cabe integralmente no mercado-base. Sobre essa base somam-se, como espaço de captura não incorporado às projeções, a demanda extraordinária das obras (70–100 mil t/ano) e as praças mantidas fora da linha de base (36–78 mil t/ano), o que perfaz de 305 a 375 mil t/ano durante a janela de obras.', 1),
    r(' Às obras cabe ainda outro papel: coincidem com a carência e o ramp-up (anos 1–3, vendas de 63 a 180 mil t/ano), absorvendo a produção inicial justamente no período de maturação comercial. Mercado estruturalmente deficitário'),
    r(' — sem produtor instalado na base, com o grosso do suprimento viajando de 60 a 140 km —', 1),
    r(', vantagem logística e cronologia favorável compõem um quadro de baixo risco de demanda para o financiamento pleiteado.'),
  ]),

  // --- P11: SUDENE ---
  para([
    r('O empreendimento situa-se na área de atuação da SUDENE, beneficiando-se dos instrumentos de fomento do FNE, e está alinhado às diretrizes da Política Nacional de Desenvolvimento Regional: substitui suprimento de longa distância por produção local, reduz custo de construção na região, gera emprego e renda no interior do Espírito Santo e fortalece a infraestrutura para os investimentos públicos e privados do norte capixaba.'),
  ], { after: 400 }),
];

// ---------- Nota de revisão ----------
function cel(txt, { bold, w, head } = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: 'F2F2F2' } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({
      spacing: { after: 0, line: 252 },
      children: [new TextRun({ text: txt, bold: !!bold, font: FONT, size: 17 })],
    })],
  });
}

const W = [2050, 3150, 3800];
const linhas = [
  ['Agregado de "R$ 950 milhões em obras"',
   'Suprimido o número agregado; as obras passam a ser itemizadas uma a uma, com valor e fonte.',
   'Não há fonte pública que declare esse total para São Mateus. O ~R$ 1 bilhão divulgado refere-se ao programa de macrodrenagem de Guriri (três etapas), não ao conjunto das obras do município — atribuí-lo ao município seria contestável pelo analista.'],
  ['Memória de cálculo do índice per capita e link da fonte',
   'Retirados do corpo da carta o cálculo "6.888.010,58 t ÷ 4.126.854 hab", o valor pontual de 1,66 t/hab/ano e o endereço do painel Power BI.',
   'O valor pontual não é publicado em nenhuma fonte localizável e a própria divisão resulta em 1,67, não 1,66. A carta passa a citar a faixa 1,6–1,7 t/hab/ano, declarada como estimativa própria; a metodologia fica no Estudo anexo, que é o lugar dela.'],
  ['Demanda de "285 mil t/ano" e de "275–350 mil t/ano"',
   'Substituídas pela faixa única de 235–275 mil t/ano do mercado-base de dois municípios.',
   'O texto anterior trazia três números divergentes para a mesma grandeza (220, 285 e 275–350 mil t/ano). A faixa nova é a do Estudo anexo e decorre do recorte conservador de São Mateus + Conceição da Barra.'],
  ['Núcleo de quatro municípios (208.951 hab)',
   'Reduzido ao mercado-base de São Mateus e Conceição da Barra (161.881 hab).',
   'Jaguaré tem produtor instalado e Boa Esperança gravita para Nova Venécia. Mantê-los na base inflaria a demanda com praças disputadas; eles passam a figurar como captura adicional, fora das projeções.'],
  ['"Mais populoso do norte do Espírito Santo"',
   'Trocado por "mais populoso da Microrregião Nordeste (Lei estadual nº 9.768/2011)".',
   'Linhares tem 183,8 mil habitantes (est. 2025) e é rotineiramente tratada como norte capixaba. Sem a qualificação da regionalização oficial, a frase é indefensável.'],
  ['Contorno ES-318: "R$ 164 mi, 24,6 km e três pontes"',
   'Mantido o valor de R$ 164 milhões; corrigidos a extensão (24,26 km) e o escopo (duas pontes sobre o rio Mariricu).',
   'O valor de R$ 164 milhões confere com o release mais recente do Governo do ES (nov/2025) — e é ele que prevalece sobre o R$ 190 milhões que constava da minuta anterior da carta. A terceira ponte pertence a outro contrato (rio Preto, na ES-010).'],
  ['BR-101: "21,6 km atravessando São Mateus"',
   'Corrigido para 21,6 km entre os km 50,3 e 134,1, distribuídos por cinco municípios.',
   'Os 21,6 km não estão todos em São Mateus: abrangem Conceição da Barra, São Mateus, Jaguaré, Sooretama e Linhares. As datas passam a refletir as duas etapas de entrega (fev/2027 e dez/2027).'],
  ['Guriri: "1 milhão de m² de vias e mais de 1 milhão de toneladas"',
   'Ajustado para 350 a 400 mil m² e da ordem de 500 mil toneladas de agregados.',
   'O número anterior contradizia o próprio Estudo de Mercado anexo, que dimensiona a malha principal do balneário em 350–400 mil m². As 75–90 mil t contabilizadas nas projeções permanecem inalteradas.'],
  ['Prefeitura: "nota máxima de capacidade de pagamento"',
   'Trocado por "classificação A na CAPAG do Tesouro Nacional (ano-base 2025)".',
   'A nota A está correta e é a melhor da série histórica do município, mas a metodologia vigente do Tesouro não a caracteriza como nota máxima.'],
  ['Porto de Urussuquara: "fase avançada de licenciamento" e "documentação entregue em janeiro/2025"',
   'Substituído por processo em trâmite no IBAMA desde 2021, com audiência pública em 2023 e sem licença emitida.',
   'A data de janeiro/2025 provavelmente reproduz matéria de dezembro/2024 que se referia a janeiro de 2024. Não há registro público de emissão da Licença Prévia, o que desaconselha a expressão "fase avançada".'],
  ['Concorrência: "único produtor de ~5 mil t/ano atende a região"; Rio Bananal "a ~73 km"',
   'Reescrito: nenhum produtor no mercado-base; Usibrita fora da base; maior produtor a cerca de 100 km.',
   'Rio Bananal está a ~78 km de São Mateus em linha reta, o que torna impossível a distância rodoviária de 73 km. A correção reforça a tese: o concorrente de porte está ainda mais longe do que se afirmava.'],
];

const nota = [
  new Paragraph({
    spacing: { before: 200, after: 60 },
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: 'BFBFBF', space: 10 } },
    children: [new TextRun({ text: 'NOTA DE REVISÃO — não integra o texto da carta', bold: true, color: GREY, font: FONT, size: 19 })],
  }),
  new Paragraph({
    spacing: { after: 160 },
    children: [new TextRun({
      text: 'Registro do que foi suprimido ou corrigido, para conferência antes do protocolo. Supressões não aparecem em vermelho no texto acima porque o trecho deixou de existir.',
      italics: true, color: GREY, font: FONT, size: 17,
    })],
  }),
  new Table({
    columnWidths: W,
    width: { size: W[0] + W[1] + W[2], type: WidthType.DXA },
    rows: [
      new TableRow({
        tableHeader: true,
        children: [cel('Item', { bold: true, w: W[0], head: true }), cel('O que mudou', { bold: true, w: W[1], head: true }), cel('Por quê', { bold: true, w: W[2], head: true })],
      }),
      ...linhas.map(([a, b, c]) => new TableRow({
        children: [cel(a, { w: W[0], bold: true }), cel(b, { w: W[1] }), cel(c, { w: W[2] })],
      })),
    ],
  }),
  new Paragraph({
    spacing: { before: 200 },
    children: [new TextRun({
      text: 'Pendência para o Estudo de Mercado anexo: harmonizar com esta revisão o valor do Contorno da ES-318 (hoje R$ 165 milhões), a distância de Rio Bananal (hoje ~73 km) e a posição populacional de São Mateus (hoje 7º; o correto é 8º pelo Censo 2022 e pela estimativa 2025).',
      italics: true, color: GREY, font: FONT, size: 17,
    })],
  }),
];

const doc = new Document({
  creator: 'Projet Consultoria & Investimentos',
  title: 'CIPREM — Carta Consulta, seção 3 revisada',
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    children: [titulo, legenda, ...corpo, ...nota],
  }],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(process.argv[2] || 'out.docx', b);
  console.log('ok');
});
