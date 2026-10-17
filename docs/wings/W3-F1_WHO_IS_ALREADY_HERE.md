# W3-F1 — Who Is Already Here

Home: W3 Beings. Status: COMPLETE — bounded inventory of existing lore, authored cast, source handlers and live stored records.
Date: 17 October 2026, approximately 14:50–14:53 AWST.
Links: W1 Mythos, W2 Worlds, W4 Play, W7 Engine. Return: [Wing Index](../WING_INDEX.md).
Repository source revision: 0c606f16dd6f56bacd2630285641181526b506af. Live runtime checkout: 937c007a2981d10b8e1230f293c85b6c72750425.

This is an evidence map of existing beings, not a census of every person in the fictional universe or a declaration that every NPC is implemented.

## Named lore and working cast

| Being | Existing evidence | What remains separate |
| --- | --- | --- |
| Efiishent | Red Book: recurring wizard/trickster/technician, Key bearer and Cube guardian; multiple selves are possible. Office and room references also exist. | A stored character sharing the name is not proof of one unified identity across eras or an autonomous NPC. |
| The Dark Rat Queen | Red Book: alchemist, navigator and smuggler of forgotten truths; authored den and sneak lesson. | Lore presence, scripted dialogue, account-character presence and current driver are distinct. |
| The Puzzler | Red Book: riddling architect/curator associated with Cube architecture. | No distinct autonomous runtime character was established in this inspection. |
| Portal Sluts | Red Book: composite meta-being of Efiishent, the Queen and the Puzzler. | Do not duplicate the constituent beings or infer a loaded band-agent from the lore. |
| Lord Vitriol and the comet-possessing entity | Previously recovered macro research describes their Manzo role; The Eternal Struggle carries proposed narrative direction. | Working research and author-level revelation are not public character knowledge or proof of a runtime agent. |
| Sera / Sera Venn | October trembling-glass prose trial, explicitly exploratory. | Not confirmed Chapter One casting or a verified live character. Ilex-of-Many is suggested as a future research subject, not established by that scene. |

[Red Book](../RedBook_V7.2.md); [The Eternal Struggle](../current/THE_ETERNAL_STRUGGLE.md); [research handover](../handover/FUTURE_SKY_OCTOBER_RESEARCH_RECONCILIATION_20261015.md).
Research provenance: narrative-context-trial-1 at dfe9e4a803bc75c852697af298c6d3f29c346c65, recovered during W1; not newly promoted here.

## Existing encounter participants

On-host authored Thread Nodes were inspected without invoking them.

| Participant | Evidence / location | Representation and boundary |
| --- | --- | --- |
| Queen and a small rat | drq_sneak_lesson; dark_rat_queen_den | Authored interaction offers a rhythm/quiet response and an ability path. Delivery and current driver not tested. |
| Counterkeeper | nl_barmaid_chips_name; chip_counter | Asks for a pod name to charge chips. Node ID does not establish that all bar staff are the same being. |
| Counterkeeper noticing a motif | nl_counterkeeper_motif | Authored dialogue/choice records; trigger has once-per-character but no room trigger in this definition. Dispatch requires separate source tracing. |
| Service-runner drone | nl_chips_delivered_anywhere | Delivery text and effects. Includes the absent room ID neptune_lounge_kitchen among several valid locations; that does not invalidate all other triggers. |
| Chrome security droid | nl_security_scan_designation; lounge_service_gate | Identity/designation prompt, not a complete persistent NPC identity. |
| Robed figure / priest | nl_priest_origin_birthday; lounge_priest_alcove | Idle trigger at 45 seconds; accepts a birth date or silence. Do not publish player birth data in the inventory. |
| Pod voices / drones 12 and 7 | arrival_awakening_v1; pod_room, listen option | Heard speech and identifiers; not independently verified bodies or agents. |
| Crowd | pressure_in_the_veins_v1; main_square | Authored social situation, not a fixed roster of named people. |

Source: [Thread Node catalogue](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/data/thread_nodes/thread_nodes.json).
These eight node definitions provide authored cast evidence. Being present in JSON is not proof of a completed player encounter.

## Source-expressed service and social roles

| Role | Directly inspected source | Finding |
| --- | --- | --- |
| Bartender | bar_shop.py, bar_work.py | Purchases, bar dialogue and labour/pay exchange are implemented in source, with character-scoped state. No separate bartender character identity was established. |
| Bouncer | bouncer.py and cogs/bouncer.py | Conditional social encounter with apologise/buy/charm/bluff; cog persists the resulting character flags. No live command was invoked. |
| Silver-eyed patron and companion | rumours.py | Local witnessed claim, explicitly unverified. Source says this is not autonomous NPC communication or global propagation. |
| DJ, dancers, cook-drones, speaker/audience, exercise group, guard drone, space whale | Room descriptions | Authored environmental inhabitants. They are not automatically distinct persistent Characters or autonomous agents. |

Source anchors: [bar shop](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/bot/fsbot/bar_shop.py), [bar work](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/bot/fsbot/bar_work.py), [bouncer](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/bot/fsbot/bouncer.py), [bouncer cog](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/bot/fsbot/cogs/bouncer.py), [rumours](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/bot/fsbot/rumours.py), [rooms](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/data/rooms/rooms.json).
A bartender, barmaid and counterkeeper may later be related; the inventory does not silently equate them.

## Live persistent character records

The configured on-host character file contained **5 record entries** at inspection: names matching Efiishent and the Dark Rat Queen, plus three wanderer-labelled records. Two were in the Lounge, one in the office, one at the chip counter and one in the pod.

These are stored character locations, not evidence that five people were online or physically active. No account IDs, channel IDs, birth details or inventory contents are reproduced here. Naming does not establish NPC status, control source or cross-era identity.

No class or race value was found at the top level of these five records. Do not infer that the beings lack such identities or that the whole class system is absent.

[Config](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/bot/fsbot/config.py) and [Storage](https://github.com/karun777/future-sky/blob/0c606f16dd6f56bacd2630285641181526b506af/bot/fsbot/storage.py) supply the path/load route. Live bytes, not the repository's historical character snapshot, provided the count. No character record was modified.

## Encounter creatures and enemies

The live room store had **20 enemy-instance entries across 16 room records**. Entry count is not a verified count of living creatures; health, aliases, defeat and resolver behaviour require their own checks.

Instance prefixes observed: cable_serpent, coldshade_mite, customs_eye, echo_vagrant, glass_spine_lurker, glitch_mote, guard_drone, maintenance_gremlin, panel_nibbler, pickpocket_drone, rail_warden, ratway_skulk, service_stalker, sewer_cyber_rat, sewer_cyber_rat_1, tunnel_skitterling.

The separate enemies.json held three templates: Goblin, Cyber-Rat and Rogue AI. Room instance vocabulary and template vocabulary therefore differ. Overrides and fallback resolution must be inspected before declaring missing templates, duplicates or broken enemies. No repairs are included.

## Identity, role and driver

The [current ontology](../current/ARCHITECTURE_v1.1.md) distinguishes Character, Role and Driver. The inventory supplies examples of different representations; it does not create a new NPC ontology or require every decorative inhabitant to have a record.

A persistent account character, a line of dialogue and an independently deciding agent are different evidence. The inspected data directories and repository path scan did not identify a dedicated NPC catalogue. This is a scoped finding, not proof that no NPC-related material exists elsewhere.

## Verification and return checkpoint

Read-only host inspection: character-record summaries, room descriptions and enemy entries, enemy templates, all eight authored nodes, and bouncer/bar/rumour source. Current Red Book and ontology read through GitHub. Bot was active with PID 799778; no live encounter or autonomous-agent behaviour was tested.

Reached: existing named lore, encounter cast, social roles, stored character records and encounter creatures distinguished.
Open: stable NPC identities, role equivalences, current drivers, character continuity and source-to-live delivery.
W3 completed count: 1. W1, W2 and W8 parked at 2 each.
Candidate W3-F2, not activated: make an identity/role/driver map for the existing cast, marking unknowns without creating new agents. This completes the Beings chassis before deeper character authoring.
