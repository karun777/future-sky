# W5-F2 — The Next Tick

Home: W5 Time. Status: COMPLETE — isolated phase/resolver/clock-loop integration verified.
Date: 17 October 2026.
Previous: [W5-F1](W5-F1_WHAT_TIME_IS_IT_HERE.md). Return: [Wing Index](../WING_INDEX.md).
Tested source revision: 57fc0b57e0a678d6559e6c343c8cc5ee5d54de96. No production clock or temporal policy changed.

## Question and result

**Does a comet-phase transition change subsequent clock advancement without rewriting the tick that triggered it?**

Yes, in the isolated cases tested. The actual GameState heartbeat loop advances using a previously persisted multiplier. The actual CometCycle and TemporalResolver cogs then derive and persist the new rate through the real EventBus. The next iteration reads that durable rate.

## What ran

- GameState, including its real load/save methods and _heartbeat_loop.
- CometCycleCog and TemporalResolverCog with production phase definitions and era profile.
- EventBus, with the comet subscriber before the resolver as in the inspected loader.
- Production JSON persistence into temporary files.
- Capture subscribers that compare published clock facts with the durable clock/comet/resolver state.

Only elapsed wall-clock input and async sleep were controlled: each simulated iteration spans 60 real seconds without making the test wait. The test replaces the clock module's time/asyncio references, not the production rate calculation.

Each case uses a fresh temporary world and a synthetic seed heartbeat to establish initial comet/resolver state. A fresh GameState reload after the transition verifies persisted time and rate rather than just the resolver's cached state. Event history persistence is not attached; no live history file is used.

## Three passing cases

| Case | Transition tick | Following tick | Verified result |
| --- | --- | --- | --- |
| detected → approaching | Old 60×: +3,600 world seconds | New 66×: +3,960 world seconds | Transition cannot retroactively use the new rate. |
| echo → next-cycle dormant | Old 63×: +3,780 world seconds | New 60×: +3,600 world seconds | Slowdown applies on the next tick; cycle number wraps to 1. |
| Clock save fails once | First tick advances memory but publishes no heartbeat fact | Second tick still uses old 60×; its successful event then drives resolver to 66× | No undurable heartbeat publication; rate update requires an emitted fact. |

For both successful transitions, the capture verifies:

- heartbeat real_elapsed_seconds stays 60 while world increments differ;
- durable clock value equals the announced world time;
- comet and resolver files reference that world time;
- exactly one temporal.resolved change event is emitted across the two ticks;
- the change event cites the first heartbeat as its cause;
- the first heartbeat retains its old-rate payload;
- a fresh clock instance reloads the final world counter and new effective rate.

## Failure nuance — not silently repaired

On a failed clock save, the current implementation has already advanced its in-memory counter. The test confirms that no heartbeat is published for that failed write, but the next successful save can contain both in-memory increments.

That does not establish a general recovery, replay or missed-boundary policy. It is the behaviour observed under one injected pre-write failure. A restart between failure and later save, partial disk writes and subscriber failures need separate questions. This feather does not change those semantics.

## Reproduction and evidence

Durable test: [test_temporal_next_tick.py](../../tests/test_temporal_next_tick.py).

From a disposable checkout with project dependencies:

```bash
PYTHONPATH=bot python -m unittest discover -s tests -p 'test_temporal_next_tick.py' -v
```

First run: 3 tests passed, exit status 0, in 0.011 seconds.
Disposable source checkout: /tmp/futuresky-w5f2-lzgfwxkl.
Captured output: w5f2-test-output.txt there. Temporary paths are execution evidence, not durable dependencies.

The first run used /opt/futuresky/.venv/bin/python with cwd/PYTHONPATH pointing to the disposable checkout. Each test changes cwd to its own temporary world before constructing state or cogs. No live state files, service, bot connection or Discord output are involved.

## Coverage boundary

This is a narrow integration proof, not the entire world engine. It does not exercise real scheduling jitter, restart downtime, astronomical observations, six-hour opportunity boundaries, the full live subscriber set, concurrency or the narrative's long-period comet orbit.

The two phase transitions sample existing behaviour; they do not promote implementation cycle length into canon. No production source, rates, profiles or services modified.

## Parked return

Reached: phase change → durable resolver update → subsequent clock advancement verified for acceleration and slowdown; failed-save publication boundary documented.
Open: broader recovery policy and the W5-F1 temporal/narrative seams remain unresolved.
W5 completed count: 2. W5-F3 unallocated. Time's first pass is parked.
W1 Mythos, W2 Worlds, W3 Beings, W4 Play and W8 Stewardship also remain at 2 each.
Next proposed wing: W6 Expression. No Expression feather activated here.
