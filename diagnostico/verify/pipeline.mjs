// Verificação do pipeline completo (normalizar→estratégia→fan-out→síntese→relatório)
// SEM rede: todas as fontes e a API Anthropic são interceptadas com fixtures via page.route.
// Uso: PW_CORE=/abs/playwright-core/index.js node verify/pipeline.mjs
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
const PORT = 8124;
const OUT = process.env.OUT_DIR || '/tmp/dx-verify';
fs.mkdirSync(OUT, { recursive: true });

const MIME = { '.html':'text/html', '.js':'text/javascript' };
const server = http.createServer((req,res)=>{
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p==='/favicon.ico'){ res.writeHead(204); res.end(); return; }
  if (p==='/'||p==='') p='/index.html';
  const fp = path.join(ROOT,p);
  if (!fp.startsWith(ROOT)||!fs.existsSync(fp)){ res.writeHead(404); res.end('nf'); return; }
  res.writeHead(200,{ 'Content-Type': MIME[path.extname(fp)]||'application/octet-stream' });
  res.end(fs.readFileSync(fp));
});

const results=[]; const rec=(n,ok,x='')=>{ results.push({n,ok}); console.log((ok?'✅':'❌')+' '+n+(x?('  '+x):'')); };

// ---- fixtures ----
const STRATEGY_JSON = JSON.stringify({
  doenca_en:'Multiple Myeloma', sinonimos:['plasma cell myeloma'], eh_rara:false,
  medicamentos_foco:['bortezomib','lenalidomide'], termo_ensaio:'multiple myeloma',
  queries_literatura:[{objetivo:'diretrizes', term:'"multiple myeloma"[tiab] AND guideline[pt]', retmax:3}]
});
const CALL1_BODY = JSON.stringify({
  id:'msg_1', type:'message', role:'assistant', model:'claude-sonnet-5',
  content:[{type:'text', text:STRATEGY_JSON}], stop_reason:'end_turn', usage:{output_tokens:50}
});
// SSE do relatório (mini, mas com várias seções e uma citação)
const REPORT_MD = [
'## Visão geral da doença','Mieloma múltiplo é neoplasia de plasmócitos [PMID 1].','',
'## Critérios diagnósticos e escores validados','Critérios IMWG (CRAB/SLiM).','',
'## Anamnese completa — perguntas que não podem faltar','- Dor óssea? Fadiga?','',
'## Exame físico direcionado','- Palidez, dor à palpação.','',
'## Exames complementares recomendados','- Eletroforese de proteínas, cálcio, função renal.','',
'## 🚩 Sinais de alarme (red flags)','- Hipercalcemia, insuficiência renal aguda.','',
'## Diagnósticos diferenciais que não podem ser esquecidos','- MGUS, metástases ósseas.','',
'## Cruzamento com o paciente e aproximação diagnóstica',
'| Achado esperado | Dado do paciente | Status |','|---|---|---|','| Anemia | Hb 9,2 | presente |','',
'## Checklist de verificação','- [ ] Solicitar eletroforese','- [ ] Dosar cálcio','',
'## Tratamento','Bortezomibe — confira dose no bulário/fonte oficial.','',
'## Monitoramento e sinais de piora','- Piora renal.','',
'## Armadilhas comuns de diagnóstico','- Atribuir dor a causa mecânica.','',
'## Referências','- [PMID 1] Autor et al. Multiple myeloma. Rev, 2022.'
].join('\n');
function sseReport(md){
  const parts=[];
  parts.push('event: message_start\ndata: {"type":"message_start","message":{"id":"m","model":"claude-sonnet-5"}}\n\n');
  parts.push('event: content_block_start\ndata: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}\n\n');
  // quebra em pedaços para exercitar o parser incremental
  const chunks = md.match(/[\s\S]{1,40}/g) || [md];
  for (const c of chunks){
    parts.push('event: content_block_delta\ndata: '+JSON.stringify({type:'content_block_delta',index:0,delta:{type:'text_delta',text:c}})+'\n\n');
  }
  parts.push('event: content_block_stop\ndata: {"type":"content_block_stop","index":0}\n\n');
  parts.push('event: message_delta\ndata: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":300}}\n\n');
  parts.push('event: message_stop\ndata: {"type":"message_stop"}\n\n');
  return parts.join('');
}
const ESEARCH = JSON.stringify({ esearchresult:{ idlist:['1','2'] } });
const ESEARCH_MESH = JSON.stringify({ esearchresult:{ idlist:['9'] } });
const ESUMMARY = JSON.stringify({ result:{ uids:['1','2'],
  '1':{ title:'Multiple myeloma diagnosis', fulljournalname:'Blood', pubdate:'2022 Jan', authors:[{name:'Rajkumar S'}], articleids:[{idtype:'doi',value:'10.1/a'}], pubtype:['Review'] },
  '2':{ title:'IMWG criteria update', fulljournalname:'Lancet', pubdate:'2021', authors:[{name:'Kumar S'}], articleids:[], pubtype:['Guideline'] } }});
const ESUMMARY_MESH = JSON.stringify({ result:{ uids:['9'], '9':{ ds_meshterms:['Multiple Myeloma'] } }});
const ESUMMARY_BOOKS = JSON.stringify({ result:{ uids:['b1'], 'b1':{ title:'Multiple Myeloma (StatPearls)', pubdate:'2023' }}});
const EPMC = JSON.stringify({ resultList:{ result:[
  { id:'PPR1', pmid:'3', title:'Systematic review of myeloma therapy', abstractText:'<b>Background</b> ...', journalInfo:{journal:{title:'Cochrane'}}, authorString:'Doe J', pubYear:'2023', doi:'10.2/b', pubType:'review' } ]}});
const FDA = JSON.stringify({ results:[ { openfda:{ generic_name:['bortezomib'] }, indications_and_usage:['Multiple myeloma'], dosage_and_administration:['1.3 mg/m2'], contraindications:['hypersensitivity'], warnings_and_cautions:['neuropathy'], drug_interactions:['CYP3A4'] } ]});
const CTGOV = JSON.stringify({ studies:[ { protocolSection:{ identificationModule:{ nctId:'NCT01234567', briefTitle:'Myeloma trial' }, statusModule:{ overallStatus:'RECRUITING' }, designModule:{ studyType:'INTERVENTIONAL', phases:['PHASE3'] } } } ]});
const MLP_XML = '<?xml version="1.0"?><nlmSearchResult><list><document url="https://medlineplus.gov/spanish/x.html"><content name="title">Mieloma múltiple</content><content name="FullSummary">Resumen ...</content></document></list></nlmSearchResult>';

await new Promise(r=>server.listen(PORT,r));
const base=`http://127.0.0.1:${PORT}/index.html`;
const browser=await chromium.launch({ executablePath:EXE, args:['--no-sandbox'] });
try{
  const ctx=await browser.newContext({ viewport:{width:1000,height:900} });
  const page=await ctx.newPage();
  const errs=[]; page.on('pageerror',e=>errs.push(String(e)));

  // interceptação de TODOS os hosts externos
  await ctx.route('**/*', async route=>{
    const u=route.request().url();
    const host=(()=>{ try{ return new URL(u).host; }catch(e){ return ''; } })();
    const j=(body)=>route.fulfill({ status:200, contentType:'application/json', body });
    if (host.startsWith('127.0.0.1')) return route.continue(); // app local
    if (host==='mock.anthropic.local'){
      const pd=route.request().postData()||'';
      if (pd.indexOf('"stream":true')>=0)
        return route.fulfill({ status:200, contentType:'text/event-stream', body:sseReport(REPORT_MD) });
      return route.fulfill({ status:200, contentType:'application/json', body:CALL1_BODY });
    }
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
  // configura chave + base mock via localStorage e recarrega
  await page.evaluate(()=>{ localStorage.setItem('dx.apikey','test-key');
    localStorage.setItem('dx.anthropic_base','https://mock.anthropic.local'); });
  await page.goto(base,{ waitUntil:'networkidle' });

  await page.click('#li_sem'); await page.waitForTimeout(80);
  await page.click('#ex_mm'); await page.waitForTimeout(120);   // preenche form MM
  await page.click('#f_ir');                                    // dispara pipeline

  // espera chegar ao relatório (streaming + fan-out)
  await page.waitForSelector('#rp_print', { timeout: 15000 });
  rec('pipeline chega ao relatório', true);

  const info = await page.evaluate(()=>{
    const chips=[...document.querySelectorAll('.chip')].map(c=>c.textContent);
    return { temAlarme: !!document.querySelector('.redflag'),
      temPMID: !!document.querySelector('.cita'),
      chips, temChecklist: !!document.querySelector('.chkitem'),
      html: document.querySelector('.rel') ? document.querySelector('.rel').innerText.length : 0 };
  });
  rec('relatório renderiza seção de alarme', info.temAlarme);
  rec('relatório tem citação PMID clicável', info.temPMID);
  rec('relatório tem checklist', info.temChecklist);
  rec('relatório com conteúdo substancial (>300 chars)', info.html>300, 'len='+info.html);
  const fontesChip = info.chips.find(c=>/fontes/.test(c));
  rec('fan-out coletou fontes (chip)', !!fontesChip && !/^0 /.test(fontesChip), fontesChip);
  rec('sem erro de JS no pipeline', errs.length===0, errs.join(' | '));
  await page.screenshot({ path: path.join(OUT,'07-pipeline-relatorio.png'), fullPage:true });

  // caminho degradado: fontes fora do ar → status sem_fontes
  await page.evaluate(()=>{ history.replaceState(null,'', location.pathname); });
  await ctx.unroute('**/*');
  await ctx.route('**/*', async route=>{
    const host=(()=>{ try{ return new URL(route.request().url()).host; }catch(e){ return ''; } })();
    if (host.startsWith('127.0.0.1')) return route.continue();
    if (host==='mock.anthropic.local'){ const pd=route.request().postData()||'';
      if (pd.indexOf('"stream":true')>=0) return route.fulfill({ status:200, contentType:'text/event-stream', body:sseReport(REPORT_MD) });
      return route.fulfill({ status:200, contentType:'application/json', body:CALL1_BODY }); }
    return route.abort(); // todas as fontes falham
  });
  await page.goto(base,{ waitUntil:'networkidle' });
  await page.click('#li_sem'); await page.waitForTimeout(60);
  await page.click('#ex_mm'); await page.waitForTimeout(80);
  await page.click('#f_ir');
  await page.waitForSelector('#rp_print', { timeout: 15000 });
  const semFontes = await page.evaluate(()=> !!document.querySelector('.banner.ambar'));
  rec('degradação: banner "sem verificação" quando fontes caem', semFontes);

}catch(e){ rec('exceção no harness', false, String(e)); }
finally{ await browser.close(); server.close(); }

const nFail=results.filter(r=>!r.ok).length;
console.log('\n== '+(results.length-nFail)+'/'+results.length+' ok · screenshots em '+OUT+' ==');
process.exit(nFail?1:0);
