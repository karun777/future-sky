# W6-F1 — How the World Reaches Us

Home: W6 Expression. Status: COMPLETE — bounded inventory of authored media, rendering paths and sampled delivery.
Date: 17 October 2026, approximately 16:10–16:13 AWST.
Return: [Wing Index](../WING_INDEX.md).
Main documentary source revision: c4126e1f712ad46c0a04b5fc7560ed3a16fab363.
Live source checkout: 937c007a2981d10b8e1230f293c85b6c72750425.
Links: W1 Mythos, W2 Worlds, W3 Beings, W4 Play, W7 Engine.
No artwork, prose, routing rules, media configuration or gameplay changed.

## The expression paths already present

| Surface | Existing source / content | Delivery path and boundary |
| --- | --- | --- |
| Room scene | 43 room descriptions; exits, items, enemies and presence information. | NavigationCog.look composes room output; active Thread Nodes/Cube state may change what appears. Not every look necessarily renders the ordinary room card. |
| Room images | 43 image references: 40 placeholder URLs, one external Neptune image, two references to the same hosted Dance Floor PNG. | Navigation calls embed.set_image with the room URL. A reference is not proof Discord displayed it. |
| Item inspection | Three live item image references: Triton Lager, Tiny Book, I Have No Compass. | InspectionCog builds description/type/rarity and known attributes/uses; selected knowledge depends on discovery state. |
| Encounter prose | Authored Thread Nodes, including arrival and service/social scenes already mapped by W3/W4. | Prompts, choices, results and completion state; not a general AI conversation system. |
| Private internal narration | 15 authored internal narratives, plus metadata. | Narrator selects/dispatches impressions through run-channel helpers; once-per-character state and an eight-real-second send throttle apply. |
| Ambient world expression | All 43 rooms have ambient_events; cog has default global fallback and Cube-whisper text. | Idle loop, local-first selection, anti-repeat memory, pacing, entanglement guards and existing-channel delivery. Not a continuous broadcast of every authored line. |
| HUD / fit / speech | Telemetry panels, clothing/equipment summary, speech/emotes and roleplay text. | Existing Discord text/embeds. HUD numbers are presentation fields, not proof of measured psychological states; fit does not establish a wearable-layer image renderer. |
| Music | One room SoundCloud reference, on neptune_lounge. | Look may call GameState.play_music; Wavelink/Lavalink and user voice context are needed. No playback was attempted or verified. |
| FEED7 | Core command sends https://future-sky.net/feed7.html. | HTTP page responds; full frontend behaviour or in-world integration was not audited. |

Sources: [Navigation](https://github.com/karun777/future-sky/blob/c4126e1f712ad46c0a04b5fc7560ed3a16fab363/bot/fsbot/cogs/navigation.py), [Inspection](https://github.com/karun777/future-sky/blob/c4126e1f712ad46c0a04b5fc7560ed3a16fab363/bot/fsbot/cogs/inspection.py), [Narrator](https://github.com/karun777/future-sky/blob/c4126e1f712ad46c0a04b5fc7560ed3a16fab363/bot/fsbot/cogs/narrator.py), [Ambient](https://github.com/karun777/future-sky/blob/c4126e1f712ad46c0a04b5fc7560ed3a16fab363/bot/fsbot/cogs/ambient.py), [HUD](https://github.com/karun777/future-sky/blob/c4126e1f712ad46c0a04b5fc7560ed3a16fab363/bot/fsbot/cogs/hud.py), [GameState audio](https://github.com/karun777/future-sky/blob/c4126e1f712ad46c0a04b5fc7560ed3a16fab363/bot/fsbot/state.py).

Counts came from live disk content, not the initial July attachments. Content may differ from the committed snapshots or loaded memory.

## Assets and sampled HTTP delivery

The live assets/media directories contained 12 non-hidden files in this inspection: 11 image files plus Dance Floor metadata. Included: FEED7 background, Dance Floor image, Lager variants, Tiny Book variants, Compass master/production/Discord/thumbnail variants, and a Lounge photograph.

The runtime checkout tracks six of those files. Tiny Book and Compass image directories were present locally but absent from its tracked-asset list. Their current existence/serving does not establish durable repository preservation; do not delete or regenerate them to tidy the checkout.

Read-only GET requests from the host returned:

| Asset / page | HTTP | Content type | Bytes | Compared with project file |
| --- | --- | --- | --- | --- |
| Dance Floor | 200 | image/png | 3,534,881 | Exact bytes match |
| Triton Lager Discord image | 200 | image/webp | 119,744 | Exact bytes match |
| Tiny Book Discord image | 200 | image/webp | 122,878 | Exact bytes match |
| Compass Discord image | 200 | image/webp | 176,416 | Exact bytes match |
| FEED7 | 200 | text/html | 12,658 | No corresponding project file established in this inspection |

The Dance Floor filename ends .webp.png; its observed response is PNG. That is recorded, not renamed.

These checks verify sampled hosted bytes, not visual quality, Discord caching/rendering, all image URLs, SoundCloud availability or voice playback. The 40 placeholder URLs and external Neptune image were not fetched. Previously generated universe imagery/animation outside these directories was not inventoried, imported or declared absent from the wider project.

## Where output goes

RunRoutedContext routes allowlisted commands to the participant's run channel when possible. Without a guild, character, suitable destination or allowlist match, its inspected code falls back to the invoking context. Background narration/ambient use separate existing-run-channel helpers and do not necessarily create a channel.

Selected source checks:

| In run-channel allowlist | Not in that allowlist |
| --- | --- |
| look, choose, inspect, use | answer, wardrobe, uniform, fit, counterkeeper, search, offer, bar, buy, work, give, bouncer, rumours, create_character, feed7, hud |

The right-hand column is not proof those commands fail. It means their ordinary ctx.send path can remain in the invoking channel. Running them within the intended run channel may conceal that inconsistency; a command issued elsewhere can behave differently.

Source: [Router](https://github.com/karun777/future-sky/blob/c4126e1f712ad46c0a04b5fc7560ed3a16fab363/bot/fsbot/cogs/router.py). No message was sent to a user/channel to test routing in this feather.

## Narrative and ambient pacing

Narrator's room-entry subscription is visible in the sampled service log. Its source records successful delivery and seen state, with once-per-character gating where authored. A missing channel or send throttle can suppress delivery; a catalogue entry does not guarantee every character sees it.

AmbientCog's inspected defaults are: minimum idle 120 real seconds, minimum 90 seconds between ambient events and cap of two per five minutes. The loop scans on a 30-second task cadence and prioritises active-node guards and Rest. Those defaults do not promise precise wall-clock delivery.

The on-disk data/ambient/global_ambient.json has older global_ambient/player_feelings keys. The current cog selects fallback_events/cube_whispers and optionally calls Storage.load_global_ambient. The inspected Storage source has no such method, and a source search found that loader name only in AmbientCog. The expected unpatched source route therefore uses its built-in defaults, not that older file. In-process monkey patches were not introspected; no claim of full runtime configuration equivalence is made.

Ambient also contains a rest path that can move a character to a reset location after idle. It is therefore more than cosmetic output. No rest, idle, narration or arrival event was triggered by this inspection.

## What is still unverified

- Actual player viewing/listening experience, mobile legibility, accessibility and image composition.
- Full Discord delivery, media caching, missing-channel behaviour and routing consistency.
- Lavalink readiness, voice permissions and SoundCloud track resolution. The sampled journal did not establish audio connectivity or successful playback.
- Ownership/provenance and durable preservation of every image variant.
- A coherent audiovisual experience across an entire scene; references and renderers alone do not prove that integration.
- The old ambient-file lineage and whether it should be reconciled with current defaults.

Presentation selects form; it does not gain authority to invent world truth or character knowledge.

## Verification and return checkpoint

Read live room/item media fields, internal narrative count, asset paths/tracking, relevant render/router/audio/ambient/narrator source and sampled logs. Verified four first-party images by HTTP byte comparison and FEED7 by HTTP response. No bot command, channel send, voice connection, media edit or service restart performed.

Reached: prose, images, sound, HUD, routing, private narration and ambient paths inventoried with delivery evidence boundaries.
Open: player experience, routing gaps, audio delivery, asset preservation and global ambient lineage.
W6 completed count: 1. W1/W2/W3/W4/W5/W8 parked at 2 each.
Candidate W6-F2, not activated: One Card That Tells the Truth — verify an existing item inspection card in isolation, including discovery boundaries, image reference and captured presentation. No new artwork or mechanics required.
