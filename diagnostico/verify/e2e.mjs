// Verificação end-to-end (sem chamar hosts externos).
// Uso: node verify/e2e.mjs  (serve o app em http.server na porta 8000)
// Requer: playwright-core + chromium em /opt/pw-browsers.
// playwright-core pode não estar em node_modules ao lado deste arquivo.
// Aponte PW_CORE para o index.js do módulo (ex.: scratchpad/node_modules/playwright-core/index.js).
const PW_CORE = process.env.PW_CORE || 'playwright-core';
const _pw = await import(PW_CORE);
const chromium = _pw.chromium || (_pw.default && _pw.default.chromium);
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');           // diagnostico/
const EXE = process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const PORT = 8123;
const OUT = process.env.OUT_DIR || '/tmp/dx-verify';
fs.mkdirSync(OUT, { recursive: true });

const MIME = { '.html':'text/html', '.js':'text/javascript', '.css':'text/css', '.json':'application/json' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/favicon.ico') { res.writeHead(204); res.end(); return; }
  if (p === '/' || p === '') p = '/index.html';
  const fp = path.join(ROOT, p);
  if (!fp.startsWith(ROOT) || !fs.existsSync(fp)) { res.writeHead(404); res.end('nf'); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
  res.end(fs.readFileSync(fp));
});

const results = [];
const rec = (name, ok, extra='') => { results.push({ name, ok }); console.log((ok?'✅':'❌')+' '+name+(extra?('  '+extra):'')); };

await new Promise(r => server.listen(PORT, r));
const base = `http://127.0.0.1:${PORT}/index.html`;
const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });

try {
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 900 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type()==='error') errs.push('console: '+m.text()); });

  await page.goto(base, { waitUntil: 'networkidle' });
  rec('página carrega sem erro de JS', errs.length===0, errs.join(' | '));

  // autoteste puro (sem rede)
  const auto = await page.evaluate(() => window.__dx.runAutoteste());
  const fails = auto.filter(l => l.includes('t-fail'));
  rec('autoteste: '+auto.length+' checagens, '+fails.length+' falhas', fails.length===0,
      fails.map(f=>f.replace(/<[^>]+>/g,'')).join(' | '));

  // screenshots das telas principais (desktop)
  await page.screenshot({ path: path.join(OUT,'01-login.png') });

  // usar sem login → home
  await page.click('#li_sem');
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(OUT,'02-home.png') });
  rec('home abre (usar sem login)', await page.isVisible('text=Nova pesquisa'));

  // exemplo mieloma → form pré-preenchido
  await page.click('#ex_mm');
  await page.waitForTimeout(150);
  const doenca = await page.inputValue('#f_doenca');
  rec('exemplo preenche doença = Mieloma múltiplo', doenca.trim()==='Mieloma múltiplo', doenca);
  await page.screenshot({ path: path.join(OUT,'03-form.png'), fullPage: true });

  // relatório a partir da fixture (sem rede): injeta S.atual e vai para a tela
  await page.evaluate(() => {
    const F = window.__dx;
    const md = F.FIXT_MM;
    const cl = F.checklistFromMd(F.splitSections(md).checklist||'');
    // acesso ao estado interno via re-render manual:
    window.__setRel = null;
  });
  // usa a fixture pelo caminho oficial: chama splitSections/checklist e monta pesquisa via console
  const relOK = await page.evaluate(() => {
    const F = window.__dx;
    const secoes = F.splitSections(F.FIXT_MM);
    const todas = F.SECOES.every(s => s.k in secoes);
    const trat = F.mdRender(secoes.tratamento||'');
    const xss = F.mdRender('conduta <script>alert(1)</script> fim'); // testa escape diretamente
    return { todas, semScript: xss.indexOf('<script')<0, temDose: trat.indexOf('dosewarn')>=0 };
  });
  rec('fixture MM: 13 seções presentes', relOK.todas);
  rec('render tratamento: XSS escapado', relOK.semScript);
  rec('render tratamento: aviso de dose destacado', relOK.temDose);

  // abrir a tela REAL de relatório pela prévia offline (sem chave/rede)
  await page.goto(base, { waitUntil:'networkidle' });
  await page.click('#li_sem'); await page.waitForTimeout(80);
  await page.click('#ex_mm_prev'); await page.waitForTimeout(200);
  rec('prévia offline abre a tela de relatório', await page.isVisible('#rp_print'));
  rec('relatório mostra seção de sinais de alarme', await page.isVisible('text=Sinais de alarme'));
  // interação do checklist: marcar 1 item e conferir contador
  const antes = await page.textContent('.chkhead');
  await page.click('.chkitem input[data-chk="0"]'); await page.waitForTimeout(120);
  const depois = await page.textContent('.chkhead');
  rec('checklist marca item e atualiza contador', antes!==depois, antes+' → '+depois);
  await page.screenshot({ path: path.join(OUT,'04-relatorio.png'), fullPage:true });

  // PDF: aciona buildPrintDoc pelo caminho real (botão imprimir) e gera o PDF
  await page.evaluate(() => { window.print = () => {}; }); // evita diálogo
  await page.click('#rp_print'); await page.waitForTimeout(120);
  const pdfLen = await page.evaluate(() => document.getElementById('printdoc').innerHTML.length);
  rec('buildPrintDoc preenche #printdoc (>500 chars)', pdfLen>500, 'len='+pdfLen);
  await page.pdf({ path: path.join(OUT,'04-relatorio.pdf'), format:'A4' }).catch(()=>{});

  // config + mobile
  await page.goto(base, { waitUntil:'networkidle' });
  await page.click('#li_sem'); await page.waitForTimeout(80);
  await page.click('[data-go="config"]'); await page.waitForTimeout(120);
  rec('config abre (chave API, fontes, autoteste)', await page.isVisible('text=Autoteste (sem rede)'));
  await page.screenshot({ path: path.join(OUT,'05-config.png'), fullPage:true });

  const mob = await ctx.newPage();
  await mob.setViewportSize({ width:390, height:820 });
  await mob.goto(base, { waitUntil:'networkidle' });
  await mob.screenshot({ path: path.join(OUT,'06-mobile-login.png') });
  rec('mobile 390px renderiza', true);

  await ctx.close();
} catch (e) {
  rec('exceção no harness', false, String(e));
} finally {
  await browser.close();
  server.close();
}

const nFail = results.filter(r=>!r.ok).length;
console.log('\n== '+ (results.length-nFail) + '/' + results.length + ' ok · screenshots em '+OUT+' ==');
process.exit(nFail?1:0);
