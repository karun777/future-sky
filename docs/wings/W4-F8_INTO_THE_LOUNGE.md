# W4-F8 — Into the Lounge

Home: **W4 Play**  
Status: **REVIEW — implemented and verified offline; not deployed or played in Discord.**  
Allocated by Karun: 21 October 2026, Australia/Perth.  
Source baseline: `6a5fa58`, expression/w6-f5-before-first-breath.  
Working branch: `play/w4-f8-into-the-lounge`.  
Counts unchanged: W4 six sealed; total twenty-two. Next unallocated W4-F9.

## Bounded outcome

Connect the existing awakening to a discoverable, optional first interaction in Neptune Lounge. Reuse the pod token/counterkeeper exchange rather than invent a new quest, resident identity or mission gate.

Read alongside [W4-F3](W4-F3_TWO_DAYS_AT_NEPTUNE_LOUNGE.md), [W4-F2](W4-F2_ONE_LOOP_THAT_HOLDS.md), [W3-F3 playable arrival](W3-F3_FIRST_PLAYABLE_ARRIVAL.md) and [the adopted experience direction](../current/IMMERSIVE_PLAYER_EXPERIENCE_20261018.md).

## What the player encounters

Existing route, unchanged: pod west → hostel hallway down → hostel stairwell down → Neptune Lounge.

An arrival with an established pod opening receives a short attention field alongside the normal room description:
- Hallway: Lounge noise below, with the existing down route.
- Stairwell: sound, warm metal, detergent and chips, with the existing down route.
- Lounge: counterkeeper and optional inspection/bar actions; the existing inside route is offered when its destination matches.
- A remembered gig appears only when the booking discovery is recorded and this arrival has not explicitly excluded a performance booking.

Example at the Lounge:

> A counterkeeper works behind the counter. You can pause here before going farther.
>
> Try `!inspect counterkeeper` or `!bar`. `!go inside` takes you farther into the Lounge.

A player who has read the performance notice also remembers the gig tomorrow night and the still-unknown format. A generic arrival receives no gig appointment.

Counterkeeper inspection responds to the inspecting character:
- Carrying the pod token: offers `!offer token` as an option.
- Token already exchanged: recalls the existing warning and remembered exchange.
- No token: offers the bar or exploration without requiring an exchange.

The existing offer action consumes the token and records the exchange. It does not award a new item, disclose the Queen, satisfy the diplomatic quest or invent a next objective. The counterkeeper remains an existing scripted role; no autonomous NPC is claimed.

Players can bypass the token and continue exploring. Existing bar buying remains another available consequential action, not a requirement to consume alcohol.

## Implementation and ownership

`bot/fsbot/lounge_arrival.py` selects local prose and guidance without mutation. Navigation remains movement authority; inspection presents the counterkeeper card; existing token exchange code remains inventory/consequence authority.

The navigation render adds one attention field. It does not replace room descriptions, exits, other occupants, enemies or images. Guidance follows verified exit mappings rather than hardcoding movement authority.

Added offer/bar/buy to the existing private run-channel routing allowlist, as these existing commands are now explicitly surfaced by the passage. No command, schema, cog, renderer or engine layer is added.

## Verification

**161 isolated tests pass**, including five new tests in `tests/test_lounge_arrival.py`:
1. Registered NavigationCog command callbacks walk west/down/down, persist real fixture movement, publish three room-entry facts, inspect and offer the token, then reload and reject replay.
2. Generic arrival with no token or booking remains able to inspect and explore; inspection is non-mutating.
3. Booking appears only after discovery; no ambassador/Queen/meeting secret is disclosed.
4. Scene/cube boundaries, unrelated inspection and changed exits suppress inappropriate guidance.
5. All surfaced action commands are included in private run routing.

The movement trial registers the cog with a Discord Bot without connecting, so internal command calls bind as they do in the live bot. Character storage uses production JSON writes exclusively in temporary directories; other-character state is preserved. The suite retains existing token failure/retry tests.

`git diff --check` passes. No live character, room, item, clock or service changes. No live walkthrough, audio playback, real Discord routing or simultaneous-player trial claimed.

## Shared checkpoints

W1: no new cosmology or hidden identity disclosure.  
W2: existing route retained; shared room contents untouched.  
W3: existing counterkeeper role, not a new autonomous character; generic/particular arrivals remain distinct.  
W5: “tomorrow night” remains remembered notice wording; no timer or deadline implementation.  
W6: short contextual guidance composed with normal room output; no new art or automatic messages.  
W7: existing authority boundaries; isolated worktree, no runtime installation.  
W8: W6-F5 return preserved below; one allocated home feather, no completion increment.

## W6-F5 return carried forward

The supplied Discord transcript confirms illustrated stages through Gathering/review and Awakening. Karun likes the images and says the functional run felt good, while prose and timing need work; he did not fully immerse himself and wants to return later.

Keep W6-F5 in REVIEW. Image delivery/functionality is evidenced; immersive pacing and final prose are not approved. Final cancellation after the illustrated run is not supplied in the transcript. W3-F3 remains REVIEW with fresh-character/server handoff still untested live.

## Return

Review this first passage before installation. Next check is a controlled live walk from the existing pod to the counterkeeper, preserving Efiishent's actual state and accepting either a prior exchange or no token rather than resetting him to force the scene. Full gig preparation and the allied-representative quest remain W4-F3 authoring work; they are not silently implemented here.
