// Gera roteiro.md e roteiro-video-ciprem.docx a partir de scenes.json.
// Uso: NODE_PATH=<pasta com node_modules/docx> node build_roteiro.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, BorderStyle, LevelFormat, PageBreak,
} = require("docx");

const DIR = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(DIR, "scenes.json"), "utf8"));
const { meta, scenes, trilha } = data;

const fmt = (s) => {
  const m = Math.floor(s / 60);
  const sec = s - m * 60;
  return `${String(m).padStart(2, "0")}:${sec.toFixed(1).padStart(4, "0")}`;
};

// ---------- conteúdo (blocos neutros, renderizados em md e docx) ----------
const blocks = [];
const h1 = (t) => blocks.push({ t: "h1", text: t });
const h2 = (t) => blocks.push({ t: "h2", text: t });
const h3 = (t) => blocks.push({ t: "h3", text: t });
const p = (t) => blocks.push({ t: "p", text: t });
const ul = (items) => blocks.push({ t: "ul", items });
const kv = (rows) => blocks.push({ t: "kv", rows });
const tbl = (header, rows) => blocks.push({ t: "table", header, rows });
const pb = () => blocks.push({ t: "pagebreak" });

h1("Roteiro do vídeo comercial CIPREM");
p("Vídeo para o evento com construtoras, concreteiras e poder público de São Mateus/ES. Objetivo: fazer o público querer comprar os produtos da britagem e sair do evento com parcerias e pré-contratos encaminhados.");
p("Formato: 1 min 30 s de conteúdo novo depois da vinheta de abertura de 18 s (\"Grupo São Vicente apresenta\"). 16:9, 1920x1080, 25 fps. Sem locução: texto na tela + trilha + efeitos sonoros. Montagem prevista em Remotion.");
p("Regra de conteúdo: a carta consulta serviu de base para os argumentos, mas nenhum valor dela (investimento, receita, toneladas, quilômetros, percentuais, financiamento) entra no vídeo. Só entram produtos, vantagens e fatos qualitativos.");

h2("1. Estratégia de venda em 8 blocos");
p("A ordem das cenas segue um arco de decisão de compra. Cada bloco existe por um motivo:");
ul([
  "Gancho (0–8 s): uma frase que o público de São Mateus reconhece como verdade e que cria expectativa. \"Até agora\" abre a curiosidade.",
  "Dor (8–16 s): nomeia o problema que todo comprador de brita da região sente no bolso, o frete. Sem números, só a lógica: distância vira frete, frete vira custo.",
  "Solução (16–26 s): apresenta a CIPREM como a resposta local. É o ponto de virada da trilha e o maior impacto sonoro do vídeo.",
  "Produtos (26–42 s): mostra que existe fração para cada tipo de cliente. O comprador se enxerga na lista. Fecha com laboratório próprio, que responde à objeção de qualidade de uma pedreira nova.",
  "Quem entrega (42–56 s): responde à objeção \"vocês são novos\". O grupo já opera pedreiras iguais na Bahia e em Minas, com a mesma tecnologia. Licenças obtidas mostram que o projeto é real.",
  "Por que agora (56–66 s): urgência real, o ciclo de obras públicas do município. Quem constrói aqui precisa decidir fornecedor agora.",
  "Parceria (66–80 s): convite segmentado, cada público lê a sua oferta. Imagem de aperto de mão e da equipe.",
  "Chamada final (80–90 s): o que fazer nos próximos minutos, ali no evento. Contatos e assinatura.",
]);

h2("2. Identidade visual (herdada da vinheta)");
kv([
  ["Fundo", `Navy profundo ${meta.paleta.navy_fundo} (medido na vinheta); navy claro ${meta.paleta.navy_claro} para gradientes`],
  ["Texto", `Branco ${meta.paleta.branco}; prata metálica ${meta.paleta.prata_clara} → ${meta.paleta.prata_escura} para títulos com brilho`],
  ["Destaque", `Âmbar ${meta.paleta.ambar_destaque} (conversa com os uniformes laranja e com os números dourados dos clipes do grupo)`],
  ["Tipografia", `${meta.tipografia.familia}. Títulos: ${meta.tipografia.titulo}. Apoio: ${meta.tipografia.apoio}`],
  ["Enquadramento", `Barras cinematográficas de ${meta.letterbox_px} px em cima e embaixo em todo o vídeo, iguais às da vinheta`],
  ["Reveal", "Textos entram por máscara horizontal e brilho metálico da esquerda para a direita, como o logo da vinheta. Linha fina prata como divisor"],
  ["Regras de texto", "No máximo 2 linhas por título e 7 palavras por linha. Cada texto fica pelo menos 3 s na tela. Nunca dois textos novos no mesmo segundo"],
  ["Transições", "Os clipes do grupo já têm feixes de luz gravados; usar esses momentos como corte. Entre cenas: corte seco no hit da trilha ou fade de 8 frames"],
]);

pb();
h2("3. Roteiro cena a cena");
p(`Duração total do conteúdo: ${meta.duracao_conteudo_s} s (${meta.duracao_conteudo_frames} frames a ${meta.fps} fps), somando as 8 cenas abaixo. A vinheta de ${meta.vinheta.duracao_s} s toca antes, intacta, com o áudio original e crossfade de 1 s para a trilha nova.`);

for (const sc of scenes) {
  h3(`Cena ${sc.id} — ${sc.nome}  (${fmt(sc.start_s)} → ${fmt(sc.end_s)}, ${sc.durationFrames} frames)`);
  const f = sc.footage;
  let imagem;
  if (f.cortes) {
    imagem = f.descricao + "\n" + f.cortes.map((c, i) => `${i + 1}. ${c.arquivo} ${fmt(c.in_s)}–${fmt(c.out_s)}: ${c.descricao}`).join("\n");
  } else {
    imagem = `${f.arquivo} ${fmt(f.in_s)}–${fmt(f.out_s)}: ${f.descricao}`;
  }
  if (f.alternativa) imagem += `\nAlternativa: ${f.alternativa}`;
  const textos = [];
  textos.push(`${sc.title_in_s.toFixed(1)} s — TÍTULO: ${sc.title}`);
  if (sc.subtitle) textos.push(`${sc.subtitle_in_s.toFixed(1)} s — APOIO: ${sc.subtitle}`);
  if (sc.products) for (const pr of sc.products) textos.push(`${pr.in_s.toFixed(1)} s — ITEM: ${pr.nome} · ${pr.uso}`);
  if (sc.cards) for (const c of sc.cards) textos.push(`${c.in_s.toFixed(1)} s — CARTÃO ${c.para}: ${c.oferta}`);
  if (sc.extra) for (const e of sc.extra) textos.push(`${e.in_s.toFixed(1)} s — ${e.text}  [${e.style}]`);
  kv([
    ["Imagem", imagem],
    ["Tratamento", f.tratamento],
    ["Texto na tela", textos.join("\n")],
    ["Animação", sc.animation],
    ["Som e efeitos", sc.sfx],
    ["Trilha", sc.musicCue],
  ]);
}

pb();
h2("4. Trilha sonora e mixagem");
kv([
  ["Estilo", trilha.estilo],
  ["Estrutura", trilha.estrutura],
  ["Onde buscar", trilha.referencias_de_busca],
  ["Pontos de sincronia", trilha.pontos_de_sincronia_s.map((s) => `${s} s`).join(", ")],
  ["Mixagem", trilha.mixagem],
  ["Áudio dos clipes", meta.audio.clipes_originais],
  ["Vinheta", meta.audio.vinheta],
]);

h2("5. Inventário do material recebido");
p("Os três vídeos do Drive não são brutos: são trechos já editados, com mapas, títulos, feixes de luz e alguns números gravados na imagem. O roteiro escolhe só os trechos limpos ou com sobreposições aceitáveis.");
tbl(["Arquivo", "O que tem"], Object.entries(meta.footage).map(([k, v]) => [k, v]));
p("Trechos que NÃO devem entrar: novo_investimento 13–14 s (rótulo \"≈40 km\") e 26–35 s (investimento total e geração de empregos gravados, com valores diferentes dos da carta consulta). Os mapas e logos das outras empresas do grupo também ficam de fora, para o vídeo falar da CIPREM.");

h2("6. Textos alternativos para escolha");
tbl(["Cena", "Versão A (no roteiro)", "Versão B"], [
  ["1 Gancho", "SÃO MATEUS NUNCA TEVE UMA PEDREIRA PRÓPRIA. / ATÉ AGORA.", "A BRITA QUE SÃO MATEUS SEMPRE BUSCOU LONGE / AGORA NASCE AQUI."],
  ["3 Solução", "BRITA PRODUZIDA AQUI. ENTREGUE AQUI.", "DA JAZIDA À SUA OBRA, DENTRO DO MUNICÍPIO."],
  ["6 Por que agora", "QUEM CONSTRÓI AQUI PRECISA DE BRITA AQUI.", "AS OBRAS JÁ COMEÇARAM. O FORNECEDOR LOCAL TAMBÉM."],
  ["7 Parceria", "VAMOS CONSTRUIR SÃO MATEUS JUNTOS.", "SEJA PARCEIRO DESDE A PRIMEIRA TONELADA."],
  ["8 Chamada", "Parcerias e pré-contratos: fale com a nossa equipe hoje, aqui no evento.", "Garanta prioridade de fornecimento: converse com a equipe CIPREM antes de sair."],
]);

h2("7. Pendências antes de renderizar");
ul([
  "Contatos reais da cena 8 (WhatsApp comercial, Instagram, site).",
  "Logo da CIPREM em vetor (SVG ou PNG com fundo transparente) para as cenas 3 e 8. Se não existir, o nome entra em tipografia no mesmo estilo do logo do grupo.",
  "Trilha licenciada para uso comercial em evento, com marcações a cada 8 s.",
  "Opcional: drone das obras de Guriri e do Contorno ES-318 para substituir a cena 6.",
  "Confirmar com os sócios os fatos usados: mais de 20 anos do grupo, britadores Metso, laboratório próprio, licenças ANM e IEMA obtidas.",
  "Validar o texto do cartão \"Poder público\" com quem vai apresentar para a prefeitura.",
]);

h2("8. Próximo passo: montagem em Remotion");
ul([
  "Pasta footage/ com os 4 vídeos (vinheta + 3 clipes) já baixados no ambiente de trabalho; não entram no repositório.",
  "Uma composição de 25 fps, 1920x1080, com a vinheta (18.22 s) seguida das 8 cenas de scenes.json (2250 frames). Barras de 110 px sobre tudo.",
  "Cada cena lê do scenes.json: trecho de vídeo (startFrom/endAt), textos e tempos de entrada, tipo de animação. Mudar um texto é editar o JSON e renderizar de novo.",
  "Fonte Montserrat empacotada localmente. Trilha e efeitos entram como arquivos de áudio na pasta audio/.",
  "Remotion exige licença de empresa para uso comercial acima de 3 pessoas; conferir antes do uso final.",
]);

// ---------- render markdown ----------
let md = "";
for (const b of blocks) {
  if (b.t === "h1") md += `# ${b.text}\n\n`;
  else if (b.t === "h2") md += `## ${b.text}\n\n`;
  else if (b.t === "h3") md += `### ${b.text}\n\n`;
  else if (b.t === "p") md += `${b.text}\n\n`;
  else if (b.t === "ul") md += b.items.map((i) => `- ${i}`).join("\n") + "\n\n";
  else if (b.t === "kv") md += "| Campo | Conteúdo |\n|---|---|\n" + b.rows.map(([k, v]) => `| **${k}** | ${v.replace(/\n/g, "<br>")} |`).join("\n") + "\n\n";
  else if (b.t === "table") md += `| ${b.header.join(" | ")} |\n|${b.header.map(() => "---").join("|")}|\n` + b.rows.map((r) => `| ${r.map((c) => c.replace(/\n/g, "<br>")).join(" | ")} |`).join("\n") + "\n\n";
  else if (b.t === "pagebreak") md += "";
}
md += `_Gerado por build_roteiro.js a partir de scenes.json em ${new Date().toISOString().slice(0, 10)}._\n`;
fs.writeFileSync(path.join(DIR, "roteiro.md"), md);

// ---------- render docx ----------
const NAVY = "0B1F5C", AMBER = "D9A441", GREY = "F2F4F8";
const FONT = "Arial";
const runs = (text, opts = {}) => text.split("\n").flatMap((line, i) => (i === 0 ? [] : [new TextRun({ break: 1 })]).concat([new TextRun({ text: line, font: FONT, size: 20, ...opts })]));
const cell = (text, w, opts = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  shading: opts.shade ? { type: ShadingType.CLEAR, fill: opts.shade, color: "auto" } : undefined,
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  children: [new Paragraph({ children: runs(text, { bold: !!opts.bold, color: opts.color }) })],
});
const border = { style: BorderStyle.SINGLE, size: 4, color: "C9CED8" };
const borders = { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border };
const children = [];
for (const b of blocks) {
  if (b.t === "h1") children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: b.text, font: FONT, bold: true, color: NAVY, size: 48 })] }));
  else if (b.t === "h2") children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 120 }, children: [new TextRun({ text: b.text, font: FONT, bold: true, color: NAVY, size: 30 })] }));
  else if (b.t === "h3") children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 100 }, children: [new TextRun({ text: b.text, font: FONT, bold: true, color: AMBER, size: 24 })] }));
  else if (b.t === "p") children.push(new Paragraph({ spacing: { after: 140 }, children: runs(b.text) }));
  else if (b.t === "ul") for (const it of b.items) children.push(new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60 }, children: runs(it) }));
  else if (b.t === "kv") {
    children.push(new Table({ width: { size: 9600, type: WidthType.DXA }, columnWidths: [1900, 7700], borders,
      rows: b.rows.map(([k, v]) => new TableRow({ children: [cell(k, 1900, { bold: true, shade: GREY, color: NAVY }), cell(v, 7700)] })) }));
    children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  } else if (b.t === "table") {
    const n = b.header.length; const w = Math.floor(9600 / n); const widths = b.header.map((_, i) => (i === n - 1 ? 9600 - w * (n - 1) : w));
    children.push(new Table({ width: { size: 9600, type: WidthType.DXA }, columnWidths: widths, borders,
      rows: [new TableRow({ tableHeader: true, children: b.header.map((h, i) => cell(h, widths[i], { bold: true, shade: NAVY, color: "FFFFFF" })) })]
        .concat(b.rows.map((r) => new TableRow({ children: r.map((c, i) => cell(c, widths[i])) }))) }));
    children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  } else if (b.t === "pagebreak") children.push(new Paragraph({ children: [new PageBreak()] }));
}
children.push(new Paragraph({ spacing: { before: 300 }, children: runs(`Gerado por build_roteiro.js a partir de scenes.json em ${new Date().toISOString().slice(0, 10)}.`, { italics: true, color: "777777" }) }));

const doc = new Document({
  creator: "Projet Consultoria",
  title: "Roteiro do vídeo comercial CIPREM",
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children }],
});
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(path.join(DIR, "roteiro-video-ciprem.docx"), buf);
  console.log("ok: roteiro.md e roteiro-video-ciprem.docx gerados");
});
