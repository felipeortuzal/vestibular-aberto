/* HTML/CSS/JS puro. Conteúdo textual entra no DOM por textContent. */
(function(){
  'use strict';
  const {questions,taxonomy,sources,inventory}=window.VA_DATA;
  const inventoryDocs=inventory?.documents||[];
  const C=window.VACore, $=id=>document.getElementById(id), KEY='vestibular-aberto.progress.v1';
  const empty=()=>({version:1,attempts:[],favorites:[]});
  let progress=empty(),page=1,view='questoes',toastTimer;
  const PAGE_SIZE=4, selected=new Map(),revealed=new Set();
  try{const saved=localStorage.getItem(KEY);if(saved)progress=C.cleanProgress(JSON.parse(saved),questions);}catch{$('storage-warning').hidden=false;}
  const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
  const button=(text,cls,fn)=>{const b=el('button',cls,text);b.type='button';b.addEventListener('click',fn);return b;};
  const link=(text,url,cls)=>{const a=el('a',cls,text);a.href=url;if(url.startsWith('https://')){a.target='_blank';a.rel='noopener noreferrer';}return a;};
  function toast(message){$('toast').textContent=message;$('toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').hidden=true,3500);}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(progress));$('storage-warning').hidden=true;}catch{$('storage-warning').hidden=false;}updateStats();}
  function updateStats(){const s=C.summary(questions,progress);$('question-total').textContent=questions.length;$('catalog-total').textContent=inventoryDocs.length;$('answered-total').textContent=s.answered;$('fav-count').textContent=progress.favorites.length;}
  function options(id,items,placeholder){const s=$(id);s.replaceChildren();const blank=el('option','',placeholder);blank.value='';s.append(blank);items.forEach(i=>{const o=el('option','',i.label);o.value=i.id;s.append(o);});}
  options('subject',taxonomy.subjects,'Todas as matérias');
  function syncTopics(){const sub=taxonomy.subjects.find(s=>s.id===$('subject').value);options('topic',sub?.topics||[],sub?'Todos os assuntos':'Escolha uma matéria');$('topic').disabled=!sub;syncSubtopics();}
  function syncSubtopics(){const sub=taxonomy.subjects.find(s=>s.id===$('subject').value),t=sub?.topics.find(t=>t.id===$('topic').value);options('subtopic',t?.subtopics||[],t?'Todos os subassuntos':'Escolha um assunto');$('subtopic').disabled=!t;}
  function filters(){return {institution:$('institution').value,subject:$('subject').value,topic:$('topic').value,subtopic:$('subtopic').value,status:$('status').value,search:$('search').value,includeDemo:$('include-demo').checked,favoritesOnly:view==='favoritas'};}
  function classification(q){const s=taxonomy.subjects.find(s=>s.id===q.classification.subjectId),t=s.topics.find(t=>t.id===q.classification.topicId),st=t.subtopics.find(t=>t.id===q.classification.subtopicId);return [s.label,t.label,st.label];}
  function makeCard(q){
    const article=el('article','question-card');article.id='card-'+q.id;
    const meta=el('div','question-meta');meta.append(el('span','badge','AUTORAL'),el('span','badge demo','DEMONSTRAÇÃO'),el('span','question-id',q.id.toUpperCase()));
    const favorite=button(progress.favorites.includes(q.id)?'★':'☆','favorite',()=>{const index=progress.favorites.indexOf(q.id);if(index<0)progress.favorites.push(q.id);else progress.favorites.splice(index,1);save();renderQuestions();if(view==='favoritas'&&index>=0){$('results-title').focus({preventScroll:true});}else{document.querySelector('#card-'+q.id+' .favorite')?.focus({preventScroll:true});}toast(index<0?'Questão salva nas favoritas.':'Questão removida das favoritas.');});
    favorite.setAttribute('aria-label',progress.favorites.includes(q.id)?'Remover '+q.id+' das favoritas':'Salvar '+q.id+' nas favoritas');favorite.setAttribute('aria-pressed',progress.favorites.includes(q.id));meta.append(favorite);
    article.append(meta,el('p','breadcrumb',classification(q).join('  ›  ')));
    const title=el('h3','',q.statement);title.id='title-'+q.id;article.append(title);article.setAttribute('aria-labelledby',title.id);
    const fieldset=el('fieldset','alternatives');fieldset.append(el('legend','','Escolha uma alternativa para '+q.id));
    const last=progress.attempts.filter(a=>a.questionId===q.id).at(-1),isRevealed=revealed.has(q.id);
    q.choices.forEach(c=>{const label=el('label','alternative');const radio=el('input');radio.type='radio';radio.name=q.id;radio.value=c.id;radio.checked=selected.get(q.id)===c.id;radio.disabled=isRevealed;radio.addEventListener('change',()=>{selected.set(q.id,c.id);submit.disabled=false;});label.append(radio,el('span','alt-letter',c.id),el('span','',c.text));if(isRevealed&&c.id===q.answer.choiceId)label.classList.add('correct');if(isRevealed&&c.id===last?.choiceId&&!last.correct)label.classList.add('wrong');fieldset.append(label);});article.append(fieldset);
    const actions=el('div','card-actions');actions.append(el('small','','Questão criada para testar a plataforma.'));
    const submit=button(isRevealed?'Tentar novamente':'Conferir resposta','button',()=>{
      if(revealed.has(q.id)){revealed.delete(q.id);selected.delete(q.id);renderQuestions();document.querySelector('#card-'+q.id+' input')?.focus({preventScroll:true});return;}
      const choiceId=selected.get(q.id);if(!choiceId){toast('Selecione uma alternativa.');return;}
      progress.attempts.push({questionId:q.id,choiceId,correct:choiceId===q.answer.choiceId,at:new Date().toISOString()});revealed.add(q.id);save();renderQuestions();const feedback=$('feedback-'+q.id);feedback?.focus({preventScroll:true});if(!feedback){$('results-title').focus({preventScroll:true});toast('Resposta registrada. A questão saiu do filtro atual.');}
    });submit.disabled=!isRevealed&&!selected.has(q.id);actions.append(submit);article.append(actions);
    if(isRevealed&&last){const feedback=el('div','feedback'+(last.correct?'':' wrong'));feedback.id='feedback-'+q.id;feedback.tabIndex=-1;feedback.setAttribute('role','status');feedback.append(el('strong','',last.correct?'Você acertou!':'Vamos entender: alternativa '+q.answer.choiceId+'.'),el('span','',q.explanation));article.append(feedback);}
    else if(last)article.append(el('p','small muted','Última tentativa: '+(last.correct?'acertou':'errou')+'. Você pode responder novamente.'));
    return article;
  }
  function renderQuestions(){
    const f=filters();let result=C.filterQuestions(questions,f,progress);
    if($('sort').value==='subject')result.sort((a,b)=>classification(a)[0].localeCompare(classification(b)[0],'pt-BR'));
    const pages=Math.max(1,Math.ceil(result.length/PAGE_SIZE));page=Math.min(page,pages);
    $('result-count').textContent=result.length+' '+(result.length===1?'questão encontrada':'questões encontradas');$('results-title').textContent=view==='favoritas'?'Suas questões favoritas':'Questões para praticar';
    const list=$('question-list');list.replaceChildren();
    if(!result.length){const box=el('div','empty-state');box.append(el('h3','','Ainda não há questões aqui.'),el('p','',f.institution&&f.institution!=='autoral'?'As questões oficiais desta instituição ainda não foram importadas. Consulte seu acervo ou explore as questões autorais.':'Nenhuma questão atende aos filtros. Limpe os filtros ou inclua os exemplos de demonstração.'));box.append(link('Consultar provas oficiais →','#provas','button outline'));list.append(box);}
    else result.slice((page-1)*PAGE_SIZE,page*PAGE_SIZE).forEach(q=>list.append(makeCard(q)));
    const pagination=$('pagination');pagination.replaceChildren();if(pages>1){const move=delta=>{page+=delta;renderQuestions();$('results-title').focus({preventScroll:true});$('results-title').scrollIntoView({block:'start'});};const prev=button('← Anterior','',()=>move(-1));prev.disabled=page===1;const next=button('Próxima →','',()=>move(1));next.disabled=page===pages;pagination.append(prev,el('span','','Página '+page+' de '+pages),next);}
  }
  function renderExams(){
    const box=$('exam-list');box.replaceChildren();
    const countByInstitution=id=>inventoryDocs.filter(d=>d.institutionId===id).length;
    sources.forEach((s,i)=>{
      const card=el('article','exam-card');
      card.append(el('span','number',String(i+1).padStart(2,'0')),el('span','badge','FONTE OFICIAL'),el('h3','',s.name),
        el('p','',s.description),link('Abrir diretório oficial ↗',s.url,'button outline'),
        el('p','small',countByInstitution(s.id)+' registros catalogados · 0 questões importadas'));
      box.append(card);
    });
    const typeLabels={booklet:'Caderno',commented_booklet:'Prova comentada',answer_key:'Gabarito',
      expected_answers:'Respostas esperadas',collection:'Coleção / índice'};
    const institution=$('inventory-institution').value,year=$('inventory-year').value,kind=$('inventory-type').value;
    const results=inventoryDocs.filter(d=>(!institution||d.institutionId===institution)&&(!year||String(d.editionYear)===year)&&(!kind||d.documentType===kind));
    $('inventory-total').textContent=results.length+' de '+inventoryDocs.length+' registros';
    const list=$('inventory-list');list.replaceChildren();
    if(!results.length){
      const emptyState=el('div','empty-state');
      emptyState.append(el('h3','','Nenhum registro com esses filtros.'),el('p','','Tente outra edição ou instituição. Não vamos inventar documentos para preencher a lista.'));
      list.append(emptyState);return;
    }
    const byInstitution=Object.fromEntries(sources.map(s=>[s.id,s.name]));
    results.forEach(d=>{
      const card=el('article','inventory-row');
      const main=el('div','inventory-body');
      const meta=el('div','inventory-meta');
      meta.append(el('span','inventory-label'+(d.sourceUrl?'':' pending'),d.sourceUrl?'LINK DE PDF':'ÍNDICE / PENDENTE'),
        el('span','',byInstitution[d.institutionId]||d.institutionId),
        el('span','',typeLabels[d.documentType]||'Documento'));
      if(d.admissionSemester)meta.append(el('span','',d.admissionSemester));
      if(d.applicationId)meta.append(el('span','',d.applicationId));
      if(d.bookletCode)meta.append(el('span','',d.bookletCode));
      if(d.school||d.course||d.campus)meta.append(el('span','',[d.school,d.course,d.campus].filter(Boolean).join(' · ')));
      main.append(meta,el('h4','',d.title),el('p','',d.notes||'Metadados localizados em fonte oficial. Reprodução integral não autorizada.'));
      const dest=d.sourceUrl||d.landingPageUrl;
      const open=link(d.sourceUrl?'Abrir PDF na fonte ↗':'Ver no acervo oficial ↗',dest,'inventory-link');
      card.append(el('div','inventory-year',String(d.editionYear)),main,open);
      list.append(card);
    });
  }
  function renderProgress(){const s=C.summary(questions,progress),box=$('progress-content');box.replaceChildren();box.append(el('h2','','Seu estudo até aqui'),el('p','muted','Os números usam sua última resposta em cada questão. Questões não respondidas ficam fora da taxa de acerto.'));
    const row=el('div','progress-summary');[[s.answered,'questões respondidas'],[s.accuracy===null?'—':s.accuracy+'%','acerto na última tentativa'],[s.attempts,'tentativas registradas']].forEach(([n,label])=>{const d=el('div','progress-box');d.append(el('strong','',n),el('span','',label));row.append(d);});box.append(row);
    const table=el('table','progress-table'),head=el('thead'),tr=el('tr');['Matéria','Respondidas','Acerto'].forEach(t=>{const th=el('th','',t);th.scope='col';tr.append(th);});head.append(tr);table.append(head);const body=el('tbody');taxonomy.subjects.forEach(subject=>{const subset=questions.filter(q=>q.classification.subjectId===subject.id),ids=new Set(subset.map(q=>q.id));const st=C.summary(subset,{attempts:progress.attempts.filter(a=>ids.has(a.questionId)),favorites:[]});if(st.answered){const r=el('tr');[subject.label,st.answered,st.accuracy+'%'].forEach(t=>r.append(el('td','',t)));body.append(r);}});table.append(body);if(s.answered)box.append(table);else box.append(el('p','coverage-note','Responda uma questão para começar a acompanhar seu desempenho.'));
  }
  function route(){const requested=location.hash.slice(1);view=['questoes','provas','favoritas','desempenho'].includes(requested)?requested:'questoes';document.querySelectorAll('nav a').forEach(a=>{const active=a.dataset.view===view;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});$('questions-view').hidden=!['questoes','favoritas'].includes(view);$('exams-view').hidden=view!=='provas';$('progress-view').hidden=view!=='desempenho';const copy={questoes:['Estude o conteúdo.\nEntenda a prova.','Pratique por assunto e consulte as provas anteriores direto na fonte.'],provas:['Cada prova tem\numa história.','Encontre cadernos, gabaritos e índices nas páginas oficiais — sem material inventado.'],favoritas:['Vale a pena\nvoltar aqui.','Suas questões marcadas para revisar, todas no mesmo lugar.'],desempenho:['O seu avanço\nem perspectiva.','Seu histórico local mostra acertos, novas tentativas e o que revisar.']};$('page-title').textContent=copy[view][0];$('page-description').textContent=copy[view][1];page=1;if(view==='provas')renderExams();else if(view==='desempenho')renderProgress();else renderQuestions();}
  $('filters').addEventListener('submit',e=>e.preventDefault());
  document.querySelectorAll('.topic-shortcut').forEach(b=>b.addEventListener('click',()=>{
    $('subject').value=b.dataset.subject;syncTopics();page=1;
    location.hash='#questoes';renderQuestions();
    $('results-title').scrollIntoView({block:'start'});
    $('results-title').focus({preventScroll:true});
  }));
  ['inventory-institution','inventory-year','inventory-type'].forEach(id=>$(id).addEventListener('change',renderExams));
  $('subject').addEventListener('change',()=>{syncTopics();page=1;renderQuestions();});$('topic').addEventListener('change',()=>{syncSubtopics();page=1;renderQuestions();});
  ['institution','subtopic','status','include-demo','sort'].forEach(id=>$(id).addEventListener('change',()=>{page=1;renderQuestions();}));$('search').addEventListener('input',()=>{page=1;renderQuestions();});
  $('filters').addEventListener('reset',()=>setTimeout(()=>{syncTopics();page=1;renderQuestions();},0));
  $('export-progress').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(progress,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=link('Exportar',url,'');a.download='vestibular-aberto-progresso.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $('import-trigger').addEventListener('click',()=>$('import-progress').click());
  $('import-progress').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>5*1024*1024)throw new Error('Arquivo maior que 5 MB.');const imported=C.cleanProgress(JSON.parse(await file.text()),questions);if(!confirm('Importar substituirá as respostas e favoritas deste navegador. Continuar?'))return;progress=imported;selected.clear();revealed.clear();save();renderProgress();toast('Progresso importado.');}catch(error){toast('Não foi possível importar. '+error.message);}finally{e.target.value='';}});
  $('reset-progress').addEventListener('click',()=>{if(confirm('Apagar respostas e favoritas deste navegador? Exporte uma cópia antes se quiser recuperá-las.')){progress=empty();revealed.clear();selected.clear();save();renderProgress();toast('Progresso apagado.');}});
  window.addEventListener('hashchange',route);updateStats();route();
})();
