// Verifica o MODO DOSSIÊ gratuito (sem IA/sem chave) ponta a ponta.
// Todas as fontes são interceptadas com fixtures via page.route (nenhuma rede real).
const PW_CORE = process.env.PW_CORE || 'playwright-core';
const _pw = await import(PW_CORE);
const chromium = _pw.chromium || (_pw.default && _pw.default.chromium);
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const EXE = process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const PORT = 8126;
const OUT = process.env.OUT_DIR || '/tmp/dx-verify';
fs.mkdirSync(OUT, { recursive: true });

const server = http.createServer((req,res)=>{
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p==='/favicon.ico'){ res.writeHead(204); res.end(); return; }
  if (p==='/'||p==='') p='/index.html';
  const fp = path.join(ROOT,p);
  if (!fp.startsWith(ROOT)||!fs.existsSync(fp)){ res.writeHead(404); res.end('nf'); return; }
  res.writeHead(200,{ 'Content-Type': p.endsWith('.html')?'text/html':'application/octet-stream' });
  res.end(fs.readFileSync(fp));
});

const results=[]; const rec=(n,ok,x='')=>{ results.push({n,ok}); console.log((ok?'✅':'❌')+' '+n+(x?('  '+x):'')); };

const ESEARCH = JSON.stringify({ esearchresult:{ idlist:['1','2'] } });
const ESEARCH_MESH = JSON.stringify({ esearchresult:{ idlist:['9'] } });
const ESUMMARY = JSON.stringify({ result:{ uids:['1','2'],
  '1':{ title:'Multiple myeloma: a review', fulljournalname:'Blood', pubdate:'2023', authors:[{name:'A'}], articleids:[], pubtype:['Review'] },
  '2':{ title:'IMWG guideline update', fulljournalname:'Lancet Oncol', pubdate:'2024', authors:[{name:'B'}], articleids:[], pubtype:['Guideline'] } }});
const ESUMMARY_MESH = JSON.stringify({ result:{ uids:['9'], '9':{ ds_meshterms:['Multiple Myeloma'] } }});
const ESUMMARY_BOOKS = JSON.stringify({ result:{ uids:['b1'], 'b1':{ title:'Multiple Myeloma (StatPearls)', pubdate:'2024' }}});
const EPMC = JSON.stringify({ resultList:{ result:[
  { id:'PPR9', pmid:'3', title:'Bispecifics in myeloma (preprint)', abstractText:'BCMA/GPRC5D...', journalInfo:{journal:{title:'medRxiv'}}, authorString:'C', pubYear:'2025', doi:'', pubType:'preprint' } ]}});
const FDA = JSON.stringify({ results:[ { openfda:{ generic_name:['bortezomib'] }, indications_and_usage:['Multiple myeloma'], dosage_and_administration:['1.3 mg/m2'], warnings_and_cautions:['neuropathy'] } ]});
const CTGOV = JSON.stringify({ studies:[
  { protocolSection:{ identificationModule:{ nctId:'NCT05555555', briefTitle:'Anito-cel (anitocabtagene) phase 2' }, statusModule:{ overallStatus:'RECRUITING' }, designModule:{ studyType:'INTERVENTIONAL', phases:['PHASE2'] } } },
  { protocolSection:{ identificationModule:{ nctId:'NCT06666666', briefTitle:'Mezigdomide SUCCESSOR-2' }, statusModule:{ overallStatus:'ACTIVE_NOT_RECRUITING' }, designModule:{ studyType:'INTERVENTIONAL', phases:['PHASE3'] } } } ]});
const MLP_XML = '<?xml version="1.0"?><nlmSearchResult><list><document url="https://medlineplus.gov/spanish/x.html"><content name="title">Mieloma múltiple</content><content name="FullSummary">Resumen</content></document></list></nlmSearchResult>';

await new Promise(r=>server.listen(PORT,r));
const base=`http://127.0.0.1:${PORT}/index.html`;
const browser=await chromium.launch({ executablePath:EXE, args:['--no-sandbox'] });
try{
  const ctx=await browser.newContext({ viewport:{width:1000,height:900} });
  const page=await ctx.newPage();
  const errs=[]; page.on('pageerror',e=>errs.push(String(e)));

  await ctx.route('**/*', async route=>{
    const u=route.request().url();
    const host=(()=>{ try{ return new URL(u).host; }catch(e){ return ''; } })();
    const j=(b)=>route.fulfill({ status:200, contentType:'application/json', body:b });
    if (host.startsWith('127.0.0.1')) return route.continue();
    if (host.indexOf('eutils.ncbi')>=0){
      if (u.indexOf('esearch')>=0) return j(u.indexOf('db=mesh')>=0?ESEARCH_MESH:ESEARCH);
      if (u.indexOf('esummary')>=0){ if(u.indexOf('db=mesh')>=0) return j(ESUMMARY_MESH);
        if(u.indexOf('db=books')>=0) return j(ESUMMARY_BOOKS); return j(ESUMMARY); }
      return j('{}');
    }
    if (host.indexOf('ebi.ac.uk')>=0) return j(EPMC);
    if (host.indexOf('api.fda.gov')>=0) return j(FDA);
    if (host.indexOf('clinicaltrials.gov')>=0) return j(CTGOV);
    if (host.indexOf('nlm.nih.gov')>=0) return route.fulfill({ status:200, contentType:'text/xml', body:MLP_XML });
    return route.fulfill({ status:404, body:'' });
  });

  await page.goto(base,{ waitUntil:'networkidle' });
  await page.click('#li_sem'); await page.waitForTimeout(80);      // usar sem login (SEM chave)
  await page.click('[data-go="form"]'); await page.waitForTimeout(80);
  await page.fill('#f_doenca','Mieloma múltiplo');
  rec('botão de dossiê grátis visível sem chave', await page.isVisible('#f_dossie'));
  rec('botão de IA oculto sem chave', !(await page.isVisible('#f_ir')));
  await page.click('#f_dossie');
  await page.waitForSelector('#rp_print', { timeout: 15000 });
  rec('dossiê chega ao relatório', true);

  const info = await page.evaluate(()=>({
    temEnsaios: document.body.innerText.indexOf('Ensaios clínicos')>=0,
    temDiretrizes: document.body.innerText.indexOf('Diretrizes')>=0,
    temNCT: !!document.querySelector('a.cita'),
    temLinkExterno: !!document.querySelector('.rel a[href^="https://"]'),
    chipDossie: [...document.querySelectorAll('.chip')].some(c=>/dossiê/.test(c.textContent)),
    txtLen: (document.querySelector('.rel')||{innerText:''}).innerText.length
  }));
  rec('dossiê tem seção de ENSAIOS/tratamentos experimentais', info.temEnsaios);
  rec('dossiê tem seção de diretrizes', info.temDiretrizes);
  rec('dossiê tem citação NCT clicável', info.temNCT);
  rec('dossiê tem link externo real', info.temLinkExterno);
  rec('chip "dossiê grátis" presente', info.chipDossie);
  rec('conteúdo substancial (>300)', info.txtLen>300, 'len='+info.txtLen);
  rec('sem erro de JS', errs.length===0, errs.join(' | '));
  await page.screenshot({ path: path.join(OUT,'08-dossie.png'), fullPage:true });

  // impressão do dossiê
  await page.evaluate(()=>{ window.print=()=>{}; });
  await page.click('#rp_print'); await page.waitForTimeout(100);
  const plen=await page.evaluate(()=>document.getElementById('printdoc').innerHTML.length);
  rec('impressão do dossiê montada (>300)', plen>300, 'len='+plen);
}catch(e){ rec('exceção', false, String(e)); }
finally{ await browser.close(); server.close(); }

const nFail=results.filter(r=>!r.ok).length;
console.log('\n== '+(results.length-nFail)+'/'+results.length+' ok ==');
process.exit(nFail?1:0);
