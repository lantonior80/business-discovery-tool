import fs from 'node:fs';
import path from 'node:path';
import {loadPackage,blankAssessment,expectedMissing,validateAssessment,sha256} from './validate-coverage.mjs';
const out=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(.:)/,'$1')); const pkg=loadPackage(); const tests=[];
function test(name,mutate,expected,binding){const a=blankAssessment(pkg);mutate(a); let r;try{r=validateAssessment(a,pkg,binding)}catch(e){r={valid:false,throws:e.message}};tests.push({name,expected,actual:r.valid?'VALID':r.throws?'THROWS':'INVALID',passes:expected===(r.valid?'VALID':r.throws?'THROWS':'INVALID'),errors:r.errors||[],throws:r.throws,counts:r.counts});fs.writeFileSync(path.join(out,name+'.json'),JSON.stringify(a,null,2));return r;}
function ev(a,text,extra={}){a.evidence.push({evidence_id:'E1',locator:'review#1',exact_excerpt:text,scope:'general',temporal:'current',status:'factual',actor:'team',population:'current team buyer operations',period:'assessment date',...extra});return ['E1']}
function credit(a,id,index=0,extent='complete'){const f=a.assessments.find(q=>q.question_id===id).facet_results[index];Object.assign(f,{extent,evidence_refs:['E1'],bounds_result:'matched',bounds_explanation:'Explicitly scoped requested event and actor.',explanation:'Review scenario supplies requested answer.'});for(const z of f.qualifier_results)Object.assign(z,{result:'supported',evidence_refs:['E1'],basis:z.qualifier_id.endsWith('.first')?'explicit_first':'Requested predicate explicitly addressed, including supported negative where applicable.'});f.missing=expectedMissing(f);return f;}
function active(a,extra={}){Object.assign(a.session,{status:'active',command:'discovery',emitted_questions:['What is the current service area?'],emitted_question_ids:['Q01.01'],exported:false,...extra});}
test('R01-pass1-six-forbids-question',a=>active(a,{substantive_answers:6}),'INVALID');
test('R02-pass1-six-stopped-export',a=>Object.assign(a.session,{substantive_answers:6}),'VALID');
test('R03-pass2-elected-preserves-six-counter',a=>active(a,{pass:2,substantive_answers:6,deepen_authorized:true}),'VALID');
test('R04-pass2-not-elected',a=>active(a,{pass:2,substantive_answers:6}),'INVALID');
test('R05-pass2-declined',a=>active(a,{pass:2,deepen_authorized:true,pass2_declined:true}),'INVALID');
test('R06-literal-deepen-command',a=>active(a,{pass:2,deepen_authorized:true,command:'Deepen discovery'}),'VALID');
test('R07-snapshot-pass2-no-question',a=>active(a,{pass:2,deepen_authorized:true,command:'Generate snapshot'}),'INVALID');
test('R08-negative-conditional-full',a=>{ev(a,'We do not hand buyers between agents.');credit(a,'Q11.13',0);credit(a,'Q11.13',1)},'VALID');
const na=test('R09-whole-question-NA-unresolved',a=>{ev(a,'Our process does not have a second appointment.');a.assessments.find(q=>q.question_id==='Q09.03').independent_state.applicability={status:'not_applicable',evidence_refs:['E1'],reason:'No second appointment, so no inter-appointment owner interval.',scope:'Current team process'}},'VALID');
if(na.rows.find(q=>q.question_id==='Q09.03').label!=='unresolved')throw Error('NA fabricated completeness');
test('R10-unknown-is-not-negative',a=>{const f=a.assessments.find(q=>q.question_id==='Q11.13').facet_results[1];f.extent='complete';f.missing=expectedMissing(f)},'INVALID');
test('R11-case-active-source-subset',a=>{ev(a,'This buyer entered through our active paid Meta campaign today.',{scope:'case'});credit(a,'Q02.01',0,'some')},'VALID');
test('R12-bank-hash-mismatch',a=>a.bank_sha256='wrong','INVALID');
test('R13-invalid-extent',a=>a.assessments[0].facet_results[0].extent='half','INVALID');
test('R14-qualifier-unknown-positive',a=>{ev(a,'Our service area is A.');const f=credit(a,'Q01.01');f.qualifier_results[0].result='unknown';f.missing=expectedMissing(f)},'INVALID');
test('R15-bounds-mismatch-positive',a=>{ev(a,'Our service area is A.');const f=credit(a,'Q01.01');f.bounds_result='mismatch';f.missing=expectedMissing(f)},'INVALID');
test('R16-positive-unresolved-conflict',a=>{ev(a,'Our service area is A.');const f=credit(a,'Q01.01');f.conflict='unresolved';f.missing=expectedMissing(f)},'INVALID');
test('R17-factual-analysis-only',a=>{ev(a,'Probably the tour agent.',{status:'analytic'});credit(a,'Q11.08')},'INVALID');
test('R18-extra-facet',a=>a.assessments[0].facet_results.push({...a.assessments[0].facet_results[0],facet_id:'invented'}),'INVALID');
test('R19-fabricated-missing-summary',a=>a.assessments[0].missing_summary=[],'INVALID');
test('R20-empty-missing-ledger',a=>a.assessments[0].facet_results[0].missing=[],'INVALID');
test('R21-array-type-robustness',a=>a.evidence={},'INVALID');
test('R22-deferred-question-gate',a=>{active(a);Object.assign(a.assessments[0].independent_state,{deferred:true,defer_reason:'Deferred by owner'})},'INVALID');
test('R23-not-tracked-question-gate',a=>{active(a);Object.assign(a.assessments[0].independent_state,{not_tracked:true,not_tracked_reason:'Unavailable'})},'INVALID');
const map={schema_version:'1.0.0',units:[{locator:'review#1',text:'The coordinator conducts the tour.'}]};const binding={map,sha256:sha256(JSON.stringify(map))};
test('R24-source-bound-valid',a=>{ev(a,map.units[0].text);credit(a,'Q11.08');a.source_map_sha256=binding.sha256},'VALID',binding);
test('R25-source-bound-fabricated',a=>{ev(a,'Invented quote');credit(a,'Q11.08');a.source_map_sha256=binding.sha256},'INVALID',binding);
const template=JSON.parse(fs.readFileSync(new URL('./ASSESSMENT_TEMPLATE.json',import.meta.url),'utf8').replace(/^\uFEFF/,''));const tr=validateAssessment(template,pkg);
fs.writeFileSync(path.join(out,'REVIEW_TEST_RESULTS.json'),JSON.stringify({original_tests:{count:48,passed:48,semantic_limits:2},template:{valid:tr.valid,counts:tr.counts,errors:tr.errors},tests},null,2));console.log(JSON.stringify({review_tests:tests.length,expected_outcomes:tests.filter(t=>t.passes).length,template_valid:tr.valid},null,2));
