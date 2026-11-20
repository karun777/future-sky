# FS-W3-F4 — A Cast Worth Becoming

**W3 Beings · ACTIVE / cast review · 20 November 2026**

Karun authorised a cast whose characters can participate as NPCs and later be assigned to human players through Discord. F14’s opening preview is sealed at 0f13a2f. This feather owns the cast and the preparation for driver assignment. Linked W4 owns undertaking participation and W7 owns a future shared account resolver.

Dedicated worktree /home/efiishent/future-sky-worktrees/w3-f4, branch beings/fs-w3-f4-a-cast-worth-becoming. Base 0f13a2f. Next unallocated Beings feather FS-W3-F5. W3 completed count remains two, overall seals 39.

## People to meet

All six names, appearances, histories, inclinations and relationships below are proposed for author review. Their IDs are stable authoring identifiers independent of names, accounts and jobs. They can be renamed while retaining continuity. No real people or private records were used.

The JSON companion preserves the same drafts as structured data. Role suggestions describe possible contributions. The initial draft left seats vacant; the current author-confirmed plan assigns Efiishent as pilot and Vela as navigator. Other seats remain unassigned. Efiishent may contribute wherever the story and his choices take him. Nemi can collaborate with him or take another part in the work.

## Vela Marr

fs-being-0001 · she/her · navigator (author-confirmed for this undertaking) · Astro Cartographer inclination

A silver braid held with a bent spoon. She turns her cup by its handle before answering.

Once flew freight through the outer settlements. Keeps handwritten arrival notes because she likes knowing who was waiting at the other end.

Wants enough unhurried time ashore to visit someone she has kept postponing.

Speaks lightly while checking every assumption. When frightened, becomes excessively polite.

Can make a difficult approach feel ordinary. Finds it harder to admit she needs relief.

At the briefing she asks which part of the return journey everyone has forgotten to plan.

> “Getting there is usually the easy bit.”

## Oru Penn

fs-being-0002 · they/them · possible kitchen · Mystic Kin inclination

Broad hands, flour caught in a cuff, a little pot tucked under one arm.

Learned communal cooking in a crowded transit habitat. Remembers people through what they ate during bad weeks.

Wants to grow one ingredient aboard that has never survived a voyage.

Offers a taste before advice. Can become stubborn when someone treats rest as wasted time.

Understands provisioning and reads a tired crew well. Sometimes gives help before asking whether it is wanted.

Arrives with something warm to share and asks about allergies before anybody discusses engines.

> “Tell me what you can eat. We can argue about what you like later.”

## Brin Sedge

fs-being-0003 · he/him · possible engineering · Dreamer Technician inclination

A neatly repaired coat over a thoroughly untidy tool roll. One sleeve is always pushed higher than the other.

Kept workshop equipment running through a long supply shortage. Labels his repairs with the names of people who taught him the trick.

Wants to build something that nobody needs him to rescue afterward.

Explains faults through stories. Resents being praised for miracles that should have been routine maintenance.

Good at tracing a fault under pressure. Can keep improving a repair past the point when the crew needs it finished.

Has brought a small failed component to the table and is trying to convince Vela it deserves a proper retirement.

> “It worked yesterday. That is useful information, eventually.”

## Ilex Renn

fs-being-0004 · they/them · possible portal / navigation · Glyph Speaker inclination

Short copper hair and a notebook full of routes drawn over routes. Keeps a clean margin on every page.

Apprenticed among transit surveyors. Learned to annotate uncertainty after two crews confidently described the same crossing in incompatible ways.

Wants a colleague who will challenge their route before it becomes everybody’s problem.

Asks precise questions and waits through uncomfortable silences. Laughs suddenly and warmly.

Strong at portal alignment and explaining route assumptions. Can mistake a fluent explanation for shared understanding.

Leaves a blank sheet in the middle of the table and asks everyone to mark what they think the job involves.

> “Show me where our versions stop agreeing.”

## Tamsin Vale

fs-being-0005 · she/her · possible medic · Mystic Kin inclination

A small practical bag, bright socks, and an expression that makes it difficult to pretend you slept well.

Worked recovery shifts at a transit clinic. Her friendships tend to begin after the emergency, when somebody finally has time to talk.

Wants to travel with people who remember they are allowed to enjoy being alive.

Direct about needs, playful about almost everything else. Dislikes having every conversation made clinical.

Calm triage and attentive follow-through. Has trouble letting others look after her.

Chooses a seat with room for another chair and asks who has actually eaten.

> “Before the dramatic account, how are you now?”

## Nemi Coil

fs-being-0006 · he/they · possible dj · Commotionist inclination

A long scarf tied twice, worn headphones, and fingers that tap until someone else starts speaking.

Learned to play in small rooms where the audience included whoever was cleaning up. Keeps recordings of awkward transitions that later became favourites.

Wants to make a set with someone whose taste unsettles his own.

Listens with his whole posture. Jokes when uncertain, sometimes one joke too far.

Good at noticing when a group loses its rhythm. Sometimes fills a silence that another person needed.

Asks Efiishent which moment of last night’s music stayed with him, and listens to the answer.

> “There was a bit where everybody stopped trying. Did you hear it?”

## Relationships and room for players

Vela trusts Brin’s repairs and presses him for a stopping point. Brin trusts her flying and asks for honest fault reports.

Oru and Tamsin take turns making sure the other one eats. Neither admits this is an arrangement.

Ilex likes the space Nemi leaves between phrases. Nemi enjoys trying to draw Ilex out of careful explanations.

A player receives the character’s established history, present knowledge, relationships and choices already made. Motivation and voice are starting points they can develop. Future plot outcomes stay outside their brief. NPC portrayal can initially be authored by a human facilitator. The draft driver value narrative records that authoring approach and does not claim an autonomous NPC engine.

## Account assignment audit

Verified source at 7db9fef / inherited source 216bd02 establishes these current routes.

| Source | Finding |
| --- | --- |
| bot/fsbot/state.py, ensure_player_records | Uses str(user_id) as storage key and writes ch["id"] = uid. |
| bot/fsbot/state.py, resolve_room_for_user | Normalises and retrieves characters[uid], then may save a repaired room. |
| bot/fsbot/web_character_view.py, character_view | Uses the verified Discord session ID, checks the allowlist and reads storage.characters.get(uid). |
| bot/fsbot/cogs/core.py | Multiple command paths read the invoking Discord account’s character directly. |
| FS-W3-F2 — Who Carries Whom | Already establishes Character / Role / Driver distinctions and identifies controller transfer as open work. |

Consequently, the present game has no verified general NPC-to-account handover. Copying a record under a tester’s account ID would sever or duplicate identity and could replace their existing character. Adding a discord_account_id field to these drafts alone would not change command routing.

The prepared cast is authoring data, not runtime characters.json input. Its null account bindings reserve no accounts and grant no access. Role occupancy is separate from driver assignment. A Discord identity controls a character through a future authenticated binding; a character occupies an undertaking role through an explicit story decision.

## Bounded integration path

1. Introduce a shared account-to-character resolver while preserving legacy records. Existing account-keyed characters need a deterministic identity mapping, with history and references retained.
2. Route both Discord commands and authenticated HUD projection through that resolver. Audit direct storage accesses across command handlers, private-channel routing, saved scene namespaces and history before claiming coverage.
3. Provide an operator-mediated assignment for a nominated account and character. Confirm current controller and account occupancy in the same transaction. Reject conflicting assignments and keep an existing player character safe.
4. Suspend the previous NPC decision source when a human takes control. Check current assignment for each action, including stale sessions and queued NPC actions. A disconnect alone must not hand the character back to an NPC.
5. Record who made each action and the handover event. Preserve the character ID, belongings, relationships, knowledge, location and undertaking occupancy.
6. Rehearse with synthetic accounts through the ordinary Discord/HUD entry points. Cover legacy characters, competing claims, retry, failed persistence, stale former-controller actions and role independence.

These are the concrete requirements for W7 implementation after cast review. No production transfer, new authentication path or autonomous NPC driver has been implemented in this documentary pass. Real tester identities and assignments remain pending Karun’s nominations.

## Draft data and verification

[Structured cast](../cast/DRAGONFLY_RESCUE_CAST.json) contains six unique stable IDs, six independently vacant undertaking roles, reciprocal relationship references and null Discord bindings. A local validation checks identities and references. Runtime tests are unnecessary for this authoring-only change.

Review the people first, then settle the first meeting and select the smallest assignment rehearsal. FS-W3-F4 remains unsealed. F14’s loopback preview is preserved.

[Wing Index](../WING_INDEX.md) · [Who Carries Whom](W3-F2_WHO_CARRIES_WHOM.md) · [Opening](FS-W4-F14_WORK_FINDS_YOU.md)

## Natal foundation — 20 November 2026

Karun requires a birth chart for every significant individual character. For NPCs it will inform the underlying logic of responses, alongside memory, relationships, needs, current circumstances and choice. This is now an acceptance requirement of FS-W3-F4, not a new duplicate cast feather. The six drafts carry explicit pending natal records; no chart has been invented or calculated from their proposed personalities.

The chart belongs to the stable character, independent of role or driver. Assigning a Discord player does not replace it with the account holder’s chart. The older Red Book real-player birth-chart premise needs explicit reconciliation with transferable fictional characters; no real tester birth data is requested by this change. Birth, stasis, reanimation and awakening are distinct events until the framework specifies their meanings.

[Astrology and the living world](../design/ASTROLOGY_AND_LIVING_WORLD.md) records verified source, missing interpretation machinery, system boundaries and the bounded follow-up. W3 owns character natal identity and portrayal; W1 owns meaning; W5 owns temporal/reference-frame reconciliation; W7 owns computation and eventual response execution; W4 consumes permitted effects in undertakings. Existing feathers retain their counts and status. The shared interpretation-engine implementation is a named carry-forward, not an allocated or sealed feather.

Acceptance additions: reconcile the authoritative framework; choose fictional birth inputs with their precision and provenance; calculate reproducible charts; review their interpretation against the cast; demonstrate differing responses to the same situation without deterministic fate or player compulsion. A driver handover preserves natal identity and continuity. Missing time/place must remain explicit uncertainty.

### Interpretive clarification

Karun’s follow-up frames the natal chart as a possible map of unconscious drives, brought into future/off-world play through the Earth-based context of present-day players. The [design checkpoint](../design/ASTROLOGY_AND_LIVING_WORLD.md#author-clarification-earth-context-and-the-unconscious--20-november-2026) distinguishes that psychological premise from local-sky calculation and records shared-framework selection as near-term work. It preserves player agency, character continuity and explicit chart provenance without requiring a complete alien astrology system first. No chart basis or school has yet been selected.

### Foundation selected

Karun has now selected traditional Hellenistic astrology with modern esoteric additions, especially modern planets. The design checkpoint contains a source shortlist for his review and proposed conventions. Earlier statements that no school is selected are superseded; specific conventions and the modern/esoteric source selection remain open. Proceed toward framework v0.1 and a single Vela study within this feather; recovering older NL notes is useful but no longer blocks a source-led draft.

### Sources accepted; AAB kept separate

Karun accepts the source list and retains Alice A. Bailey as a separately referenced body of knowledge. Possible reservation for advanced “mythic” characters is recorded as tentative in the design checkpoint. Baseline cast interpretation remains distinct; no mythic tier, eligibility rule or character assignment is introduced. Framework v0.1 remains the next deliverable within this open feather.

### Supplied report and resource paths — 20 November 2026

Vela now references `fs-resource-0001`, an author-supplied natal report copied byte-for-byte into the isolated worktree. Its supplied chart replaces the planned invented birth-input/calculation exercise for this character. Existing invented characterization remains provisional. Personal identity linkage and source details are retained in the private manifest. No Discord binding or invitation has been made.

[Resource registry](../../resources/registry.json) and [path convention](../../resources/README.md) establish stable character/resource IDs and author-only local source manifests. The private copy is excluded from Git; only the registry and convention travel with the branch. File size and SHA-256 were matched to the original. Preserve/migrate the private directory before worktree removal. Interpretation and resource delivery remain unimplemented; this feather stays open.

### First source-grounded character study — 20 November 2026

Vela has an author-only review study, `fs-resource-0002`, derived from the complete supplied report `fs-resource-0001`. It distinguishes supplied chart factors, traditional conventions, modern interpretation and new fiction, and contains three short scene sketches: introduction, disagreement and a training difficulty. No chart was recalculated, no AAB layer applied and no scene entered live play.

The earlier invented appearance, freight biography, inclination and pilot role remain provisional. The study is a bounded working method, not a completed general framework v0.1 or NPC implementation. Author review of recognisability, voice and role is next. Personal interpretation and scene drafts remain private local resources; the tracked registry provides their stable references. FS-W3-F4 stays open and seal counts do not change.

### Pilot, navigator and second source intake — 20 November 2026

Karun explicitly assigns Efiishent as pilot and Vela as navigator in this undertaking. These are authored scenario assignments, not a live acceptance or movement event. The earlier Vela pilot proposal is superseded. The combined portal/navigation slot is separated into navigator (Vela) and portal engineering (unassigned); Ilex remains only a candidate for portal engineering.

`fs-being-0007` is an authoring/resource reference to the existing Efiishent, not a new runtime character. Runtime mapping remains unverified; no reset, replacement or account reassignment occurred. Resource `fs-resource-0003` preserves his supplied report. Source and destination size/SHA-256 match. The original report uses Placidus; the navigator’s supplied report uses whole signs. Both originals and their conventions remain intact, with differences recorded privately. Efiishent’s full interpretive study remains pending.

The private Vela study v0.1 now carries an explicit supersession notice for its pilot possibility and training sketch. Other hypotheses remain in review. Resource validation covers every manifest, file digest, subject and cast reference. Shared source and installed services are unchanged.

### Regenerated pilot report and private study

The pilot’s supplied report fs-resource-0003 is now revision 2; the prior original and manifest are preserved privately. Transfer checksum and size verified. Source metadata is internally mixed: declared whole signs with the previous Placidus cusp table retained. The text comparison and precise caveat are in the private manifest and fs-resource-0004 study. The new study offers a provisional portrayal and pilot–navigator exchange using supplied positions, explicit whole-sign intent and no recalculation or live effects. Review remains open; no clean whole-sign export is falsely claimed.

### Corrected source and pilot–navigator encounter — 20 November 2026

The corrected pilot report is installed as fs-resource-0003 revision 3. Both labels and the complete cusp table now agree on whole signs. At Karun’s explicit request, obsolete Efiishent report copies were removed from this worktree; historical documentary entries above remain history, not current source warnings. fs-resource-0004 was refreshed against the new digest; the supplied positions and prose are unchanged, so its central interpretation remains applicable.

New private encounter fs-resource-0005 gives the navigator initiative in exploring a route and the pilot a concrete contribution to its flyability. It is a hypothetical author-review rehearsal, not live participation, established mission mechanics or forced player dialogue. Both character resource lists reference it. Review this encounter before further implementation. No seal, deployment, account assignment or live action.

### Interactive encounter preview — 20 November 2026

Authorised continuation implements a bounded, authored Vela encounter in `tools/authoring/w3f4/`, within this isolated cast worktree. Loopback URL http://127.0.0.1:8779 (Mac SSH forward) is separate from sealed F14 on 8778. The inherited visual frame is copied, not modified. Vela invites inspection; typed commands reveal a proposed route, its obstructed exit, a wider-turn suggestion and a quiet exchange. Leave/return preserves tab-local observations without acceptance. Efiishent has no forced dialogue or feelings.

This selectively adapts private fs-resource-0005 into fictional scene prose; no natal data or private resources are served. Route furniture remains provisional. No generic AI response engine, Discord assignment, live movement, service installation or production deployment. Reload resets only this fictional rehearsal.

Verified in connected Chrome: inspect route, optional-prefix inspect exit, suggest wider turn, leave/return with sketch retained, unsupported accept-job refusal, Help, Escape and reload. Visual opening reviewed at desktop size; no browser warnings/errors captured. HTTP checks: three assets 200; registry/private traversal 404; POST rejected 501. Python server syntax compiled; Node syntax CLI unavailable on server, JavaScript instead exercised in browser. Phone layout is authored but not yet visually verified.

Review target: Vela’s initiative and voice, Efiishent’s room to contribute, and whether this feels like an encounter worth continuing. ACTIVE / unsealed; no new feather or seal count.

### Choice and continuity system rehearsal — 20 November 2026

Karun accepts this direction as a system test; dialogue/content remains provisional for later review. Expanded the existing preview with `ask vela why`, `suggest longer route` and `defer`. Vela distinguishes repeated reasoning and suggestions, recalls the current preference after leave/return, and acknowledges reconsideration. The Journal separates discussion memory from discovered route facts. Preferring the longer route preserves the previously explored wider sketch for comparison; no route is selected or validated by discussion.

Memory is tab-local only: reason discussed, latest preference, prior deferral, drink discussed, and existing inspection facts. This is authored branching, not a general memory service or AI agent. Reload intentionally starts the fictional rehearsal afresh. No acceptance transition exists.

Chrome checks exercised curiosity, repeated question, longer-route disagreement before inspection, defer/return, premature wider-turn refusal, inspection and obstruction discovery, changing to wider, repeated wider suggestion, changing back to longer, departure action guard, retained Journal and reload. No browser warning/error was captured. The updated preview remains on loopback 8779. Private sources, sealed F14, live characters and installed services remain untouched. FS-W3-F4 ACTIVE / unsealed; 39 seals unchanged.

### Browser-local persistence rehearsal — 20 November 2026

Authorised next pass adds versioned localStorage saves to the existing loopback preview. Rehearsal A/B are separate fictional encounter copies, not two authenticated users. Stable subject/partner/encounter IDs anchor each record. Closing/reopening now restores observations, preferences, deferral and position at/away from the table; earlier tab-only/reload-reset statements are superseded. No live state, personal resources or commitment transition is included.

Verified in Chrome: close A and reopen, restore its preference and departure, return with recalled reasoning; B begins separately and its drink discussion does not change A; a stale A tab is blocked after another A saves. Final reload and compact-window visual check pass without captured errors. Node harness checks restoration, no implicit acceptance, malformed record preservation, inconsistent-state rejection, failed writes and stale preflight. Source tests run locally with Node 24; server has no Node executable.

Limits: same browser/origin only; slots are not an access-control boundary. Sequential stale-write guards are not atomic concurrency control. Shared server persistence, authenticated character assignment and real player isolation remain future W7 work. This completes the proposed persistence system test for author review; stop here before further implementation. FS-W3-F4 remains ACTIVE / unsealed pending review and explicit scope closure. Content remains provisional; cast/natal/framework carry-forwards remain open.
