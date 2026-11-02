/* HTML/CSS/JS puro. Conteúdo textual entra no DOM por textContent. */
(function(){
  'use strict';
  const {questions,taxonomy,sources,inventory,exams=[],publication={}}=window.VA_DATA;
  const official=questions.filter(q=>q.kind==='official');
  const institutionNames=Object.fromEntries(sources.map(x=>[x.id,x.name]));
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
  function updateStats(){const s=C.summary(questions,progress);$('question-total').textContent=questions.filter(q=>q.kind==='demo').length;$('catalog-total').textContent=inventoryDocs.length;$('official-total').textContent=official.length;$('answered-total').textContent=s.answered;$('fav-count').textContent=progress.favorites.length;}
  function options(id,items,placeholder){const s=$(id);s.replaceChildren();const blank=el('option','',placeholder);blank.value='';s.append(blank);items.forEach(i=>{const o=el('option','',i.label);o.value=i.id;s.append(o);});}
  options('subject',taxonomy.subjects,'Todas as matérias');
  options('institution',[...sources.map(x=>({id:x.id,label:x.name})),{id:'autoral',label:'Exercícios autorais'}],'Todos os vestibulares');
  function refreshAcademicFilters(){
    const institution=$('institution').value;
    const available=[...exams.map(e=>({institutionId:e.institutionId,editionYear:e.editionYear,
      admissionSemester:e.admissionSemester,phase:e.phase,schools:e.schools,courses:e.courses})),
      ...official];
    const scoped=available.filter(x=>!institution||institution===x.institutionId);
    const dimensions=[
      ['edition','editionYear','Todas as edições',x=>String(x)],
      ['semester','admissionSemester','Todos os semestres',x=>x],
      ['phase','phase','Todas as fases',x=>x],
      ['school','schools','Todas as escolas',x=>x],
      ['course','courses','Todos os cursos',x=>x]
    ];
    dimensions.forEach(([id,field,blank,format])=>{
      const previous=$(id).value;
      const unique=[...new Set(scoped.flatMap(x=>Array.isArray(x[field])?x[field]:x[field]==null?[]:[x[field]]))];
      const items=unique.sort((a,b)=>String(a).localeCompare(String(b),'pt-BR')).map(v=>({id:String(v),label:format(v)}));
      options(id,items,blank);$(id).disabled=!items.length;
      if(items.some(x=>x.id===previous))$(id).value=previous;
    });
  }
  refreshAcademicFilters();
  function syncTopics(){const sub=taxonomy.subjects.find(s=>s.id===$('subject').value);options('topic',sub?.topics||[],sub?'Todos os assuntos':'Escolha uma matéria');$('topic').disabled=!sub;syncSubtopics();}
  function syncSubtopics(){const sub=taxonomy.subjects.find(s=>s.id===$('subject').value),t=sub?.topics.find(t=>t.id===$('topic').value);options('subtopic',t?.subtopics||[],t?'Todos os subassuntos':'Escolha um assunto');$('subtopic').disabled=!t;}
  function filters(){return {institution:$('institution').value,edition:$('edition').value,semester:$('semester').value,phase:$('phase').value,school:$('school').value,course:$('course').value,subject:$('subject').value,topic:$('topic').value,subtopic:$('subtopic').value,status:$('status').value,search:$('search').value,includeDemo:$('include-demo').checked,favoritesOnly:view==='favoritas'};}
  function classification(q){const s=taxonomy.subjects.find(s=>s.id===q.classification.subjectId),t=s.topics.find(t=>t.id===q.classification.topicId),st=t.subtopics.find(t=>t.id===q.classification.subtopicId);return [s.label,t.label,st.label];}
  function renderBlocks(parent,blocks){
    for(const block of blocks||[]){
      if(block.type==='text'){
        parent.append(el('p','content-text',block.text));
      }else if(block.type==='math'){
        const math=el('span','math-accessible',block.altText);
        math.setAttribute('role','math');math.setAttribute('aria-label',block.altText);
        math.title='Notação LaTeX: '+block.latex;
        parent.append(math);
      }else if(block.type==='image'){
        const figure=el('figure','question-figure'),img=el('img');
        if(!/^assets\/official\/[a-z][a-z0-9-]{2,90}\.(png|jpg|webp)$/.test(block.url))continue;
        img.src=block.url;img.alt=block.altText;img.loading='lazy';img.decoding='async';
        figure.append(img);
        const caption=[block.caption,block.credit].filter(Boolean).join(' · ');
        if(caption)figure.append(el('figcaption','',caption));
        parent.append(figure);
      }else if(block.type==='table'){
        const wrap=el('div','content-table-wrap'),table=el('table','content-table');
        if(block.caption)table.append(el('caption','',block.caption));
        block.rows.forEach((r,i)=>{
          const tr=el('tr');
          r.forEach(v=>{const cell=el(i===0?'th':'td','',v);if(i===0)cell.scope='col';tr.append(cell);});
          if(i===0){const th=el('thead');th.append(tr);table.append(th);}
          else {let body=table.querySelector('tbody');if(!body){body=el('tbody');table.append(body);}body.append(tr);}
        });
        wrap.append(table);parent.append(wrap);
      }
    }
  }
  function makeCard(q){
    const isOfficial=q.kind==='official',scorable=C.scoreable(q);
    const article=el('article','question-card');article.id='card-'+q.id;
    const meta=el('div','question-meta');
    if(isOfficial){
      meta.append(el('span','badge','QUESTÃO OFICIAL'),el('span','badge',institutionNames[q.institutionId]||q.institutionId),
        el('span','question-id',String(q.editionYear)+' · QUESTÃO '+q.number));
    }else{
      meta.append(el('span','badge','AUTORAL'),el('span','badge demo','DEMONSTRAÇÃO'),el('span','question-id',q.id.toUpperCase()));
    }
    const favorite=button(progress.favorites.includes(q.id)?'★':'☆','favorite',()=>{
      const index=progress.favorites.indexOf(q.id);
      if(index<0)progress.favorites.push(q.id);else progress.favorites.splice(index,1);
      save();renderQuestions();
      if(view==='favoritas'&&index>=0)$('results-title').focus({preventScroll:true});
      else document.querySelector('#card-'+q.id+' .favorite')?.focus({preventScroll:true});
      toast(index<0?'Questão salva nas favoritas.':'Questão removida das favoritas.');
    });
    favorite.setAttribute('aria-label',progress.favorites.includes(q.id)?'Remover '+q.id+' das favoritas':'Salvar '+q.id+' nas favoritas');
    favorite.setAttribute('aria-pressed',progress.favorites.includes(q.id));meta.append(favorite);
    article.append(meta,el('p','breadcrumb',classification(q).join('  ›  ')));
    const title=el('h3','',isOfficial?'Questão '+q.number+' · '+(institutionNames[q.institutionId]||q.institutionId)+' '+q.editionYear:q.statement);
    title.id='title-'+q.id;article.append(title);article.setAttribute('aria-labelledby',title.id);
    if(isOfficial){
      const statement=el('div','question-content');renderBlocks(statement,q.contentBlocks);article.append(statement);
      const prov=el('p','source-line','Fonte: '+(q.organizer||institutionNames[q.institutionId])+
        ' · caderno '+(q.bookletCode||'não identificado')+' · página física '+q.provenance.page);
      article.append(prov,link('Consultar documento oficial ↗',q.provenance.url,'source-link'));
    }
    const fieldset=el('fieldset','alternatives');
    fieldset.append(el('legend','','Escolha uma alternativa para '+q.id));
    const last=progress.attempts.filter(a=>a.questionId===q.id).at(-1),isRevealed=revealed.has(q.id);
    q.choices.forEach(choice=>{
      const label=el('label','alternative'),radio=el('input');
      radio.type='radio';radio.name=q.id;radio.value=choice.id;
      radio.checked=selected.get(q.id)===choice.id;radio.disabled=isRevealed||!scorable;
      radio.addEventListener('change',()=>{selected.set(q.id,choice.id);submit.disabled=false;});
      label.append(radio,el('span','alt-letter',choice.label||choice.id));
      if(isOfficial){const blocks=el('div','choice-content');renderBlocks(blocks,choice.blocks);label.append(blocks);}
      else label.append(el('span','',choice.text));
      if(isRevealed&&choice.id===q.answer.choiceId)label.classList.add('correct');
      if(isRevealed&&choice.id===last?.choiceId&&last.correct===false)label.classList.add('wrong');
      fieldset.append(label);
    });
    article.append(fieldset);
    const actions=el('div','card-actions');
    actions.append(el('small','',isOfficial?
      'Gabarito '+(q.answer.status==='corrected'?'retificado':'final')+' · revisão '+q.answer.revision+
      ' · explicação editorial revisada':'Questão criada para testar a plataforma.'));
    const submit=button(isRevealed?'Tentar novamente':'Conferir resposta','button',()=>{
      if(revealed.has(q.id)){
        revealed.delete(q.id);selected.delete(q.id);renderQuestions();
        document.querySelector('#card-'+q.id+' input')?.focus({preventScroll:true});return;
      }
      if(!scorable){toast('Esta questão não possui gabarito final pontuável.');return;}
      const choiceId=selected.get(q.id);if(!choiceId){toast('Selecione uma alternativa.');return;}
      progress.attempts.push({questionId:q.id,choiceId,correct:choiceId===q.answer.choiceId,
        at:new Date().toISOString(),answerRevision:q.answer.revision??null,
        evaluatedAnswerRevision:q.answer.revision??null});
      revealed.add(q.id);save();renderQuestions();
      const feedback=$('feedback-'+q.id);feedback?.focus({preventScroll:true});
      if(!feedback){$('results-title').focus({preventScroll:true});toast('Resposta registrada. A questão saiu do filtro atual.');}
    });
    submit.disabled=!scorable||(!isRevealed&&!selected.has(q.id));
    actions.append(submit);article.append(actions);
    if(isRevealed&&last&&scorable){
      const feedback=el('div','feedback'+(last.correct?'':' wrong'));
      feedback.id='feedback-'+q.id;feedback.tabIndex=-1;feedback.setAttribute('role','status');
      feedback.append(el('strong','',last.correct?'Você acertou!':'Vamos entender: alternativa '+q.answer.choiceId+'.'));
      if(isOfficial)renderBlocks(feedback,q.explanationBlocks);
      else feedback.append(el('span','',q.explanation));
      article.append(feedback);
    }else if(last){
      article.append(el('p','small muted',last.correct===null?'Tentativa preservada sem pontuação.':
        'Última tentativa: '+(last.correct?'acertou':'errou')+'. Você pode responder novamente.'));
    }
    return article;
  }
  function renderQuestions(){
    const f=filters();let result=C.filterQuestions(questions,f,progress);
    if($('sort').value==='subject')result.sort((a,b)=>classification(a)[0].localeCompare(classification(b)[0],'pt-BR'));
    const pages=Math.max(1,Math.ceil(result.length/PAGE_SIZE));page=Math.min(page,pages);
    $('result-count').textContent=result.length+' '+(result.length===1?'questão encontrada':'questões encontradas');$('results-title').textContent=view==='favoritas'?'Suas questões favoritas':'Questões para praticar';
    const list=$('question-list');list.replaceChildren();
    if(!result.length){const box=el('div','empty-state');box.append(el('h3','','Ainda não há questões aqui.'),el('p','',f.institution&&f.institution!=='autoral'?'Ainda não há questões oficiais aprovadas com esses filtros. Consulte o caderno identificado e o estado de revisão em Provas.':'Nenhuma questão atende aos filtros. Limpe os filtros ou inclua os exemplos de demonstração.'));box.append(link('Consultar provas oficiais →','#provas','button outline'));list.append(box);}
    else result.slice((page-1)*PAGE_SIZE,page*PAGE_SIZE).forEach(q=>list.append(makeCard(q)));
    const pagination=$('pagination');pagination.replaceChildren();if(pages>1){const move=delta=>{page+=delta;renderQuestions();$('results-title').focus({preventScroll:true});$('results-title').scrollIntoView({block:'start'});};const prev=button('← Anterior','',()=>move(-1));prev.disabled=page===1;const next=button('Próxima →','',()=>move(1));next.disabled=page===pages;pagination.append(prev,el('span','','Página '+page+' de '+pages),next);}
  }
  function renderExamCatalog(){
    const institution=$('exam-institution').value,edition=$('exam-edition').value,phase=$('exam-phase').value;
    const items=exams.filter(x=>(!institution||x.institutionId===institution)&&
      (!edition||String(x.editionYear)===edition)&&(!phase||x.phase===phase));
    $('exam-catalog-total').textContent=items.length+' '+(items.length===1?'prova identificada':'provas identificadas');
    const box=$('official-exam-list');box.replaceChildren();
    if(!items.length){
      const emptyBox=el('div','empty-state');emptyBox.append(el('h3','','Nenhuma prova para esses filtros.'),
        el('p','','Ainda não temos uma prova individualizada nessa combinação. O inventário abaixo contém outras referências em pesquisa.'));
      box.append(emptyBox);return;
    }
    items.forEach(e=>{
      const card=el('article','exam-card real-exam');
      card.append(el('span','number',e.institutionId==='unicamp'?'COMVEST':e.organizer.toUpperCase()),
        el('span','badge demo',e.status==='metadata_only'?'REFERÊNCIA · NÃO IMPORTADA':'QUESTÕES APROVADAS'),
        el('h3','',e.title),
        el('p','',e.editionYear+' · fase '+e.phase+' · aplicado em '+e.appliedAt+
          (e.admissionSemester?' · ingresso '+e.admissionSemester:'')),
        el('p','',e.notes));
      const coverage=el('div','exam-coverage');
      coverage.append(el('strong','',e.approvedQuestionCount+' questões aprovadas'),
        el('span','',e.expectedQuestionCount===null?'Total de questões da prova: ainda não apurado':
          'Total de questões da prova: '+e.expectedQuestionCount),
        el('span','',e.pilotCandidates+' candidatas em revisão · não publicadas'));
      card.append(coverage);
      const links=el('div','exam-document-links');
      e.documents.forEach(d=>links.append(link((d.type==='commented_booklet'?'Prova comentada':d.title)+' ↗',d.url,'button outline')));
      card.append(links);
      if(e.finalAnswerDocumentStatus!=='verified')card.append(el('p','small muted',
        'Gabarito final/retificado: documento ainda não conciliado. Não há correção oficial publicada.'));
      box.append(card);
    });
  }
  function renderExams(){
    renderExamCatalog();
    const box=$('exam-list');box.replaceChildren();
    const countByInstitution=id=>inventoryDocs.filter(d=>d.institutionId===id).length;
    sources.forEach((s,i)=>{
      const card=el('article','exam-card');
      card.append(el('span','number',String(i+1).padStart(2,'0')),el('span','badge','FONTE OFICIAL'),el('h3','',s.name),
        el('p','',s.description),link('Abrir diretório oficial ↗',s.url,'button outline'),
        el('p','small',countByInstitution(s.id)+' registros catalogados · '+official.filter(q=>q.institutionId===s.id).length+' questões oficiais aprovadas'));
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
    const regraded=progress.attempts.filter(a=>a.answerRevision!=null&&
      a.evaluatedAnswerRevision!=null&&a.answerRevision!==a.evaluatedAnswerRevision).length;
    if(regraded)box.append(el('p','coverage-note',regraded+
      ' tentativa(s) foram reavaliadas com uma versão posterior do gabarito. O registro da versão original foi mantido.'));
    const table=el('table','progress-table'),head=el('thead'),tr=el('tr');['Matéria','Respondidas','Acerto'].forEach(t=>{const th=el('th','',t);th.scope='col';tr.append(th);});head.append(tr);table.append(head);const body=el('tbody');taxonomy.subjects.forEach(subject=>{const subset=questions.filter(q=>q.classification.subjectId===subject.id),ids=new Set(subset.map(q=>q.id));const st=C.summary(subset,{attempts:progress.attempts.filter(a=>ids.has(a.questionId)),favorites:[]});if(st.answered){const r=el('tr');[subject.label,st.answered,st.accuracy+'%'].forEach(t=>r.append(el('td','',t)));body.append(r);}});table.append(body);if(s.answered)box.append(table);else box.append(el('p','coverage-note','Responda uma questão para começar a acompanhar seu desempenho.'));
  }
  function route(){const requested=location.hash.slice(1);view=['questoes','provas','favoritas','desempenho'].includes(requested)?requested:'questoes';document.querySelectorAll('nav a').forEach(a=>{const active=a.dataset.view===view;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});$('questions-view').hidden=!['questoes','favoritas'].includes(view);$('exams-view').hidden=view!=='provas';$('progress-view').hidden=view!=='desempenho';const copy={questoes:['Estude o conteúdo.\nEntenda a prova.','Pratique por assunto e consulte as provas anteriores direto na fonte.'],provas:['Cada prova tem\numa história.','Encontre cadernos, gabaritos e índices nas páginas oficiais — sem material inventado.'],favoritas:['Vale a pena\nvoltar aqui.','Suas questões marcadas para revisar, todas no mesmo lugar.'],desempenho:['O seu avanço\nem perspectiva.','Seu histórico local mostra acertos, novas tentativas e o que revisar.']};$('page-title').textContent=copy[view][0];$('page-description').textContent=copy[view][1];page=1;if(view==='provas')renderExams();else if(view==='desempenho')renderProgress();else renderQuestions();}
  options('exam-institution',sources.map(x=>({id:x.id,label:x.name})),'Todas as instituições');
  options('exam-edition',[...new Set(exams.map(x=>x.editionYear))].sort((a,b)=>b-a).map(x=>({id:String(x),label:String(x)})),'Todas as edições');
  options('exam-phase',[...new Set(exams.map(x=>x.phase).filter(Boolean))].map(x=>({id:x,label:x})),'Todas as fases');
  ['exam-institution','exam-edition','exam-phase'].forEach(id=>$(id).addEventListener('change',renderExamCatalog));
  $('filters').addEventListener('submit',e=>e.preventDefault());
  document.querySelectorAll('.topic-shortcut').forEach(b=>b.addEventListener('click',()=>{
    $('subject').value=b.dataset.subject;syncTopics();page=1;
    location.hash='#questoes';renderQuestions();
    $('results-title').scrollIntoView({block:'start'});
    $('results-title').focus({preventScroll:true});
  }));
  ['inventory-institution','inventory-year','inventory-type'].forEach(id=>$(id).addEventListener('change',renderExams));
  $('subject').addEventListener('change',()=>{syncTopics();page=1;renderQuestions();});$('topic').addEventListener('change',()=>{syncSubtopics();page=1;renderQuestions();});
  $('institution').addEventListener('change',()=>{refreshAcademicFilters();page=1;renderQuestions();});
  ['edition','semester','phase','school','course','subtopic','status','include-demo','sort'].forEach(id=>$(id).addEventListener('change',()=>{page=1;renderQuestions();}));$('search').addEventListener('input',()=>{page=1;renderQuestions();});
  $('filters').addEventListener('reset',()=>setTimeout(()=>{refreshAcademicFilters();syncTopics();page=1;renderQuestions();},0));
  $('export-progress').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(progress,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=link('Exportar',url,'');a.download='vestibular-aberto-progresso.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $('import-trigger').addEventListener('click',()=>$('import-progress').click());
  $('import-progress').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>5*1024*1024)throw new Error('Arquivo maior que 5 MB.');const imported=C.cleanProgress(JSON.parse(await file.text()),questions);if(!confirm('Importar substituirá as respostas e favoritas deste navegador. Continuar?'))return;progress=imported;selected.clear();revealed.clear();save();renderProgress();toast('Progresso importado.');}catch(error){toast('Não foi possível importar. '+error.message);}finally{e.target.value='';}});
  $('reset-progress').addEventListener('click',()=>{if(confirm('Apagar respostas e favoritas deste navegador? Exporte uma cópia antes se quiser recuperá-las.')){progress=empty();revealed.clear();selected.clear();save();renderProgress();toast('Progresso apagado.');}});
  window.addEventListener('hashchange',route);updateStats();route();
})();
