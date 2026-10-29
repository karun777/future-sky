// Execute the shipped browser script with a minimal DOM and controlled clock.
// These test interactions and scheduling, not browser layout or rendering.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = process.env.FS_STATIC || path.join(__dirname, '../bot/fsbot/web_static');
const source = fs.readFileSync(path.join(root, 'game.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
class Node {
  constructor(tag='div') { this.tagName=tag; this.children=[]; this.listeners={}; this.dataset={}; this.hidden=false; this.disabled=false; this.value=''; }
  set textContent(v) { this.value=String(v); this.children=[]; }
  get textContent() { return this.value+this.children.map(x=>x.textContent).join(''); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.value=''; this.children=nodes; }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  emit(type) { return Promise.all((this.listeners[type]||[]).map(fn=>fn({type}))); }
  removeAttribute(name) { delete this[name]; }
  querySelectorAll(tag) { return this.children.flatMap(n=>[...(n.tagName===tag?[n]:[]),...n.querySelectorAll(tag)]); }
}
const drain = async () => { for(let i=0;i<40;i++) await Promise.resolve(); };
function data(room='a') {
  return {session:{csrf:'csrf'}, character:{name:'Pilot',credits:4},
    location:{id:room,title:room==='a'?'Hallway':'Pod',description:'A quiet room.\n\n**A gig** and `!inspect hands`.',image:null},
    walking:{token:'token-'+room,exits:['west'],notice:''},inventory:{bag:[],equipped:{}},idle_home:{enabled:false}};
}
async function setup() {
  const elements={};
  for (const m of html.matchAll(/id="([^"]+)"/g)) elements[m[1]]=new Node();
  const doc=new Node(), win=new Node(); doc.hidden=false;
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
test('polls without commands and preserves unchanged DOM controls',async()=>{
  const h=await setup(), button=h.elements.exits.children[0], paragraph=h.elements['room-description'].children[0];
  await h.tick(12000);
  assert.equal(h.calls.length,4);assert.ok(h.calls.every(c=>c.url==='/play/api/me'));
  assert.equal(h.elements.exits.children[0],button);assert.equal(h.elements['room-description'].children[0],paragraph);
  assert.equal(h.elements.connection.textContent,'Up to date');
});
test('external move and idle completion update room and observed change',async()=>{
  const h=await setup();h.data=data('b');h.data.idle_home={enabled:true,status:'home',at_home:true};
  await h.tick(4000);
  assert.equal(h.elements['room-title'].textContent,'Pod');
  assert.match(h.elements['walk-feedback'].textContent,/idle return is complete/);
  assert.equal(h.elements.recent.children.length,1);
});
test('hidden tab pauses reads and return fetches current room',async()=>{
  const h=await setup();h.doc.hidden=true;await h.doc.emit('visibilitychange');await h.tick(20000);
  assert.equal(h.calls.length,1);assert.equal(h.elements.exits.children[0].disabled,true);
  h.data=data('b');h.doc.hidden=false;await h.doc.emit('visibilitychange');await drain();
  assert.equal(h.elements['room-title'].textContent,'Pod');assert.equal(h.elements.exits.children[0].disabled,false);
});
test('offline disables movement; online resumes without refreshing manually',async()=>{
  const h=await setup();h.navigator.onLine=false;await h.win.emit('offline');await h.tick(12000);
  assert.equal(h.calls.length,1);assert.equal(h.elements.exits.children[0].disabled,true);
  h.navigator.onLine=true;h.data=data('b');await h.win.emit('online');await drain();
  assert.equal(h.elements['room-title'].textContent,'Pod');assert.equal(h.elements.message.hidden,true);
});
test('failed read becomes stale and backs off then recovers',async()=>{
  const h=await setup();h.fail=true;await h.tick(4000);
  assert.equal(h.elements.exits.children[0].disabled,true);assert.match(h.elements.message.textContent,/last known view/);
  h.fail=false;await h.tick(8000);assert.equal(h.elements.exits.children[0].disabled,false);
});
test('formatting uses safe text nodes and preserves literal HTML',async()=>{
  const h=await setup();h.data.location.description='**Bold** *soft* `!look` <img src=x onerror=alert(1)> [link](javascript:bad)';await h.tick(4000);
  const n=h.elements['room-description'];
  assert.equal(n.querySelectorAll('strong')[0].textContent,'Bold');assert.equal(n.querySelectorAll('em')[0].textContent,'soft');
  assert.equal(n.querySelectorAll('code')[0].textContent,'!look');assert.equal(n.querySelectorAll('img').length,0);
  assert.equal(n.querySelectorAll('a').length,0);assert.match(n.textContent,/<img/);
});
test('double click sends one movement; post completion refreshes',async()=>{
  const h=await setup();h.handler=async(url)=>{if(url.endsWith('walk')){h.data=data('b');return response(200,{ok:true,message:'You walk west.'});}};
  const button=h.elements.exits.children[0];await Promise.all([button.emit('click'),button.emit('click')]);await drain();
  assert.equal(h.calls.filter(c=>c.url.endsWith('walk')).length,1);assert.equal(h.elements['room-title'].textContent,'Pod');
  assert.equal(h.elements['walk-feedback'].textContent,'You walk west.');
});
test('lost action response is not retried and saved location is fetched',async()=>{
  const h=await setup();h.handler=async(url)=>{if(url.endsWith('walk')){h.data=data('b');throw Error('lost');}};
  await h.elements.exits.children[0].emit('click');await h.tick(12000);
  assert.equal(h.calls.filter(c=>c.url.endsWith('walk')).length,1);assert.equal(h.elements['room-title'].textContent,'Pod');
  assert.match(h.elements['walk-feedback'].textContent,/will not be repeated/);
});
test('expired session clears private view and stops polling',async()=>{
  const h=await setup();h.handler=async()=>response(401,'Sign in');await h.tick(4000);const count=h.calls.length;
  await h.tick(20000);assert.equal(h.calls.length,count);assert.equal(h.elements.game.hidden,true);
  assert.equal(h.elements['character-name'].textContent,'');assert.equal(h.elements.inventory.children.length,0);
});
test('stale clock blocks command even before watchdog runs',async()=>{
  const h=await setup();h.now+=13000;await h.elements.exits.children[0].emit('click');await drain();
  assert.equal(h.calls.filter(c=>c.url.endsWith('walk')).length,0);
});
test('slow read times out and leaves stale controls disabled',async()=>{
  const h=await setup();h.handler=(_url,options)=>new Promise((_,reject)=>options.signal.addEventListener('abort',()=>reject(Error('timeout'))));
  await h.tick(14000);assert.equal(h.elements.exits.children[0].disabled,true);assert.match(h.elements.message.textContent,/retrying/);
});
