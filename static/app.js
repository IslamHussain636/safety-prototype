'use strict';
const $ = id => document.getElementById(id);
const STORAGE = 'pcgml-practice-v2';
let catalog = {}, current = null, batch = null, busy = false, initialized = false, practice = null, selected = null, vrReady = false, vrLoading = null;
let history = {profile:{}, sessions:[]};
function message(text, error=false) { $('status').textContent=text; $('status').className='status'+(error?' error':''); }
function text(tag, value, className) { const el=document.createElement(tag); el.textContent=value; if(className) el.className=className; return el; }
function loadHistory() {
  try {
    const stored=JSON.parse(localStorage.getItem(STORAGE));
    if(stored && stored.profile && Array.isArray(stored.sessions)) {
      for(const [k,v] of Object.entries(stored.profile)) if(!catalog[k] || !Number.isInteger(v.attempts) || !Number.isInteger(v.correct) || v.correct<0 || v.attempts<v.correct || v.attempts>100000) throw Error('Invalid profile');
      history=stored; history.sessions=history.sessions.slice(-100);
    }
  } catch { history={profile:{},sessions:[]}; }
}
function persist() { try { localStorage.setItem(STORAGE,JSON.stringify(history)); } catch { message('Browser storage is unavailable. Export the practice log before closing this page.',true); } }
function exportJSON(data,name) { const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000); }
function syncControls() {
  const fixed=$('strategy').value==='static';
  for(const id of ['level','seed','focus','source','prompt']) $(id).disabled=busy||!!practice||fixed;
  for(const id of ['strategy','generate','batch','resetProfile']) $(id).disabled=!initialized||busy||!!practice;
  $('startPractice').disabled=busy||!current||!!practice;
  $('export').disabled=!current||!!practice;
  $('tokenWrap').hidden=fixed||$('source').value==='procedural';
  for(const button of $('comparisonCards').querySelectorAll('button')) button.disabled=busy||!!practice;
}
async function requestJSON(path,body) {
  const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),80000);
  try {
    const headers={'Content-Type':'application/json'};
    if($('source').value!=='procedural' && $('accessToken').value) headers.Authorization='Bearer '+$('accessToken').value;
    const response=await fetch(path,{method:'POST',headers,body:JSON.stringify(body),signal:controller.signal});
    let data;try {data=await response.json();}catch {throw Error('The server returned a non-JSON response. Check the deployment logs.');}
    if(!response.ok) throw Error(data.error||`Request failed (${response.status}).`);
    return data;
  } finally {clearTimeout(timer);}
}
function parameters() {
  if($('strategy').value==='static') return {prompt:'Fixed baseline',source:'procedural',strategy:'static',level:'apprentice',seed:0,focus:[],profile:{}};
  const seed=Number($('seed').value);
  if(!Number.isInteger(seed)||seed<0||seed>2147483644) throw Error('Seed must be an integer from 0 to 2147483644.');
  if(!$('prompt').value.trim()) throw Error('Enter an instructor prompt.');
  return {prompt:$('prompt').value.trim(),source:$('source').value,strategy:$('strategy').value,level:$('level').value,seed,focus:$('focus').value?[$('focus').value]:[],profile:history.profile};
}
async function generate(isBatch=false) {
  if(!initialized||busy||practice) return;
  busy=true;syncControls();message('Composing modules and checking the generated layout…');
  try {
    const data=await requestJSON(isBatch?'/api/batch':'/api/generate',parameters());
    if(isBatch) {
      if(!data.items.every(i=>i.validation.passed)) throw Error('The server did not approve every layout.');
      batch=data;showBatch();show({...data.items[0],metadata:data.metadata});
    } else {show(data);}
    message(isBatch?'Three layouts passed the encoded teaching checks. Select a layout to inspect it.':'Scenario passed the encoded teaching checks. Inspect modules or start practice.');
  } catch(e) {message(e.name==='AbortError'?'Request timed out. The previous scene is unchanged.':e.message,true);}
  finally {busy=false;syncControls();}
}
function show(data) {
  if(!data.validation?.passed) throw Error('Scenario did not pass the server validation gate.');
  current=data;selected=null;
  $('empty').hidden=true;$('planWrap').hidden=false;$('vrWrap').hidden=true;
  $('view2d').classList.add('selected');$('view3d').classList.remove('selected');$('view2d').setAttribute('aria-pressed','true');$('view3d').setAttribute('aria-pressed','false');
  if(vrReady) document.querySelector('a-scene')?.pause();
  const s=data.scenario;
  $('gate').textContent='Passed';$('count').textContent=s.hazards.length;
  $('latency').textContent=data.metadata.generation_ms+' ms';
  $('target').textContent=s.targeted_weak_category?catalog[s.targeted_weak_category].label:'—';
  $('sceneMeta').textContent=`${s.site_width_m} × ${s.site_depth_m} m · seed ${s.seed} · ${s.strategy} · ${data.metadata.provider.source}`;
  $('detailTitle').textContent='Inspect a module';$('detail').replaceChildren(text('p','Select a numbered module to review its conditions and source.','muted'));
  $('raw').textContent=JSON.stringify(data,null,2);
  $('practiceResult').replaceChildren();$('practiceStatus').textContent=`${history.sessions.length} saved sessions in this browser. Practice supplies locations and observations.`;
  $('validation').replaceChildren();
  for(const c of data.validation.checks) $('validation').append(text('div',c,'check'));
  for(const l of [...data.validation.limitations,...data.metadata.notes]) $('validation').append(text('p',l,'limitation'));
  renderPlan();syncControls();
}
const NS='http://www.w3.org/2000/svg';
function svg(tag,attrs,parent) {const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs)) n.setAttribute(k,String(v));parent.append(n);return n;}
function svgText(value,x,y,attrs,parent) {const n=svg('text',{x,y,...attrs},parent);n.textContent=value;return n;}
function renderPlan() {
  if(!current)return;const root=$('plan');root.replaceChildren();const s=current.scenario;
  const scale=25,ox=80,oy=42,px=x=>ox+x*scale,py=y=>oy+y*scale;
  for(let x=0;x<=s.site_width_m;x++) svg('line',{x1:px(x),x2:px(x),y1:py(0),y2:py(s.site_depth_m),stroke:x%4===0?'#29405a':'#192b40','stroke-width':1},root);
  for(let y=0;y<=s.site_depth_m;y++) svg('line',{x1:px(0),x2:px(s.site_width_m),y1:py(y),y2:py(y),stroke:y%4===0?'#29405a':'#192b40','stroke-width':1},root);
  svg('rect',{x:ox,y:oy,width:600,height:500,fill:'none',stroke:'#47617d'},root);
  for(let x=0;x<=24;x+=4) svgText(`${x}m`,px(x),oy-13,{'text-anchor':'middle',fill:'#91aac4','font-size':12},root);
  for(let y=0;y<=20;y+=4) svgText(`${y}m`,ox-14,py(y)+4,{'text-anchor':'end',fill:'#91aac4','font-size':12},root);
  for(const [i,h] of s.hazards.entries()) {
    const cat=catalog[h.type],color=practice?'#a1b6ce':cat.color;
    const g=svg('g',{role:'button',tabindex:0,'aria-label':`Module ${i+1}${practice?'':': '+cat.label}`},root);
    svg('rect',{class:'module',x:px(h.x-2),y:py(h.y-1.5),width:100,height:75,rx:4,fill:'#20344c',stroke:selected===h.id?'#fff':color,'stroke-width':1.5},g);
    // Schematic asset footprint, drawn to the same metric scale as the 3D module.
    if(h.asset==='platform') {
      svg('rect',{x:px(h.x-1.6),y:py(h.y-1),width:80,height:50,fill:'#445a70',stroke:'#a4b1bd'},g);
      svg('line',{x1:px(h.x-1.6),y1:py(h.y+1),x2:px(h.x+1.6),y2:py(h.y+1),stroke:'#f68b60','stroke-dasharray':'5 4','stroke-width':3},g);
    } else if(h.asset==='trench') {
      svg('rect',{x:px(h.x-1.6),y:py(h.y-.6),width:80,height:30,fill:'#0a0e14',stroke:'#a78361','stroke-width':5},g);
    } else {
      svg('rect',{x:px(h.x-.65),y:py(h.y-.6),width:32.5,height:30,fill:'#51647b',stroke:'#8b9daf'},g);
    }
    svg('circle',{cx:px(h.x-1.5),cy:py(h.y-1.05),r:12,fill:color},g);
    svgText(i+1,px(h.x-1.5),py(h.y-1.05)+4,{'text-anchor':'middle',fill:'#0b1421','font-size':13,'font-weight':700},g);
    svgText(practice?'Module '+(i+1):cat.label,px(h.x),py(h.y+2.15),{'text-anchor':'middle',fill:color,'font-size':12},root);
    svg('line',{x1:px(h.x),y1:py(h.y+1.5),x2:px(h.approach.x),y2:py(h.approach.y),stroke:'#647c97','stroke-dasharray':'3 4'},root);
    svg('circle',{cx:px(h.approach.x),cy:py(h.approach.y),r:3,fill:'#a6b9d0'},root);
    g.addEventListener('click',()=>inspect(h));g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspect(h);}});
  }
  svg('circle',{cx:px(s.spawn.x),cy:py(s.spawn.y),r:7,fill:'#73e0c1'},root);
  svgText('OBSERVER START',px(s.spawn.x),py(s.spawn.y)+23,{'text-anchor':'middle',fill:'#73e0c1','font-size':11},root);
}
function inspect(h) {
  selected=h.id;renderPlan();const cat=catalog[h.type],el=$('detail');el.replaceChildren();
  $('detailTitle').textContent=`Module ${h.id.slice(1)}${practice?'':' · '+cat.label}`;
  if(practice) {
    if(!practice.firstViewed[h.id]) practice.firstViewed[h.id]=performance.now();
    el.append(text('p',h.observation));
    if(practice.answers[h.id]) {el.append(text('p','Answer recorded. Select another module.','muted'));return;}
    const label=text('label','Which category best describes the primary hazard?');label.htmlFor='answerCategory';el.append(label);
    const select=document.createElement('select');select.id='answerCategory';
    const placeholder=text('option','Choose a category');placeholder.value='';select.append(placeholder);
    for(const [k,v] of Object.entries(catalog)) {const option=text('option',v.label);option.value=k;select.append(option);}
    el.append(select);const button=text('button','Record answer','primary');button.style.marginTop='12px';
    button.addEventListener('click',()=>{
      if(!select.value){select.focus();return;}
      practice.answers[h.id]={selected_category:select.value,correct:select.value===h.type,latency_ms:Math.round(performance.now()-practice.firstViewed[h.id])};
      $('practiceStatus').textContent=`${Object.keys(practice.answers).length} / ${current.scenario.hazards.length} answers recorded. Finish to reveal feedback; unanswered modules count as incorrect.`;
      inspect(h);
    });el.append(button);
  } else {
    el.append(text('span','Intentional training hazard','tag'),text('p',h.description),text('p',h.action));
    const link=text('a',`OSHA ${h.osha_ref} ↗`);link.href=h.source_url;link.target='_blank';link.rel='noopener noreferrer';el.append(link,text('p',cat.basis,'hint'));
  }
}
function startPractice() {
  if(!current||practice||busy)return;
  practice={started:performance.now(),started_at:new Date().toISOString(),answers:{},firstViewed:{},visibility_interrupted:false};
  $('startPractice').hidden=true;$('finishPractice').hidden=false;$('jsonPanel').hidden=true;$('comparison').hidden=true;
  $('practiceResult').replaceChildren();$('detail').replaceChildren(text('p','Select any numbered module and classify its observed condition.','muted'));$('detailTitle').textContent='Classify a module';
  $('practiceStatus').textContent='Session started. Answers remain hidden until you finish.';renderPlan();if(vrReady)renderVR();syncControls();
}
function finishPractice() {
  if(!practice)return;
  const rows=current.scenario.hazards.map(h=>({hazard_id:h.id,category:h.type,...(practice.answers[h.id]||{selected_category:null,correct:false,latency_ms:null})}));
  const correct=rows.filter(r=>r.correct).length,answered=rows.filter(r=>r.selected_category).length;
  const latencies=rows.filter(r=>r.latency_ms!==null).map(r=>r.latency_ms);
  const record={session_id:crypto.randomUUID(),scenario_id:current.scenario.scenario_id,scenario:current.scenario,metadata:current.metadata,started_at:practice.started_at,completed_at:new Date().toISOString(),task:'cued_category_classification',duration_ms:Math.round(performance.now()-practice.started),visibility_interrupted:practice.visibility_interrupted,accuracy:correct/rows.length,answered,total:rows.length,mean_answer_latency_ms:latencies.length?Math.round(latencies.reduce((a,b)=>a+b,0)/latencies.length):null,responses:rows};
  for(const r of rows){const p=history.profile[r.category]||{attempts:0,correct:0};p.attempts++;p.correct+=Number(r.correct);history.profile[r.category]=p;}
  history.sessions.push(record);history.sessions=history.sessions.slice(-100);persist();
  practice=null;$('startPractice').hidden=false;$('finishPractice').hidden=true;$('jsonPanel').hidden=false;$('comparison').hidden=!batch;
  $('practiceStatus').textContent=`${correct}/${rows.length} correct · ${answered} answered · ${Math.round(record.accuracy*100)}% classification accuracy. Select Adaptive for the next generation.`;
  $('practiceResult').replaceChildren();for(const r of rows)$('practiceResult').append(text('div',`${r.hazard_id}: ${catalog[r.category].label} — ${r.correct?'correct':r.selected_category?'incorrect':'unanswered'}`,'result-row'));
  $('detail').replaceChildren(text('p','Feedback is now visible. Select a module to review the recommended action.','muted'));
  renderPlan();if(vrReady)renderVR();syncControls();
}
function showBatch() {
  $('comparison').hidden=false;$('comparisonCards').replaceChildren();
  batch.items.forEach((item,i)=>{const b=text('button',`Layout ${i+1}`);b.append(text('span',`Seed ${item.scenario.seed} · ${item.scenario.hazards.length} modules`));b.addEventListener('click',()=>{if(!practice&&!busy)show({...item,metadata:batch.metadata});});$('comparisonCards').append(b);});
  $('diversity').textContent=JSON.stringify(batch.diversity,null,2);
}
async function ensureVR() {
  if(vrReady)return;if(vrLoading)return vrLoading;
  vrLoading=(async()=>{
    if(!window.AFRAME) await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='/static/vendor/aframe.min.js';script.onload=resolve;script.onerror=()=>{script.remove();reject(Error('3D library unavailable. The 2D plan remains usable.'));};document.head.append(script);});
    const scene=document.createElement('a-scene');scene.setAttribute('embedded','');scene.setAttribute('background','color: #15253a');scene.setAttribute('renderer','colorManagement: true');scene.setAttribute('vr-mode-ui','enabled: true');
    const add=(tag,attrs,parent=scene)=>{const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);parent.append(e);return e;};
    add('a-entity',{light:'type: ambient; intensity: 0.9'});add('a-entity',{light:'type: directional; intensity: 0.8',position:'0 15 5'});
    add('a-plane',{id:'ground',width:24,height:20,rotation:'-90 0 0',color:'#344357'});
    add('a-entity',{id:'assetsRoot'});
    const rig=add('a-entity',{id:'rig',position:'0 0 9'});
    const camera=add('a-camera',{position:'0 1.6 0','wasd-controls':'acceleration: 15','look-controls':'pointerLockEnabled: false'},rig);
    add('a-cursor',{raycaster:'objects: .module-hit',color:'#ffffff',fuse:'false'},camera);
    add('a-entity',{cursor:'rayOrigin: mouse',raycaster:'objects: .module-hit'},scene);
    const ready=new Promise(resolve=>scene.addEventListener('loaded',resolve,{once:true}));$('vrMount').append(scene);await ready;vrReady=true;
  })();
  try {await vrLoading;}catch(e){vrLoading=null;throw e;}
}
function renderVR() {
  if(!vrReady||!current)return;
  const root=$('assetsRoot');root.replaceChildren();const s=current.scenario;
  $('rig').setAttribute('position',`${s.spawn.x-12} 0 ${s.spawn.y-10}`);
  function add(tag,attrs,parent=root){const el=document.createElement(tag);if(tag==='a-text'){el.setAttribute('font','/static/vendor/Roboto-msdf.json');el.setAttribute('font-image','/static/vendor/Roboto-msdf.png');}for(const[k,v]of Object.entries(attrs))el.setAttribute(k,v);parent.append(el);return el;}
  function box(parent,w,h,d,x,y,z,color){return add('a-box',{width:w,height:h,depth:d,position:`${x} ${y} ${z}`,color},parent);}
  function worker(parent,x,y,z,helmet=true){add('a-cylinder',{radius:.18,height:.75,position:`${x} ${y+.75} ${z}`,color:'#edbd5b'},parent);add('a-sphere',{radius:.19,position:`${x} ${y+1.3} ${z}`,color:helmet?'#e7edf4':'#c89b79'},parent);}
  for(const [i,h] of s.hazards.entries()){
    const cat=catalog[h.type],g=add('a-entity',{position:`${h.x-12} 0 ${h.y-10}`});
    box(g,4,.025,3,0,.02,0,'#405772');
    if(h.asset==='platform'){
      const top=h.conditions.height_ft*.3048;
      box(g,3.2,.15,2,0,top-.075,0,'#8f9daa');
      for(const x of [-1.4,1.4])for(const z of [-.8,.8])box(g,.15,top,.15,x,top/2,z,'#677b8f');
      // Three schematic rail segments; fourth side is truly absent.
      box(g,3.2,.06,.06,0,top+1.07,-1,'#d5dce4');
      for(const x of [-1.6,1.6])box(g,.06,.06,2,x,top+1.07,0,'#d5dce4');
      for(const x of [-1.6,1.6])for(const z of [-1,1])box(g,.06,1.07,.06,x,top+.535,z,'#d5dce4');
      worker(g,0,top,.5);
    }else if(h.asset==='panel'){
      box(g,1,1.6,.4,0,.8,0,'#536777');box(g,.8,1.2,.04,0,.9,.23,'#151c26');
      for(const x of [-.2,0,.2])box(g,.05,.8,.05,x,.9,.28,'#e9a443');worker(g,1,0,.5);
    }else if(h.asset==='materials'){
      for(const x of [-1.4,1.4])box(g,.15,2.8,.15,x,1.4,-.3,'#8295a7');
      box(g,3,.1,1.2,0,2.6,-.3,'#8295a7');
      for(const x of [-.8,0,.8])box(g,.65,.35,.5,x,2.82,-.3,'#ad8054');worker(g,0,0,.5,false);
    }else if(h.asset==='trench'){
      // Raised cutaway indicates depth; not a simulated hole in the ground plane.
      const depth=h.conditions.depth_ft*.3048;
      for(const z of [-.8,.8])box(g,3.4,depth,.25,0,depth/2,z,'#8c684d');
      box(g,3.2,.05,1.3,0,.04,0,'#141b23');worker(g,0,0,0);
      add('a-text',{value:'6 ft soil trench (cutaway)',width:4,align:'center',position:'0 2.5 0',color:'#d5dce4'},g);
    }else{
      box(g,1.6,.15,.8,0,.85,0,'#a69174');for(const x of [-.6,.6])box(g,.1,.8,.1,x,.4,0,'#8295a7');
      add('a-cylinder',{radius:.17,height:.12,rotation:'90 0 0',position:'0 1.05 .1',color:'#acb7c3'},g);worker(g,1,0,.5,false);
    }
    const marker=add('a-sphere',{radius:.25,position:'0 1.1 2.1',color:practice?'#a1b6ce':cat.color},g);marker.classList.add('module-hit');marker.addEventListener('click',()=>inspect(h));
    add('a-text',{value:practice?`Module ${i+1}`:`${i+1}. ${cat.label}`,width:4,align:'center',position:'0 1.65 2.1',color:'#ffffff'},g);
  }
}
async function view3D(){
  if(!current){message('Generate a scenario first.');return;}
  $('planWrap').hidden=true;$('vrWrap').hidden=false;$('view2d').classList.remove('selected');$('view3d').classList.add('selected');$('view2d').setAttribute('aria-pressed','false');$('view3d').setAttribute('aria-pressed','true');
  try{await ensureVR();renderVR();if(!$('vrWrap').hidden)document.querySelector('a-scene').play();$('vrStatus').textContent='Select a marker to inspect its module. The trench is shown as a raised cutaway.';}
  catch(e){$('vrStatus').textContent=e.message;}
}
$('generate').addEventListener('click',()=>generate());$('batch').addEventListener('click',()=>generate(true));
$('source').addEventListener('change',syncControls);$('strategy').addEventListener('change',syncControls);
$('export').addEventListener('click',()=>current&&!practice&&exportJSON(current,`scenario-${current.scenario.scenario_id}.json`));
$('exportBatch').addEventListener('click',()=>batch&&!practice&&exportJSON(batch,'layout-comparison.json'));
$('exportSessions').addEventListener('click',()=>exportJSON(history,'pcgml-practice-log.json'));
$('resetProfile').addEventListener('click',()=>{if(confirm('Clear the practice profile and saved sessions from this browser? Export first if you need them.')){history={profile:{},sessions:[]};persist();$('practiceStatus').textContent='Local profile reset.';$('practiceResult').replaceChildren();}});
$('startPractice').addEventListener('click',startPractice);$('finishPractice').addEventListener('click',finishPractice);
$('view3d').addEventListener('click',view3D);$('view2d').addEventListener('click',()=>{$('vrWrap').hidden=true;$('planWrap').hidden=!current;$('view2d').classList.add('selected');$('view3d').classList.remove('selected');$('view2d').setAttribute('aria-pressed','true');$('view3d').setAttribute('aria-pressed','false');if(vrReady)document.querySelector('a-scene').pause();});
document.addEventListener('visibilitychange',()=>{if(practice&&document.hidden)practice.visibility_interrupted=true;});
window.addEventListener('beforeunload',e=>{if(practice){e.preventDefault();e.returnValue='';}});
(async()=>{
  try{
    const responses=await Promise.all([fetch('/api/catalog'),fetch('/health')]);if(responses.some(r=>!r.ok))throw Error('Backend unavailable');
    const [c,h]=await Promise.all(responses.map(r=>r.json()));catalog=c.hazards;
    for(const[k,v]of Object.entries(catalog)){const option=text('option',v.label);option.value=k;$('focus').append(option);}
    loadHistory();initialized=true;$('connection').textContent=h.openrouter_configured?'Backend ready · OpenRouter configured':'Backend ready · no-key mode available';
    syncControls();
  }catch(e){$('connection').textContent='Backend unavailable';message('Start backend_server.py and open its http://localhost:7860 address. Do not open this HTML as a file.',true);$('generate').disabled=true;$('batch').disabled=true;}
})();
