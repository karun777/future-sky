# W6-F9 — Learning to See: The Future Sky HUD

Status: ACTIVE / DESIGN REVIEW — 5 November 2026, on Karun's acceptance of the next-step proposal. W7-F7 sealed on 5 November after player screenshots confirmed HUD equipment change and matching Discord fit. This is the next design return. No seal/count increment. Next unallocated W6-F10.

## Purpose

Adopt Future Sky HUD as the player-facing name for the web game window at https://future-sky.net/play/. Develop one stable frame through which a character attends to the world. This is a design direction; the complete awakening handoff and progression mechanics are not yet implemented. Discord remains supported. Chapter 1 / W4 remains paused until explicitly unpaused.

Read W6-F3 — The Display Behind Your Eyes before implementation. That feather distinguishes technological HUD, internal voice and ambient reception. The broader product name does not silently turn the character's senses or intuition into implant output. HUD off/fault states must not remove the player's basic command access or ordinary perception.

## Design agreement

- Stable frame: current scene/image, present narrative, persistent commands and quiet bearings with obvious exits. No outer-page scrolling. Reference panels can scroll internally.
- Type to act; click to consult inventory, character, journal, map and history. Main-panel attention follows inspection, conversations and encounters. Closing a reference panel restores the prior focus.
- Perception presents what this character's senses reveal in this situation. Artwork is a view, not proof of hidden knowledge. Use a clearly contextual room image when a detail has no illustration; do not invent a close-up or reuse misleading unread-notice artwork.
- Technology adds capabilities supported by actual equipment/state: recordings, communications, analysis, maps, feeds, audio/video and possible AI assistance. These are future candidates, not unlocked by this document.
- Internal voice carries associations, remembered fragments, intuitive impressions and uncertainty: Karun's warm data. It develops with the character independently of implant ownership/enablement. Do not dress conjecture as a measurement.
- Capabilities may unfold; essential readability, keyboard access and familiar control placement are never progression rewards. Avoid controls unexpectedly moving as the character develops.
- Each presented signal needs an authoritative producer, recipient/knowledge rules, freshness, and a clear distinction between observation and interpretation. No invented percentages or automatic upgrades.

## First comparison — design only

Same room, same physical world, two hypothetical stages. This is illustrative presentation, not new canon or a grant to Efiishent.

Newly awakened: the pod image, immediate visible surfaces and the authored room narrative. Commands and obvious exits remain plainly available. A discovered notice is readable; undiscovered information is withheld.

More developed: the same room layout and command position. An acquired instrument could provide a labelled analysis of a signal; a learned ability could reveal a separate intuitive association. Each addition appears near the relevant detail, with its origin and uncertainty evident. Greater perception need not mean a busier permanent dashboard.

The next reviewable deliverable is a paired visual using existing pod artwork and explicitly fictional capability fixtures. Keep it isolated from live progression until accepted. Then choose one existing, authoritative capability for implementation, rather than building an upgrade tree all at once.

## Awakening handoff

Proposed flow: Discord brings the player to the threshold; an Attend to the world link opens /play/ through existing Discord authentication. The supported awakening sequence should then be completable in the web window without compulsory repeated app switching. Audit verbs and recovery/returning-player paths before unpausing Chapter 1. Do not auto-send new Discord messages merely because this design is recorded.

## Boundaries and acceptance

No general combat, hacking, vehicles, AI narrator, live media feed, progression economy, sensory/chakra simulation or event-history implementation in this initial feather scope. Shared game history rendered in both web and Discord is separately scoped; current per-tab history is not that system.

Review: visual continuity at laptop sizes; command and reference-panel accessibility; ordinary perception survives technological HUD off; discovered/undiscovered and stale information; internal voice retains independent provenance; Discord and web show the same authoritative state. No live character reset to demonstrate a fresh awakening.

W6 owns presentation; W3 owns character faculties; W4 owns awakening/play consequences; W5 timing and attention; W7 producers/persistence; W8 acceptance and scope. No duplicate feather counts.

## Return from W7-F7 seal — 5 November 2026

Carry presentation polish into this design pass: render equipment confirmations without raw Markdown, improve wardrobe imagery beyond the contextual room fallback, make internally scrolling detail content evident, and avoid duplicated bearings or technical offer language. Keep the stable command box and type-to-act contract. Pod-delivery collection through the web needs a separately scoped W7 adapter; do not claim it exists. The inherited fresh-character discovery and first-selection live checks remain outstanding. Chapter 1 remains paused.

## First design rehearsal — 5 November 2026

W6-F9 activated on Karun's instruction “let's go W6-F9”. Isolated branch expression/w6-f9-learning-to-see, based on W7-F7 seal 3955ef5. Source: tools/authoring/w6f9/. Rehearsal: https://future-sky.net/assets/experiments/w6-f9/index.html. Hosted on the existing Neptune Lounge server; no new hosting product or live-frame replacement.

Built the agreed comparison as one stable frame with two command-selected fixtures: stage awakened and stage developed. listen presents the same illustrative sound. The developed fixture adds a hypothetical acoustic instrument and a separately labelled uncertain inner association. hud off hides the instrument but retains hearing and intuition; hud state signal degraded marks the reading unavailable without showing a prior sample as current. No measurements, numeric meters, timestamps or factual source identification are invented. These controls configure only this rehearsal; they do not unlock abilities or represent the live character.

Existing p01/p02/p06 pod artwork and authored pod/panels/viewport descriptions are reused. Listening prose, instrument output and inner association are explicitly design-only proposals. The awakened fixture is a moment when sight and hearing are available, not an implementation or reordering of sensory-return stages. Reference overlays are nonmodal; Escape/Close returns focus to commands. The history captures command, result and the displayed perception channels in memory only. Actual movement, wardrobe, collection, live signals, real audio, saved progression and authentication are deliberately absent from this isolated comparison.

### Verification and deployment
- Public rehearsal index returned HTTP 200; three public file hashes checked against source.
- Chrome visual review at the user's existing 1512 × 784 viewport: stable frame, visible commands/exits, ordinary and developed listening views. Reduced secondary-text spacing after observing the lower inner-voice note clipped in the first pass.
- Browser interaction checks: listen; stage developed retains listening focus; hud off retains hearing and inner voice; degraded signal conceals the normal instrument reading; commands work with guide open; Escape closes guide; history retains meaningful results including the two extra channels; viewport inspection changes attention and image.
- No browser console errors reported in the checked final comparison. No automated Python suite rerun for this isolated static study. Other viewport sizes and player acceptance remain pending.
- Only /assets/experiments/w6-f9/ is published. No bot restart, backend, player-state, /play/ or W7-F7 asset change. Chapter 1 remains paused.

### First live capability candidate
Current source bot/fsbot/cogs/hud.py already derives discovered FEED7, unread notification and remembered booking from saved discoveries and respects enabled/dark/degraded settings. Recommend reusing that projection as the first real HUD capability after the visual agreement, with a shared presentation-neutral producer and authenticated web projection. Do not activate the hypothetical instrument/inner association as a substitute for authoritative data. FEED7 playback, shared event history and pod-delivery collection remain separately scoped.

Status: ACTIVE / DESIGN REVIEW. Await Karun's judgement of the same-room comparison before connecting a live capability. 33 feathers sealed, W6 seven; no seal increment.

## Cinematic veil rehearsal — 5 November 2026

Karun selected A, Cinematic veil, after three visual studies and approved stronger text on a shadowed backing panel. Follow-up bright-scene and Inventory-open studies accepted. This supersedes the first rehearsal's large prose and stacked image/narrative proportions.

Implemented in tools/authoring/w6f9/: full-window existing pod illustration; compact semibold ivory narrative on a dark translucent, blurred, shadowed panel; quiet bearings; persistent command input; restored Character, Inventory and Quest Log references. Panels are nonmodal and internally scrollable; opening them preserves attention. On narrow screens the reference temporarily replaces the narrative overlay, while commands remain available. Escape/Close restores command focus. Character reference refreshes when comparison state changes while it is open.

Reference contents are explicitly fictional fixtures, not live character/inventory/quest projections. Existing pod artwork remains; generated concept scenes are visual targets, not newly adopted room canon or production assets. Source uses textContent for dynamic text. No live API, equipment action, discovery, bot restart or /play/ modification.

Verification:
- Chrome review at native 1512x784, 1280x720, short 1366x600 and narrow 390x844; commands and reference controls remain accessible. Temporary viewport override reset afterwards.
- Inventory, Character and Quest Log open; current attention survives switching/closing references.
- Typed commands work with references open. Character updates without stealing command focus.
- listen / stage developed / hud off preserves hearing and inner association while removing instrument output.
- degraded signal explicitly shows no usable reading; no prior reading shown as current.
- Escape closes reference; no browser console errors observed.
- git diff --check clean. Public assets compared to source hashes.

Published only the existing /assets/experiments/w6-f9/ rehearsal. Await player review of actual browser composition before live integration. W6-F9 remains ACTIVE / DESIGN REVIEW; Chapter 1 paused; no feather seal/count change.

### Cinematic veil refinement — 5 November 2026

Karun approved a refinement pass after supplying four screenshots of room, listening, viewport and panels.
- Reduced body prose from bold to regular weight; retained stronger headings and high-contrast ivory text.
- Softened narrative borders, shadow and translucency; reduced panel width and padding.
- Combined desktop commands and icon-labelled references into one dock row with a small feedback line (about 70 CSS pixels recovered at 1512x784). Smaller widths retain stacked controls and horizontally scrollable references.
- Consolidated location and exits into the top strip. Stage/device comparison labels and notes are now under Rehearsal; typed comparison commands still work. Rehearsal state refreshes while open without stealing typing focus.
- Room/listening framing favours lower room features; viewport and panel views have individual focal positions. Existing artwork retained; cover cropping remains aspect-ratio dependent.
- Verified Chrome at 1512x784, 1366x600 and 390x844: room, viewport, Inventory, Quest Log and Rehearsal; commands usable with reference open; Escape closes; listening and inner association retained with implant off. No console errors observed.
- Public HTML/CSS/JS hashes checked against source; diff whitespace check passed.
- Versioned review link: /assets/experiments/w6-f9/index.html?v=veil2 (avoids stale cached HTML during comparison).
Still an isolated rehearsal. No live character/quest projection, bot/backend or /play/ changes. Await player judgement; no seal/count change.
