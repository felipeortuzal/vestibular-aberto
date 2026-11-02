const {test}=require('node:test');
const assert=require('node:assert/strict');
const C=require('../assets/core.js');
const questions=require('../data/questions.json');
const empty={version:1,attempts:[],favorites:[]};
const base={includeDemo:true};
test('busca sem acentos e filtros combinados por hierarquia',()=>{
  assert.equal(C.filterQuestions(questions,{...base,search:'triangulo'},empty).length,1);
  assert.equal(C.filterQuestions(questions,{...base,subject:'matematica',topic:'matematica.geometria-plana'},empty).length,2);
  assert.equal(C.filterQuestions(questions,{...base,subject:'matematica',topic:'matematica.geometria-plana',subtopic:'matematica.geometria-plana.areas-de-figuras-planas'},empty)[0].id,'demo-001');
});
test('não disfarça demonstrações como provas oficiais',()=>{
  for(const institution of ['fuvest','unicamp','insper','fgv']) assert.equal(C.filterQuestions(questions,{...base,institution},empty).length,0);
  assert.equal(C.filterQuestions(questions,{includeDemo:false},empty).length,0);
});
test('última tentativa governa filtros sem contar repetição como questão nova',()=>{
  const p={...empty,attempts:[{questionId:'demo-001',correct:false},{questionId:'demo-001',correct:true}]};
  assert.equal(C.filterQuestions(questions,{...base,status:'incorrect'},p).length,0);
  assert.equal(C.filterQuestions(questions,{...base,status:'correct'},p).length,1);
  assert.deepEqual(C.summary(questions,p),{answered:1,correct:1,accuracy:100,attempts:2});
});
test('importação descarta ids inexistentes e recalcula acerto em vez de confiar no arquivo',()=>{
  const p=C.cleanProgress({version:1,favorites:['demo-001','demo-001','inventado'],attempts:[{questionId:'demo-001',choiceId:'A',correct:true,at:'2026-10-31T12:00:00Z'},{questionId:'inexistente',choiceId:'A',at:'2026-10-31T12:00:00Z'},{questionId:'demo-002',choiceId:'Z',at:'2026-10-31T12:00:00Z'}]},questions);
  assert.equal(p.attempts.length,1);assert.equal(p.attempts[0].correct,false);assert.deepEqual(p.favorites,['demo-001']);
});
test('formato de importação inválido é rejeitado',()=>{
  for(const value of [null,{},[],{version:2,attempts:[],favorites:[]}]) assert.throws(()=>C.cleanProgress(value,questions));
});
test('estado vazio não inventa taxa de acerto; favoritas respeitam filtros',()=>{
  assert.equal(C.summary(questions,empty).accuracy,null);
  assert.equal(C.filterQuestions(questions,{...base,favoritesOnly:true},{...empty,favorites:['demo-002']})[0].id,'demo-002');
  assert.equal(C.filterQuestions(questions,{...base,favoritesOnly:true,subject:'fisica'},{...empty,favorites:['demo-002']}).length,0);
});

test('estados vazios: matéria sem exemplo, termo inexistente e progresso novo',()=>{
  const used=new Set(questions.map(q=>q.classification.subjectId));
  const taxonomy=require('../data/taxonomy.json');
  const noExample=taxonomy.subjects.find(s=>!used.has(s.id));
  assert.ok(noExample, 'A V0 deve documentar ao menos uma matéria ainda sem exemplos.');
  assert.equal(C.filterQuestions(questions,{...base,subject:noExample.id},empty).length,0);
  assert.equal(C.filterQuestions(questions,{...base,search:'naoexiste123456'},empty).length,0);
  assert.deepEqual(C.summary(questions,empty),{answered:0,correct:0,accuracy:null,attempts:0});
});
test('último acerto define desempenho sem descartar histórico de erros',()=>{
  const wrong={questionId:'demo-001',choiceId:'A',correct:false,at:'2026-10-31T12:00:00Z'};
  const right={questionId:'demo-001',choiceId:'B',correct:true,at:'2026-10-31T12:01:00Z'};
  const p=C.cleanProgress({version:1,favorites:[],attempts:[wrong,right]},questions);
  assert.deepEqual(C.summary(questions,p),{answered:1,correct:1,accuracy:100,attempts:2});
  assert.equal(C.filterQuestions(questions,{...base,status:'incorrect'},p).length,0);
  assert.equal(C.filterQuestions(questions,{...base,status:'correct'},p).length,1);
});
test('importação rejeitada não altera dados anteriores',()=>{
  const old=C.cleanProgress({version:1,favorites:['demo-001'],attempts:[]},questions);
  assert.throws(()=>C.cleanProgress({version:999,favorites:[],attempts:[]},questions));
  assert.deepEqual(old,{version:1,favorites:['demo-001'],attempts:[]});
});

test('filtros do banco oficial combinam edição, semestre, fase, escola e curso',()=>{
  const q={...questions[0],id:'test-in-memory-only',kind:'official',institutionId:'unicamp',
    editionYear:2026,admissionSemester:'2026.2',phase:'1',
    schools:['Escola A'],courses:['Curso A']};
  const rows=[...questions,q];
  const filters={includeDemo:false,institution:'unicamp',edition:'2026',semester:'2026.2',
    phase:'1',school:'Escola A',course:'Curso A'};
  assert.deepEqual(C.filterQuestions(rows,filters,empty).map(x=>x.id),['test-in-memory-only']);
  assert.equal(C.filterQuestions(rows,{...filters,course:'Curso B'},empty).length,0);
  assert.equal(C.filterQuestions(rows,{...filters,semester:'2026.1'},empty).length,0);
  assert.equal(C.filterQuestions(rows,{...filters,includeDemo:true},empty).length,1);
});

test('gabarito corrigido recalcula último acerto sem inventar versão anterior',()=>{
  const q={...questions[0],id:'test-version-only',kind:'official',
    answer:{status:'corrected',choiceId:'A',revision:2}};
  const answer=C.cleanProgress({version:1,favorites:[],
    attempts:[{questionId:q.id,choiceId:'B',correct:true,answerRevision:1,at:'2026-10-30T12:00:00Z'}]},[q]);
  assert.equal(answer.attempts[0].correct,false);
  assert.equal(answer.attempts[0].answerRevision,2);
  assert.deepEqual(C.summary([q],answer),{answered:1,correct:0,accuracy:0,attempts:1});
});

test('anuladas e sem gabarito final não contam acerto nem erro',()=>{
  const q={...questions[0],id:'test-annulled-only',kind:'official',
    answer:{status:'annulled',choiceId:null,revision:3}};
  const p=C.cleanProgress({version:1,favorites:[],
    attempts:[{questionId:q.id,choiceId:'A',correct:false,at:'2026-10-30T12:00:00Z'}]},[q]);
  assert.equal(p.attempts[0].correct,null);
  assert.deepEqual(C.summary([q],p),{answered:0,correct:0,accuracy:null,attempts:1});
  assert.equal(C.filterQuestions([q],{includeDemo:false,status:'incorrect'},p).length,0);
});
