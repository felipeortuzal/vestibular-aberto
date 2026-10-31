/* Auditoria da V0 com Chrome/Chromium real via DevTools Protocol, sem dependências npm. */
'use strict';
const assert=require('node:assert/strict');
const {spawn,spawnSync}=require('node:child_process');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const http=require('node:http');
const dist=path.resolve(__dirname,'../dist');
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const chrome=['google-chrome','google-chrome-stable','chromium','chromium-browser'].find(name=>spawnSync('which',[name]).status===0);
async function main(){
  if(!chrome)throw new Error('Chrome ou Chromium não encontrado: teste visual obrigatório na CI.');
  assert.ok(fs.existsSync(path.join(dist,'index.html')),'Execute npm run build antes de test:browser.');
  const server=http.createServer((req,res)=>{
    try{
      const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      let file=path.resolve(dist,'.'+pathname);
      if(file!==dist&&!file.startsWith(dist+path.sep)){res.writeHead(403).end();return;}
      if(fs.statSync(file).isDirectory())file=path.join(file,'index.html');
      const ext=path.extname(file),types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.json':'application/json'};
      res.writeHead(200,{'Content-Type':(types[ext]||'application/octet-stream')+'; charset=utf-8'});
      res.end(fs.readFileSync(file));
    }catch{res.writeHead(404).end('Não encontrado');}
  });
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'vestibular-v0-'));
  let processChrome,ws,chromeErrors='';
  try{
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const url='http://127.0.0.1:'+server.address().port+'/';
    processChrome=spawn(chrome,['--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--remote-allow-origins=*','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{stdio:['ignore','ignore','pipe']});
    processChrome.stderr.on('data',chunk=>{chromeErrors+=chunk.toString();});
    const portFile=path.join(profile,'DevToolsActivePort');
    for(let n=0;n<120&&!fs.existsSync(portFile);n++)await sleep(100);
    assert.ok(fs.existsSync(portFile),'O Chrome ('+chrome+') não iniciou o protocolo de depuração: '+chromeErrors.slice(-2500)+'; exit='+processChrome.exitCode);
    const port=fs.readFileSync(portFile,'utf8').trim().split(/\s+/)[0];
    const tabs=await(await fetch('http://127.0.0.1:'+port+'/json')).json();
    const tab=tabs.find(t=>t.type==='page');
    assert.ok(tab,'Aba do Chrome ausente.');
    ws=new WebSocket(tab.webSocketDebuggerUrl);
    await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
    let next=0;
    const pending=new Map();
    ws.onmessage=event=>{
      const msg=JSON.parse(event.data);
      if(!msg.id)return;
      const p=pending.get(msg.id);if(!p)return;
      pending.delete(msg.id);
      if(msg.error)p.reject(new Error(JSON.stringify(msg.error)));else p.resolve(msg.result);
    };
    const send=(method,params={})=>new Promise((resolve,reject)=>{
      const id=++next;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));
    });
    const evaluate=async expression=>{
      const data=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
      if(data.exceptionDetails)throw new Error('Erro no navegador: '+JSON.stringify(data.exceptionDetails));
      return data.result.value;
    };
    const until=async (fn,msg)=>{
      for(let n=0;n<100;n++){try{if(await fn())return;}catch{}await sleep(100);}
      throw new Error('Tempo esgotado: '+msg);
    };
    const ready=()=>until(()=>evaluate("document.readyState==='complete'&&document.getElementById('question-total')?.textContent==='12'"),'inicialização da V0');
    const set=async (id,value,event='change')=>evaluate("(()=>{const el=document.getElementById("+JSON.stringify(id)+");el.value="+JSON.stringify(value)+";el.dispatchEvent(new Event("+JSON.stringify(event)+",{bubbles:true}));return document.getElementById('result-count').textContent;})()");
    await send('Page.enable');
    await send('Runtime.enable');
    await send('Page.navigate',{url});
    await ready();
    assert.equal(await evaluate("document.getElementById('answered-total').textContent"),'0');
    assert.equal(await evaluate("document.querySelectorAll('.question-card').length"),4);
    fs.mkdirSync(path.join(__dirname,'.screenshots'),{recursive:true});
    for(const width of [360,768,1440]){
      await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});
      await sleep(150);
      const measure=await evaluate("({width:innerWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth})");
      assert.equal(measure.width,width,'largura simulada incorreta');
      assert.ok(measure.document<=width+1&&measure.body<=width+1,'Overflow horizontal em '+width+' px: '+JSON.stringify(measure));
      const png=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
      fs.writeFileSync(path.join(__dirname,'.screenshots','v0-'+width+'.png'),Buffer.from(png.data,'base64'));
      console.log('OK layout '+width+' px, largura '+measure.document+' px');
    }
    await evaluate("location.hash='#provas'");
    await until(()=>evaluate("document.querySelectorAll('#inventory-list .inventory-row').length===29"),'inventário na biblioteca');
    assert.equal(await evaluate("document.querySelectorAll('#exam-list .exam-card').length"),4,'quatro diretórios oficiais');
    assert.equal(await evaluate("document.getElementById('catalog-total').textContent"),'29');
    await set('inventory-institution','unicamp');
    assert.equal(await evaluate("document.querySelectorAll('#inventory-list .inventory-row').length"),6);
    await set('inventory-year','2025');
    assert.equal(await evaluate("document.querySelectorAll('#inventory-list .inventory-row').length"),2);
    await set('inventory-institution','insper');
    assert.equal(await evaluate("document.querySelectorAll('#inventory-list .inventory-row').length"),0);
    await set('inventory-year','2026');
    assert.equal(await evaluate("document.querySelectorAll('#inventory-list .inventory-row').length"),2);
    assert.equal(await evaluate("[...document.querySelectorAll('#inventory-list .inventory-link')].every(x=>x.href.startsWith('https://www.vunesp.com.br/'))"),true);
    await set('inventory-institution','');
    await set('inventory-year','');
    for(const width of [360,768,1440]){
      await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});
      await sleep(140);
      const w=await evaluate("document.documentElement.scrollWidth");
      assert.ok(w<=width+1,'Overflow da biblioteca em '+width+': '+w);
      console.log('OK biblioteca '+width+' px, largura '+w+' px');
    }
    await evaluate("location.hash='#questoes'");
    await until(()=>evaluate("document.querySelectorAll('.question-card').length===4"),'retorno aos exercícios');
    await evaluate("document.getElementById('search').focus()");
    await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
    await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
    assert.equal(await evaluate('document.activeElement.id'),'institution','Ordem de Tab entre busca e vestibular');
    assert.match(await set('institution','fuvest'),/^0 /,'Nenhuma questão oficial deve aparecer');
    await set('institution','');
    const missing=await evaluate("(()=>{const used=new Set(window.VA_DATA.questions.map(q=>q.classification.subjectId));return [...document.getElementById('subject').options].map(o=>o.value).find(id=>id&&!used.has(id));})()");
    assert.ok(missing,'Matéria sem exemplo ausente');
    assert.match(await set('subject',missing),/^0 /);
    await set('subject','');
    assert.match(await set('search','naoexiste123456','input'),/^0 /);
    assert.match(await set('search','triangulo','input'),/^1 /,'Busca sem acentos');
    await set('search','','input');
    assert.match(await evaluate("document.getElementById('result-count').textContent"),/^12 /);
    await evaluate("document.querySelector('#pagination button:last-child').click()");
    assert.equal(await evaluate("document.getElementById('pagination').textContent.includes('Página 2 de 3')"),true);
    assert.equal(await evaluate("document.activeElement.id"),'results-title','O foco deve voltar ao título ao paginar');
    await evaluate("document.querySelector('#pagination button:first-child').click()");
    assert.equal(await evaluate("document.activeElement.id"),'results-title');
    await evaluate("document.querySelector('#card-demo-001 input[value=A]').click();document.querySelector('#card-demo-001 .card-actions button').click()");
    assert.equal(await evaluate("!!document.querySelector('#feedback-demo-001.wrong')"),true);
    assert.equal(await evaluate("document.activeElement.id"),'feedback-demo-001');
    await evaluate("document.querySelector('#card-demo-001 .card-actions button').click()");
    await evaluate("document.querySelector('#card-demo-001 input[value=B]').click();document.querySelector('#card-demo-001 .card-actions button').click()");
    assert.equal(await evaluate("!!document.querySelector('#feedback-demo-001:not(.wrong)')"),true);
    await evaluate("document.querySelector('#card-demo-001 .favorite').click();location.hash='#favoritas'");
    await until(()=>evaluate("document.getElementById('results-title').textContent==='Suas questões favoritas'"),'rota favoritas');
    assert.equal(await evaluate("document.querySelectorAll('.question-card').length"),1);
    await evaluate("document.querySelector('#card-demo-001 .favorite').click()");
    assert.equal(await evaluate("document.activeElement.id"),'results-title','Foco ao remover uma favorita');
    assert.match(await evaluate("document.getElementById('result-count').textContent"),/^0 /);
    await evaluate("location.hash='#desempenho'");
    await until(()=>evaluate("document.querySelectorAll('#progress-content .progress-box').length===3"),'rota desempenho');
    assert.deepEqual(await evaluate("[...document.querySelectorAll('.progress-box strong')].map(el=>el.textContent)"),['1','100%','2']);
    await evaluate("(()=>{const dt=new DataTransfer();dt.items.add(new File(['{invalido'],'ruim.json',{type:'application/json'}));const input=document.getElementById('import-progress');input.files=dt.files;input.dispatchEvent(new Event('change',{bubbles:true}));})()");
    await until(()=>evaluate("document.getElementById('toast').textContent.includes('Não foi possível importar')"),'importação inválida');
    assert.deepEqual(await evaluate("[...document.querySelectorAll('.progress-box strong')].map(el=>el.textContent)"),['1','100%','2']);
    await send('Page.reload');await sleep(300);await ready();
    assert.equal(await evaluate("document.getElementById('answered-total').textContent"),'1','Persistência após recarregar');
    const injection=await send('Page.addScriptToEvaluateOnNewDocument',{source:"Object.defineProperty(window,'localStorage',{configurable:true,get(){throw new Error('teste de armazenamento bloqueado')}});"});
    await send('Page.reload');await sleep(300);await ready();
    assert.equal(await evaluate("document.getElementById('storage-warning').hidden"),false,'Aviso de armazenamento bloqueado');
    assert.equal(await evaluate("document.getElementById('answered-total').textContent"),'0','Uso da memória temporária quando storage falha');
    await send('Page.removeScriptToEvaluateOnNewDocument',{identifier:injection.identifier});
    await send('Page.reload');await sleep(300);await ready();
    assert.equal(await evaluate("document.getElementById('answered-total').textContent"),'1','Falha temporária não apaga histórico persistido');
    console.log('OK navegador: filtros, busca, paginação, teclado, correção, repetição, favoritas, progresso, importação inválida, bloqueio e recuperação.');
  }finally{
    try{ws?.close();}catch{}
    if(processChrome)processChrome.kill();
    await new Promise(resolve=>server.close(resolve));
    try{fs.rmSync(profile,{recursive:true,force:true});}catch{}
  }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
