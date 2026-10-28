# W4-F11 — A Space to Rehearse

Status: ACTIVE — authoring first slice, 28 October 2026. No runtime implementation or deployment in this feather yet. W4-F10 remains sealed; 24 sealed overall.

## Author direction

Elemental Sound is a bustling creative space, especially for musicians and DJs. Locals rehearse, produce and record. Its O’Connor counterpart may inspire future development; no external research has yet been performed for this draft. The agreed proposed location is reached through Sector 42 above the market. Travel may matter. The player must rehearse before receiving music from the Dark Rat Queen, without rehearsing that music. The relationship to the required approval outcome, “it turns out it turns in”, remains open.

The rat’s future delayed return requires both at least two hours AND an interim requirement. Finding/rehearsing at Elemental Sound is the proposed interim activity; its exact completion gate and clock basis remain undecided. Existing messenger runtime still immediately arranges a meeting; no silent reset or migration.

## First slice — listing, booking, journey

Approved direction: FEED7 advertises a rehearsal room with DJ equipment before tomorrow’s gig; booking provides directions and a clear appointment. Another booking follows, giving punctuality a practical consequence.

Proposed player-facing listing:

> ELEMENTAL SOUND — REHEARSAL SPACE
>
> A room, decks, monitors. Bring something you want to work on.
>
> Above the market, Sector 42. Rehearsal, production and recording rooms share the building. Slots are shared too: arrive ready; the next booking starts when yours ends.

Proposed interaction: preserve the existing !feed7 transmission link and add the local listing for the relevant chapter context. One booking action should reserve the slot and show appointment plus route; do not introduce separate inspect/select/confirm steps. Command spelling is not yet allocated. The booking must not claim a time until the scheduling rule is authored.

Existing route from Stardock Overlook: north to lounge_main_floor; outside to neptune_lounge; north to main_square; up to sector_42. Proposed new exit from sector_42 leads to Elemental Sound’s common area. Keep original room exits and public world data intact. No such new exit or room is live yet.

Arrival draft:

> A bass phrase stops, starts again, then resolves differently. Flight cases pass between open doors. Someone at the desk is listening to a mix with one ear uncovered. Beyond them, room lights mark sessions already underway.

Scope ends at finding and booking the space for this first slice. Actual rehearsal, lateness outcomes and unattended behaviour need their own concrete rules before implementation.

## Time and unconscious scripting — direction recovered 28 October

Author explicitly wants characters to act when timely conscious player input is absent. Past player actions shape habitual choices, including familiarity, proficiency, moral/factional inclination and routine. Mastery needs conscious effort; changing conditions/entropy require renewed creative response. Absence can yield an interesting lived history, including mundane work/spending cycles, rather than frozen characters or mere attendance penalties.

This supersedes any earlier interpretation that character decisions must always stop without the human driver. Record whether an action was consciously directed or habitual/scripted. Do not claim a habit-learning engine, catch-up simulation, temporal cohort system or driver handover already exists.

Cohorts share narrative/temporal contexts and may change as participants progress. Current direction supports one world history with different lived temporal experiences. Automatically pausing each personal clock was an assistant proposal, not an agreed rule.

## Next bounded design decision

Define a scenario progression rule that makes the appointment legible, lets unattended characters respond at authored beats, and relates the rat’s minimum wait to the same chapter context. Specify start, advance, deadline, late consequence and re-entry semantics. Do not translate two hours into real seconds at the changing shared multiplier or advance the global clock for one player’s journey by convenience.

## Source check

Inspected live rooms: no dedicated rehearsal room exists; Main Square, Sector 42 and Transit Pod Bay provide existing foundations. FEED7 currently only sends the public transmission link in CoreCog.feed7. No booking service is implemented there. This document is a concrete authoring checkpoint, not a runtime-completion claim.


## First playable implementation — 28 October 2026

Approved timings: start minute 30, end minute 90, direct travel 20 each way. Early start waits to minute 30; late start retains only the remainder; at/after minute 90 the slot is missed and can be rebooked. Direct complete return is minute 110. No automatic mapping to the rat request timestamp.

Commands: !feed7 retains its existing link and adds the relevant local listing; !rehearsal book; !rehearsal go; !rehearsal start; !rehearsal return. !rehearsal wait N explicitly advances 1–1440 minutes. !rehearsal routine is an explicit habitual-response rehearsal, not an idle trigger or learned habit engine. Status/reading do not advance time. Generic !go movement is not billed by this bounded clock; use the rehearsal travel actions for the timed playcheck. No shared room capacity/reservation system is claimed. Rebooking is per-character, first-pass availability.

Scene state lives in extra.rehearsal_v1. Save precedes success, movement fact follows saved movement. Room registration is additive and collision guarded. Travel validates every route connection before moving. Existing USB, Queen approval, global clock and messenger state are untouched. No images or researched O’Connor-specific details added. Full suite 211 tests passed. Automatic inactivity trigger, richer conscious choices, world/cohort clock integration and delayed-rat gate remain open.

Deployment verified 28 October 2026 19:52 AWST: b7ff3de, six selective code files, 122 data paths unchanged at install. Backup /opt/futuresky/backups/w4f11-rehearsal-20261028-195206/deployment.json. PID 908031 loaded rehearsal, logged into Discord, heartbeat seven successes/zero errors. Live author playcheck pending; feather remains ACTIVE.
