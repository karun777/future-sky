# Future Sky — session handover, 29 October 2026

## Start here: the author's correction

Karun wants a game window on the existing Future Sky website and neptunelounge server. He did not request a separate hosted product. The Two Windows study was visually interesting and a useful quick experiment, but looked like a website rather than an invitation to play.

The next interface should show the current room image and accompanying text, avatar, character information, inventory, map, quest notes and available actions, with a persistent command input. Treat timing and presentation as gameplay. Retain basic Discord participation, sharing the same authoritative character/world state with the web client.

Use the existing website/server. Inspect its actual hosting, application and account arrangements before choosing implementation. The author called the domain futuresky.net in this correction; existing project assets and operations also use future-sky.net. Verify the configured domains rather than silently assuming they are interchangeable.

Open source components may be repurposed. HTML/CSS/JavaScript and PHP are welcome possibilities; no CMS, LMS, framework or account system has been selected. Assess what serves the game. Do not initiate another externally hosted Site as the next implementation.

## Current feather and counts

- W6-F6 — Time, Timing and Two Windows: ACTIVE, UNSEALED. The isolated prototype remains a disposable study; the author's correction redirects this feather toward our own game window. Do not count the study as approved or sealed.
- W7-F4 — Return Home When Idle: SEALED. Live route and interruption behavior verified, refinement notes retained.
- W7-F3 — Explicit Sequence Runner: SEALED, a significant author-recognised milestone.
- W4-F12 — An Audience with the Queen: SEALED; music received in the author's live playthrough.
- W6-F5 remains REVIEW. W4-F9/F11 are parked functional drafts.
- 27 sealed feathers overall. W4 chapter work stays paused while engine/presentation work develops. W6-F7, W7-F5 and W4-F13 remain unallocated.

Read ../WING_INDEX.md and the linked feather documents for the full register. Do not infer readiness from historical headers further down the index.

## Immediate next work

1. Read this handover, W6-F6, W7-F4 and the wing index.
2. Refresh Desktop Commander/GitHub connections and inspect the existing server website, routing and authentication arrangements without altering runtime.
3. Produce a concrete game-window layout using existing room imagery and the requested character/game panels. Keep any fictional preview state explicitly labelled.
4. Establish the smallest authenticated, server-authoritative integration after inspecting current code. The Discord context-based sequence runner is not a web API.
5. Review with Karun before expanding scope. Do not resume the paused chapter automatically.

The layout and integration are next work, not completed deliverables in this handover.

## Source and operations

Repository: karun777/future-sky.
Current documentation/source branch: expression/w6-f6-two-windows.
Server worktree: /home/efiishent/future-sky-worktrees/w6-f6.
This branch includes earlier feather work. Do not begin from a stale main checkout without examining ancestry.
Remote Desktop Commander server device: b3786b93-367a-4c51-a8aa-558b0228140c.
SSH: ssh -p 777 efiishent@future-sky.net.

Live runtime /opt/futuresky; service futuresky-bot.service; actual cwd /opt/futuresky/bot.
Consequently live JSON is under /opt/futuresky/bot/data. A separate /opt/futuresky/data exists and differs.
Python /opt/futuresky/.venv/bin/python.
The live checkout contains selective overlays. Never reset/checkout the whole live tree or replace character/room JSON to deploy code.
Server has no rg; use grep when necessary. Refresh service/heartbeat status before treating older evidence as current.
Last recorded deployment: W7-F4, 240 runtime tests passing, PID 915486, eight successful heartbeat subscribers. These are dated evidence, not a new connectivity check.
This handover changes documentation only; no runtime, player state, account system or web deployment changes.

## What currently works

W7-F3: !sequence accepts up to 12 semicolon-separated supported actions (go, work bar, queen pay), validates before execution, executes sequentially through normal checks, stops on failure/choice, preserves earlier committed actions. Live 4/4 route and 0/2 failure-stop verified.

W7-F4: opt-in !idlehome on [real seconds], default 30 real minutes, minimum 60 seconds; off/status/home commands. After inactivity, one checked walking step per roughly minute heartbeat, toward configurable home (initially pod_room). Messages/typing/commands interrupt/rearm. Blocked paths and unsafe states stop movement; no teleport. The 60-second author test reached the pod successfully over several heartbeats. Distinguish idle threshold from travel duration. Observation semantics and visible progress need refinement.

W4-F12: Queen audience at Stardock Overlook after rehearsal and minimum 120 chapter minutes since the rat request. Talk establishes rapport; pay costs one ordinary credit (bar tab excluded) and grants protected Queen music. Author paid and received it. Approval remains unresolved. Rat delay is bounded chapter-clock scaffolding, not complete shared-world time.

Elemental Sound rehearsal uses an isolated booking clock. Direct travel 20 minutes, start at minute 30, rehearse 60, return 20 = 110; wait 10 reaches 120. Travel command starts only at Overlook; clunky route guidance is known. Stale “back at dock windows” text appears even in other rooms. Rehearsal precedes Queen music and does not use it.

## Time and scripting trajectory

The world continues; participation can change. Conscious repeated choices should gradually shape unconscious habits, familiarity and proficiency. Mastery still needs conscious effort; obstacles/entropy call for a new response. Moral/faction habits and long-absence narrative summaries are future direction, not implemented features.

Keep real idle time, shared simulation time, bounded chapter clocks and presentation cadence distinct. Current live world time is persisted heartbeat-driven accelerated time; no general downtime catch-up. Cohorts and long-absence behavior remain design work.

Custom player scripts, generic conditional routines and learned routines are future work. W7-F3 is explicit execution; W7-F4 is a narrow authored automatic routine. Neither proves a general autonomous character system.

## W6-F6 study: retained evidence, not architecture

See ../wings/W6-F6_TIME_TIMING_AND_TWO_WINDOWS.md for exact source/deployment identifiers and verification limitations.
Private external preview: https://future-sky-two-windows.royalpuppy66.chatgpt.site
Source mirror: tools/authoring/w6f6/two_windows (HTML/CSS/JS/tests; bundled images remain in the separate Site source).
Local authoring copy was /workspace/sites/future-sky-two-windows; do not assume scratch survives a new session.
Fictional in-tab state only, no live character connection, refresh resets.
Useful findings: pace independent of story-time costs; interruptible habitual movement; obstacle requiring conscious choice; two renderers sharing one state.
The web Discord view is a mockup, not a real Discord client integration. Optional audio is off by default.
Pure engine and desktop browser flows passed. Mobile visual QA and perceptual audio QA were not performed.
Do not mistake owner-private preview access for game-account authentication. The external preview has not been deleted or promoted.

## Chapter continuity to preserve while paused

Dreamer Technician pathway: freeform attire; tomorrow-night gig; cryptic counterkeeper; 25 restricted bar credits (author spent 5); blue chilled non-alcoholic psychedelic Triton Lager.
Terrace capsule arrives gently on a straight precise trajectory, containing antique box opened by neck key, USB marked tunes. That provisional USB is distinct from Queen music until future mechanics resolve the loop.
An actual rat carries a request to the Dark Rat Queen; she is difficult to reach, at least two hours plus interim work.
Player rehearses before receiving her music. Later evade Vitriol or agent sabotage, send Queen music back to self with Cube power as last action before the performance.
Queen/princess/ambassador identity is author knowledge and must not be disclosed prematurely. Approval phrase “it turns out it turns in” remains unresolved; do not invent its mechanics.
Sabotage, send-back, performance and remaining chapter conclusion are not implemented.

## Working style

One bounded feather at a time, clear Git review documents, distinguish author canon from proposals, favour functional progress with later narrative/aesthetic passes.
Act on authorisation; avoid repeated confirmations. Preserve existing state but do not overcomplicate a fix merely to preserve fragmented player memory.
The author requested a fresh-chat handoff at this boundary. This record is the restart point.
