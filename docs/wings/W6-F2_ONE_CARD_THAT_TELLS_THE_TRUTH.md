# W6-F2 — One Card That Tells the Truth

Home: W6 Expression. Status: COMPLETE — existing Compass inspection card verified in isolation.
Date: 17 October 2026.
Previous: [W6-F1](W6-F1_HOW_THE_WORLD_REACHES_US.md). Return: [Wing Index](../WING_INDEX.md).
Tested source revision: 6fbb6e6f65574c793f08ba01a28d3ee8a137db89.
Linked wings: W1 Mythos, W3 Beings, W4 Play, W7 Engine.
No item definition, artwork, discovery rule, presentation code or mechanic changed.

## Existing card selected

**I Have No Compass**, item ID itm_i_have_no_compass.

The test uses the real item definition from the pinned repository catalogue, the real inspect_item helper and the actual InspectionCog.inspect callback. A synthetic character/room and capture context receive a real discord.Embed in memory. No bot connection, run-channel send or player account is involved.

## What the public card says

The captured embed shows:

- Title: I Have No Compass.
- The catalogue's public description of the weathered compass, sealed glass and loose needle.
- Type Artifact and rarity Unique.
- Public attributes, including the glass not being removable and the needle remaining inside.
- Known use label: Attempt to reseat the needle.
- The exact catalogue HTTPS image reference:
  https://future-sky.net/assets/images/world/manzo/triton_central/neptune_lounge/objects/i_have_no_compass/i_have_no_compass_discord_v001.webp

It does not print the catalogue's internal notes, repair-DC notes, temporal compulsion or undiscovered seven-times/left-direction attribute.

A displayed use label is authored information, not proof that repair, compulsion or navigation mechanics execute. This test does not activate any of them.

## Verified presentation boundaries

| Fixture state / check | Captured result |
| --- | --- |
| No discoveries | Only public attributes and public use label. No compulsion, mastery or restored-navigation attributes. |
| restored_navigation supplied | Meaningful-direction and seven-times/left-direction attributes appear; compulsion stays hidden. |
| Both existing discoveries supplied | Authored navigation and temporal attributes appear; inspection adds no gameplay state or further discovery. |
| Unknown discovery key supplied | No extra attributes granted. |
| Item carried | Card available. |
| Item equipped | Card available. |
| Item on room ground | Card available. |
| Item absent | Rejection text; no embed. |
| Repeated inspection | Identical serialized card for the same fixture state. |
| State preservation | Character, room and item catalogue snapshots unchanged around every callback; persistence hooks are configured to fail the test if called. |
| Image emission | Exact catalogue URL appears in the serialized embed; no generated/replaced asset. |

Discovery knowledge was explicitly seeded in synthetic test records. This proves the rendering boundary, not a gameplay path for earning either discovery.

## Tests and evidence

**9 tests passed:** 4 existing helper tests plus 5 new inspection-card tests. The visibility case exercises carried/equipped/ground/absent states as subcases.

Durable test: [test_item_inspection_card.py](../../tests/test_item_inspection_card.py).
Existing helper tests: [test_item_inspection.py](../../tests/test_item_inspection.py).

From a disposable checkout with dependencies:

```bash
PYTHONPATH=bot python -m unittest discover -s tests -p 'test_item_inspection*.py' -v
```

First run: exit status 0; 9 tests in 0.008 seconds.
Disposable checkout: /tmp/futuresky-w6f2-uf5op5n8.
Captured run output: w6f2-test-output.txt there. These temporary paths are evidence, not durable dependencies.
The run used /opt/futuresky/.venv/bin/python with cwd/PYTHONPATH in that disposable checkout.

## Coverage limit

The test serializes a real embed; it is not a visual screenshot or a Discord client preview. It does not establish mobile readability, network delivery, caching, audience permissions or complete end-to-end player experience.

W6-F1 separately verified that the referenced hosted Compass image returned matching bytes at its inspection time. This feather does not repeat that network check or claim perpetual availability.

It does not verify the Compass's actual room placement, its discovery-acquisition path, numerical repair rules or temporal effects. Public/hidden catalogue boundaries remain authored decisions; this test checks the current implementation against them.

## Changes and parked return

Added the repeatable test and this record; updated the wing index. No production gameplay code, world state, media or service restart.

Reached: one existing item card's public text, selectively discovered attributes, access conditions, image reference and non-mutation verified.
Open: actual Discord presentation and the W6-F1 routing/audio/asset-preservation seams.
W6 completed count: 2. W6-F3 remains unallocated. Expression's first pass is parked.
W1 Mythos, W2 Worlds, W3 Beings, W4 Play, W5 Time and W8 Stewardship also remain at 2 each.
Next proposed wing: W7 Engine. No Engine feather activated here.
