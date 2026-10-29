# W6-F6 — Time, Timing and Two Windows

Status: ACTIVE, UNSEALED — author correction received 29 October 2026. The separate private study is retained as an experiment; the next direction is a game window on our existing website/server. W4 remains paused. No new seal; 27 overall. W6-F5 remains in review.

## Live-account implementation preparation — 29 October 2026

Karun accepted the game-window layout as a start, prioritised connecting existing
Efiishent through Discord website login, and requested explicit technical oversight.
See [the architecture and deployment record](W6-F6_WEB_PORTAL_ARCHITECTURE.md).
An optional aiohttp/Authlib read-only pilot is implemented in source; 267 tests pass.
It is NOT deployed: Discord redirect registration and private OAuth client secret
configuration are outstanding. Existing runtime, website and player state unchanged.
No new seal; W4 remains paused.

## Author review and corrected direction — 29 October 2026

Karun found the study interesting and impressive as a quick experiment, but it looked like a website rather than an invitation to play. He explicitly wants to build on our existing website and neptunelounge server, considering open source options, rather than create a separate hosted product.

The desired game window includes avatar, character information, inventory, map, quest notes, current room image and accompanying text. Retain basic Discord play over the same authoritative game state. No CMS/LMS/framework has been chosen. Inspect the existing hosting and accounts before selecting components or integration. The study has not been accepted as the game interface or sealed.

Read [the fresh-session handover](../handover/FUTURE_SKY_GAME_WINDOW_HANDOVER_20261029.md) before continuing. The historical study details below describe what was built, not the approved deployment architecture.

## Review the study

https://future-sky-two-windows.royalpuppy66.chatgpt.site

Owner-private Sites publication, requires the owner's ChatGPT sign-in. This is not deployed to future-sky.net and does not connect to the bot or live character records.

Site project: appgprj_6ae30cdcb0f081918ff9e362b7a57f5c
Source commit: 5792a16b56f9b55e2def2d3e5950be233c9e4aab
Saved version: appgprj_6ae30cdcb0f081918ff9e362b7a57f5c~appgver_81d90512d4bc81918c21885af779fab2
Deployment: appgdep_6ae30e9def04819188177ab31851fba2 — succeeded.

## What to try

Start “Let the journey unfold”. A six-preview-second idle transition starts a familiar route home. Take control to stop it, deliberately choose one next step or resume. Observe without interrupting as a proposed alternative to the live all-command reset. Switch World view / Discord study without resetting the fictional state.

Use Experiment to close the balcony passage. The routine stops for a conscious decision: wait five story minutes or take the hostel stairs. Change the home destination to Neptune Lounge to see the same intention resolve differently. Journey journal preserves routine, observation and directed traces. Sound is optional synthesized Web Audio, initially off.

## Time and pacing

Each walking step costs ten fictional story minutes. The default presentation shows a step after seven preview seconds; options are three or twelve. Visual cadence changes do not change story-time costs. These are expressly prototype assumptions, not new canon or world-clock policy. Six preview seconds do not replace the live idle threshold.

The prototype pauses animation progress while its browser tab is hidden. Reading/listening does not interrupt; taking control does. There is no automatic live server timing, offline catch-up, identity/session linkage or multi-user participation. Both views are renderers over one in-tab fictional state.

## Two presentations

World view: persistent existing artwork, quiet scene prose, compact intention/home/progress panel, story-time indicator, immediate agency, optional journal.

Discord study: an illustrated message/status panel updated in place, compact action buttons and the same state. This is a browser mockup of a possible Discord presentation, not an actual bot message, Discord iframe or SDK integration.

Reused assets: Stardock Overlook, Domefront/Lounge, hostel hallway/stairwell and a pod berth detail from existing generated project art. Balcony intentionally reuses the Overlook illustration. No new imagery generated. No researched real-world interiors or new chapter content.

## Verification

Pure engine checks pass for arrival, observation, pause/one-step/resume, obstacle stop, detour, waiting cost, changed home, presentation-rate independence and shared-view state. Browser QA verified the full initial layout, experiment toggle, routine reaching the obstacle, the same blocked state in Discord view, choosing a detour and arrival at the pod. Desktop viewport verified. Responsive CSS and reduced-motion styles are present; mobile-device visual testing is not claimed. Sound controls implemented; perceptual audio QA not claimed.

Native Sites reports successful private deployment. Opening the published origin in the QA browser showed the expected private sign-in gate; authenticated owner viewing is for the author's review. Preview QA used the managed local preview, not a signed-in production session.

## Source and rebuild

Full buildless source and bundled WebP assets are persisted in the private Site's Git source at the commit above. No credentials are stored in project documents. The Future Sky repository mirrors HTML/CSS/JS, engine checks and README under tools/authoring/w6f6/two_windows; image binaries remain in the Site source to avoid duplicating existing art in this repository. Retrieve the Site source/assets for an exact standalone rebuild. Run node test-engine.mjs; dist is served as static files.

## Game integration boundary

The running game remains Python/Discord. The sequence runner is not a web API. A live web client requires an authenticated session-to-character mapping, server-side action permissions, shared action/result semantics and arbitration of overlapping input. Private member-only hosting is not game-account authentication. Neither PHP, WordPress, LMS adoption, Discord OAuth nor Activities SDK integration is implemented or selected here.

Next review: Does the persistent world view capture the intended aesthetic? Which updates should be quiet, paced, prominent or interruptible? Decide what observation means before changing live idle semantics. Use that feedback to choose the smallest live adapter/presentation step rather than a platform rewrite.
