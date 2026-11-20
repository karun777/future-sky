# FS-W3-F4 — A Cast Worth Becoming

**W3 Beings · ACTIVE / cast review · 20 November 2026**

Karun authorised a cast whose characters can participate as NPCs and later be assigned to human players through Discord. F14’s opening preview is sealed at 0f13a2f. This feather owns the cast and the preparation for driver assignment. Linked W4 owns undertaking participation and W7 owns a future shared account resolver.

Dedicated worktree /home/efiishent/future-sky-worktrees/w3-f4, branch beings/fs-w3-f4-a-cast-worth-becoming. Base 0f13a2f. Next unallocated Beings feather FS-W3-F5. W3 completed count remains two, overall seals 39.

## People to meet

All six names, appearances, histories, inclinations and relationships below are proposed for author review. Their IDs are stable authoring identifiers independent of names, accounts and jobs. They can be renamed while retaining continuity. No real people or private records were used.

The JSON companion preserves the same drafts as structured data. Role suggestions describe possible contributions. All undertaking seats start vacant. Efiishent may contribute wherever the story and his choices take him. Nemi can collaborate with him or take another part in the work.

## Vela Marr

fs-being-0001 · she/her · possible pilot · Astro Cartographer inclination

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
