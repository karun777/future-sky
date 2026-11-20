const vm=require('node:vm');const assert=require('node:assert/strict');
const source=require('node:fs').readFileSync(process.argv[2],'utf8');
function harness(seed=null,failWrite=false){
 const map=new Map(seed||[]),els=new Map();const events={};
 const node=id=>{if(!els.has(id))els.set(id,{textContent:'',value:'',open:false,style:{},dataset:{},classList:{toggle(){}},toggleAttribute(){},setAttribute(){},focus(){},show(){this.open=true},close(){this.open=false},addEventListener(k,f){this[k]=f}});return els.get(id)};
 const context=vm.createContext({document:{getElementById:node,querySelector:node,querySelectorAll:()=>[],addEventListener(){}},window:{addEventListener(k,f){events[k]=f}},location:{hash:'#rehearsal-a',reload(){}},localStorage:{getItem:k=>map.get(k)??null,setItem(k,v){if(failWrite)throw Error('quota');map.set(k,v)}}});
 vm.runInContext(source,context);
 return {map,node,send(cmd){node('command').value=cmd;node('commandForm').submit({preventDefault(){}})},state(){return JSON.parse(vm.runInContext('JSON.stringify(state)',context))}};
}
const a=harness();a.send('suggest longer route');a.send('defer');
const key=[...a.map.keys()][0];assert(key.includes('fs-being-0007:vela-route-rehearsal-v1'));
const b=harness(a.map);assert.equal(b.state().away,true);assert.equal(b.state().preference,'longer');
b.send('accept job');assert.equal(b.state().away,true);
const bad=harness([[key,'{bad']]);bad.send('leave');assert.equal(bad.state().away,false);assert.equal(bad.map.get(key),'{bad');
const record=JSON.parse(a.map.get(key));record.state.exit=true;record.state.route=false;
const inconsistent=harness([[key,JSON.stringify(record)]]);inconsistent.send('leave');assert.equal(inconsistent.state().away,false);
const failed=harness(null,true);failed.send('ask vela why');assert.match(failed.node('saveStatus').textContent,/could not save/);assert.equal(failed.map.size,0);failed.send('leave');assert.equal(failed.state().away,false);
const stale=harness(a.map);stale.map.set(key,'changed');stale.send('return');assert.equal(stale.state().away,true);assert.equal(stale.map.get(key),'changed');
console.log('PASS: restore, no acceptance, corrupt-save preservation, inconsistent-state rejection, failed writes, stale preflight.');
