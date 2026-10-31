(function(root){
  'use strict';
  const normalize=value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  function filterQuestions(questions, filters, progress){
    const latest=new Map(progress.attempts.map(a=>[a.questionId,a]));
    return questions.filter(q=>{
      const a=latest.get(q.id), tags=q.classification;
      return (filters.includeDemo||q.kind!=='demo') && (!filters.institution||q.institutionId===filters.institution) &&
        (!filters.subject||tags.subjectId===filters.subject) && (!filters.topic||tags.topicId===filters.topic) &&
        (!filters.subtopic||tags.subtopicId===filters.subtopic) &&
        (!filters.search||normalize(q.statement+' '+q.tags.join(' ')).includes(normalize(filters.search.trim()))) &&
        (!filters.favoritesOnly||progress.favorites.includes(q.id)) &&
        (!filters.status||(filters.status==='new'&&!a)||(filters.status==='correct'&&a?.correct===true)||(filters.status==='incorrect'&&a?.correct===false));
    });
  }
  function cleanProgress(raw,questions){
    if(!raw||raw.version!==1||!Array.isArray(raw.attempts)||!Array.isArray(raw.favorites))throw new Error('Formato de progresso inválido.');
    const byId=new Map(questions.map(q=>[q.id,q]));
    const attempts=raw.attempts.filter(a=>a&&byId.has(a.questionId)&&typeof a.at==='string'&&Number.isFinite(Date.parse(a.at))&&byId.get(a.questionId).choices.some(c=>c.id===a.choiceId)).slice(-50000).map(a=>({questionId:a.questionId,choiceId:a.choiceId,correct:a.choiceId===byId.get(a.questionId).answer.choiceId,at:a.at}));
    return {version:1,favorites:[...new Set(raw.favorites.filter(id=>byId.has(id)))],attempts};
  }
  function summary(questions,progress){
    const last=new Map(progress.attempts.map(a=>[a.questionId,a]));
    const correct=[...last.values()].filter(a=>a.correct).length;
    return {answered:last.size,correct,accuracy:last.size?Math.round(correct/last.size*100):null,attempts:progress.attempts.length};
  }
  const api={normalize,filterQuestions,cleanProgress,summary};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.VACore=api;
})(typeof window!=='undefined'?window:this);
