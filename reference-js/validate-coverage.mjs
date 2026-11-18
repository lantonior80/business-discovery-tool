import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const HOME=path.dirname(fileURLToPath(import.meta.url));
export const sha256=b=>crypto.createHash('sha256').update(b).digest('hex');
const parse=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const nonempty=x=>typeof x==='string'&&x.trim().length>0;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const missingCodes=['no_answer','incomplete_component','qualifier_unknown','qualifier_contradicted','bounds_unknown','bounds_mismatch','unresolved_conflict'];
export function loadPackage(dir=HOME){
 const manifest=parse(path.join(dir,'MANIFEST.json')),rubric=parse(path.join(dir,'COVERAGE_RUBRIC.json'));
 const bank=fs.readFileSync(path.join(dir,'QUESTION_BANK.md'));
 const errors=[];
 if(sha256(bank)!==manifest.bank_sha256)errors.push('QUESTION_BANK.md: immutable bank hash mismatch');
 if(sha256(fs.readFileSync(path.join(dir,'COVERAGE_RUBRIC.json')))!==manifest.rubric_sha256)errors.push('COVERAGE_RUBRIC.json: frozen rubric hash mismatch');
 const qs=[...bank.toString('utf8').matchAll(/<!-- (Q\d{2}\.\d{2}) -->\s*\d+\. \*\*\[([EDO])\]\*\* ([^\r\n]+)/g)].map(m=>({question_id:m[1],priority:m[2],question_text:m[3]}));
 const n=manifest.question_count;if(!Number.isInteger(n)||n<1||qs.length!==n||!same(qs,manifest.question_manifest))errors.push('MANIFEST: exact question count/IDs/text/priorities do not match bank');
 if(!Array.isArray(rubric.questions)||rubric.questions.length!==qs.length)errors.push('RUBRIC: question count must match the bank');
 const seenQ=new Set(),seenF=new Set();
 for(const [i,q] of (rubric.questions||[]).entries()){
  if(seenQ.has(q.question_id))errors.push(q.question_id+': duplicate rubric question');seenQ.add(q.question_id);
  if(!same({question_id:q.question_id,priority:q.priority,question_text:q.question_text},qs[i]))errors.push(q.question_id+': exact manifest mismatch');
  if(!['factual','evaluative','mixed'].includes(q.mode))errors.push(q.question_id+': invalid mode');
  if(!Array.isArray(q.facets)||!q.facets.length)errors.push(q.question_id+': empty facets');
  for(const f of q.facets||[]){
   if(!nonempty(f.facet_id)||seenF.has(f.facet_id))errors.push(q.question_id+': invalid/duplicate facet ID');seenF.add(f.facet_id);
   if(!nonempty(f.proposition)||typeof f.required_for_full!=='boolean'||typeof f.allows_some!=='boolean')errors.push(f.facet_id+': invalid facet definition');
   if(!['factual','evaluative','mixed'].includes(f.mode)||!['general_required','general_for_complete','bounded_answer'].includes(f.scope_policy))errors.push(f.facet_id+': invalid mode/scope');
   const seen=new Set();for(const z of f.material_qualifiers||[]){if(!nonempty(z.qualifier_id)||seen.has(z.qualifier_id)||!nonempty(z.requirement))errors.push(f.facet_id+': invalid qualifier');seen.add(z.qualifier_id);}
   for(const k of ['actor','event','population','time','unit'])if(!nonempty(f.bounds?.[k]))errors.push(f.facet_id+': missing bound '+k);
  }
 }
 if(errors.length)throw Error(errors.join('\n'));
 return {manifest,rubric};
}
export function expectedMissing(f){
 const out=[];
 if(f.extent==='none')out.push({code:'no_answer'});
 if(f.extent==='some')out.push({code:'incomplete_component'});
 for(const q of (Array.isArray(f.qualifier_results)?f.qualifier_results:[]).filter(q=>q&&typeof q==='object'))if(['unknown','contradicted'].includes(q.result))out.push({code:'qualifier_'+q.result,qualifier_id:q.qualifier_id});
 if(['unknown','mismatch'].includes(f.bounds_result))out.push({code:'bounds_'+f.bounds_result});
 if(f.conflict==='unresolved')out.push({code:'unresolved_conflict'});
 return out;
}
function canonicalMissing(a){return [...a].map(x=>JSON.stringify(x)).sort();}
export const defaultIndependentState=()=>({applicability:{status:'unknown',evidence_refs:[],reason:'Not assessed',scope:'Unknown'},deferred:false,defer_reason:'',not_tracked:false,not_tracked_reason:'',conflicts:[]});
export function blankAssessment(pkg=loadPackage()){
 return {schema_version:'1.0.0',bank_sha256:pkg.manifest.bank_sha256,rubric_sha256:pkg.manifest.rubric_sha256,
  session:{status:'stopped',command:'Generate snapshot',timing_reliable:false,substantive_answers:0,budget_minutes:12,active_minutes:null,pass:1,deepen_authorized:false,pass2_declined:false,emitted_questions:[],exported:true},
  evidence:[],context:[],assessments:pkg.rubric.questions.map(q=>({question_id:q.question_id,question_text:q.question_text,priority:q.priority,independent_state:defaultIndependentState(),facet_results:q.facets.map(f=>{
   const r={facet_id:f.facet_id,extent:'none',evidence_refs:[],qualifier_results:f.material_qualifiers.map(z=>({qualifier_id:z.qualifier_id,result:'unknown',evidence_refs:[],basis:'Not established'})),bounds_result:'unknown',bounds_explanation:'No answer evidence yet',conflict:'none',missing:[],explanation:'No supported answer to this proposition'};if(f.scope_evidence_role==='answer_evidence_refs')r.answer_evidence_refs=[];if(f.component_scope_required){r.component_scope='unknown';r.component_scope_basis='No supported paperwork scope yet';r.component_scope_evidence_refs=[];}r.missing=expectedMissing(r);return r;
  })}))};
}

export function normalizeCommand(value){
 if(typeof value!=='string')return null;
 const k=value.trim().toLowerCase().replace(/[’]/g,"'").replace(/\s+/g,' ').replace(/\?$/,'');
 const map={'discovery':'discovery','start quick discovery':'start_quick_discovery','what do you already know':'known_summary',"what's missing":'gap_summary','generate snapshot':'snapshot','pause discovery':'pause','stop discovery':'stop','stop':'stop','generate final report':'final_report','generate discovery report':'final_report','resume discovery':'resume','deepen discovery':'deepen','show full questionnaire':'questionnaire'};
 return map[k]||null;
}
function shapeErrors(a,binding){
 const errors=[];const obj=(v,p)=>{if(!v||typeof v!=='object'||Array.isArray(v)){errors.push(p+': must be an object');return false;}return true;};
 const arr=(v,p,visit)=>{if(!Array.isArray(v)){errors.push(p+': must be an array');return;}if(visit)v.forEach((x,i)=>visit(x,p+'['+i+']'));};
 if(!obj(a,'assessment'))return errors;
 arr(a.evidence,'evidence',(e,p)=>obj(e,p));arr(a.context,'context',(c,p)=>{if(obj(c,p))arr(c.evidence_refs,p+'.evidence_refs');});
 arr(a.assessments,'assessments',(q,p)=>{if(!obj(q,p))return;
  if(obj(q.independent_state,p+'.independent_state')){const z=q.independent_state;if(obj(z.applicability,p+'.applicability'))arr(z.applicability.evidence_refs,p+'.applicability.evidence_refs');arr(z.conflicts,p+'.conflicts',(c,t)=>{if(obj(c,t))arr(c.evidence_refs,t+'.evidence_refs');});}
  arr(q.facet_results,p+'.facet_results',(f,t)=>{if(!obj(f,t))return;arr(f.evidence_refs,t+'.evidence_refs');if(f.answer_evidence_refs!==undefined)arr(f.answer_evidence_refs,t+'.answer_evidence_refs');arr(f.qualifier_results,t+'.qualifier_results',(z,u)=>{if(obj(z,u))arr(z.evidence_refs,u+'.evidence_refs');});arr(f.missing,t+'.missing',(m,u)=>obj(m,u));});
 });
 if(obj(a.session,'session')){arr(a.session.emitted_questions,'session.emitted_questions');if(a.session.emitted_question_ids!==undefined)arr(a.session.emitted_question_ids,'session.emitted_question_ids');}
 if(binding&&obj(binding,'sourceBinding')&&obj(binding.map,'sourceBinding.map'))arr(binding.map.units,'sourceBinding.map.units',(u,p)=>obj(u,p));
 return errors;
}

export function validateAssessment(a,pkg=loadPackage(),sourceBinding=null){
 const shape=shapeErrors(a,sourceBinding);if(shape.length)return {valid:false,outcome:'INVALID',errors:shape,rows:[]};
 const errors=[],rows=[];const err=(p,m)=>errors.push(p+': '+m);
 const en=(v,values,p)=>{if(!values.includes(v))err(p,'must be one of '+values.join(', '));};
 if(!a||typeof a!=='object')return {valid:false,errors:['Assessment must be an object'],rows:[]};
 if(a.schema_version!=='1.0.0')err('schema_version','expected 1.0.0');
 for(const k of ['bank_sha256','rubric_sha256'])if(a[k]!==pkg.manifest[k])err(k,'assessment is not bound to this frozen package');
 const evidence=new Map();
 if(!Array.isArray(a.evidence))err('evidence','must be an array');
 for(const e of a.evidence||[]){
  if(!e||typeof e!=='object'){err('evidence','invalid entry');continue;}
  if(!nonempty(e.evidence_id)||evidence.has(e.evidence_id))err('evidence','duplicate or absent evidence_id');evidence.set(e.evidence_id,e);
  for(const k of ['locator','exact_excerpt','actor','population','period'])if(!nonempty(e[k]))err(e.evidence_id,k+' must be a nonempty string (use unknown explicitly)');
  en(e.scope,['case','general'],e.evidence_id+'.scope');en(e.temporal,['current','historical','proposed','policy','configured','unknown'],e.evidence_id+'.temporal');en(e.status,['factual','analytic'],e.evidence_id+'.status');
 }
 const sourceUnits=new Map();
 if(sourceBinding){
  if(a.source_map_sha256!==sourceBinding.sha256)err('source_map_sha256','assessment must bind to supplied frozen source map');
  if(sourceBinding.map?.schema_version!=='1.0.0'||!Array.isArray(sourceBinding.map?.units))err('source map','expected schema_version 1.0.0 and units array');
  for(const u of sourceBinding.map?.units||[]){
   if(!nonempty(u.locator)||!nonempty(u.text)||sourceUnits.has(u.locator))err('source map','each unit needs unique locator and nonempty text');
   sourceUnits.set(u.locator,u.text);
  }
  for(const e of evidence.values()){
   const text=sourceUnits.get(e.locator);
   if(typeof text!=='string')err(e.evidence_id,'locator absent from frozen source map');
   else if(typeof e.exact_excerpt!=='string'||!text.includes(e.exact_excerpt))err(e.evidence_id,'exact_excerpt is not an exact substring at source locator');
  }
 }else if(a.source_map_sha256!==undefined)err('source map','assessment declares a source hash but no source map was supplied');
 const refs=(arr,p)=>{if(!Array.isArray(arr)){err(p,'must be an array');return [];}if(new Set(arr).size!==arr.length)err(p,'duplicate references');for(const id of arr)if(!evidence.has(id))err(p,'unknown evidence '+id);return arr.map(id=>evidence.get(id)).filter(Boolean);};
 if(!Array.isArray(a.context))err('context','must be an array, separate from credit');
 for(const [i,c] of (Array.isArray(a.context)?a.context:[]).entries()){if(!c||typeof c!=='object'){err('context['+i+']','invalid entry');continue;}refs(c.evidence_refs,'context['+i+']');if(!nonempty(c.note))err('context['+i+']','note required');}
 const assessments=new Map();
 if(!Array.isArray(a.assessments)||a.assessments.length!==pkg.rubric.questions.length)err('assessments','exactly '+pkg.rubric.questions.length+' rows required, including unresolved rows');
 for(const q of a.assessments||[]){if(!q||typeof q!=='object'){err('assessments','invalid row');continue;}if(assessments.has(q.question_id))err(q.question_id,'duplicate question');assessments.set(q.question_id,q);}
 const validIds=new Set(pkg.rubric.questions.map(q=>q.question_id));for(const id of assessments.keys())if(!validIds.has(id))err(String(id),'unknown question ID');
 for(const q of pkg.rubric.questions){
  const r=assessments.get(q.question_id);if(!r){err(q.question_id,'missing assessment');continue;}
  if(r.question_text!==q.question_text||r.priority!==q.priority)err(q.question_id,'exact question text/priority mismatch');
  const state=r.independent_state;
  if(!state||typeof state!=='object')err(q.question_id,'independent_state required; restore applicability, deferral, tracking and conflicts instead of flattening them');
  else{
   const ap=state.applicability;
   if(!ap||typeof ap!=='object')err(q.question_id,'applicability object required');else{
    en(ap.status,['applicable','unknown','not_applicable'],q.question_id+'.applicability');
    const ae=refs(ap.evidence_refs,q.question_id+'.applicability.evidence_refs');
    if(!nonempty(ap.reason)||!nonempty(ap.scope))err(q.question_id,'applicability reason and scope required');
    if(ap.status==='not_applicable'&&!ae.some(e=>e.status==='factual'))err(q.question_id,'not_applicable requires factual evidence for its scoped premise');
   }
   for(const [flag,reason] of [['deferred','defer_reason'],['not_tracked','not_tracked_reason']]){
    if(typeof state[flag]!=='boolean'||typeof state[reason]!=='string')err(q.question_id,'explicit '+flag+' flag and '+reason+' required');
    if(state[flag]&&!nonempty(state[reason]))err(q.question_id,flag+' requires reason');
   }
   if(!Array.isArray(state.conflicts))err(q.question_id,'conflicts must be an array');
   const cs=new Set();for(const c of Array.isArray(state.conflicts)?state.conflicts:[]){
    if(!c||!nonempty(c.conflict_id)||cs.has(c.conflict_id)||!nonempty(c.note)){err(q.question_id,'conflict needs unique ID and note');continue;}cs.add(c.conflict_id);
    if(refs(c.evidence_refs,q.question_id+'.conflict '+c.conflict_id).length<2)err(q.question_id,'conflict must retain at least two evidence references');
   }
  }
  const ledger=new Map();
  if(!Array.isArray(r.facet_results)||r.facet_results.length!==q.facets.length)err(q.question_id,'exactly the predefined facets required');
  for(const f of r.facet_results||[]){if(!f||typeof f!=='object'){err(q.question_id,'invalid facet result');continue;}if(ledger.has(f.facet_id))err(q.question_id,'duplicate facet '+f.facet_id);ledger.set(f.facet_id,f);}
  const fids=new Set(q.facets.map(f=>f.facet_id));for(const id of ledger.keys())if(!fids.has(id))err(q.question_id,'unknown facet '+id);
  const positives=[],gaps=[];
  for(const f of q.facets){
   const x=ledger.get(f.facet_id),p=f.facet_id;if(!x){err(p,'missing facet result');continue;}
   en(x.extent,['none','some','complete'],p+'.extent');en(x.bounds_result,['matched','unknown','mismatch'],p+'.bounds_result');en(x.conflict,['none','unresolved'],p+'.conflict');
   if(!nonempty(x.explanation)||!nonempty(x.bounds_explanation))err(p,'explanation and bounds_explanation required');
   const ev=refs(x.evidence_refs,p+'.evidence_refs');
   const qr=new Map();if(!Array.isArray(x.qualifier_results)||x.qualifier_results.length!==f.material_qualifiers.length)err(p,'exact qualifier_results required');
   for(const z of (Array.isArray(x.qualifier_results)?x.qualifier_results:[])){if(!z||typeof z!=='object'){err(p,'invalid qualifier result');continue;}if(qr.has(z.qualifier_id))err(p,'duplicate qualifier');qr.set(z.qualifier_id,z);}
   const expected=new Set(f.material_qualifiers.map(z=>z.qualifier_id));for(const id of qr.keys())if(!expected.has(id))err(p,'unknown qualifier '+id);
   for(const z of f.material_qualifiers){
    const v=qr.get(z.qualifier_id);if(!v){err(p,'missing qualifier '+z.qualifier_id);continue;}
    en(v.result,['supported','unknown','contradicted'],z.qualifier_id);const ze=refs(v.evidence_refs,z.qualifier_id+'.evidence_refs');
    if(!nonempty(v.basis))err(z.qualifier_id,'basis required');
    if(v.result==='supported'){
     if(!ze.length)err(z.qualifier_id,'supported qualifier requires evidence');
     if(Array.isArray(v.evidence_refs)&&v.evidence_refs.some(id=>!Array.isArray(x.evidence_refs)||!x.evidence_refs.includes(id)))err(z.qualifier_id,'qualifier evidence must also be in facet evidence_refs');
     if(['current','active','unused'].includes(z.kind)&&!ze.some(e=>e.temporal==='current'))err(z.qualifier_id,'requires current evidence, not only historical/configured/proposed');
     if(['usual','pattern','rank','all'].includes(z.kind)&&!(z.kind==='all'&&z.partial_population_allowed&&x.extent==='some'&&f.scope_policy==='general_for_complete')&&!ze.some(e=>e.scope==='general'))err(z.qualifier_id,'requires general/representative evidence, not isolated case');
     if(z.kind==='attributed_wish'&&(!ze.length||ze.some(e=>e.status!=='factual')))err(z.qualifier_id,'assigned agent wish requires factual attributed evidence, not analytic advice');
     if(z.kind==='first'&&!['explicit_first','complete_chronology'].includes(v.basis))err(z.qualifier_id,'basis must be explicit_first or complete_chronology; an occurrence alone is insufficient');
    }
    if(x.extent!=='none'&&v.result!=='supported')err(z.qualifier_id,'positive extent cannot coexist with '+v.result+' material qualifier');
   }
   if(f.component_scope_required){
    en(x.component_scope,['unknown','subset','all_applicable'],p+'.component_scope');
    if(!nonempty(x.component_scope_basis))err(p,'component_scope_basis required');
    const scopeEv=refs(x.component_scope_evidence_refs,p+'.component_scope_evidence_refs');
    if(Array.isArray(x.component_scope_evidence_refs)&&x.component_scope_evidence_refs.some(id=>!x.evidence_refs.includes(id)))err(p,'component-scope evidence must also be in facet evidence_refs');
    if(x.extent!=='none'&&!scopeEv.some(e=>e.status==='factual'))err(p,'positive paperwork scope requires factual component-scope evidence');
    if(x.extent==='some'&&x.component_scope!=='subset')err(p,'some requires a supported nonempty paperwork subset');
    if(x.extent==='complete'&&x.component_scope!=='all_applicable')err(p,'complete requires all applicable disclosures and agreements within the stated scope');
   }
   const answerEv=f.scope_evidence_role==='answer_evidence_refs'?refs(x.answer_evidence_refs,p+'.answer_evidence_refs'):ev;
   if(f.scope_evidence_role==='answer_evidence_refs'&&Array.isArray(x.answer_evidence_refs)&&x.answer_evidence_refs.some(id=>!x.evidence_refs.includes(id)))err(p,'answer evidence must also be in facet evidence_refs');
   if(x.extent!=='none'){
    for(const dep of f.requires_supported_facets||[]){const dr=ledger.get(dep);if(!dr||!['some','complete'].includes(dr.extent))err(p,'positive extent requires supported referent facet '+dep);else if(!dr.evidence_refs.some(id=>x.evidence_refs.includes(id)))err(p,'dependent reason must retain ranking evidence from '+dep);}
    if(f.scope_evidence_role==='answer_evidence_refs'&&!answerEv.some(e=>e.status==='factual'))err(p,'positive reason requires separate factual answer_evidence_refs');
    if(!ev.length)err(p,'positive extent requires evidence');
    if(x.extent==='some'&&!f.allows_some)err(p,'some is not permitted for this indivisible proposition');
    if(x.bounds_result!=='matched')err(p,'positive extent requires matched bounds');
    if(x.conflict!=='none')err(p,'positive extent cannot carry unresolved conflict');
    if(!ev.some(e=>e.status==='factual'))err(p,'positive extent requires factual evidence or factual premises; analysis alone cannot satisfy it');
    if(f.mode==='factual'&&ev.every(e=>e.status==='analytic'))err(p,'analysis-only evidence cannot satisfy factual facet');
    if(f.scope_policy==='general_required'&&!ev.some(e=>e.scope==='general'))err(p,'general evidence required');
    if(f.scope_policy==='general_for_complete'&&x.extent==='complete'&&!answerEv.some(e=>e.scope==='general'))err(p,'complete requires general scope; a true case method can be some');
    if(f.mode==='factual'&&ev.every(e=>['proposed','unknown'].includes(e.temporal)))err(p,'proposed/unknown-only evidence does not establish factual practice');
    positives.push({facet_id:p,extent:x.extent,proposition:f.proposition,evidence_refs:x.evidence_refs,scope:[...new Set(ev.map(e=>e.scope))],...(f.component_scope_required?{component_scope:x.component_scope,component_scope_basis:x.component_scope_basis,component_scope_evidence_refs:x.component_scope_evidence_refs}:{})});
   }
   if(!Array.isArray(x.missing))err(p,'structured missing array required');
   else{
    for(const m of x.missing){if(!m||typeof m!=='object'){err(p,'missing entry must be an object');continue;}if(!missingCodes.includes(m.code))err(p,'unknown missing code '+m.code);if(Object.keys(m).some(k=>!['code','qualifier_id'].includes(k)))err(p,'unsupported missing field');}
    const required=expectedMissing(x);if(!same(canonicalMissing(x.missing),canonicalMissing(required)))err(p,'missing ledger must equal derived codes '+JSON.stringify(required));
   }
   for(const m of expectedMissing(x))gaps.push({facet_id:p,proposition:f.proposition,...m});
  }
  const complete=q.facets.filter(f=>f.required_for_full).every(f=>ledger.get(f.facet_id)?.extent==='complete');
  const label=complete?'fully_answered':positives.length?'partially_answered':'unresolved';
  if(r.label!==undefined&&r.label!==label)err(q.question_id,'supplied label disagrees; derived '+label);
  if(r.positive_summary!==undefined&&!same(r.positive_summary,positives))err(q.question_id,'positive_summary disagrees with derived ledger');
  if(r.missing_summary!==undefined&&!same(r.missing_summary,gaps))err(q.question_id,'missing_summary disagrees with derived ledger');
  const hasConflict=[...ledger.values()].some(f=>f.conflict==='unresolved');
  if(hasConflict&&!(state?.conflicts?.length))err(q.question_id,'unresolved facet conflict requires preserved conflict history in independent_state');
  const suppression=state?.applicability?.status==='not_applicable'?'supported_not_applicable':state?.deferred?'deferred':state?.not_tracked?'not_tracked_retrieve_or_defer':label==='fully_answered'?'already_answered':null;
  rows.push({question_id:q.question_id,label,independent_state:state,question_gate:{eligible_for_gap_selection:suppression===null,suppression_reason:suppression,authorization:'Eligibility is not permission: apply session stop, budget and one-question rules separately.'},positive_summary:positives,missing_summary:gaps});
 }
 const s=a.session;
 if(!s||typeof s!=='object')err('session','session record required');else{
  en(s.status,['active','paused','stopped','complete'], 'session.status');const command=normalizeCommand(s.command);if(!command)err('session.command','unknown documented command');if(command==='deepen'&&(s.pass!==2||!s.deepen_authorized||s.pass2_declined))err('session','Deepen discovery requires explicit authorized nondeclined Pass 2');
  if(typeof s.timing_reliable!=='boolean'||!Number.isInteger(s.substantive_answers)||s.substantive_answers<0)err('session','valid timing reliability and answer counter required');
  if(![1,2].includes(s.pass)||typeof s.deepen_authorized!=='boolean'||typeof s.pass2_declined!=='boolean')err('session','valid pass and depth decisions required');
  if(!Number.isFinite(s.budget_minutes)||s.budget_minutes<=0)err('session','positive budget required');
  if(s.timing_reliable&&(!Number.isFinite(s.active_minutes)||s.active_minutes<0))err('session','reliable timing requires active_minutes');
  if(!Array.isArray(s.emitted_questions)||s.emitted_questions.some(x=>!nonempty(x)))err('session','emitted_questions must be string array');
  if(typeof s.exported!=='boolean')err('session','exported boolean required');
  const normalized=normalizeCommand(s.command);const outputOnly=!['discovery','start_quick_discovery','resume','deepen'].includes(normalized);const exportCommand=['snapshot','pause','stop','final_report'].includes(normalized);
  const exhausted=s.pass===1&&(s.timing_reliable?s.active_minutes>=s.budget_minutes:s.substantive_answers>=6);
  const stopped=['paused','stopped','complete'].includes(s.status)||outputOnly||exhausted;
  if(stopped&&(s.emitted_questions||[]).length)err('session','stop/output-only/budget exhaustion forbids new questions');
  if((['paused','stopped','complete'].includes(s.status)||exportCommand||exhausted)&&!s.exported)err('session','stop/output-only/budget exhaustion requires qualified export');
  if(s.pass===2&&(!s.deepen_authorized||s.pass2_declined))err('session','Pass 2 requires explicit nondeclined authorization');
  if((s.emitted_questions||[]).length){
   if(!Array.isArray(s.emitted_question_ids)||s.emitted_question_ids.length!==s.emitted_questions.length)err('session','each emitted question needs an emitted_question_ids entry for the independent-state gate');
   else for(const id of s.emitted_question_ids){const row=rows.find(r=>r.question_id===id);if(!row)err('session','unknown emitted question ID '+id);else if(!row.question_gate.eligible_for_gap_selection)err('session','question selection blocked for '+id+': '+row.question_gate.suppression_reason);}
  }
  if((s.emitted_questions||[]).length>1)err('session','one natural question maximum per interaction');
 }
 return errors.length?{valid:false,outcome:'INVALID',errors,rows:[]}:{valid:true,outcome:'VALID',normalized_command:normalizeCommand(a.session.command),validation_scope:'Structural consistency only; semantic entailment and destination execution are not proven.',excerpt_verification:sourceBinding?'Exact substrings and locators checked against supplied frozen source map':'Unverified: no frozen source map supplied',bank_sha256:pkg.manifest.bank_sha256,rubric_sha256:pkg.manifest.rubric_sha256,errors:[],independent_state_counts:{not_applicable:rows.filter(r=>r.independent_state.applicability.status==='not_applicable').length,deferred:rows.filter(r=>r.independent_state.deferred).length,not_tracked:rows.filter(r=>r.independent_state.not_tracked).length,conflicted:rows.filter(r=>r.independent_state.conflicts.length>0).length},counts:rows.reduce((n,r)=>(n[r.label]++,n),{fully_answered:0,partially_answered:0,unresolved:0}),rows};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{
  const pkg=loadPackage();const args=process.argv.slice(2);
  if(args[0]==='--check-package')console.log(JSON.stringify({valid:true,questions:pkg.rubric.questions.length,facets:pkg.rubric.questions.reduce((n,q)=>n+q.facets.length,0),bank_sha256:pkg.manifest.bank_sha256,rubric_sha256:pkg.manifest.rubric_sha256},null,2));
  else if(args[0]==='--template'){const text=JSON.stringify(blankAssessment(pkg),null,2)+'\n';if(args[1])fs.writeFileSync(args[1],text,{flag:'wx'});else process.stdout.write(text);}
  else if(args[0]){const si=args.indexOf('--sources');let binding=null;if(si>=0){if(!args[si+1])throw Error('--sources requires a JSON source-map path');const bytes=fs.readFileSync(args[si+1]);binding={map:JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/,'')),sha256:sha256(bytes)};}const out=validateAssessment(parse(args[0]),pkg,binding);const text=JSON.stringify(out,null,2)+'\n';if(args[1]&&args[1]!=='--sources')fs.writeFileSync(args[1],text,{flag:'wx'});else process.stdout.write(text);if(!out.valid)process.exitCode=1;}
  else {console.error('Usage: node validate-coverage.mjs --check-package | --template [new.json] | assessment.json [new-result.json] [--sources source-map.json]');process.exitCode=2;}
 }catch(e){console.error('INVALID: '+e.message);process.exitCode=2;}
}
