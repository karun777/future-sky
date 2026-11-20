'use strict';
const el=id=>document.getElementById(id);
const state={away:false,route:false,exit:false,wide:false};
const help='look — take in the table\ninspect route — examine Vela’s idea\nask vela about route — hear what she is considering\ninspect exit — look from the other angle\nsuggest wider turn — offer a pilot’s adjustment\nask vela about drink — a quieter exchange\nleave — step away, without accepting anything\nreturn — return to the table\ncommands — show this list\nOptional ! prefixes work.';
const panels={
notes:['Preview notes','FS-W3-F4 · A Cast Worth Becoming\n\nA fictional, authored rehearsal. The display and route problem are proposed scene furniture. Responses are written for the commands listed in Help; this is not an open-ended AI conversation.\n\nNothing here accepts work, moves a live character or binds a Discord account. State lasts only in this tab; reloading starts this rehearsal again. Personal chart reports are not served.\n\nReview Vela’s initiative, the room for your own choices, and whether the exchange feels worth continuing.'],
character:['Character','Efiishent · Pilot\nVela Marr · Navigator\n\nRoles for this authored undertaking. You choose Efiishent’s actions; his dialogue and feelings are not supplied for you.'],
journal:['Journal',()=>state.wide?'A wider approach is sketched. Vela still needs to check it. Nothing submitted.':state.exit?'The proposed shortcut meets an obstruction. Nothing submitted.':state.route?'Vela has sketched a possible approach. Its exit is unchecked.': 'Vela has invited you to look at a route. Nothing accepted.'],
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
function look(){
if(state.away){show('A little space.','You have stepped away from the table. The conversation can wait.','return · look · commands');return;}
show('A route between.',state.wide?'Vela studies the wider curve. “Something worth checking,” she says. Her cup sits empty beside the display.':state.exit?'The obstruction hangs beside Vela’s curve. She hasn’t erased it. “There might still be something here.”':state.route?'A gold curve crosses the gap between two pale routes. Vela is watching its exit.':'Vela has found the route display before anyone has found the briefing notes.\n\nTwo pale lines cross it. She is looking at the space between them.\n\n“Efiishent. Come and look at this.”','inspect route · ask vela about route · leave');
}
function command(raw){
const cmd=raw.trim().toLowerCase().replace(/^!/,'').replace(/\s+/g,' ');
if(!cmd)return;
if(el('reference').open)closePanel();
el('feedback').textContent='You can leave this here.';
if(cmd==='commands'||cmd==='help'){panel('help');return;}
if(panels[cmd]){panel(cmd);return;}
if(cmd==='leave'){state.away=true;look();el('feedback').textContent='You step away. Nothing accepted; the sketch remains.';return;}
if(cmd==='return'){state.away=false;look();el('feedback').textContent='Back at the table. Your earlier observations remain.';return;}
if(cmd==='look'){look();return;}
if(state.away){el('feedback').textContent='You are away from the table. Try return, look or commands.';return;}
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
state.wide=true;
show('For a little while.','You indicate a wider turn. Vela follows the new departure angle.\n\n“That puts us back into the longer route.”\n\nShe holds the model still, then traces where the lines part.\n\n“For a little while. Yes. Then we come out here.”\n\nShe leaves the curve on the display. “Once I’ve checked it.”','inspect exit · ask vela about drink · leave');return;
}
if(cmd==='ask vela about drink'){
show('An empty cup.','Vela reaches for her cup, discovers it is empty, and looks briefly offended by the fact.\n\n“Apparently I can’t keep track of a drink.”\n\nShe sets it beside the display.','inspect route · leave');return;
}
el('feedback').textContent='No action taken. This rehearsal has authored commands; type commands to see them.';
}
el('commandForm').addEventListener('submit',event=>{event.preventDefault();command(el('command').value);el('command').value='';});
document.querySelectorAll('[data-panel]').forEach(button=>button.addEventListener('click',()=>panel(button.dataset.panel)));
el('closePanel').addEventListener('click',closePanel);
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&el('reference').open){event.preventDefault();closePanel();}});
look();
