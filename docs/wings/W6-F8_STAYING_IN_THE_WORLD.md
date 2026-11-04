# W6-F8 — Staying in the World

Status: SEALED — 4 November 2026. Fixed-screen presentation and parallel live pilot delivered and accepted. See seal below for verification boundaries; earlier checkpoints remain historical.
Home: W6 Expression. Baseline: sealed W6-F7; source 0914578 before documentation seal.
W6 six sealed; project 30. Next unallocated W6-F9. Chapter 1 / W4 remains paused.

## Author direction and outcome

Karun accepted closing the W6-F7 foundation but explicitly rejects treating the window as sufficiently inhabitable. Continue improving this existing window on future-sky.net and neptunelounge, keeping Discord in sync. Aim for a place where a player can stay, attend to the room, understand their condition and pursue available interactions without repeatedly losing context.

## Proposed first slice — for design discussion

Keep the room as the visual centre. Bring relevant room details and available interactions close to the prose; make a selected detail readable in place. Give character condition (including recovery or combat restrictions) a legible place. Make inventory more useful without crowding the scene. Provide a compact recent-events area that distinguishes observed changes from authoritative action results. Preserve quiet passive observation and the existing stable updates.

These are design proposals, not claims that new actions or event history are implemented. Start by inspecting existing inspection, narrative and character-state pathways. Select a small real interaction to carry through both interfaces before expanding the action set. Present a concrete layout/interaction proposal for Karun's feedback; do not substitute generic dashboard decoration for play.

## Boundary and dependencies

Use the existing website, assets, login and shared character authority. Discord remains a supported way to play. Chapter 1 authoring stays paused. No automatic adoption of combat/vehicle/hacking/crafting modes, multiplayer instancing, new game rules, broad account access or a frontend framework migration. Map, portrait and quest notes remain desired parts of the wider direction; decide their order rather than promising all in this feather.

## Acceptance to refine

A player should be able to orient themselves, choose an available interaction, read its consequence and return to the room without losing place. A Discord-side change should update the same character in the web window. No misleading active controls, invented discoveries, hidden activity from passive reads or duplicate actions. Preserve focus/readability during refresh. Define the exact walkthrough after choosing the first interaction.

## Shared wing checkpoints

- W2: room detail and discovery presentation must respect existing geography and knowledge.
- W3: show actual character condition; portrait and richer identity remain separate choices.
- W4: share existing action rules; no Chapter 1 resumption implied.
- W5: viewing remains passive; recovery/idle time must be legible without changing policy.
- W7: inspect and reuse authoritative actions, permissions and persistence before adding endpoints.
- W8: distinguish this continuing ambition from W6-F7's completed foundation; one home/count.

## Return

Read W6-F7 seal and this brief, inspect current web projection and existing interaction services, then develop the first inhabitable scene with Karun. Known defects carried forward: combat enemy-ID consistency, stale rehearsal copy and thin recovery experience. No implementation or deployment in this allocation. Repository documentation remains on expression/w6-f7-window-we-can-inhabit until an isolated W6-F8 implementation worktree is created.

## Web-first experiment — 4 November 2026

Karun chooses to push web gameplay further, with Discord primarily for chat and as a supported fallback. Avoid compulsory switching between apps. Visual references: original DOS Bard's Tale and Sierra/King's Quest, detailed static artwork within nostalgic frames and deliberate typography. Simulation depth remains the priority. The user authorised trying the three proposed treatments.

An isolated, public rehearsal is now available at https://future-sky.net/assets/experiments/w6-f8/index.html on the existing server. Source: tools/authoring/w6f8. The same pod inspection fixture, artwork, journal and command input is shared by three layouts; changing style preserves tab state. It does not connect to the authenticated player or advance Chapter 1. No Discord embed installed: WidgetBot remains an option to evaluate for permissions and login before adoption.

Browser checks confirmed rendering and the panels → display → booking observation loop, typed chain inspection and belongings. Source/public bytes match for all four delivered files. Mobile testing and integration with authoritative inspection/discovery services remain future work. User should compare reading comfort, controls, scene/text balance and sense of place before selecting or combining treatments. W6-F8 remains active, total 30; next unallocated W6-F9.

## Fixed-screen rehearsal v2 — 4 November 2026

Karun rejected all three initial treatments as webpages. Approved direction: one full-viewport frame with no outer scrolling; prominent present text and response controls; separate in-frame inventory, character, journal and map; movement/actions, fictional implant HUD and distinct inner voice. Important passages temporarily occupy most of the screen. Combat may overlay the scene. Approval: “let's fucking go!” after design discussion.

The public rehearsal now implements that direction. Previous treatments are preserved in tools/authoring/w6f8/study-v1. V2 uses existing static artwork and observation fixtures, plain HTML/CSS/JavaScript and native modal dialogs; no new framework. Three fixture rooms allow local movement. Important booking discovery opens a large passage. Combat is a labelled, manually advanced demonstration, not the live combat rules. Inner voice is labelled provisional design sample, not new canon. Inventory, character, journal, map and implant panels are fixture presentations. Escape/Return restores the scene; implant display can be hidden without hiding game controls.

Verification: desktop cloud browser at 1363×936 reported document dimensions exactly equal to viewport (no outer overflow). Visually checked fixed scene/prose/dock; panels → display → booking takeover; movement pod → hallway; map; Escape; implant off with controls retained; combat guard round and withdrawal. Corrected withdrawal to end the demonstration without falsely reducing opponent HP to zero, then rechecked. Source/public byte equality and JavaScript syntax checked. No mobile or live-player integration test claimed.

Boundary unchanged: isolated public assets only; no live API calls, authenticated character changes, Discord messages, service restart or Chapter 1 progression. W6-F8 ACTIVE, not sealed. Next: Karun evaluates the frame and attention transitions; then choose one real shared action for integration. The v2 brief supersedes the initial proposed layout above. Source branch expression/w6-f8-staying-in-the-world, worktree /home/efiishent/future-sky-worktrees/w6-f8.

## Live frame pilot — 4 November 2026

Karun accepted the fixed-screen direction and authorised a live deployment for tests. Deployed a parallel live frame at https://future-sky.net/assets/experiments/w6-f8/live/index.html. It uses the existing authenticated /play API and unchanged pinned walking/connection code; no backend or service change. Original /play remains available, and the parent rehearsal remains isolated. Movement in the live pilot affects the actual character and retains Discord notifications. Source/deployment/test details: tools/authoring/w6f8/live/README.md.

Connected now: room image/prose, movement, inventory/equipment, character name/credits, recent observed changes, closer-reading overlay. Not connected: inspection, map/quest knowledge, implant/internal voice, combat modes. Live page excludes demonstration mechanics and marks unavailable map/journal controls. Sign-in callback still lands at /play; reopen pilot after signing in. No auth widening.

13 automated checks passed (11 existing transport behaviors against the pilot HTML, 2 frame privacy/overlay checks), syntax checked, all four public files byte-matched. Browser verified signed-out gate and viewport fit at1363x936; anonymous API401, original portal200. No authenticated browser session available: Karun's live movement/Discord sync walkthrough is still pending. No mobile assurance or live gameplay pass implied.

## Evolving interface — design direction, not newly authored canon

Karun asks whether the interface can subtly evolve as immersion deepens. Proposed rule: stable navigation and spatial anchors, evolving perception/content. Previously unfamiliar places can acquire remembered meanings; discovered faculties and implant upgrades may reveal new information or actions. Internal voice remains distinct from implant output. Drive any change from explicit server-owned knowledge/ability state, not time spent staring at the browser, a separate frontend progression counter or involuntary visual effects. Never withhold essential controls, condition, connection state or accessibility. Preserve reduced motion/readability and allow a stable presentation. These remain proposals for author review; no progression policy or canon was changed in this deployment.

W6-F8 remains ACTIVE, total30 sealed; Chapter1/W4 paused. Next checkpoint is Karun's real-character test, then shared inspection integration if the frame holds up.

## Seal — 4 November 2026

Karun explicitly authorised sealing this as a substantial step forward and requested a recommendation for the next feather. Sealed outcome: the accepted fixed-screen interaction direction, working isolated rehearsal, and parallel live frame connected to existing authenticated viewing and walking. This is a presentation/pilot milestone, not completion of web gameplay or an assertion of an authenticated player acceptance test.

Evidence: rehearsal implementation 0d63a51; live pilot implementation 08a05f9; 13 passing automated checks, syntax and public-byte verification, signed-out browser gate and viewport checks. User feedback accepted the frame as feeling substantially better and showing a viable path. Authenticated live movement/Discord walkthrough remains pending and must be recorded explicitly when performed. Mobile playability is unverified. No player data reset, backend deployment, service restart or Chapter 1 resumption occurred.

Delivered at https://future-sky.net/assets/experiments/w6-f8/index.html (isolated rehearsal) and https://future-sky.net/assets/experiments/w6-f8/live/index.html (real-character pilot). Original https://future-sky.net/play/ remains available. Source branch expression/w6-f8-staying-in-the-world; seal documentation is not a main-branch merge.

W6 now has seven sealed feathers; project total 31. Next unallocated W6-F9. W7-F6 remains unallocated pending acceptance of the proposal below. Chapter 1 / W4 stays paused, Discord supported.

## Proposed next feather — W7-F6: Attend to the World

Proposal only, not yet allocated or started. Home W7 Engine because the core work is bringing existing authoritative inspection/discovery through both clients. W6 supplies the accepted frame; W2/W4 own existing room knowledge and consequences. No duplicate feather count.

Outcome: a player can inspect a visible pod detail in the live window, see its authored close-up/prose, register the same legitimate discovery as Discord, and return without losing context. Begin with panels → display → booking and a repeat observation. Reuse existing inspection rules; do not implement a second browser progression system.

First checkpoint: complete the pending live-frame movement/Discord walkthrough. Then inspect current Discord action handling and extract/reuse a shared service as needed. Verify identity, current location, body/recovery restrictions and discovery prerequisites server-side; explicit inspection is an action, passive refresh remains a read. Handle duplicate clicks and interrupted responses without repeating consequences. Show only available targets and preserve reading/focus across background updates.

Acceptance: one pod inspection sequence works through the web and Discord against the same saved character knowledge; first/repeat prose agrees with existing rules; revisiting in the other client recognises prior discovery; denied actions and stale room choices are clear; no discovery from merely watching. Record actual live evidence before calling the integration verified. Client synchronization need not spam Discord with every observation: define the useful feedback at implementation review.

Outside this feather: combat interface/rules, crafting, vehicles, broad map/journal rollout, new story content, interface-progression mechanics and embedded Discord chat. Chapter 1 stays paused; connecting existing mechanics is not permission for a fresh Chapter 1 authoring pass. Follow shared inspection with meaningful discovered journal entries if justified by the tested loop, rather than expanding this proposal pre-emptively.

## Shared-wing return after seal

W6: stable scene, prominent present prose, in-frame overlays; essential navigation stays predictable as perception develops. W7: retain existing session/action protections and one authoritative character; pinned pilot transport must not drift. W2/W4: expose only discovered/available knowledge and preserve authored first/repeat observations. W5: passive viewing must not alter idle policy; reading overlays do not pause the simulation. W8: 31 sealed, live player walkthrough outstanding, next proposal unallocated.
