# W4-F7 — Getting Dressed

Home: **W4 Play**
Status: **REVIEW — source installed; service stopped, administrator start required**
Allocated by Karun: 20 October 2026, 14:30 AWST.
Counts unchanged: W4 five completed; total twenty-one. Next unallocated W4-F8.

## Outcome and boundary
Make the existing browse → inspect → choose → wear → remove/change → check-appearance loop usable for fresh and returning characters. Keep existing catalogue, first-selection rules, possessions, identities and equipment requirements.
No new wardrobe stock/conditional catalogue, clothes grants for returners, social permissions, layered body model, body creation, live data edits or restart.

## Existing friction and implementation
Returning players saw first-selection prompts despite selection already being consumed. Equipment changes required IDs/slots; core saves failed silently.
- !wardrobe: context-aware first-selection versus returning-player guidance, text-only.
- !wardrobe inspect formal (or full option name): inspect existing catalogue description without granting/wearing.
- !uniform utility/formal/technical/freeform: existing first selection; returners get owned-clothes guidance.
- !wear Travel Coat: exact case-insensitive, whitespace-normalised carried item name or ID; ambiguous names fail with guidance.
- !remove Travel Coat: worn name or ID resolved to its slot.
- !fit: worn state and action guidance; empty chest explicitly described.
- Existing !inspect and !inventory remain available for owned item investigation.
New wearable name resolution lives in dressing.py; CoreCog remains equipment steward and enforces existing requirements. Hand items stay with equip/unequip; no weapon manipulation through wear/remove.
Core equip/unequip now operate on a copied record and restore original memory on save failure, reporting failure instead of success. Existing slot/equipment semantics retained.
Routing and help include new commands. No new extension loader or runtime authority.

## Concrete review walkthrough (fictional fixtures)
A fictional character carries Travel Coat and wears Plain Shirt.
!wear Travel Coat → coat equipped; shirt returned to bag.
!remove Travel Coat → coat returned to bag; chest slot empty.
!wear Travel Coat → one coat equipped again, no duplicate.
Other possessions, hand equipment, other characters and existing arrival records remain intact.
The commands currently render existing equipment confirmations (Equipped/Unequipped), rather than new dress-specific narrative.
Returners cannot obtain another first uniform through this loop. Broader access to wardrobe stock remains an authoring decision.

## Verification
See tests/test_dressing.py: real callbacks, temporary JSON storage, reload-equivalent disk comparison, forced-save failure, requirements, ambiguity, ownership, read-only/text-only browsing, returning guidance, truthful fit, multiword discord.py parsing and run-channel routing.
Full source suite and test count recorded in final verification checkpoint below.
No production deployment or Discord delivery claimed; integration with active choice/recovery gates needs live checks as appropriate.

## Shared checkpoints
W2: pod preparation and wardrobe fixture unchanged.
W3: clothes are presentation, not job/faction/identity/competence.
W4 owns the interaction/equipment loop.
W6: open wardrobe remains text-only; contextual guidance, current outfit and name-based commands.
W7: existing persistent character/equipment store remains authoritative; copied mutation and save-failure reporting.
W8: branch play/w4-f7-getting-dressed builds on sealed W4-F6/W6-F4 branch; main/deployment not implied.

## Return
Review implementation and command walkthrough before selecting live deployment. Preserve existing live overlays if installing selectively. No live character reset.

## Verification checkpoint — 20 October 2026

Full isolated source suite: **140 tests passed**, including ten W4-F7 cases. git diff --check passed. Fictional records and temporary JSON only; no live commands or data edits. Branch ready for review; deployment and actual Discord checks pending. No completion increment.

## Chapter dependency — Karun, 20 October 2026, 14:47
Wardrobe choices should eventually link to unfolding chapter events, employment options and larger factional forces. Record now; author this later, outside W4-F7. Clothing, employment, faction affiliation and actual authority remain distinct. Shared W2/W3/W4 dependency; provisional catalogue retained.

## Deployment attempt — 20 October 2026, approximately 14:49 AWST
Author explicitly authorised deployment. Source 5451ff7; six files installed (dressing.py, core.py, wardrobe.py, router.py, help.py, pod_opening.py).
All five existing targets matched fetched baseline before replacement; six sources compile and installed hashes match. All 61 live data files compared equal immediately before/after installation. Private backup: /opt/futuresky/backups/w4f7-deploy-20261020-144852.
Restart failed operationally: SIGTERM to PID 813169 was treated as clean exit, leaving service inactive with MainPID=0 under Restart=on-failure. Earlier expectation of automatic restart was incorrect. No new Discord readiness or command-load evidence exists yet.
Noninteractive systemctl start was denied: interactive authentication required. Karun was given Mac terminal command ssh -t efiishent@neptunelounge 'sudo systemctl start futuresky-bot'. Do not ask for or expose credentials.
Next: once administrator starts service, verify active PID, extension loads, Discord readiness, Recovery heartbeat, installed hashes and actual dressing commands. No seal/count increment. Do not mistake installed files for a successful running deployment.
