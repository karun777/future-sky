'use strict';

// This authored preview holds attention in this tab only. It has no game transport.
const byId = id => document.getElementById(id);
let arrived = false;
let read = false;
let waiting = false;
let focus = 'waking';

const views = {
  "waking": [
    "WAKING",
    "The morning after.",
    "You wake with a little of last night’s music still going round in your head. You follow it for a few beats before you realise the sound is a memory.\n\nYour fingers uncurl. You take a longer breath."
  ],
  "notice": [
    "HUD · NOTICE",
    "Something has come through.",
    "A small glimmer catches behind your eyes. You blink, and the words stay with you.\n\nDRAGONFLY RESCUE\nCrew call\n\nWork. Already."
  ],
  "call": [
    "HUD · CREW CALL",
    "Dragonfly Rescue",
    "We’re heading out from Triton Central for a routine comet catch.\n\nMeet at Neptune Lounge for a drink and the briefing. We’ll go through the job together.\n\nCome hear what’s involved."
  ],
  "left": [
    "ATTENTION",
    "A little longer.",
    "You let the message slip to the edge of your attention.\n\nFor a moment you find the tune again. A few notes, then it escapes you. You stretch your fingers.\n\nThe call can wait."
  ]
};

function render() {
  const [channel, title, prose] = views[focus];
  byId('channel').textContent = channel;
  byId('title').textContent = title;
  byId('prose').textContent = prose;
  byId('glimpse').hidden = !arrived;
  byId('callStatus').textContent = arrived ? (waiting ? 'Crew call · left waiting' : read ? 'Crew call · read' : 'Crew call · unread') : '';
  byId('hint').textContent = arrived ? 'inspect crew call · leave · look' : 'Take a breath. The morning can wait a moment.';
}

function arrive() {
  if (arrived) return;
  arrived = true;
  focus = 'notice';
  render();
  byId('feedback').textContent = 'A crew call has arrived. You can inspect it or leave it waiting.';
}

function panel(name) {
  const entries = {
    character: ['Efiishent', 'Awake. A few notes from last night keep returning.'],
    journal: ['Journal', arrived ? 'Dragonfly Rescue — ' + (waiting ? 'left waiting' : read ? 'read' : 'noticed') + '.\n\nNo reply sent. No undertaking accepted.' : 'The morning is beginning.'],
    feed7: ['FEED7', 'FEED7 remains available in the wider HUD. This fictional opening supplies no feed content.'],
    help: ['Commands', 'inspect crew call — read the notice\nleave — let it wait, before or after reading\nlook — return attention to the morning\ncommands — this guide\ncharacter · journal · feed7 — references\n\nAn optional ! prefix is supported. Escape closes a reference.'],
    notes: ['Preview notes', 'FS-W4-F14 · fictional visual rehearsal\n\nThe light suggests waking and leaves the location open. Text and timing are proposals for review.\n\nThis tab holds only noticed, read and waiting states. Reload starts this fictional scene again. It has no live connection or saved player state.']
  };
  const [title, text] = entries[name];
  byId('panelTitle').textContent = title;
  byId('panelContent').textContent = text;
  byId('reference').show();
}

byId('commandForm').addEventListener('submit', event => {
  event.preventDefault();
  const command = byId('command').value.trim().replace(/^!/, '').toLowerCase().replace(/\s+/g, ' ');
  byId('command').value = '';
  if (!command) return;
  const panels = {commands:'help', help:'help', character:'character', journal:'journal', feed7:'feed7'};
  if (panels[command]) { panel(panels[command]); return; }
  byId('reference').close();
  if (['inspect crew call', 'inspect call', 'open crew call'].includes(command)) {
    if (!arrived) { byId('feedback').textContent = 'The words have yet to arrive. Take a moment, or type look.'; return; }
    read = true;
    focus = 'call';
    byId('feedback').textContent = 'You read the call. You can leave it waiting.';
  } else if (['leave', 'leave call', 'leave crew call'].includes(command)) {
    if (!arrived) { byId('feedback').textContent = 'There is no call to set aside yet. You have a moment to yourself.'; return; }
    waiting = true;
    focus = 'left';
    byId('feedback').textContent = 'The call waits. No reply has been sent.';
  } else if (command === 'look') {
    focus = arrived ? (waiting ? 'left' : 'notice') : 'waking';
    byId('feedback').textContent = 'Your attention returns to the morning.';
  } else {
    byId('feedback').textContent = 'That action is outside this opening. Try inspect crew call, leave, look or commands.';
    return;
  }
  render();
});

document.querySelectorAll('[data-panel]').forEach(button => {
  button.addEventListener('click', () => panel(button.dataset.panel));
});
function closePanel() { byId('reference').close(); byId('command').focus(); }
byId('closePanel').addEventListener('click', closePanel);
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') closePanel();
});
render();
setTimeout(arrive, 10000);
