# W4-F1 — What Can We Actually Do?

Home: W4 Play. Status: COMPLETE — source-grounded command, requirement and consequence map.
Date: 17 October 2026. Return: [Wing Index](../WING_INDEX.md).
Main documentary revision: 71a1c166ce006c453cc8fae5484b4ca2545f6728. Inspected runtime source: /opt/futuresky/bot at 937c007a2981d10b8e1230f293c85b6c72750425.
Links: W2 Worlds, W3 Beings, W6 Expression, W7 Engine.

## Evidence level

The running process points to /opt/futuresky/bot/run_bot.py. Its prefix is ! and declared loader contains 43 extensions. The accessible startup journal at 12:50–12:52 AWST records all 43 loading, including the gameplay cogs below. That is startup evidence, not an in-process command-registry query or a successful player walkthrough.

AST scanning of the live fsbot/cogs/*.py source found **80 unique decorated command definitions and 15 aliases**. The appendix maps every definition to source; counts include utilities and renewal functions, not 80 universally available actions.

No game commands were invoked, messages sent to players, application imports run or stateful trials performed. This feather establishes what source provides and where the live-tested boundary remains.

## Player action and consequence map

Requirements below are the inspected material ones, not a proof that every validation branch has been tested. “Saves” describes a code path, not a demonstrated successful live action.

| Area / commands | Requirements and available response | Consequence / boundary |
| --- | --- | --- |
| Orientation: !help, !commands, !look | Character/room context; available verbs may depend on discovery. | Help/presentation. Look and related helpers may ensure records or rescue an invalid location; do not assume all inspection is side-effect free. |
| Character creation: !create_character / !create / !cc | Name, YYYY-MM-DD and valid class_id; optional origin note. | Character creation path. Existing-record behaviour and complete onboarding require their own test. |
| Arrival: !choose, !answer | An active Thread Node and a valid option or prompt. | Authored results/effects, flags, identity answers, completion and unlocks persist on the participant record. These are not arbitrary freeform NPC conversations. |
| Clothing: !wardrobe, !uniform, !fit | Wardrobe/first selection in pod; valid choice and item catalogue. | Selection is recorded; fit is derived from current equipment. No layered avatar pipeline demonstrated. |
| Pod discovery: !search panel | In pod; one-time character-scoped discovery. | Brass token and arrival flag added to the character, not taken from shared room stock. |
| Token exchange: !offer token | At Neptune Lounge, carrying token, not already exchanged. | Token consumed; exchange flag stored on participant. Not a global counterkeeper memory system. |
| Motif follow-up: !counterkeeper | Lounge; freeform selection, first impression and matching chest equipment; ThreadNodesCog available. | Starts motif node or gives response based on stored answer. Resolves W3-F1's open dispatch question for this particular node. |
| Movement: !go / !move <exit> | Valid exact exit; cube state is checked. | Current room saved; entry event published after movement. Static map is in W2-F2. Cube movement restrictions are not ordinary doorway failures. |
| Item inspection: !inspect | Character; target resolvable through inventory/room/catalogue helper. | Public/discovery-gated description, attributes and image reference. Listed uses do not implement their advertised mechanics automatically. |
| Inventory: !inventory / !inv, !equip, !unequip, !sheet | Stored items, slot/type rules and valid character state. | Bag/equipped state and character display. Full slot-swap/combat-modifier integration not tested here. |
| Room transfers: !take, !drop | Valid character/room/item and matching quantity. | Saves both character and room; code has compensation attempts on save failure. Not proven transactional under crash/concurrency. Lounge freebies add character-scoped social counters. |
| Gifts: !give <item> to <character> | Exactly one different stored character with matching name in same room. | Both bags saved through shared character store. Stored co-location does not prove recipient is online. Tiny Book/Queen acknowledgement is authored conditional text. |
| Item use: !use <item> | Carrying an unambiguous catalogue item with supported use_action. | Helper supports read and heal. Healing may consume even at full HP when specified; unsupported actions fail rather than invent effects. |
| Bar: !bar, !buy Triton Lager | At Lounge, catalogue stock and sufficient credits. | Menu or bag/credit exchange; price in inspected source is 5 credits. |
| Labour: !work bar | Lounge, valid balance/work record, below intoxication threshold and cooldown elapsed. | Bar helper pays 5 credits with 300 real-second cooldown; stores shift history. No general employment simulation inferred. |
| Intoxication / rumour: !use Triton Lager, !sober, !rumours | Item-use conditions; local rumour query uses current room. | Consumed lager triggers intoxication and potentially a witnessed unverified claim. !sober reports state; it is not an instant sobriety action. Rumours do not autonomously propagate. |
| Bouncer: !bouncer apologise/buy/charm/bluff | Pending/free-lager encounter at Lounge; buy also requires credits. | Resolves social flags; buy spends 5 credits. Not generic persuasion or combat. |
| Speech: !say, !think, !pose, !tell, !whisper; emotes | Appropriate content, recipient/run channel and room rules. | Sends roleplay messages. !think projects to the room; it is not private journalling. !whisper requires same room; !tell uses a real mention. No autonomous NPC interpretation inferred. |
| Combat: !combat / !draw / !engage, !attack, !disengage / !flee, !combat_status | Hostile room entries, not in Cube; attack requires active engagement and valid target. | Combat starts auto-round processing and may seed default attack intent. !attack sets ongoing intent, not one isolated strike. Disengage clears engagement/intent but does not move to another room. Full fight/rewards/death not exercised. |
| Learned attention: !perceive | Global unlock gate unless DPC/admin; valid room. | Produces contextual perceptual text. Helpers may ensure character shape. Does not establish clairvoyant world truth. |
| Learned posture: !hold, !attune, !sneak, !descalate, !absorb, !catalyse | Global unlock gate unless DPC/admin; valid character and, where used, room. | Toggle character status and optional intent/timestamps. Stance text is not proof that time stops, NPCs de-escalate or consequence chains execute. Sneaking is supplied to movement; all downstream effects remain task-specific. |
| HUD: !hud, !hud_on, !hud_off, !hud_state | Character; state must be normal/signal_degraded/dark_mode. | Display preferences/state saved; HUD getter may seed defaults in memory. Does not turn canonical world conditions on/off. |
| Time/sky/media: !time, !astro, !feed7 | Their own presentation context; !feed7 sends a URL. | Views/interfaces to other wings. Sending a link is not verified media playback or a verified external page. |
| Cube: !cube | Character/personal cube; prime view is DPC-only. | Personal-cube inspection can ensure/save cube records. Lore-scale travel/lockers not established by this command. |
| Scenario proof: !scenario_start, !scenario_status, !scenario_memory, !scenario_reset | The supported proof scenario is portal_run. | In-memory scenario state/history; separate from persistent Thread Node completion and world opportunity stores. Not the complete arrival scenario implementation. |
| Teleport: !teleport | DPC or explicit teleport unlock, valid target syntax and destination. | Moves stored character; not an ordinary unrestricted navigation verb. |
| Renewal: !reincarnate, !suicide | Separate naming/confirmation flow. | Character-progress-changing game functions; not routine inspection or a session reset. Complete lifecycle not audited or invoked here. |

## Discoverability and implementation seams

- The global gate covers exactly seven skill names: perceive, hold, attune, sneak, descalate, absorb and catalyse. Help/commands bypass it; other commands can still have their own guards.
- The help text advertises !combat on, but the inspected combat handler accepts no on argument. Treat this as a documentation/handler mismatch, not working syntax. No fix in this feather.
- Movement's Cube-state message mentions !cube_exit; that name was absent from the 80-definition scan. Likewise, archived arrival instructions mention !code love, but no decorated code command was found in this scan. Neither absence alone proves no dynamic/other handler exists; do not promise the advertised paths without tracing them.
- The earlier integration document's uncertainty about !use is superseded by the present item-use cog/helper inspection; it is not still a missing-command assumption.
- W3-F1 left the motif node's dispatch open. WardrobeCog.counterkeeper explicitly dispatches it under conditions above; this source finding does not retroactively prove any player's encounter occurred.
- “Read”, “view” and “status” describe intended purpose, not a blanket no-write guarantee: ensure helpers, defaults, schema repair and personal-cube creation can mutate state.
- Persisted text/flags, scheduled combat and emergent world consequences are different strengths of implementation. Do not present posture or flavour as a completed world simulation.

## Complete source command index

All 80 definitions appear once. This is a developer index, not a spoiler-free player menu. Unless explicitly marked, requirements are in the handler/global gate and the matrix above; the label “ordinary/source” is not a permission grant.

| Command | Aliases | Surface | Source |
| --- | --- | --- | --- |
| `!absorb` | — | unlock-gated | [absorb.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/absorb.py) |
| `!runwhere` | — | steward/utility guards | [activity.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/activity.py) |
| `!astro` | — | ordinary/source | [astro_cog.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/astro_cog.py) |
| `!attune` | — | unlock-gated | [attune.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/attune.py) |
| `!bar` | — | ordinary/source | [bar_shop.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/bar_shop.py) |
| `!buy` | — | ordinary/source | [bar_shop.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/bar_shop.py) |
| `!bouncer` | — | ordinary/source | [bouncer.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/bouncer.py) |
| `!catalyse` | — | unlock-gated | [catalyse.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/catalyse.py) |
| `!combat` | `!draw`, `!engage` | ordinary/source | [combat.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/combat.py) |
| `!disengage` | `!sheath`, `!flee` | ordinary/source | [combat.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/combat.py) |
| `!combat_status` | `!status` | ordinary/source | [combat.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/combat.py) |
| `!attack` | — | ordinary/source | [combat.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/combat.py) |
| `!time` | `!gtime`, `!worldtime` | ordinary/source | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!loaded` | `!loaded_commands` | diagnostic | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!create_character` | `!create`, `!cc` | ordinary/source | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!inventory` | `!inv` | ordinary/source | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!inventory_debug` | `!invdebug` | diagnostic | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!equip` | — | ordinary/source | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!unequip` | — | ordinary/source | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!feed7` | — | ordinary/source | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!character_sheet` | `!sheet` | ordinary/source | [core.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/core.py) |
| `!cube` | — | ordinary/source | [cubes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/cubes.py) |
| `!descalate` | — | unlock-gated | [descalate.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/descalate.py) |
| `!emote` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!smile` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!grin` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!dance` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!nod` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!shrug` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!wave` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!bow` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!laugh` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!stare` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!hum` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!toast` | — | ordinary/source | [emotes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/emotes.py) |
| `!give` | — | ordinary/source | [gifting.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/gifting.py) |
| `!help` | — | ordinary/source | [help.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/help.py) |
| `!commands` | `!command` | ordinary/source | [help.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/help.py) |
| `!unlock_command` | — | steward/utility guards | [help.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/help.py) |
| `!hold` | — | unlock-gated | [hold.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/hold.py) |
| `!hud` | — | ordinary/source | [hud.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/hud.py) |
| `!hud_on` | — | ordinary/source | [hud.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/hud.py) |
| `!hud_off` | — | ordinary/source | [hud.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/hud.py) |
| `!hud_state` | — | ordinary/source | [hud.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/hud.py) |
| `!inspect` | — | ordinary/source | [inspection.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/inspection.py) |
| `!sober` | — | ordinary/source | [intoxication.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/intoxication.py) |
| `!take` | — | ordinary/source | [item_transfer.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/item_transfer.py) |
| `!drop` | — | ordinary/source | [item_transfer.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/item_transfer.py) |
| `!use` | — | ordinary/source | [item_usage.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/item_usage.py) |
| `!narrator_reload` | — | steward/utility guards | [narrator.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/narrator.py) |
| `!narrate` | — | steward/utility guards | [narrator.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/narrator.py) |
| `!look` | — | ordinary/source | [navigation.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/navigation.py) |
| `!go` | `!move` | ordinary/source | [navigation.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/navigation.py) |
| `!rooms_find` | — | steward/utility guards | [navigation.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/navigation.py) |
| `!teleport` | — | DPC or unlock | [navigation.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/navigation.py) |
| `!perceive` | — | unlock-gated | [perceive.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/perceive.py) |
| `!reincarnate` | — | renewal/confirmation | [rebirth.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/rebirth.py) |
| `!suicide` | — | renewal/confirmation | [rebirth.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/rebirth.py) |
| `!rumours` | — | ordinary/source | [rumours.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/rumours.py) |
| `!scenario_start` | — | ordinary/source | [scenario_engine.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/scenario_engine.py) |
| `!scenario_status` | — | ordinary/source | [scenario_engine.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/scenario_engine.py) |
| `!scenario_memory` | — | ordinary/source | [scenario_engine.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/scenario_engine.py) |
| `!scenario_reset` | — | ordinary/source | [scenario_engine.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/scenario_engine.py) |
| `!sneak` | — | unlock-gated | [sneak.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/sneak.py) |
| `!say` | — | ordinary/source | [speech.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/speech.py) |
| `!think` | — | ordinary/source | [speech.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/speech.py) |
| `!pose` | — | ordinary/source | [speech.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/speech.py) |
| `!tell` | — | ordinary/source | [speech.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/speech.py) |
| `!whisper` | — | ordinary/source | [speech.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/speech.py) |
| `!choose` | — | ordinary/source | [threadnodes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/threadnodes.py) |
| `!answer` | — | ordinary/source | [threadnodes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/threadnodes.py) |
| `!node` | — | steward/utility guards | [threadnodes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/threadnodes.py) |
| `!nodes_reload` | — | steward/utility guards | [threadnodes.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/threadnodes.py) |
| `!wardrobe` | — | ordinary/source | [wardrobe.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/wardrobe.py) |
| `!uniform` | — | ordinary/source | [wardrobe.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/wardrobe.py) |
| `!counterkeeper` | — | ordinary/source | [wardrobe.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/wardrobe.py) |
| `!search` | — | ordinary/source | [wardrobe.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/wardrobe.py) |
| `!offer` | — | ordinary/source | [wardrobe.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/wardrobe.py) |
| `!fit` | — | ordinary/source | [wardrobe.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/wardrobe.py) |
| `!work` | — | ordinary/source | [work.py](https://github.com/karun777/future-sky/blob/71a1c166ce006c453cc8fae5484b4ca2545f6728/bot/fsbot/cogs/work.py) |

## Verification and return checkpoint

Read live loader, global gate, command decorators, relevant handlers/helpers and startup load records. Every decorated command appears once in the appendix; 80 unique primary names and 15 aliases counted. No application execution or character/world writes; no messages sent through gameplay.

Reached: source-backed action surface, main requirements and consequences mapped with known mismatches.
Open: actual in-process registry, end-to-end player experience, state consistency under failures, and full combat/renewal outcomes.
W4 completed count: 1. W1/W2/W3/W8 parked at 2 each.
Candidate W4-F2, not activated: verify one small non-combat player loop in an isolated fixture environment and record what holds across its steps, without touching live state. Choose from existing interactions rather than expanding mechanics.
