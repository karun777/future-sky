# Future Sky — FS-W3-F4 seal and next-chat handover
20 November 2026 · author-approved bounded seal

## Start here
Connect through Desktop Commander to neptunelounge, device b3786b93-367a-4c51-a8aa-558b0228140c.
Read this file in /home/efiishent/future-sky-worktrees/w3-f4.
Expected branch: beings/fs-w3-f4-a-cast-worth-becoming.
Reviewed implementation checkpoint: 1f5f9963b1ec06b90cff588b6dbc402437b753e6.
The seal/documentation commit follows this checkpoint; verify current HEAD and upstream rather than checking out the checkpoint.

Karun explicitly approved sealing the bounded foundation and preparing this handover. FS-W3-F4 is SEALED for authoring identity/resource groundwork and an isolated encounter system rehearsal. This does not finalise the cast, dialogue, chart interpretations or a general astrology engine. 40 sealed feathers; W3 three, W4 ten, W6 nine, W7 ten, remaining Wings two each. FS-W3-F5 remains unallocated.

## Read in order
1. Applicable AGENTS.md and docs/CONTRIBUTING.md.
2. docs/KNOWLEDGE_ATLAS.md and docs/WING_INDEX.md (current sections override historical entries).
3. docs/wings/FS-W3-F4_A_CAST_WORTH_BECOMING.md, especially seal and carry-forwards.
4. docs/cast/DRAGONFLY_RESCUE_CAST.json.
5. resources/README.md and resources/registry.json.
6. docs/design/ASTROLOGY_AND_LIVING_WORLD.md.
7. docs/wings/W3-F2_WHO_CARRIES_WHOM.md and relevant current W7/shared-core returns before engine edits.
8. tools/authoring/w3f4/README.md, scene.js, serve.py and persistence.test.cjs.
9. For scene lineage: FS-W4-F14_WORK_FINDS_YOU.md, own-worktree W4-F13 home/return, W6-F11 and NL handover /home/efiishent/neptune-lounge-worktrees/w6-f1/docs/handover/FS-W4-F14_EFIISHENT_PREVIEW_HANDOVER.md.

## Verified worktrees at seal preparation
All listed worktrees had no dirty files. Recheck before any edits; preserve concurrent changes.
- w3-f4: beings/fs-w3-f4-a-cast-worth-becoming; HEAD/upstream 1f5f996 before seal.
- w7-f8: engine/w7-f10-beginning-again; HEAD df5a555e42f9e81f002973e1785afdc594a5056e, upstream 216bd0255f0c91a5f3891ea0764f2df2bbc5e4e9. AHEAD TWO: unpublished image-provenance commits 1318de9 and df5a555. Preserve them; do not reset, switch, merge or push this shared branch incidentally.
- w4-f13: play/w4-f13-a-workspace-already-waiting; HEAD/upstream 57d6ad2f6c990d409f5c6a67a3432dc21dd44cd9.
- nl-w7-f5: integration/nl-w7-f5-two-desks-one-engine; HEAD/upstream 909628fee9c176ef0c4177b6d43d33431b075523.
- w4-f14-preview: play/fs-w4-f14-morning-preview; HEAD 0f13a2fa77305b5f150e957c518849ce7a372421; no upstream configured at verification.
Paths above are under /home/efiishent/future-sky-worktrees/. Do not alter installed services or sealed previews.

## What exists
Six provisional cast drafts, stable authoring IDs, independent role suggestions, null Discord bindings. Vela fs-being-0001 is Flame's intended Future Sky counterpart and the navigator. Efiishent fs-being-0007 is an authoring reference to the EXISTING player character, pilot in this undertaking; it is not a new runtime identity. Runtime mapping remains unverified. Other roles are unassigned candidates; portal engineering is separate from navigation.

The fictional Vela route encounter has typed curiosity, disagreement, collaboration, deferral, departure and return. Observations and current preference are distinct; talking never accepts a job. Dialogue is authored branching; astrology informed private studies and writing, not runtime interpretation. Karun is reviewing system behaviour now and will return to content later.

Preview: http://127.0.0.1:8779/#rehearsal-a and #rehearsal-b, through Mac SSH loopback forwarding. Mac device 5bcb9fd1-5e42-43a6-b20c-b861bd1eb152; SSH alias neptunelounge. Server command: python3 tools/authoring/w3f4/serve.py. Check listeners/processes before restarting. Do not reuse F14 port 8778. Serve only the existing whitelist, never repository root.

Versioned localStorage saves are keyed by fictional slot, character and encounter; include partner identity. A/B are independent copies of the same fictional encounter, NOT two authenticated players. Same origin/browser only; clearing browser data removes them. Stale-tab events and preflight comparison block sequential overwrites, but are not atomic concurrency control. No live state or account assignment, no API/storage server and no AI agent.

Tests: connected Chrome exercised branch choices, repeat responses, reconsideration, leave/return, close/reopen, independent A/B histories, stale-tab refusal, reference panels and compact layout. Node harness covers restore, no implicit acceptance, corrupt/inconsistent save preservation, failed writes and stale preflight:
node tools/authoring/w3f4/persistence.test.cjs tools/authoring/w3f4/scene.js
Node was available in ChatGPT execution environment (v24), not on server. HTTP whitelist/private-path rejection verified in initial preview; no endpoint changes since. Phone layout remains unverified.

## Private resource custody
resources/private/ is gitignored and exists ONLY locally in this worktree; preserve/migrate it before removing the worktree. Tracked registry/manifests references do not mean personal originals were pushed to GitHub. Never serve or publish this directory or import it into beta players' context.
- fs-resource-0001: Vela supplied report, private characters/fs-being-0001/source/flame.rtf.
- fs-resource-0002: private Vela study.
- fs-resource-0003: corrected Efiishent report revision 3, private characters/fs-being-0007/source/efiishent.rtf. SHA256 611c3fb834d1bce75f44eae180e749aba71328ef9208f7d2d559763b47173adc; 131401 bytes. Labels and complete cusp table agree on whole signs. Obsolete Efiishent report versions deleted at explicit request; do not restore them.
- fs-resource-0004: refreshed private Efiishent study.
- fs-resource-0005: private pilot/navigator encounter study.
Read registry for precise paths/manifests; do not reproduce personal birth metadata in public handovers or served assets. Source Dropbox reports are user-supplied; no chart recalculation was requested.

Framework direction: traditional Hellenistic foundation with modern planets/esoteric additions. Accepted source shortlist in design checkpoint. AAB retained separately, possibly for advanced mythic characters; no eligibility rule or mythic implementation approved. Chart as an imaginative map of unconscious tendencies, never compulsory player behaviour or a claim of factual diagnosis. Earth-based interpretive context and future/offworld sky computation remain separate questions. General framework v0.1 and other significant characters' natal foundations remain unfinished.

## Next proposed work — engine continuity
Propose a focused W7 feather for stable character continuity and controller assignment, beginning with synthetic accounts. Next W7 ID was W7-F11 in this branch, but verify current shared register and concurrent allocations BEFORE assigning an ID. No new W7 feather allocated here. Use a NEW isolated worktree after reconciling source ancestry; do not build production identity on localStorage or fictional A/B selectors.

Concrete target: a character keeps identity, history, belongings, relationships, natal reference and undertaking role when the controller changes. Separate character, authenticated account, controller and undertaking participation. Existing runtime uses characters[str(discord_id)]; audit shared Discord/HUD resolution before designing migration.

First bounded proof should cover:
- Preserve existing Efiishent identity and inventory; no reset or replacement.
- Synthetic NPC-to-player handover and second synthetic account with proper access separation.
- Suspend NPC actions on human assignment; stale former-controller/queued actions denied.
- No automatic NPC reclaim on disconnect.
- Durable server persistence; atomic assignment, retry and failed-write behaviour; competing claims.
- Provenance of actions and handovers without exposing private charts.
- No real tester invitations, account bindings, live advancement or production deployment in initial proof.

Carry forward cast/content review and interpretation engine separately; do not reopen F4 merely to add more dialogue. Before sealing the next feather, show evidence in the existing HUD and review with Karun.
