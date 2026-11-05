"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const source=fs.readFileSync(process.env.FS_FRAME || path.join(__dirname,"../tools/authoring/w6f8/live/frame.js"),"utf8");
function setup(){
 const elements={},dialogs=[],openers=[],closers=[];
 class Node{
  constructor(){this.textContent="";this.children=[];this.listeners={};this.hidden=false;this.open=false;this.dataset={};}
  addEventListener(n,fn){this.listeners[n]=fn;}
  click(){return this.listeners.click();}
  show(){this.open=true;}
  close(){this.open=false;}
  replaceChildren(...nodes){this.children=nodes;}
  cloneNode(){const n=new Node();n.textContent=this.textContent;return n;}
  querySelector(){return null;}
  focus(){this.focused=true;}
 }
 const ids=["command-input","game","movement","refresh","exits","read-closely","room-title","room-description","passage-title","passage-copy","fullscreen","inventory-panel","passage"];
 for(const id of ids)elements[id]=new Node();
 dialogs.push(elements["inventory-panel"],elements.passage);
 const opener=new Node();opener.dataset.open="inventory-panel";openers.push(opener);
 const closer=new Node();closers.push(closer);
 let observe;let mutation;
 const document={getElementById:id=>elements[id],
 querySelectorAll:q=>q==="dialog"?dialogs:q==="[data-open]"?openers:closers,
 addEventListener(){},fullscreenElement:null};
 class Observer{constructor(fn){mutation=fn;}observe(node,options){observe={node,options};}}
 vm.runInNewContext(source,{document,MutationObserver:Observer});
 return {elements,dialogs,opener,closer,mutation,observe,Node};
}
test("panels open only with authenticated game visible and close on return",()=>{
 const h=setup();h.elements.game.hidden=true;h.opener.click();assert.equal(h.dialogs[0].open,false);
 h.elements.game.hidden=false;h.opener.click();assert.equal(h.dialogs[0].open,true);
 h.closer.click();assert.ok(h.dialogs.every(d=>!d.open));
});
test("session expiry closes private references",()=>{
 const h=setup();h.elements.game.hidden=false;h.opener.click();
 h.elements.game.hidden=true;h.mutation();
 assert.ok(h.dialogs.every(d=>!d.open));assert.equal(h.observe.node,h.elements.game);
});
test("return restores command focus without changing the underlying scene",()=>{
 const h=setup();h.elements.game.hidden=false;h.elements["room-description"].textContent="Current observation";
 h.opener.click();h.closer.click();
 assert.equal(h.elements["command-input"].focused,true);
 assert.equal(h.elements["room-description"].textContent,"Current observation");
});
