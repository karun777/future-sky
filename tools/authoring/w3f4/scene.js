'use strict';
const el=id=>document.getElementById(id);
const state={away:false,route:false,exit:false,wide:false,reason:false,preference:null,deferred:false,drink:false};
const help='look — take in the table\ninspect route — examine Vela’s idea\nask vela about route — hear what she is considering\nask vela why — hear her reasoning\nsuggest longer route — disagree without closing the discussion\ndefer — leave the question open\ninspect exit — look from the other angle\nsuggest wider turn — offer a pilot’s adjustment\nask vela about drink — a quieter exchange\nleave — step away, without accepting anything\nreturn — return to the table\ncommands — show this list\nOptional ! prefixes work.';
const panels={
notes:['Preview notes','FS-W3-F4 · A Cast Worth Becoming\n\nA fictional, authored rehearsal. The display and route problem are proposed scene furniture. Responses are written for the commands listed in Help; this is not an open-ended AI conversation.\n\nNothing here accepts work, moves a live character or binds a Discord account. State lasts only in this tab; reloading starts this rehearsal again. Personal chart reports are not served.\n\nSystem rehearsal: test distinct choices, recalled discussion, disagreement and free departure. Dialogue remains provisional.'],
character:['Character','Efiishent · Pilot\nVela Marr · Navigator\n\nRoles for this authored undertaking. You choose Efiishent’s actions; his dialogue and feelings are not supplied for you.'],
journal:['Journal',()=>memory()+'\n\n'+(state.wide?'A wider approach is sketched. Vela still needs to check it. Nothing submitted.':state.exit?'The proposed shortcut meets an obstruction. Nothing submitted.':state.route?'Vela has sketched a possible approach. Its exit is unchecked.': 'Vela has invited you to look at a route. Nothing accepted.')],
help:['Commands',help]
};
function panel(name){const [title,body]=panels[name];el('panelTitle').textContent=title;el('panelContent').textContent=typeof body==='function'?body():body;el('reference').show();el('closePanel').focus();}
function closePanel(){el('reference').close();el('command').focus();}
function show(title,prose,hint){
el('title').textContent=title;el('prose').textContent=prose;el('hint').textContent=hint||'look · ask vela about route · leave';
el('callStatus').textContent=state.away?'The conversation is waiting.':'Route study · nothing submitted';
el('proposal').toggleAttribute('hidden',!state.route);
el('obstruction').toggleAttribute('hidden',!state.exit);
el('proposal').style.display=state.route?'':'none';
el('obstruction').style.display=state.exit?'':'none';
el('proposal').setAttribute('d',state.wide?'M75 350C230 350 280 408 440 388S625 242 725 130':'M75 350C220 350 260 170 445 220S600 240 725 130');
el('mapStatus').textContent=state.wide?'Wider approach · still to be checked':state.exit?'Exit inspected · obstruction found':state.route?'Possible approach · exit unchecked':'Two pale lines. A gap between them.';
el('mapDesc').textContent=el('mapStatus').textContent;
document.querySelector('.chart').classList.toggle('away',state.away);
document.querySelector('.attention').scrollTop=0;
}
function memory(){
return [
state.reason?'Vela explained why she is exploring the gap.':null,
state.preference==='longer'?'You favour the longer route; Vela has kept that preference in view.':state.preference==='wider'?'You proposed the wider turn; it remains unverified.':null,
state.deferred?'You previously left the question open.':null,
state.drink?'You have spoken about the empty cup.':null
].filter(Boolean).join('\n')||'No discussion recorded yet.';
}
function recall(){
const lead=state.deferred?'“We left this open,” Vela says.': 'Vela keeps the alternatives on the display.';
show('Where you left it.',lead+'\n\n'+memory(),'ask vela why · suggest longer route · inspect route · defer · leave');
}
function look(){
if(state.away){show('A little space.','You have stepped away from the table. The conversation can wait.','return · look · commands');return;}
if(state.deferred||state.preference==='longer'){recall();return;}
show('A route between.',state.wide?'Vela studies the wider curve. “Something worth checking,” she says. Her cup sits empty beside the display.':state.exit?'The obstruction hangs beside Vela’s curve. She hasn’t erased it. “There might still be something here.”':state.route?'A gold curve crosses the gap between two pale routes. Vela is watching its exit.':'Vela has found the route display before anyone has found the briefing notes.\n\nTwo pale lines cross it. She is looking at the space between them.\n\n“Efiishent. Come and look at this.”','inspect route · ask vela why · suggest longer route · leave');
}
function command(raw){
const cmd=raw.trim().toLowerCase().replace(/^!/,'').replace(/\s+/g,' ');
if(!cmd)return;
if(el('reference').open)closePanel();
el('feedback').textContent='You can leave this here.';
if(cmd==='commands'||cmd==='help'){panel('help');return;}
if(Object.hasOwn(panels,cmd)){panel(cmd);return;}
if(cmd==='leave'){state.away=true;look();el('feedback').textContent='You step away. Nothing accepted; the sketch remains.';return;}
if(cmd==='return'){const wasAway=state.away;state.away=false;if(wasAway&&(state.reason||state.preference||state.deferred||state.drink))recall();else look();el('feedback').textContent='Back at the table. Your earlier observations remain.';return;}
if(cmd==='look'){look();return;}
if(state.away){el('feedback').textContent='You are away from the table. Try return, look or commands.';return;}
if(cmd==='defer'){
state.deferred=true;state.away=true;
show('Leave it open.','“All right. I’ll leave the sketch here,” Vela says.\n\nYou step away with the question still open.','return · journal · commands');
el('feedback').textContent='Discussion deferred. No route selected or undertaking accepted.';return;
}
if(cmd==='ask vela why'){
const repeated=state.reason;state.reason=true;
show(repeated?'The same question, another angle.':'Why the gap?',
repeated?'“That was my thought: a different approach angle,” Vela says. “A possibility, not a reason to trust it.”'+(state.preference==='longer'?'\n\n“I remember you favour the longer route. We can compare them without committing to mine.”':''):
'“These two routes leave a gap. I want to know whether it gives us a better approach angle.”\n\nShe touches the edge of the display. “Shorter isn’t automatically better. If the exit costs us the room you need, it isn’t useful.”',
'inspect route · suggest longer route · defer · leave');return;
}
if(cmd==='suggest longer route'){
const repeated=state.preference==='longer';state.preference='longer';
show('Keep the longer route in view.',
repeated?'“Yes. We have that as your preference,” Vela says. “I’m keeping the alternative alongside it, not replacing it.”':
'“Fair,” Vela says. “The longer line gives us more room to think.”\n\nShe leaves both routes visible. “I still want to understand the gap. But we don’t have to use it.”',
'ask vela why · inspect route · defer · leave');
el('feedback').textContent='Preference recorded, not a route selection. You can change your mind.';return;
}
if(cmd==='inspect route'||cmd==='ask vela about route'){
state.route=true;
show('Neither, yet.',state.wide?'“The wider turn brings us back into the longer route for a while,” Vela says. “Then out here. I still need to check it.”':state.exit?'“The exit needs room,” Vela says. She moves her finger away from the obstruction. “What would you need to fly that bend?”':'Vela draws a short curve between the two lines.\n\n“This might give us a better approach.”\n\nShe pauses at its far end. “I haven’t checked the exit.”','inspect exit · suggest wider turn · leave');return;
}
if(cmd==='inspect exit'){
if(!state.route){el('feedback').textContent='There are two existing routes. Try inspect route to see Vela’s proposal first.';return;}
state.exit=true;
show(state.wide?'Room to come out.':'The other angle.',state.wide?'Vela turns the model again. The wider sketch goes around the marked obstruction.\n\n“That looks more promising. I’ll need to check the clearances.”':'Vela turns the model. From this angle her curve runs almost directly into a marked obstruction.\n\n“Oh.”\n\nShe looks at it for a moment. “Terrible place for the rest of the ship.”\n\nShe pulls the end of the curve sideways, leaving the bend for you to consider.','suggest wider turn · ask vela about route · leave');return;
}
if(cmd==='suggest wider turn'){
if(!state.exit){el('feedback').textContent='Check the proposed exit first: inspect route, then inspect exit. No adjustment made.';return;}
if(state.preference==='wider'){show('Still to be checked.','“The wider turn is still here,” Vela says. “It still needs checking.”','inspect exit · suggest longer route · defer · leave');return;}
const changing=state.preference==='longer';
state.wide=true;state.preference='wider';
show('For a little while.',(changing?'“A different possibility, then,” Vela says. “We can keep the longer route for comparison.”\n\n':'')+'You indicate a wider turn. Vela follows the new departure angle.\n\n“That puts us back into the longer route.”\n\nShe holds the model still, then traces where the lines part.\n\n“For a little while. Yes. Then we come out here.”\n\nShe leaves the curve on the display. “Once I’ve checked it.”','inspect exit · ask vela about drink · leave');return;
}
if(cmd==='ask vela about drink'){
if(state.drink){show('Still empty.','Vela glances at the cup. “Still haven’t solved that one.”','inspect route · defer · leave');return;}
state.drink=true;
show('An empty cup.','Vela reaches for her cup, discovers it is empty, and looks briefly offended by the fact.\n\n“Apparently I can’t keep track of a drink.”\n\nShe sets it beside the display.','inspect route · leave');return;
}
el('feedback').textContent='No action taken. This rehearsal has authored commands; type commands to see them.';
}
el('commandForm').addEventListener('submit',event=>{event.preventDefault();command(el('command').value);el('command').value='';});
document.querySelectorAll('[data-panel]').forEach(button=>button.addEventListener('click',()=>panel(button.dataset.panel)));
el('closePanel').addEventListener('click',closePanel);
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&el('reference').open){event.preventDefault();closePanel();}});
look();
