"use strict";
const $=id=>document.getElementById(id);
const state={stage:"awakened",device:"on",focus:"room",history:[]};
const root="/assets/images/world/manzo/triton_central/neptune_lounge/pod/v1/";
const views={
room:{title:"The world comes into focus.",channel:"PERCEPTION / SIGHT",prose:"A berth, a frosted viewport and a hatch within reach. A red light burns beside a button. A welcome brochure protrudes from a dispenser. Storage panels occupy the side wall; their recessed grips invite a closer look.",image:"p01.png",alt:"Pod interior with viewport, hatch and storage",hint:"listen · inspect viewport · inspect panels",trail:"surroundings"},
listen:{title:"A low thump.",channel:"PERCEPTION / HEARING",prose:"A low thump reaches you through the room. It comes again. You can hear a rhythm without yet knowing its source.",image:"p01.png",alt:"The same pod interior while you listen",hint:"look · inspect viewport · hud off",trail:"listening"},
viewport:{title:"Light through water.",channel:"PERCEPTION / SIGHT",prose:"Droplets merge and run down the glass. Blue light comes through, but the outside does not resolve. Your movement returns as an incomplete reflection.",image:"p06.png",alt:"Droplets and blue light on the frosted viewport",hint:"look · listen · inspect panels",trail:"viewport"},
panels:{title:"The side wall.",channel:"PERCEPTION / SIGHT",prose:"A closed wardrobe and lower storage drawer have recessed grips. Beside them, a small display flickers. A signal tile reads FEED7. Below it is a separate notification: Performance booking.",image:"p02.png",alt:"Pod side wall with storage panels and display",hint:"look · listen · inspect viewport",trail:"side wall"}
};
function render(){
 const v=views[state.focus];$("sceneImage").src=root+v.image;$("sceneImage").alt=v.alt;
 $("title").textContent=v.title;$("channelLabel").textContent=v.channel;$("prose").textContent=v.prose;$("hint").textContent=v.hint;
 $("trail").textContent="Pod Room › "+v.trail;$("focusLabel").textContent=state.focus==="room"?"Wakefulness Module":v.title;
 $("stageLabel").textContent=state.stage==="awakened"?"01 · Newly awakened":"02 · Developed perception";
 $("deviceLabel").textContent=state.device==="off"?"Implant · off":state.device==="degraded"?"Implant · signal unavailable":state.stage==="awakened"?"Implant · quiet":(state.focus==="listen"?"Implant · listening":"Implant · available");
 const developed=state.stage==="developed", listening=state.focus==="listen";
 $("instrument").hidden=!(developed&&listening&&state.device!=="off");
 $("inward").hidden=!(developed&&listening);
 $("quiet").hidden=developed&&listening;
 $("instrumentText").textContent=state.device==="degraded"?"No usable reading.":"A repeating acoustic pattern is detected. Its source is unresolved.";
 $("instrumentOrigin").textContent=state.device==="degraded"?"Signal unavailable · no earlier reading shown as current.":"Acoustic instrument · hypothetical capability · sample for this observation.";
 $("quiet").textContent=developed?"Attend to a detail. Additional perception appears where it matters.":"You have a place to attend. There is no need to understand everything yet.";
}
function command(raw){
 const text=raw.trim().replace(/^!/,"").toLowerCase().replace(/\s+/g," ");
 let reply;
 if(text==="help"||text==="commands"){openPanel("guide");reply="Command guide opened.";}
 else if(text==="look"){state.focus="room";reply="Your attention returns to the room.";}
 else if(text==="listen"){state.focus="listen";reply="You attend to the sound.";}
 else if(/^inspect (viewport|panels)$/.test(text)){state.focus=text.slice(8);reply="You attend to the "+state.focus+".";}
 else if(/^stage (awakened|developed)$/.test(text)){state.stage=text.slice(6);reply="Comparison stage changed. Your focus and implant setting are retained.";}
 else if(text==="hud on"||text==="hud off"){state.device=text.slice(4);reply=state.device==="off"?"The implant recedes. Your senses and inner voice remain.":"The implant is available again.";}
 else if(text==="hud state signal degraded"){state.device="degraded";reply="Instrument readings are unavailable. Ordinary perception remains.";}
 else if(text==="hud state normal"){state.device="on";reply="Instrument display restored.";}
 else if(text==="history"){openPanel("history");reply="Recent activity opened.";}
 else if(text==="go west"){reply="This rehearsal stays in the pod. Use the Live game link for actual movement.";}
 else{reply="This rehearsal understands look, listen, inspect viewport, inspect panels, stage awakened, stage developed and hud on/off. Type help for more.";}
 render();$("feedback").textContent=reply;
 state.history.push({command:raw.trim(),reply,focus:views[state.focus].title,prose:views[state.focus].prose,stage:state.stage,device:state.device,instrument:$("instrument").hidden?"":$("instrumentText").textContent,inward:$("inward").hidden?"":$("inward").querySelector("p").textContent});
 state.history=state.history.slice(-30);return reply;
}
const guide=[
["look","Return attention to the room."],["listen","Attend to the same sound in either comparison stage."],["inspect viewport / inspect panels","Focus on an existing pod detail."],["stage awakened / stage developed","Change the hypothetical character stage; keep your current focus. These are rehearsal controls only."],["hud off / hud on","Switch the illustrative implant off/on. Senses and inner voice are unaffected."],["hud state signal degraded / hud state normal","Compare unavailable instrument data with a normal display."],["help / history","Consult reference panels. Escape closes them."]
];
function el(tag,text){const e=document.createElement(tag);e.textContent=text;return e;}
function openPanel(name){
 const panel=$("panelContent");panel.replaceChildren();$("panelTitle").textContent={guide:"Commands",history:"Recent activity",notes:"Learning to See"}[name];
 if(name==="guide"){const dl=document.createElement("dl");guide.forEach(([a,b])=>{dl.append(el("dt",a),el("dd",b));});panel.append(dl);}
 else if(name==="history"){if(!state.history.length)panel.append(el("p","Your observations will appear here."));state.history.slice().reverse().forEach(h=>{panel.append(el("h3","> "+h.command),el("small",h.stage+" · implant "+h.device),el("p",h.reply),el("p",h.focus+" "+h.prose));if(h.instrument)panel.append(el("p","Instrument (illustrative): "+h.instrument));if(h.inward)panel.append(el("p","Inner voice (illustrative): "+h.inward));});}
 else{
 ["One room. A developing capacity to perceive it.","This is an isolated design rehearsal with fictional capability examples. It does not read or alter your character, advance time or unlock abilities. Reloading resets this example.",
 "The room, viewport and side-wall descriptions and images come from the existing pod material. The listening passage, acoustic analysis and inner association are illustrative proposals, not new canon.",
 "Try listen, then stage developed, then hud off. The instrument reading should disappear; hearing and the inward impression should remain. Try hud state signal degraded to see an explicitly unavailable reading.",
 "The developed stage pairs two independently hypothetical abilities for comparison. Intuition does not depend on having an implant. We are showing additional awareness, not a busier permanent dashboard.",
 "Next live candidate: discovered signals/notices from the existing HUD rules, respecting discovery and off/degraded states. No numeric meters, upgrade system, AI narrator or shared Discord history is implemented here."
 ].forEach(t=>panel.append(el("p",t)));
 }
 if(!$("reference").open)$("reference").show();
}
$("commandForm").addEventListener("submit",e=>{e.preventDefault();if(!$("command").value.trim())return;command($("command").value);$("command").select();});
document.querySelectorAll("[data-panel]").forEach(b=>b.addEventListener("click",()=>openPanel(b.dataset.panel)));
$("closePanel").addEventListener("click",()=>$("reference").close());
$("reference").addEventListener("close",()=>$("command").focus());
render();

document.addEventListener("keydown",e=>{if(e.key==="Escape"&&$("reference").open)$("reference").close();});
