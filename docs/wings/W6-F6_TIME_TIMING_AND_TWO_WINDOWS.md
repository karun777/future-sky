# W6-F6 — Two Windows, One Character

Status: SEALED — author closed this feather on 29 October 2026 following the process report and successful live owner playcheck. Home: W6 Expression. W6 has five sealed feathers; overall total 28. W6-F5 remains REVIEW. Chapter 1 / W4 remains paused.

Original allocated title: **Time, Timing and Two Windows**. The existing filename and feather ID are retained to preserve links and lineage. The timing study remains historical evidence; the seal concerns the bounded outcome below, not a completed game client or general timing system.

## Seal checkpoint — 29 October 2026

**Outcome:** authenticated observation of one existing character through the website and Discord, using the same authoritative game state on neptunelounge. Live portal: https://future-sky.net/play/.

**Boundary:** Discord OAuth identifies the existing Efiishent; an allowlisted read-only web view displays character name, ordinary credits, current location, approved room artwork and ordinary carried/equipped inventory. Refresh reflects Discord movement. Discord remains supported. No character duplication, data reset, new chapter content or website actions.

**Evidence:** implementation 7cf10d4; private setup 6fcf63b; reversible activation 370a909; deployment record 00bdabd; author playcheck 5317615. Source branch expression/w6-f6-two-windows; no merge to main is claimed. Deployment at 18:40 AWST; backup /opt/futuresky/backups/web-portal-20261029-184031. Public page/assets HTTP 200, unauthenticated character API HTTP 401, Discord redirect and bot reconnection independently checked. Author screenshots at 18:45–18:46 show signed-in Efiishent moving from Hostel Hallway to Hostel Stairwell after Discord !go down, with matching artwork and stable inventory.

**Verification:** full 267-test suite passed in the staged runtime environment; three additional installer transaction tests passed separately. Real owner sign-in and desktop rendering were verified by the author's live screenshots. Automated browser visual QA was blocked by unavailable Chromium downloads. Mobile QA, other-account login and live logout/re-login were not established. Do not describe these separate runs as one 270-test full-suite run.

**Retained limits:** manual refresh; single-account pilot; read-only website; narrative, visible exits, map, quest notes, special inventories, portrait and fuller character information are future integration. Image sizing pushes text below the desktop viewport. The stale rehearsal message about dock windows remains a known presentation defect. Sessions expire on restart; no changed world-clock, downtime catch-up or Discord idle-interruption policy.

**Dependencies and operations:** existing Nginx/HTTPS, Python game authority, discord.py and aiohttp; Authlib/HTTPX2 for OAuth. Runtime uses /opt/futuresky/.venv-web-pilot-20261029 through a systemd drop-in. Credentials are private and outside Git. [Architecture and deployment details](W6-F6_WEB_PORTAL_ARCHITECTURE.md) remain the operational record.

**Process reconciliation:** the original presentation study expanded through author-approved corrections into a live account connection. The scope changes were authorised, but the feather boundary and register lagged implementation. This close-out explicitly consolidates that lineage under one W6 feather, with shared checkpoints rather than duplicate Engine/Stewardship counts. The external study is not promoted or newly approved by this seal.

## Shared checkpoints and return

- **W2 Worlds:** existing approved room art can be presented over live location; later maps/exits must respect discovery and room-state rules.
- **W3 Beings:** verified Discord identity maps to the existing character; this adds no new character, ancestry or class canon.
- **W4 Play:** Discord play remains authoritative and supported. Website actions are absent; Chapter 1 remains paused. Carry the stale rehearsal cue forward as a presentation fix.
- **W5 Time:** observing the web view does not count as a Discord command or interrupt idle-home. This is not a new simulation-time policy; future actions need explicit activity semantics.
- **W6 Expression:** authenticated room imagery and character/inventory presentation are proven. Next presentation pass should fit scene, narrative and actions together and adapt existing player-facing text.
- **W7 Engine:** one in-memory game authority, authenticated session ownership and selective deployment are established. Before web actions, preserve checks and persistence and arbitrate competing web/Discord/sequence/idle-home input.
- **W8 Stewardship:** explicit boundary, current summary, author playcheck and deploy/source distinction must accompany future scope changes. Historical records below are superseded where they conflict with this seal.

**Next bounded candidate, NOT allocated:** W7-F5 — One Action, Two Doors: shared checked action execution, initially ordinary movement, with cross-client arbitration and actual web-to-Discord verification. W7-F5 and W6-F7 remain unallocated; no automatic wing switch or new implementation is authorised by this close-out. Resume via the reset ritual, Knowledge Atlas, wing index, this seal and current operational checks.

## Historical development record

The following dated sections retain the earlier study and implementation history. Earlier ACTIVE/UNSEALED, not-deployed and unselected-technology statements are historical and do not override the seal or current architecture summary above.

## Live-account implementation preparation — 29 October 2026

Karun accepted the game-window layout as a start, prioritised connecting existing
Efiishent through Discord website login, and requested explicit technical oversight.
See [the architecture and deployment record](W6-F6_WEB_PORTAL_ARCHITECTURE.md).
An optional aiohttp/Authlib read-only pilot is implemented in source; 267 tests pass.
Read-only portal deployed at 18:40 AWST after private credential setup. Public
routes and Discord reconnection verified. Author screenshots at 18:45–18:46 verify
real owner login and Discord hallway-to-stairwell movement reflected on the website.
See the architecture record for deployment evidence and remaining limits.
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
