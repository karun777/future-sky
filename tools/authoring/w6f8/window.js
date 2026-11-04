'use strict';
const data=window.REHEARSAL, $=id=>document.getElementById(id);
let seen=new Set(), entries=[], target='pod';
const titles={hands:'Hands',pod:'The pod',panels:'Storage panels',viewport:'Viewport',brochure:'Brochure',berth:'Berth',light:'Red light',button:'Button',hatch:'Hatch',display:'Display',booking:'Booking notice',chain:'Chain',body:'Body',garment:'Garment',reflection:'Reflection',surfaces:'Surfaces',lighting:'Lighting'};
const related={pod:['hands','viewport','panels','brochure','berth','hatch'],hands:['body','garment','pod'],body:['chain','garment','pod'],garment:['chain','pod'],chain:['pod','panels'],viewport:['reflection','light','panels','pod'],reflection:['panels','pod'],panels:['display','surfaces','pod'],display:['booking','panels','pod'],booking:['pod','panels'],brochure:['panels','pod'],berth:['surfaces','panels','pod'],hatch:['button','light','pod'],button:['brochure','panels','pod'],light:['button','pod'],surfaces:['hatch','panels','berth'],lighting:['light','viewport','display']};
function prose(el,text){el.replaceChildren();for(const para of text.split('\n\n')){const p=document.createElement('p');para.split(/(\*\*[^*]+\*\*)/g).forEach(t=>{if(t.startsWith('**')){const b=document.createElement('strong');b.textContent=t.slice(2,-2);p.append(b)}else p.append(document.createTextNode(t))});el.append(p)}}
function inspect(key,record=true){key=data.aliases[key]||key;if(!data.views[key]){ $('feedback').textContent='This rehearsal supports inspection of the pod. Try “inspect pod” to find a detail.';return}
if(key==='booking'&&!seen.has('panels')&&!seen.has('display')){$('feedback').textContent='You have not located a booking notice yet. Look at the storage panels.';return}
target=key;const view=data.views[key], copy=seen.has(key)?view.again:view.first;
if(record){seen.add(key);entries.unshift({key,title:copy[0],text:copy[1]});entries=entries.slice(0,20)}
$('detail-title').textContent=copy[0];prose($('prose'),copy[1]);$('feedback').textContent='';
const closeup=view.image&&!(seen.has('booking')&&(key==='display'||key==='panels'));
$('scene').src=closeup?view.image:data.roomImage;$('scene').alt=closeup?copy[0]:'The interior of the pod';$('image-label').textContent=closeup?copy[0]:'The cubicle';$('mode').textContent=key==='pod'?'TAKE IN YOUR SURROUNDINGS':'INSPECT / '+(titles[key]||key).toUpperCase();
$('targets').replaceChildren();for(const k of related[key]||['pod']){const b=document.createElement('button');b.textContent=titles[k]||k;b.addEventListener('click',()=>inspect(k));$('targets').append(b)}
$('discoveries').replaceChildren();for(const k of seen){const li=document.createElement('li'),b=document.createElement('button');b.textContent=titles[k]||k;b.addEventListener('click',()=>inspect(k));li.append(b);$('discoveries').append(li)}
$('journal-empty').hidden=seen.size>0;$('count').textContent=seen.size+' details noticed';
$('possessions').textContent=seen.has('chain')?'A small metal key and a little wooden cube hang against your chest. A thin chain disappears beneath your garment.':'Your garment rests against your skin. You have yet to look more closely.';
renderHistory();
}
function renderHistory(){$('history').replaceChildren();for(const e of entries.slice(1)){const a=document.createElement('article'),h=document.createElement('h3'),p=document.createElement('div');h.textContent=e.title;prose(p,e.text);a.append(h,p);$('history').append(a)}if(entries.length<2)$('history').textContent='Your earlier observations will appear here.'}
function panel(which){$('journal').hidden=which!=='journal';$('belongings').hidden=which!=='belongings';$('journal-tab').setAttribute('aria-pressed',String(which==='journal'));$('belongings-tab').setAttribute('aria-pressed',String(which==='belongings'))}
document.querySelectorAll('.study [data-skin]').forEach(b=>b.addEventListener('click',()=>{document.body.dataset.skin=b.dataset.skin;document.querySelectorAll('.study [data-skin]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));$('theme-note').textContent={cabinet:'An adventure cabinet / warm metal, ink & light',terminal:'A Neptune terminal / signals within reach',storybook:'An illustrated storybook / room to read'}[b.dataset.skin]}));
$('back').onclick=()=>inspect('pod');$('journal-tab').onclick=()=>panel('journal');$('belongings-tab').onclick=()=>panel('belongings');
$('history-toggle').onclick=()=>{const on=$('history').hidden;$('history').hidden=!on;$('history-toggle').setAttribute('aria-expanded',String(on))};
$('command-form').onsubmit=e=>{e.preventDefault();let q=$('command').value.trim().toLowerCase().replace(/^!/,'').replace(/\s+/g,' ');$('command').value='';if(q==='look'){inspect('pod');return}if(q==='journal'||q==='inventory'){panel(q==='journal'?'journal':'belongings');$('feedback').textContent=q==='journal'?'Journal opened.':'Belongings opened.';return}if(q.startsWith('inspect ')){inspect(q.slice(8));return}$('feedback').textContent='Try “look”, “inspect viewport”, “journal” or “inventory”. Other actions are not connected in this rehearsal.'};
$('reset').onclick=()=>{seen=new Set();entries=[];$('history').hidden=true;$('history-toggle').setAttribute('aria-expanded','false');panel('journal');inspect('pod',false)};
inspect('pod',false);
