# W4-F2 — One Loop That Holds

Home: W4 Play. Status: COMPLETE — isolated non-combat command/persistence loop verified.
Date: 17 October 2026.
Previous: [W4-F1](W4-F1_WHAT_CAN_WE_ACTUALLY_DO.md). Return: [Wing Index](../WING_INDEX.md).
Tested source revision: ae16e38133d55b4ad3288fa57457fb929dda6f66.
Linked wings: W2 Worlds, W3 Beings, W7 Engine. No new mechanic or canon introduced.

## Existing loop selected

**Search the pod → retain a found token → reach the Lounge → offer the token → remember the exchange.**

Existing implementation: WardrobeCog.search_pod / offer_item and _persist_item_action; token_exchange.discover_token / exchange_token; production storage.save_json.

No new scene, reward or world-state rule was invented. The small brass-token interaction already exists. The test adds repeatable evidence around its command and persistence boundary.

## What the isolated test actually does

The test calls the real Discord command callback functions directly, on the real WardrobeCog class. A capture context receives messages in memory; a tiny storage fixture uses the production atomic JSON writer with a temporary absolute path.

The fixture uses two synthetic characters. After meaningful saves it creates a fresh fixture storage instance from JSON, so later actions must consume reloaded state rather than relying only on the prior in-memory object.

Relocation uses the existing pod → hostel hallway → hostel stairwell → Lounge graph, checking west/down/down against the pinned room data and saving/reloading each step. **This is fixture relocation, not an execution of NavigationCog, entry events, Thread Node gating or a playable arrival flow.**

The bot entrypoint is never imported or started. Storage is not instantiated; only its JSON writer is used. No Discord login, real messages, player records or live world files are accessed by the test fixture.

## Verified results

| Check | Result |
| --- | --- |
| Search command | Token added once; found flag saved; success text captured. |
| Persistence boundary | Discovery survives JSON reload into fresh fixture storage. |
| Repeat discovery | Rejected after reload; disk and in-memory fixture remain unchanged. |
| Offer command | Token removed; exchange and counterkeeper receipt flags saved; acknowledgement captured. |
| Repeat exchange | Rejected after reload; no second effect. |
| Participant isolation | Second synthetic character unchanged. |
| Unrelated continuity | Keepsake, credits, earlier flag and unrelated extra data preserved. |
| Discovery save failure | Injected error before write: command rolls in-memory state back, durable fixture unchanged, no success claim, retry succeeds. |
| Exchange save failure | Token and unexchanged state preserved in memory/on disk; no success claim; retry succeeds. |
| Existing helper tests | Location/possession rejection and helper non-mutation checks still pass. |

**5 tests passed:** 2 existing helper tests plus 3 new command/persistence integration tests.

Disposable source checkout: /tmp/futuresky-w4f2-72d0imhn.
Captured result: w4f2-test-output.txt inside that disposable checkout. These temporary paths are execution evidence, not durable dependencies.

Durable reproducible test: [test_token_exchange_loop.py](../../tests/test_token_exchange_loop.py).
Existing helper tests: [test_token_exchange.py](../../tests/test_token_exchange.py).

From a disposable checkout with project dependencies installed:

```bash
PYTHONPATH=bot python -m unittest discover -s tests -p 'test_token_exchange*.py' -v
```

On Neptune Lounge the first run used /opt/futuresky/.venv/bin/python, with cwd and PYTHONPATH pointing into the disposable checkout. It did not use the live working directory for fixture writes.

## What this does not prove

- Discord parsing, global command gates, run-channel routing or network delivery.
- Full onboarding, actual movement commands, events, proximity or character discovery.
- A running NPC's independent memory; receipt/exchange facts are participant-side.
- Service restart recovery, concurrency, power-loss durability or partial writes after a successful replace.
- General item exchange, combat, or every command mapped by W4-F1.

Fresh fixture reload is narrower than restarting the bot. Injected failure happens before fixture write; it does not simulate every disk failure. The test's confirmation messages are captured output, not proof they reached a human.

## Changes and verification

Added tests/test_token_exchange_loop.py and this complete record; updated the wing index. Production gameplay code, world data and services are unchanged.

A pinned repository snapshot was extracted into a fresh temporary directory. The new test was written there and run alongside existing token tests; exit status 0 and five passing tests recorded. Tests exercise actual callbacks, helpers and the production writer against disposable state.

## Parked return

Reached: one real existing non-combat sequence verified across command/helper/persistence boundaries in isolation.
Open: full player-route and delivery verification, broader interaction loops and failure/concurrency coverage.
W4 completed count: 2. W4-F3 is unallocated. Play's first pass is parked.
W1 Mythos, W2 Worlds, W3 Beings and W8 Stewardship also remain at 2 each.
Next proposed wing: W5 Time. No Time feather activated here.
