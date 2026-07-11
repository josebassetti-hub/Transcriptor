// Mock local da API Anthropic — para testar o app no navegador SEM gastar créditos.
// Uso:  node verify/mock_anthropic.mjs        (sobe em http://127.0.0.1:8787)
// Depois, em ⚙️ Configurações do app, defina "Base da API Anthropic" = http://127.0.0.1:8787
// e uma chave qualquer. Serve /v1/messages: JSON p/ a estratégia, SSE p/ a síntese.
// Modos de erro:  adicione ?fail=401 | 429 | 529 | midstream à base (ex.: http://127.0.0.1:8787?fail=429)
import http from 'http';

const PORT = process.env.PORT || 8787;

const STRATEGY = JSON.stringify({
  doenca_en:'Multiple Myeloma', sinonimos:['plasma cell myeloma'], eh_rara:false,
  medicamentos_foco:['bortezomib','lenalidomide'], termo_ensaio:'multiple myeloma',
  queries_literatura:[{objetivo:'diretrizes', term:'"multiple myeloma"[tiab] AND guideline[pt] AND (english[la] OR portuguese[la])', retmax:3}]
});
const REPORT = [
'## Visão geral da doença','Relatório de demonstração (mock) [PMID 33921211].','',
'## Critérios diagnósticos e escores validados','IMWG: CRAB/SLiM.','',
'## Anamnese completa — perguntas que não podem faltar','- Exemplo de pergunta de alto rendimento.','',
'## Exame físico direcionado','- Exemplo.','',
'## Exames complementares recomendados','- Exemplo.','',
'## 🚩 Sinais de alarme (red flags)','- Exemplo de red flag.','',
'## Diagnósticos diferenciais que não podem ser esquecidos','- Exemplo.','',
'## Cruzamento com o paciente e aproximação diagnóstica','| Achado | Paciente | Status |','|---|---|---|','| Anemia | presente | presente |','',
'## Checklist de verificação','- [ ] Item 1','- [ ] Item 2','',
'## Tratamento','Fármaco X — confira dose no bulário/fonte oficial.','',
'## Monitoramento e sinais de piora','- Exemplo.','',
'## Armadilhas comuns de diagnóstico','- Exemplo.','',
'## Referências','- [PMID 33921211] Autor et al. Título. Revista, 2022.'
].join('\n');

function sse(md, midstreamErr){
  const out=[];
  out.push('event: message_start\ndata: {"type":"message_start","message":{"id":"mock","model":"mock"}}\n\n');
  out.push('event: content_block_start\ndata: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}\n\n');
  const chunks = md.match(/[\s\S]{1,60}/g) || [md];
  chunks.forEach((c,i)=>{
    if (midstreamErr && i===3){ out.push('event: error\ndata: {"type":"error","error":{"type":"overloaded_error","message":"mock overloaded"}}\n\n'); return; }
    out.push('event: content_block_delta\ndata: '+JSON.stringify({type:'content_block_delta',index:0,delta:{type:'text_delta',text:c}})+'\n\n');
  });
  if (!midstreamErr){
    out.push('event: content_block_stop\ndata: {"type":"content_block_stop","index":0}\n\n');
    out.push('event: message_delta\ndata: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":300}}\n\n');
    out.push('event: message_stop\ndata: {"type":"message_stop"}\n\n');
  }
  return out.join('');
}

http.createServer((req,res)=>{
  // CORS p/ chamadas do navegador (o app usa anthropic-dangerous-direct-browser-access)
  res.setHeader('Access-Control-Allow-Origin','*');
  res.setHeader('Access-Control-Allow-Headers','*');
  res.setHeader('Access-Control-Allow-Methods','POST,OPTIONS');
  if (req.method==='OPTIONS'){ res.writeHead(204); res.end(); return; }
  const fail=(req.url.match(/[?&]fail=(\w+)/)||[])[1];
  if (fail==='401'||fail==='429'||fail==='529'){
    res.writeHead(fail==='529'?529:parseInt(fail,10), {'Content-Type':'application/json', 'retry-after':'1'});
    res.end(JSON.stringify({type:'error', error:{type:'error', message:'mock '+fail}})); return;
  }
  let body=''; req.on('data',c=>body+=c); req.on('end',()=>{
    if (body.indexOf('"stream":true')>=0){
      res.writeHead(200, {'Content-Type':'text/event-stream'});
      res.end(sse(REPORT, fail==='midstream'));
    } else {
      res.writeHead(200, {'Content-Type':'application/json'});
      res.end(JSON.stringify({ id:'mock', type:'message', role:'assistant', model:'mock',
        content:[{type:'text', text:STRATEGY}], stop_reason:'end_turn', usage:{output_tokens:50} }));
    }
  });
}).listen(PORT, ()=>console.log('mock Anthropic em http://127.0.0.1:'+PORT+'  (defina como "Base da API" no app)'));
