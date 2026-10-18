# W4-F4 — Whose Hands Are These?

Home wing: W4 Play. Date: 18 October 2026.
Status: SEALED — isolated implementation and verification complete. Not deployed; Discord delivery and author playtest remain open.

## The passage

Enter with `!awaken` while in the pod and outside the cube. It explicitly selects the performance-arrival strand; it does not impose a gig on every player undertaking the broader allied-representative quest.

Cold blue light. Hands that obey but are not recognised. Breath, a garment, a chain, a pulse through the wall. The player chooses what to attend to.

A supported walkthrough:
1. Create a fresh fictional character using the existing `!create_character` command; its welcome now correctly names the pod and offers `!awaken` / `!look`.
2. `!awaken`; then `!inspect hands`, `!inspect garment`, `!inspect pod`.
3. `!inspect panels` → `!inspect display` → `!feed7`.
4. `!inspect wardrobe` → `!wardrobe`; existing `!uniform utility|formal|technical|freeform` and `!fit` remain available.
5. `!inspect booking`: a gig tomorrow night, with format, instrument and collaborators unresolved.
6. `!look` resumes bearings and remembered booking while retaining ordinary room rendering, exits, presence and HUD. Existing navigation remains available; this is not a locked escape puzzle.

`!examine` aliases inspection. Hints expose supported actions. Hands, body, garment, chain, pod, hatch, viewport, incomplete reflection, light, button, brochure, panels, display, wardrobe, berth and booking have responses. Aliases support common wording. Booking cannot be recorded before panels/display locate the notice. Clothing reflects a selected equipped uniform.

## What the world remembers

The private character record holds `extra.arrival.opening`, with an explicit strand ID and discovery list. Repeated observations do not rewrite unchanged state; repeat awakening does not restart the introduction. Storage failures roll back the in-memory replacement and report failure before publishing success.

No item is granted merely by inspecting the chain; no button is pressed by looking. The existing `!search panel` token action remains separate. The opening does not replace an active Thread Node, reset a character or reveal the Queen's identity.

## Source and evidence

Built from main `b4e1b687ec66d92786f886f0624e423c13a7a0ea` in an isolated archive checkout on Neptune Lounge. No external checkout symlinks. No live character records, credentials or production configuration were copied into fixtures.

Implementation: `bot/fsbot/pod_opening.py`, InspectionCog, CoreCog welcome, NavigationCog description integration and Router command allowlist. No new startup extension is required.

Verification: `PYTHONPATH=bot /opt/futuresky/.venv/bin/python -m unittest discover -s tests` — **73 tests passed**, including **13 new opening tests**. Actual command callbacks, Discord embed construction and production JSON writer run against temporary fictional records. Checks cover fresh creation, FEED7 link, wardrobe browsing/selection, reload, booking prerequisites, repeat observations, unrelated character preservation, failed-save retry, existing node protection, item-card coexistence, non-operating inspection and resumable look. Routing checks verify allowlist eligibility; live channel routing/network delivery are not exercised.

No live code was installed, service restarted or live gameplay state changed.

## Boundaries and return

The seven-day reintegration, unknown instruction manual, full character creation, five desired work-garment categories plus casual wear, clear mirror, cinematics and all-prop visual inspection are still authoring/implementation work. No concept still was installed. FEED7 uses its existing web link.

“Tomorrow night” is narrative text relative to arrival, not a persisted timestamp, scheduler or enforced deadline. This feather implements neither the performance, ambassador conditions, exchange nor two-day reset. The generic quest can involve trade with an allied representative and optional romance; Efiishent's particular Queen encounter stays distinct.

Existing core creation behaviour is retained; this work tests fresh creation, not safe recreation of an existing character. Persistence evidence is isolated sequential callback execution, not a concurrency or live Discord guarantee.

Read alongside [W4-F3](W4-F3_TWO_DAYS_AT_NEPTUNE_LOUNGE.md), [W2-F3](W2-F3_THE_OPENING_WE_CAN_INHABIT.md), [pod inspection](W2-F3_POD_INSPECTION_AND_RECOGNITION.md), [pod preparation](W2-F3_POD_PREPARATION_AND_WORK_GARMENTS.md) and [connected reconstruction](../handover/AWAKENING_RECONSTRUCTION_20261018.md).

Shared node: W2 supplies inspectable space; W3 bodily recognition and attire; W6 presentation. W4 owns the implementation and completed count.

W4 completed count: **3** (F1, F2, F4). W4-F3 remains REVIEW. Next unallocated: **W4-F5**. Suggested next step: author review of this passage, followed by separately authorised deployment and a fictional-character Discord playtest.
