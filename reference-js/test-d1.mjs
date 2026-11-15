import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {loadPackage,blankAssessment,expectedMissing,validateAssessment} from './validate-coverage.mjs';
const dir=path.dirname(fileURLToPath(import.meta.url)),pkg=loadPackage(),results=[];
const q=(a,id)=>a.assessments.find(q=>q.question_id===id),facet=(a,id)=>q(a,id).facet_results[0];
function ev(a,text,actor){const id='E'+(a.evidence.length+1);a.evidence.push({evidence_id:id,locator:'anonymous#'+id,exact_excerpt:text,scope:'case',temporal:'current',status:'factual',actor,population:'one buyer within explicitly stated service/tour scope',period:'current'});return id;}
function support(a,id,refs,extent='complete'){const f=facet(a,id);Object.assign(f,{extent,evidence_refs:refs,bounds_result:'matched',bounds_explanation:'Correct actor, event and declared scope',explanation:'The requested actor/action is stated within the source scope'});for(const z of f.qualifier_results)Object.assign(z,{result:'supported',evidence_refs:refs,basis:z.qualifier_id.endsWith('.first')?'explicit_first':'Explicit stated support'});f.missing=expectedMissing(f);return f;}
function check(name,a,want,label){const r=validateAssessment(a,pkg);assert.equal(r.valid,want,name+': '+r.errors.join('; '));if(label)assert.equal(r.rows.find(q=>q.question_id==='Q11.04').label,label);results.push({name,expected:want?'VALID':'INVALID',actual:r.outcome});return r;}
for(const id of ['Q03.04','Q13.08']){
 const bounds=pkg.rubric.questions.find(q=>q.question_id===id).facets[0].bounds.actor;assert(bounds.includes('VA')&&bounds.includes('agent'),'role alternatives retained');
 for(const role of ['agent','VA']){
  const a=blankAssessment(pkg),e=ev(a,id==='Q03.04'?`The assigned ${role} was responsible for the first contact with this buyer.`:`The assigned ${role} was absent, so the named backup covered this buyer.`,role);
  support(a,id,[e],id==='Q13.08'?'some':'complete');check(id+'-'+role+'-permitted',a,true);
 }
 {const a=blankAssessment(pkg),e=ev(a,'The assignee handled this buyer; their role is unknown.','unknown'),f=support(a,id,[e],id==='Q13.08'?'some':'complete');const role=f.qualifier_results.find(z=>z.qualifier_id.endsWith('.role'));role.result='unknown';f.missing=expectedMissing(f);check(id+'-unknown-role-not-positive',a,false);}
 {const a=blankAssessment(pkg),e=ev(a,'An unrelated agent acted on a different event.','agent'),f=support(a,id,[e],id==='Q13.08'?'some':'complete');f.bounds_result='mismatch';f.missing=expectedMissing(f);check(id+'-different-role-event-not-positive',a,false);}
}
function paperwork(text,scope='subset',extent='some'){const a=blankAssessment(pkg),e=ev(a,text,'named verifier'),f=support(a,'Q11.04',[e],extent);Object.assign(f,{component_scope:scope,component_scope_basis:scope==='subset'?'Only the identified agreement is established; other applicable paperwork remains unknown.':'All applicable paperwork in this specified service/tour scope is covered.',component_scope_evidence_refs:[e]});return a;}
check('one-agreement-verifier-before-tour-is-partial',paperwork('The coordinator verifies this required agreement is complete before the tour. Other required paperwork is not described.'),true,'partially_answered');
check('one-disclosure-verifier-before-service-is-partial',paperwork('The coordinator verifies this required disclosure is complete before the applicable service. Other required paperwork is not described.'),true,'partially_answered');
check('subset-cannot-claim-complete',paperwork('Only one agreement verifier is established before the tour.','subset','complete'),false);
const full=paperwork('The coordinator verifies completion of all disclosures and agreements applicable to this buyer before the services or tours requiring them.','all_applicable','complete');
const fullResult=check('all-applicable-verifier-before-correct-event-is-full',full,true,'fully_answered');assert.equal(fullResult.rows.find(q=>q.question_id==='Q11.04').positive_summary[0].component_scope,'all_applicable');
check('one-item-established-as-entire-applicable-set-is-full',paperwork('For this explicitly bounded service, the only applicable required paperwork is this agreement. The coordinator verifies its completion before that service; no disclosures are applicable.','all_applicable','complete'),true,'fully_answered');
for(const extent of ['some','complete']){
 const a=paperwork('The coordinator verifies paperwork but timing is unknown.',extent==='some'?'subset':'all_applicable',extent),f=facet(a,'Q11.04');f.qualifier_results[0].result='unknown';f.qualifier_results[0].basis='Before-event timing not established';f.missing=expectedMissing(f);check('unknown-before-timing-blocks-'+extent,a,false);
}
{const a=paperwork('The coordinator checks the agreement after the relevant service.');const f=facet(a,'Q11.04');f.qualifier_results[0].result='contradicted';f.missing=expectedMissing(f);check('after-service-does-not-meet-before',a,false);}
{const a=paperwork('Paperwork was checked before a later unrelated meeting, not the applicable tour.');const f=facet(a,'Q11.04');f.bounds_result='mismatch';f.missing=expectedMissing(f);check('before-wrong-event-not-positive',a,false);}
{const a=paperwork('A person was named but their paperwork scope was not established.','unknown');check('unknown-paperwork-scope-not-partial',a,false);}
{const a=paperwork('Subset checker before tour.');delete facet(a,'Q11.04').component_scope;check('missing-paperwork-scope-rejected',a,false);}
{const a=paperwork('Subset checker before tour.');facet(a,'Q11.04').component_scope_evidence_refs=[];check('paperwork-scope-needs-evidence',a,false);}
{const a=blankAssessment(pkg);a.rubric_sha256='frozen-D-hash';check('old-assessment-binding-not-accepted',a,false);}
fs.writeFileSync(path.join(dir,'D1_TEST_RESULTS.json'),JSON.stringify({tests:results.length,passed:results.length,semantic_limit:'Declarations and source entailment still need independent review; tests do not establish true roles or paperwork applicability from prose.',results},null,2)+'\n');console.log(results.length+'/'+results.length+' D1 tests passed');
