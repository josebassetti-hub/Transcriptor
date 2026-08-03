// Renderiza a Memória de Cálculo de Quantitativos (DOCX) a partir do JSON de tools/gera_memoria.py
// Uso: node tools/memoria_docx.js memoria-data.json Memoria.docx
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  ShadingType, AlignmentType, HeadingLevel, BorderStyle, Footer, PageNumber, LevelFormat,
} = require('docx');

const [src, out] = process.argv.slice(2);
const D = JSON.parse(fs.readFileSync(src, 'utf8'));

const TEAL = '0F766E', TEAL_L = 'D6F0EC', ZEBRA = 'F1F5F9', LARANJA = 'B45309';
const fmt = (v, c = 2) => Number(v).toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c });
const border = { style: BorderStyle.SINGLE, size: 2, color: 'D0D7DE' };
const BORDERS = { top: border, bottom: border, left: border, right: border };

const P = (text, o = {}) => new Paragraph({
  children: [new TextRun({ text, size: o.size || 18, bold: o.bold, italics: o.italics, color: o.color })],
  spacing: { after: o.after ?? 60 }, alignment: o.align,
});
const H = (text, level) => new Paragraph({ heading: level, spacing: { before: 220, after: 90 },
  children: [new TextRun({ text, color: TEAL, bold: true })] });
const cell = (text, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA }, borders: BORDERS,
  shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill } : undefined,
  margins: { top: 40, bottom: 40, left: 70, right: 70 },
  children: [new Paragraph({
    alignment: o.align,
    children: [new TextRun({ text: String(text), size: o.size || 16, bold: o.bold, color: o.color })],
    spacing: { after: 0 },
  })],
});
const headerRow = (cols, widths, fill = TEAL) => new TableRow({ tableHeader: true,
  children: cols.map((c, i) => cell(c, widths[i], { bold: true, color: 'FFFFFF', fill, align: AlignmentType.CENTER })) });
const table = (widths, rows) => new Table({
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  columnWidths: widths, rows,
});

const kids = [];

// ── capa/cabeçalho ──
kids.push(new Paragraph({ spacing: { after: 40 },
  children: [new TextRun({ text: 'MEMÓRIA DE CÁLCULO DE QUANTITATIVOS', size: 34, bold: true, color: TEAL })] }));
kids.push(P(D.obra.nome, { size: 22, bold: true, after: 20 }));
kids.push(P(D.obra.local || '', { size: 18, color: '475569', after: 20 }));
kids.push(P(`Área construída ${fmt(D.obra.area)} m² · ${D.obra.pav} pavimentos · padrão ${D.obra.padrao} · ` +
  `BDI ${fmt(D.totais.bdi_pct, 1)}% · bases DER-ES Abr/2026 e SINAPI-ES 06/2026 (custo direto, BDI 0)`, { size: 17, after: 20 }));
kids.push(P(`Total geral de referência: R$ ${fmt(D.totais.total_geral_com_complemento)} ` +
  `(R$ ${fmt(D.totais.total_geral_com_complemento / D.obra.area)}/m²)`, { size: 18, bold: true, after: 160 }));

// ── 1. objeto ──
kids.push(H('1. Objeto e documentos de referência', HeadingLevel.HEADING_1));
kids.push(P('Este documento demonstra a origem de cada quantidade do orçamento, item a item, para conferência do ' +
  'responsável técnico. Documentos de base: (a) projeto arquitetônico executivo v02 (plantas, cortes, quadro de ' +
  'áreas e de esquadrias, planta de cobertura e de situação); (b) 12 imagens 3D do projeto (especificação de ' +
  'acabamentos); (c) Tabela Referencial DER-ES Abr/2026 e Cadernos Técnicos (critérios de medição); (d) SINAPI-ES ' +
  '06/2026 sem desoneração; (e) NBR 5410, 5626, 8160, 6120, 9050 e 14718. Projetos complementares (estrutural, ' +
  'elétrico, hidrossanitário, PPCI, climatização) NÃO foram fornecidos — as disciplinas correspondentes usam ' +
  'contagens sobre o arquitetônico, mínimos de norma e índices paramétricos, sempre com a classe de origem declarada.'));

// ── 2. classes ──
kids.push(H('2. Classificação da origem de cada quantidade', HeadingLevel.HEADING_1));
const CL = [['A', 'Medido no projeto — cotas, quadro de áreas/esquadrias, planta de cobertura ou de situação.'],
  ['B', 'Contado no projeto ou nas imagens 3D — peças, pontos, aparelhos, panos de parede.'],
  ['C', 'Calculado por fórmula (geometria, NBR ou regra do motor) — a expressão está exibida no item.'],
  ['D', 'Índice paramétrico (perfil estrutural comercial) — incerteza ±20%, exige projeto estrutural.'],
  ['E', 'Fechamento aritmético — saldo que garante a soma exata das áreas.'],
  ['F', 'Estimativa declarada (premissa) — a confirmar com projeto complementar ou decisão do cliente.']];
kids.push(table([800, 9300], [headerRow(['Classe', 'Significado'], [800, 9300]),
  ...CL.map(([a, b], i) => new TableRow({ children: [
    cell(a, 800, { bold: true, align: AlignmentType.CENTER, fill: i % 2 ? ZEBRA : 'FFFFFF' }),
    cell(b, 9300, { fill: i % 2 ? ZEBRA : 'FFFFFF' })] }))]));

// ── 3. ambientes ──
kids.push(H('3. Dados de entrada — quadro de ambientes (medido na planta)', HeadingLevel.HEADING_1));
const AW = [4300, 2000, 1900, 1900];
let soma = 0;
kids.push(table(AW, [headerRow(['Ambiente', 'Tipo', 'Área (m²)', 'Perímetro (m)'], AW),
  ...D.ambientes.map((a, i) => { soma += a.area; return new TableRow({ children: [
    cell(a.nome, AW[0], { fill: i % 2 ? ZEBRA : 'FFFFFF' }),
    cell(a.tipo, AW[1], { fill: i % 2 ? ZEBRA : 'FFFFFF' }),
    cell(fmt(a.area), AW[2], { align: AlignmentType.RIGHT, fill: i % 2 ? ZEBRA : 'FFFFFF' }),
    cell(fmt(a.per), AW[3], { align: AlignmentType.RIGHT, fill: i % 2 ? ZEBRA : 'FFFFFF' })] }); }),
  new TableRow({ children: [cell('SOMA (áreas úteis)', AW[0], { bold: true, fill: TEAL_L }),
    cell('', AW[1], { fill: TEAL_L }), cell(fmt(soma), AW[2], { bold: true, align: AlignmentType.RIGHT, fill: TEAL_L }),
    cell('', AW[3], { fill: TEAL_L })] })]));

// ── 4. geometria ──
kids.push(H('4. Geometria derivada', HeadingLevel.HEADING_1));
const GW = [3400, 1800, 4900];
kids.push(table(GW, [headerRow(['Grandeza', 'Valor', 'Origem / expressão'], GW),
  ...D.geometria.map((g, i) => new TableRow({ children: g.map((v, j) =>
    cell(v, GW[j], { fill: i % 2 ? ZEBRA : 'FFFFFF', align: j === 1 ? AlignmentType.RIGHT : undefined })) }))]));

// ── 5. itens DER-ES ──
kids.push(H('5. Memória por item — Tabela DER-ES', HeadingLevel.HEADING_1));
const IW = [1000, 2450, 900, 550, 4500, 700];
const itemRows = (itens) => itens.map((it, i) => new TableRow({ children: [
  cell(it.c, IW[0], { fill: i % 2 ? ZEBRA : 'FFFFFF' }),
  cell(it.d.length > 90 ? it.d.slice(0, 88) + '…' : it.d, IW[1], { fill: i % 2 ? ZEBRA : 'FFFFFF' }),
  cell(fmt(it.qtd), IW[2], { align: AlignmentType.RIGHT, fill: i % 2 ? ZEBRA : 'FFFFFF' }),
  cell(it.u, IW[3], { align: AlignmentType.CENTER, fill: i % 2 ? ZEBRA : 'FFFFFF' }),
  cell(it.mem, IW[4], { fill: i % 2 ? ZEBRA : 'FFFFFF' }),
  cell(it.classe, IW[5], { bold: true, align: AlignmentType.CENTER, fill: i % 2 ? ZEBRA : 'FFFFFF' })] }));
for (const s of D.secoes) {
  kids.push(H(`5.${s.cap} — Capítulo ${s.cap} · ${s.nome}`, HeadingLevel.HEADING_2));
  kids.push(table(IW, [headerRow(['Código', 'Serviço', 'Quant.', 'Und', 'Memória de cálculo', 'Cl.'], IW), ...itemRows(s.itens)]));
}

// ── 6. SINAPI ──
kids.push(H('6. Itens da tabela SINAPI-ES 06/2026', HeadingLevel.HEADING_1));
kids.push(table(IW, [headerRow(['Código', 'Composição', 'Quant.', 'Und', 'Memória de cálculo', 'Cl.'], IW, '15803D'),
  ...itemRows(D.sinapi)]));
kids.push(P(`Subtotal SINAPI (custo direto): R$ ${fmt(D.sinapi_tot.custo_direto)} · com BDI: R$ ${fmt(D.sinapi_tot.com_bdi)}. ` +
  'O SINAPI não publica caderno de critério de medição por composição — medição pela unidade da composição.',
  { italics: true, size: 16, after: 120 }));

// ── 7-8. verificações e apontamentos ──
const numbered = (arr, ref, color) => arr.map(t => new Paragraph({
  numbering: { reference: ref, level: 0 }, spacing: { after: 50 },
  children: [new TextRun({ text: t, size: 17, color })] }));
kids.push(H('7. Verificações de fechamento', HeadingLevel.HEADING_1));
kids.push(...numbered(D.verificacoes, 'chk'));
kids.push(H('8. Apontamentos da conferência (a validar com os projetos complementares)', HeadingLevel.HEADING_1));
kids.push(...numbered(D.apontamentos, 'apt', LARANJA));

// ── 9. substituições ──
if (D.substituicoes) {
  kids.push(H('9. Substituições para agente financeiro (resumo)', HeadingLevel.HEADING_1));
  const SW = [4200, 1900, 1900, 1100, 1000];
  const su = D.substituicoes;
  kids.push(table(SW, [headerRow(['Item de projeto', 'Valor de mercado', 'Valor de tabela', '% coberto', 'Grau'], SW, 'C2410C'),
    ...su.itens.map((x, i) => new TableRow({ children: [
      cell(x.item, SW[0], { fill: i % 2 ? ZEBRA : 'FFFFFF' }),
      cell('R$ ' + fmt(x.cotado), SW[1], { align: AlignmentType.RIGHT, fill: i % 2 ? ZEBRA : 'FFFFFF' }),
      cell('R$ ' + fmt(x.substituido), SW[2], { align: AlignmentType.RIGHT, fill: i % 2 ? ZEBRA : 'FFFFFF' }),
      cell(fmt(100 * x.substituido / x.cotado, 0) + '%', SW[3], { align: AlignmentType.RIGHT, fill: i % 2 ? ZEBRA : 'FFFFFF' }),
      cell(x.grau, SW[4], { bold: true, align: AlignmentType.CENTER, fill: i % 2 ? ZEBRA : 'FFFFFF' })] })),
    new TableRow({ children: [cell('TOTAL — diferença de escopo (recursos próprios do cliente)', SW[0], { bold: true, fill: 'FED7AA' }),
      cell('R$ ' + fmt(su.total_cotado), SW[1], { bold: true, align: AlignmentType.RIGHT, fill: 'FED7AA' }),
      cell('R$ ' + fmt(su.total_substituido), SW[2], { bold: true, align: AlignmentType.RIGHT, fill: 'FED7AA' }),
      cell('R$ ' + fmt(su.diferenca), SW[3], { bold: true, align: AlignmentType.RIGHT, fill: 'FED7AA' }),
      cell('', SW[4], { fill: 'FED7AA' })] })]));
  kids.push(P('Justificativas completas e componentes de cada substituição: aba 3 da planilha Excel do orçamento.',
    { italics: true, size: 16 }));
}

// ── 10-11. premissas e lacunas ──
kids.push(H('10. Premissas adotadas', HeadingLevel.HEADING_1));
kids.push(...numbered(D.premissas, 'pre'));
kids.push(H('11. Lacunas e pontos de atenção', HeadingLevel.HEADING_1));
kids.push(...numbered(D.lacunas, 'lac', LARANJA));

// ── 12. encerramento ──
kids.push(H('12. Encerramento', HeadingLevel.HEADING_1));
kids.push(P('Estudo indicativo por metodologia paramétrica sobre tabelas referenciais. Não substitui orçamento ' +
  'executivo com projetos complementares, nem dispensa responsável técnico. Toda quantidade classe D ou F deve ' +
  'ser revista quando os projetos das disciplinas forem emitidos.', { italics: true }));
kids.push(P(' ', { after: 300 }));
kids.push(P('_________________________________________', { after: 20 }));
kids.push(P('Responsável técnico — conferência e aprovação', { size: 16, color: '475569' }));

const doc = new Document({
  styles: { default: { document: { run: { font: 'Arial', size: 18 } } } },
  numbering: { config: ['chk', 'apt', 'pre', 'lac'].map(ref => ({
    reference: ref,
    levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START,
      style: { paragraph: { indent: { left: 360, hanging: 360 } } } }] })) },
  sections: [{
    properties: { page: { margin: { top: 850, bottom: 850, left: 850, right: 850 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'Memória de Cálculo de Quantitativos — ', size: 14, color: '64748B' }),
        new TextRun({ children: [PageNumber.CURRENT], size: 14, color: '64748B' }),
        new TextRun({ text: ' / ', size: 14, color: '64748B' }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 14, color: '64748B' })] })] }) },
    children: kids,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(out, b); console.log('gerado:', out, (b.length / 1024).toFixed(0) + ' KB'); });
