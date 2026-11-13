// Execute the shipped browser script with a minimal DOM and controlled clock.
// These test interactions and scheduling, not browser layout or rendering.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = process.env.FS_STATIC || path.join(__dirname, '../tools/authoring/w6f8/live');
const source = fs.readFileSync(path.join(root, 'game.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
class Node {
  constructor(tag='div') { this.tagName=tag; this.children=[]; this.listeners={}; this.dataset={}; this.hidden=false; this.disabled=false; this.value=''; }
  set textContent(v) { this.value=String(v); this.children=[]; }
  get textContent() { return this.value+this.children.map(x=>x.textContent).join(''); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.value=''; this.children=nodes; }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  emit(type) { return Promise.all((this.listeners[type]||[]).map(fn=>fn({type,preventDefault(){}}))); }
  showModal() { this.open=true; }
  show() { this.open=true; }
  focus() {}
  close() { this.open=false; }
  removeAttribute(name) { delete this[name]; }
  querySelectorAll(tag) { return this.children.flatMap(n=>[...(n.tagName===tag?[n]:[]),...n.querySelectorAll(tag)]); }
}
const drain = async () => { for(let i=0;i<40;i++) await Promise.resolve(); };
function data(room='a') {
  return {journal:{entries:[]},session:{csrf:'csrf'}, character:{name:'Pilot',credits:4},
    location:{id:room,title:room==='a'?'Hallway':'Pod',description:'A quiet room.\n\n**A gig** and `!inspect hands`.',image:null},
    inspection:{token:'inspect-'+room,targets:['panels'],notice:''},walking:{token:'token-'+room,exits:['west'],notice:''},inventory:{bag:[],equipped:{}},idle_home:{enabled:false}};
}
async function setup() {
  const elements={};
  for (const m of html.matchAll(/id="([^"]+)"/g)) elements[m[1]]=new Node();
  const doc=new Node(), win=new Node(); doc.hidden=false;
  doc.querySelectorAll=tag=> tag==='dialog' ? [...html.matchAll(/<dialog id="([^"]+)"/g)].map(m=>elements[m[1]]) : [];
  doc.getElementById=id=>{assert.ok(elements[id],id);return elements[id];};
  doc.createElement=tag=>new Node(tag);
  doc.createTextNode=value=>{const n=new Node('#text');n.textContent=value;return n;};
  const h={elements,doc,win,navigator:{onLine:true},now:100000,data:data(),calls:[],timers:new Map(),next:0,fail:false};
  const add=(fn,ms,repeat=0)=>{const id=++h.next;h.timers.set(id,{fn,at:h.now+ms,repeat});return id;};
  h.tick=async(ms)=>{const end=h.now+ms;for(;;){let found=[...h.timers].filter(([,x])=>x.at<=end).sort((a,b)=>a[1].at-b[1].at)[0];if(!found)break;const [id,t]=found;h.now=t.at;h.timers.delete(id);if(t.repeat)h.timers.set(id,{...t,at:h.now+t.repeat});t.fn();await drain();}h.now=end;await drain();};
  const DateBase=Date;
  class Clock extends DateBase { constructor(...a){super(...(a.length?a:[h.now]));}static now(){return h.now;} }
  h.fetch=async(url,options)=>{
    h.calls.push({url,options});
    if(h.fail) throw new Error('offline');
    if(h.handler) { const response=await h.handler(url,options);if(response)return response; }
    return response(200,h.data);
  };
  vm.runInNewContext(source,{document:doc,window:win,navigator:h.navigator,Date:Clock,AbortController,
    fetch:(...a)=>h.fetch(...a),setTimeout:(fn,ms)=>add(fn,ms),clearTimeout:id=>h.timers.delete(id),
    setInterval:(fn,ms)=>add(fn,ms,ms)}, {timeout:2000});
  await drain();return h;
}
function response(status, body) {return {status,ok:status<400,headers:{get:()=>typeof body==='object'?'application/json':'text/plain'},json:async()=>structuredClone(body),text:async()=>body};}

async function command(h,value) {
 h.elements['command-input'].value=value;
 await h.elements['command-form'].emit('submit');await drain();
}
test('passive polling never issues commands; available exits/details are plain text',async()=>{
 const h=await setup();await h.tick(12000);
 assert.ok(h.calls.every(c=>c.url==='/play/api/me'));
 assert.equal(h.elements.exits.querySelectorAll('button').length,0);
 assert.equal(h.elements['inspect-targets'].querySelectorAll('button').length,0);
 assert.equal(h.elements.exits.textContent,"west");
});
test('optional prefix and case insensitive command move once',async()=>{
 const h=await setup();h.handler=async(url)=>{if(url.endsWith('/walk')){h.data=data('b');return response(200,{ok:true,message:'Moved'});}};
 await command(h,'!GO West');
 assert.equal(h.calls.filter(c=>c.url.endsWith('/walk')).length,1);
 assert.equal(h.elements['room-title'].textContent,'Pod');
 assert.match(h.elements['command-response'].textContent,/Moved/);
});
test('unknown, unoffered and chained commands never mutate',async()=>{
 const h=await setup();
 for(const c of ['attack anyone','go north','inspect booking','go west; go west','uniform formal','wear Coat'])await command(h,c);
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
});
test('inspect typed command shows safe observation and no command buttons',async()=>{
 const h=await setup();h.handler=async(url)=>url.endsWith('/inspect')?response(200,{ok:true,observation:{title:'Panels',text:'<script>x</script>'}}):null;
 await command(h,'inspect panels');
 assert.equal(h.elements['inspection-panel'].hidden,false);
 assert.equal(h.elements['inspection-text'].querySelectorAll('script').length,0);
 assert.equal(h.elements['inspection-actions'].querySelectorAll('button').length,0);
});
test('overlapping Enter submits produce only one mutation',async()=>{
 const h=await setup();let release;
 h.handler=async(url)=>url.endsWith('/walk')?new Promise(r=>release=r):null;
 h.elements['command-input'].value='go west';
 const a=h.elements['command-form'].emit('submit');await drain();
 const b=h.elements['command-form'].emit('submit');await drain();
 assert.equal(h.calls.filter(c=>c.url.endsWith('/walk')).length,1);
 release(response(200,{ok:true,message:'Moved'}));await a;await b;
});
test('lost response is not replayed; explicit feedback survives polling',async()=>{
 const h=await setup();h.handler=async(url)=>{if(url.endsWith('/walk'))throw Error('lost');};
 await command(h,'go west');await h.tick(12000);
 assert.equal(h.calls.filter(c=>c.url.endsWith('/walk')).length,1);
 assert.match(h.elements['command-response'].textContent,/will not be repeated/);
});
test('offline and hidden command submissions never mutate',async()=>{
 const h=await setup();h.navigator.onLine=false;await h.win.emit('offline');
 await command(h,'go west');h.doc.hidden=true;await command(h,'inspect panels');
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
});
test('look, help and inventory open views without mutation',async()=>{
 const h=await setup();
 await command(h,'help');assert.equal(h.elements.actions.open,true);
 await command(h,'inventory');assert.equal(h.elements['inventory-panel'].open,true);
 await command(h,'look');assert.equal(h.elements['inventory-panel'].open,false);
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
});
async function wardrobe(h) {
 h.data.inspection.targets=['panels','wardrobe'];
 h.data.wardrobe={available:true,token:'clothes',fit:'Uniform',first_selection:false,options:[
 {id:'carried:coat',name:'Coat',description:'A coat.',action:'wear:coat',label:'Wear'},
 {id:'catalogue:pod_formal',name:'Formal Uniform',description:'Formal.',action:null,label:'Catalogue'}]};
 await h.tick(4000);
}
test('wardrobe browsing and clicking details are passive; typing wear uses fresh offer',async()=>{
 const h=await setup();await wardrobe(h);
 await command(h,'wardrobe');
 assert.equal(h.elements['wardrobe-panel'].hidden,false);
 assert.equal(h.elements['wardrobe-choices'].querySelectorAll('button').length,0);
 await command(h,'wardrobe inspect Formal Uniform');
 assert.equal(h.elements['garment-description'].textContent,'Formal.');
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
 h.handler=async(url)=>url.endsWith('/wardrobe')?response(200,{ok:true,message:'Equipped Coat'}):null;
 await command(h,'wear Coat');
 assert.equal(h.calls.filter(c=>c.url.endsWith('/wardrobe')).length,1);
});
test('first selection uses uniform command only; unavailable selection cannot be replayed',async()=>{
 const h=await setup();await wardrobe(h);
 h.data.wardrobe.options=[{id:'catalogue:pod_freeform',name:'Freeform Attire',description:'Outfit',action:'select:pod_freeform',label:'Choose'}];
 await h.tick(4000);
 h.handler=async(url)=>{if(url.endsWith('/wardrobe')){h.data.wardrobe.options=[];return response(200,{ok:true,message:'Selected'});}};
 await command(h,'uniform freeform');await command(h,'uniform freeform');
 const calls=h.calls.filter(c=>c.url.endsWith('/wardrobe'));
 assert.equal(calls.length,1);assert.equal(JSON.parse(calls[0].options.body).action,'select:pod_freeform');
});
test('auth expiry clears command history and private wardrobe',async()=>{
 const h=await setup();await wardrobe(h);await command(h,'wardrobe inspect Coat');
 h.handler=async()=>response(401,'expired');await h.tick(4000);
 assert.equal(h.elements['wardrobe-panel'].hidden,true);
 assert.equal(h.elements['garment-description'].textContent,'');
 assert.equal(h.elements['command-history'].children.length,0);
 assert.equal(h.elements['command-input'].value,'');
});
test('external room change closes wardrobe and revokes equipment action',async()=>{
 const h=await setup();await wardrobe(h);await command(h,'wardrobe');
 h.data=data('b');await h.tick(4000);
 assert.equal(h.elements['wardrobe-panel'].hidden,true);
 await command(h,'wear Coat');
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
});


test('focus survives polling and reference views; look returns to the room',async()=>{
 const h=await setup();h.handler=async(url)=>url.endsWith('/inspect')?response(200,{ok:true,observation:{title:'Panels',text:'Details'}}):null;
 await command(h,'inspect panels');await h.tick(12000);
 assert.equal(h.elements['inspection-panel'].hidden,false);
 assert.equal(h.elements['room-scene'].hidden,false);
 await command(h,'inventory');assert.equal(h.elements['inspection-panel'].hidden,false);
 await command(h,'look');assert.equal(h.elements['inspection-panel'].hidden,true);
 assert.equal(h.elements['room-scene'].hidden,false);
});
test('plain inspect outfit resolves supplied names and asks about ambiguity',async()=>{
 const h=await setup();await wardrobe(h);await command(h,'inspect Formal Uniform');
 assert.equal(h.elements['garment-description'].textContent,'Formal.');
 h.data.wardrobe.options.push({id:'carried:formal',name:'Formal Uniform',description:'Owned',action:'wear:formal'});
 await h.tick(4000);await command(h,'inspect Formal Uniform');
 assert.match(h.elements['command-response'].textContent,/Which outfit/);
 await command(h,'inspect carried:formal');assert.equal(h.elements['garment-description'].textContent,'Owned');
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
});


test('history groups command and observation; refresh does not replace the result',async()=>{
 const h=await setup();h.handler=async(url)=>url.endsWith('/inspect')?response(200,{ok:true,observation:{title:'Panels',text:'A recessed handle.'}}):null;
 await command(h,'inspect panels');
 assert.equal(h.elements['command-history'].children.length,1);
 assert.match(h.elements['command-history'].children[0].textContent,/inspect panels.*Panels/s);
 assert.match(h.elements['command-history'].children[0].textContent,/A recessed handle/);
 await h.win.emit('focus');await h.tick(4000);
 assert.match(h.elements['command-response'].textContent,/Attending to Panels/);
 assert.equal(h.elements.exits.textContent,'west');
 assert.equal(h.elements['current-location'].textContent,'Hallway');
});

test('journal follows saved discoveries without mutation, survives display off, and clears on expiry',async()=>{
 const h=await setup();await command(h,'quests');
 assert.equal(h.elements['quest-panel'].open,true);
 assert.match(h.elements['quest-entries'].textContent,/No notices/);
 h.data.journal={entries:[{id:'booking',title:'Remembered booking',text:'A gig tomorrow night.'}]};
 h.data.display={enabled:false,state:'normal'};await h.tick(4000);
 assert.match(h.elements['quest-entries'].textContent,/A gig tomorrow night/);
 assert.match(h.elements['display-state'].textContent,/off/);
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
 h.handler=async()=>response(401,'expired');await h.tick(4000);
 assert.equal(h.elements['quest-entries'].textContent,'');
 assert.equal(h.elements['display-state'].textContent,'');
});
test('shared illustration keeps inspected detail across polling and references, then restores room',async()=>{
 const h=await setup();h.data.location.image='https://future-sky.net/assets/room.png';await h.tick(4000);
 h.handler=async(url)=>url.endsWith('/inspect')?response(200,{ok:true,observation:{title:'Detail',text:'Observed',image:'https://future-sky.net/assets/detail.png'}}):null;
 await command(h,'inspect panels');assert.equal(h.elements['room-image'].src,'https://future-sky.net/assets/detail.png');
 await command(h,'quests');await h.tick(4000);
 assert.equal(h.elements['room-image'].src,'https://future-sky.net/assets/detail.png');
 await command(h,'look');assert.equal(h.elements['room-image'].src,'https://future-sky.net/assets/room.png');
});
test('reconnection refreshes saved journal and equipment without retrying commands',async()=>{
 const h=await setup();h.fail=true;await h.tick(4000);
 h.data.journal={entries:[{id:'notice',title:'Unread notice',text:'A notification.'}]};
 h.data.inventory.equipped={chest:{id:'coat',name:'Coat'}};
 h.fail=false;await h.win.emit('online');await drain();
 assert.match(h.elements['quest-entries'].textContent,/A notification/);
 assert.match(h.elements.equipped.textContent,/Coat/);
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
});
test('sheet values render as text and private fields clear on sign-out',async()=>{
 const h=await setup();h.data.sheet={class_id:'<script>bad</script>',stats:{hp:8,max_hp:12,strength:10},pools:{fire:{current:2,max:4}}};
 await h.tick(4000);await command(h,'sheet');
 assert.match(h.elements['character-details'].textContent,/HP: 8 \/ 12/);
 assert.equal(h.elements['character-details'].querySelectorAll('script').length,0);
 h.handler=async()=>response(401,'expired');await h.tick(4000);
 assert.equal(h.elements['character-details'].textContent,'');
});

test('personal delivery appears safely, updates and clears on signout',async()=>{
 const h=await setup();
 assert.equal(h.elements['personal-delivery-section'].hidden,true);
 h.data.inventory.personal_delivery=['Opened capsule containing the antique box','USB marked tunes','<img src=x>'];
 await h.tick(4000);
 assert.equal(h.elements['personal-delivery-section'].hidden,false);
 assert.equal(h.elements['personal-delivery'].children.length,3);
 assert.equal(h.elements['personal-delivery'].querySelectorAll('img').length,0);
 assert.doesNotMatch(h.elements['inventory-guidance'].textContent,/Nothing is carried/);
 h.data.inventory.personal_delivery=[];await h.tick(4000);
 assert.equal(h.elements['personal-delivery-section'].hidden,true);
 assert.equal(h.elements['personal-delivery'].children.length,0);
 h.data.inventory.personal_delivery=['USB marked tunes'];await h.tick(4000);
 h.handler=async()=>response(401,{});await h.tick(4000);
 assert.equal(h.elements['personal-delivery'].children.length,0);
 assert.equal(h.elements['personal-delivery-section'].hidden,true);
});

test('command guide follows discovered details and clears on expiry',async()=>{
 const h=await setup();
 assert.match(h.elements['help-available'].textContent,/inspect panels/);
 assert.doesNotMatch(h.elements['help-available'].textContent,/inspect booking/);
 h.data.inspection.targets=['panels','display','wardrobe'];await h.tick(4000);
 assert.match(h.elements['help-available'].textContent,/inspect display/);
 assert.doesNotMatch(h.elements['help-available'].textContent,/inspect booking/);
 h.handler=async()=>response(401,{});await h.tick(4000);
 assert.equal(h.elements['help-available'].textContent,'');
});

test('fresh opening guidance survives rendering and follows offered body observations',async()=>{
 const h=await setup();
 h.data.location.description='You are in the pod.\n\nFollow what catches your attention: `!inspect hands`, `!inspect garment` or `!inspect pod`.';
 h.data.inspection.targets=['hands','garment','pod','panels'];
 await h.tick(4000);
 assert.match(h.elements['room-description'].textContent,/Follow what catches your attention/);
 assert.match(h.elements['room-description'].textContent,/inspect hands/);
 h.handler=async(url)=>{
  if(!url.endsWith('/inspect'))return null;
  h.data.inspection.targets.push('hud','body');
  return response(200,{ok:true,observation:{title:'Your hands',text:'Yours.',guidance:'Examine `!inspect hud`, or follow `!inspect body`.'}});
 };
 await command(h,'inspect hands');
 assert.equal(h.elements['inspection-actions'].textContent,'inspect hud · inspect body');
 assert.equal(h.calls.filter(c=>c.url.endsWith('/inspect')).length,1);
 await h.tick(8000);
 assert.equal(h.calls.filter(c=>c.url.endsWith('/inspect')).length,1);
});

test('one shared refusal survives polling and does not expose blocked actions',async()=>{
 const h=await setup();
 const warning='A choice or encounter needs your attention in Discord.';
 h.data.walking={token:'blocked-walk',exits:[],notice:warning};
 h.data.inspection={token:'blocked-inspect',targets:[],notice:warning};
 h.data.wardrobe={available:false,options:[]};
 await h.tick(12000);
 assert.equal(h.elements['walk-notice'].hidden,false);
 assert.equal(h.elements['walk-notice'].textContent,warning);
 assert.equal(h.elements['inspect-notice'].hidden,true);
 assert.equal(h.elements['inspect-notice'].textContent,'');
 assert.equal(h.elements['inspection-options'].hidden,true);
 assert.equal(h.elements.exits.textContent,'none visible');
 for(const c of ['go west','inspect panels','uniform freeform'])await command(h,c);
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
 const feedback=h.elements['command-response'].textContent;
 assert.ok(feedback);
 await h.tick(8000);
 assert.equal(h.elements['command-response'].textContent,feedback);
 assert.equal(h.elements['walk-notice'].textContent,warning);
 await command(h,'inventory');
 assert.equal(h.elements['inventory-panel'].open,true);
});

test('distinct and inspection-only notices remain visible without hiding offered targets',async()=>{
 const h=await setup();
 h.data.walking={token:'walk',exits:[],notice:'Your sequence is running. Wait for it to finish.'};
 h.data.inspection={token:'inspect',targets:[],notice:'Inspection is unavailable while the game connection recovers.'};
 await h.tick(4000);
 assert.equal(h.elements['inspect-notice'].hidden,false);
 assert.equal(h.elements['walk-notice'].hidden,false);
 assert.equal(h.elements['inspection-options'].hidden,false);
 assert.equal(h.elements['inspect-notice'].textContent,h.data.inspection.notice);
 assert.equal(h.elements['walk-notice'].textContent,h.data.walking.notice);
 h.data.walking={token:'walk',exits:['west'],notice:''};
 await h.tick(4000);
 assert.equal(h.elements['inspect-notice'].hidden,false);
 assert.equal(h.elements['walk-notice'].hidden,true);
 h.data.walking.exits=[];
 await h.tick(4000);
 assert.equal(h.elements['inspect-notice'].hidden,false);
 assert.equal(h.elements['walk-notice'].textContent,'No walking exits available in this view.');
 h.data=data();
 await h.tick(4000);
 assert.equal(h.elements['inspection-options'].hidden,false);
 assert.equal(h.elements['inspect-targets'].textContent,'inspect panels');
 assert.equal(h.elements['inspect-notice'].hidden,true);
 assert.equal(h.elements['walk-notice'].hidden,true);
});

test('encounter notice clears and returns with refreshed offers, preserving ordinary commands',async()=>{
 const h=await setup();
 const blocked=()=>{
  h.data.walking={token:'blocked-walk',exits:[],notice:'A choice or encounter needs your attention in Discord.'};
  h.data.inspection={token:'blocked-inspect',targets:[],notice:h.data.walking.notice};
 };
 blocked();await h.tick(4000);
 assert.equal(h.elements['walk-notice'].hidden,false);
 h.data=data();await h.tick(4000);
 assert.equal(h.elements['walk-notice'].hidden,true);
 assert.equal(h.elements['inspect-notice'].hidden,true);
 assert.equal(h.elements['inspection-options'].hidden,false);
 assert.equal(h.elements.exits.textContent,'west');
 h.handler=async(url)=>url.endsWith('/walk')?response(200,{ok:true,message:'Moved'}):null;
 await command(h,'go west');
 assert.equal(h.calls.filter(c=>c.url.endsWith('/walk')).length,1);
 blocked();await h.tick(4000);
 assert.equal(h.elements['walk-notice'].hidden,false);
 assert.equal(h.elements['inspect-notice'].hidden,true);
 assert.equal(h.elements['inspection-options'].hidden,true);
 await command(h,'go west');
 assert.equal(h.calls.filter(c=>c.url.endsWith('/walk')).length,1);
});

for (const [typed, field] of [['go west','walking'],['inspect panels','inspection'],['wardrobe','wardrobe']]) {
 test('W6-F11 '+typed+' reports its current refusal without issuing an action',async()=>{
  const h=await setup();
  const warning='A choice or encounter needs your attention in Discord.';
  h.data.walking={exits:[],notice:warning};
  h.data.inspection={targets:[],notice:warning};
  h.data.wardrobe={available:false,options:[],notice:warning};
  await h.tick(4000);await command(h,typed);
  assert.equal(h.elements['command-response'].textContent,warning);
  assert.equal(h.elements['command-history'].children[0].children[1].textContent,warning);
  assert.equal(h.elements['walk-notice'].textContent,warning);
  assert.equal(h.elements['inspect-notice'].hidden,true);
  await h.tick(8000);
  assert.equal(h.elements['command-response'].textContent,warning);
  const specific='This action is unavailable while its connection recovers.';
  h.data[field].notice=specific;await h.tick(4000);await command(h,typed);
  assert.equal(h.elements['command-response'].textContent,specific);
  await command(h,'inventory');assert.equal(h.elements['inventory-panel'].open,true);
  assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
 });
}

test('W6-F11 empty or absent offers give complete guidance without invented reasons',async()=>{
 const h=await setup();
 for(const missing of [false,true]){
  h.data.walking=missing?undefined:{exits:[],notice:''};
  h.data.inspection=missing?undefined:{targets:[],notice:''};
  h.data.wardrobe=missing?undefined:{available:false,options:[]};
  await h.tick(4000);
  for(const [typed,expected] of [
   ['go west','No exits are available from here right now.'],
   ['inspect panels','No details are available to inspect here right now.'],
   ['wardrobe','The wardrobe is not available here right now.']]){
   await command(h,typed);
   assert.equal(h.elements['command-response'].textContent,expected);
   assert.equal(h.elements['command-history'].children[0].children[1].textContent,expected);
  }
 }
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
});

test('W6-F11 alternatives follow current offers and only suggest an offered wardrobe',async()=>{
 const h=await setup();
 await command(h,'go north');
 assert.equal(h.elements['command-response'].textContent,'Available exits: west');
 await command(h,'inspect booking');
 assert.equal(h.elements['command-response'].textContent,'That inspection is not available here in the web window. Available: panels');
 await command(h,'wardrobe');
 assert.equal(h.elements['command-response'].textContent,'The wardrobe is not available here right now. Available details: panels');
 h.data.inspection.targets=['panels','wardrobe'];await h.tick(4000);await command(h,'wardrobe');
 assert.equal(h.elements['command-response'].textContent,'Inspect the wardrobe first: inspect wardrobe. Available details: panels, wardrobe');
 h.data.wardrobe={available:false,notice:'Equipment is unavailable.',options:[]};
 await h.tick(4000);await command(h,'wardrobe');
 assert.equal(h.elements['command-response'].textContent,'Equipment is unavailable.');
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,0);
});

test('W6-F11 refreshed offers restore commands and a later block updates feedback',async()=>{
 const h=await setup();
 const block=()=>{
  const notice='A choice or encounter needs your attention in Discord.';
  h.data.walking={exits:[],notice};h.data.inspection={targets:[],notice};
  h.data.wardrobe={available:false,options:[],notice};
 };
 block();await h.tick(4000);await command(h,'wardrobe');
 h.data=data();await h.tick(4000);
 h.handler=async(url)=>url.endsWith('/walk')?response(200,{ok:true,message:'Moved'}):
  url.endsWith('/inspect')?response(200,{ok:true,observation:{title:'Panels',text:'A handle.'}}):null;
 await command(h,'go west');await command(h,'inspect panels');
 await wardrobe(h);await command(h,'wardrobe');
 assert.equal(h.elements['wardrobe-panel'].hidden,false);
 assert.equal(h.elements['command-response'].textContent,'Wardrobe opened. Examine an outfit before choosing what to wear.');
 const actionCount=h.calls.filter(c=>c.options.method==='POST').length;
 assert.equal(actionCount,2);
 block();await h.tick(4000);
 for(const typed of ['go west','inspect panels','wardrobe']){
  await command(h,typed);
  assert.equal(h.elements['command-response'].textContent,h.data.walking.notice);
 }
 assert.equal(h.calls.filter(c=>c.options.method==='POST').length,actionCount);
});
