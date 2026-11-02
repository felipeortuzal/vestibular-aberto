(function(root){
  'use strict';
  const normalize=value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const scoreable=q=>q?.answer?.status==='authoral'||q?.answer?.status==='final'||q?.answer?.status==='corrected';
  function filterQuestions(questions,filters,progress){
    const latest=new Map(progress.attempts.map(a=>[a.questionId,a]));
    return questions.filter(q=>{
      const a=latest.get(q.id),tags=q.classification;
      const text=[q.statement,...(q.tags||[])].join(' ');
      return (filters.includeDemo||q.kind!=='demo') &&
        (!filters.institution||q.institutionId===filters.institution) &&
        (!filters.edition||String(q.editionYear||'')===String(filters.edition)) &&
        (!filters.semester||q.admissionSemester===filters.semester) &&
        (!filters.phase||q.phase===filters.phase) &&
        (!filters.school||(q.schools||[]).includes(filters.school)) &&
        (!filters.course||(q.courses||[]).includes(filters.course)) &&
        (!filters.subject||tags.subjectId===filters.subject) &&
        (!filters.topic||tags.topicId===filters.topic) &&
        (!filters.subtopic||tags.subtopicId===filters.subtopic) &&
        (!filters.search||normalize(text).includes(normalize(filters.search.trim()))) &&
        (!filters.favoritesOnly||progress.favorites.includes(q.id)) &&
        (!filters.status||(filters.status==='new'&&!a)||(filters.status==='correct'&&a?.correct===true)||(filters.status==='incorrect'&&a?.correct===false));
    });
  }
  function cleanProgress(raw,questions){
    if(!raw||raw.version!==1||!Array.isArray(raw.attempts)||!Array.isArray(raw.favorites))throw new Error('Formato de progresso inválido.');
    const byId=new Map(questions.map(q=>[q.id,q]));
    const attempts=raw.attempts.filter(a=>a&&byId.has(a.questionId)&&typeof a.at==='string'&&Number.isFinite(Date.parse(a.at))&&byId.get(a.questionId).choices.some(c=>c.id===a.choiceId)).slice(-50000).map(a=>{
      const q=byId.get(a.questionId),valid=scoreable(q);
      return {questionId:a.questionId,choiceId:a.choiceId,
        correct:valid?a.choiceId===q.answer.choiceId:null,
        at:a.at,answerRevision:q.answer.revision??null};
    });
    return {version:1,favorites:[...new Set(raw.favorites.filter(id=>byId.has(id)))],attempts};
  }
  function summary(questions,progress){
    const ids=new Set(questions.map(q=>q.id));
    const last=new Map(progress.attempts.filter(a=>ids.has(a.questionId)).map(a=>[a.questionId,a]));
    const scored=[...last.values()].filter(a=>a.correct===true||a.correct===false);
    const correct=scored.filter(a=>a.correct===true).length;
    return {answered:scored.length,correct,accuracy:scored.length?Math.round(correct/scored.length*100):null,
      attempts:progress.attempts.filter(a=>ids.has(a.questionId)).length};
  }
  const api={normalize,scoreable,filterQuestions,cleanProgress,summary};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.VACore=api;
})(typeof window!=='undefined'?window:this);
