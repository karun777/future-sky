export const ROOMS={
 overlook:{name:'Stardock Overlook',chapter:'Docklight wash',image:'overlook',text:'Ships turn slowly beyond the glass. For a while, you watch without trying to remember why.',exits:['lounge']},
 lounge:{name:'Neptune Lounge',chapter:'The vibe sea',image:'lounge',text:'The music finds you before the crowd does. Your feet already know a way through.',exits:['overlook','balcony','arrival']},
 balcony:{name:'Upper Overlook',chapter:'Above the music',image:'overlook',text:'Below you, the dancers move like a single thought. The quiet way home is just ahead.',exits:['lounge','hallway']},
 arrival:{name:'Domefront Arrival',chapter:'Warm neon, distant chips',image:'lounge',text:'A counterkeeper looks up, then returns to their work. You follow the familiar curve towards the hostel.',exits:['lounge','stairs']},
 stairs:{name:'Hostel Stairwell',chapter:'Up from the sound',image:'stairwell',text:'Warm metal, a trace of detergent. The Lounge softens with every step.',exits:['arrival','hallway']},
 hallway:{name:'Hostel Hallway',chapter:'Quiet lives',image:'hallway',text:'Some pods hum. Some are dark. Your door is where you remember it being.',exits:['balcony','stairs','pod']},
 pod:{name:'Your pod',chapter:'Wakefulness module',image:'pod',text:'The hatch settles behind you. The berth is warm. Beyond it, the world continues.',exits:['hallway']}
};
export function route(from,to,avoid=false){const q=[[from]],seen=new Set([from]);while(q.length){const p=q.shift(),a=p.at(-1);if(a===to)return p;for(const b of ROOMS[a].exits){if(avoid&&((a==='lounge'&&b==='balcony')||(a==='balcony'&&b==='lounge')))continue;if(!seen.has(b)){seen.add(b);q.push([...p,b]);}}}return [from];}
export function initial(){return{at:'overlook',home:'pod',phase:'ready',clock:21*60+8,idle:0,elapsed:0,pace:7,avoid:false,obstacle:false,cleared:false,mode:'habitual',moves:0,history:[{text:'You linger at the dock windows.',actor:'scene',clock:21*60+8}],notice:'',view:'web'};}
function log(s,text,actor='scene'){s.history.push({text,actor,clock:s.clock});s.notice=text;}
export function act(state,type,value){const s=structuredClone(state);if(type==='reset')return initial();if(type==='view'){s.view=value;return s;}if(type==='pace'){s.pace=Number(value);return s;}if(type==='obstacle'){s.obstacle=!!value;return s;}if(type==='home'){s.home=value;if(s.at===value)s.phase='home';else if(s.phase==='home')s.phase='ready';log(s,`Home now means ${ROOMS[value].name}.`,'directed');return s;}
if(type==='begin'){s.phase='idle';s.idle=6;s.elapsed=0;log(s,'Your attention drifts. A familiar intention remains.');}
if(type==='observe'){log(s,'You listen. Somewhere below, a rhythm changes.','observation');}
if(type==='take'){if(['idle','walking'].includes(s.phase)){s.phase='paused';s.elapsed=0;s.mode='conscious';log(s,'You take the next decision into your own hands.','directed');}}
if(type==='resume'){s.phase=s.at===s.home?'home':'walking';s.elapsed=0;log(s,'You choose to continue home.','directed');}
if(type==='wait'&&s.phase==='blocked'){s.clock+=5;s.cleared=true;s.phase='walking';s.elapsed=0;log(s,'You wait five minutes. The balcony passage opens.','directed');}
if(type==='detour'&&s.phase==='blocked'){s.avoid=true;s.phase='walking';s.elapsed=0;s.mode='conscious';log(s,'You turn back towards the hostel stairs.','directed');}
if(type==='step'&&s.phase==='paused'){move(s);if(s.phase==='walking')s.phase='paused';}
if(type==='tick'){if(s.phase==='idle'){s.idle=Math.max(0,s.idle-value);if(s.idle===0){s.phase='walking';s.elapsed=0;log(s,`Without a further thought, you begin the familiar walk to ${ROOMS[s.home].name}.`,'habitual');}}else if(s.phase==='walking'){s.elapsed+=value;if(s.elapsed>=s.pace){s.elapsed=0;move(s);}}}
return s;}
function move(s){const path=route(s.at,s.home,s.avoid);if(path.length<2){s.phase='home';return;}if(s.obstacle&&!s.cleared&&s.at==='lounge'&&path[1]==='balcony'){s.phase='blocked';log(s,'The balcony passage is closed for cleaning. Familiarity gets you this far.');return;}s.at=path[1];s.moves++;s.clock+=10;s.phase=s.at===s.home?'home':'walking';log(s,s.phase==='home'?`You made your way home to ${ROOMS[s.home].name}.`:`You pass into ${ROOMS[s.at].name}.`,s.mode==='habitual'?'habitual':'directed');}
export function time(minutes){return `${String(Math.floor(minutes/60)%24).padStart(2,'0')}:${String(minutes%60).padStart(2,'0')}`;}
