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
