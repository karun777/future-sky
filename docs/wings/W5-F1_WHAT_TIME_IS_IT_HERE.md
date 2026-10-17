# W5-F1 — What Time Is It Here?

Home: W5 Time. Status: COMPLETE — source trace and narrow live-state/log checkpoint.
Date: 17 October 2026, approximately 16:00 AWST.
Return: [Wing Index](../WING_INDEX.md).
Main documentary source revision: f0a213ac0d679e7a70217ce730130ae993ab6c97.
Live runtime checkout: 937c007a2981d10b8e1230f293c85b6c72750425.
No clocks, profiles, cycles, persistent state or services changed.

## Four meanings of time

| Kind | Existing source | Boundary |
| --- | --- | --- |
| Real elapsed time | Clock loop uses time.time() deltas; approximate 60-second sleep cadence. | Real seconds also drive some gameplay cooldowns, such as bar work. Not every timeout is world time. |
| Canonical world time | GameState owns accumulated world_time_seconds and its durable JSON. | One shared counter, not a separate advancing clock per character. No era calendar date/epoch mapping established here. |
| Real-sky observation | AstrologicalClock computes Sun/Moon positions at heartbeat event UTC. | Uses real UTC, not an accelerated sky in fictional year 102,019. Birth-date !astro is another interface, not this current-transit authority. |
| Lived/narrative time | Trajectory describes era-specific experience, including Manzo recurrence, fragmentation and rediscovery. | This is constitutional direction, not proof of personal clocks, time travel or retrocausal event rewriting. |

## The clock's actual path

GameState loads data/time/world_clock.json. Each loop:

1. Measures elapsed real seconds, truncated to an integer and clamped to at least one.
2. Reads the **previously persisted** Temporal Resolver state.
3. Advances world time by max(1, round(real_elapsed × effective_multiplier)).
4. Atomically saves the world clock.
5. Publishes heartbeat.advanced only after successful persistence.
6. Subscribers update comet truth, temporal resolution and other derived state.

The current tick never changes the rate already used to advance itself. A resolver update is consumed by a later heartbeat.

The loader resumes the stored counter; the inspected loop establishes its real-time baseline after startup. It does not implement a persisted “last stopped” UTC calculation to fast-forward downtime. Missing/invalid world-clock input falls back to zero in the inspected load path; missing/unsafe resolver input uses neutral 1×. Those are recovery behaviours, not permission to exercise them on the live world.

Source: [GameState](https://github.com/karun777/future-sky/blob/f0a213ac0d679e7a70217ce730130ae993ab6c97/bot/fsbot/state.py).
The _persist_every_ticks setting/comment survives in the source, but the inspected loop saves every tick. Actual loop behaviour governs this checkpoint.

## Era baseline and comet contribution

The configured source is **data/modifiers/era_time_profiles.json** (v0), loaded and cached by GameState.

| Profile key | Baseline | At baseline, 1 real minute advances |
| --- | --- | --- |
| jyotzon | 43,200× | 30 world days |
| omnicron | 600× | 10 world hours |
| manzo | 60× | 1 world hour |

These are implemented policy inputs, not fixed cosmological truths or proof that all profile metadata is consumed. The same files include needs/death-policy fields; their complete gameplay consumption was not audited.

TemporalResolver resolves **effective multiplier = era baseline × comet temporal modifier** and persists data/time/temporal_resolver.json. Its era comes from event scope, falling back to the default. The world currently runs on the shared Manzo resolution; individual room/character era lookup is not itself an independently advancing personal clock.

A second file, data/era_time_profiles.json, is v1 with differently nested metabolism fields. Its presence does not override the configured modifiers/v0 file. No migration or consolidation performed.

Source: [config](https://github.com/karun777/future-sky/blob/f0a213ac0d679e7a70217ce730130ae993ab6c97/bot/fsbot/config.py), [resolver](https://github.com/karun777/future-sky/blob/f0a213ac0d679e7a70217ce730130ae993ab6c97/bot/fsbot/cogs/temporal_resolver.py).

## Authored comet cycle

CometCycle derives phase deterministically from world_time_seconds modulo a **48-world-day** implementation cycle.

| Phase | Cycle fraction | Pressure band | Temporal factor |
| --- | --- | --- | --- |
| dormant | 0.00–0.15 | still | 1.00 |
| detected | 0.15–0.25 | low | 1.00 |
| approaching | 0.25–0.45 | rising | 1.10 |
| visible | 0.45–0.65 | high | 1.25 |
| dominant | 0.65–0.82 | severe | 1.60 |
| perihelion | 0.82–0.88 | peak | 2.00 |
| departure | 0.88–0.96 | falling | 1.35 |
| echo | 0.96–1.00 | residual | 1.05 |

Intervals include their lower bound and exclude the upper bound. The factor ranges from 1× to 2×, so a 60× Manzo baseline can resolve up to 120×.

Forty-eight world days would take 19.2 real hours at a constant 60×. Actual phase-dependent rates vary, so that is not a measured full-cycle duration. Neither this cycle nor its bands calculate the working narrative's roughly 100,000-year comet orbit. That physical/narrative relationship remains open.

The Comet Pressure Field projects pressure uniformly in the current global model; it does not independently advance time or assign narrative significance.
Source: [CometCycle](https://github.com/karun777/future-sky/blob/f0a213ac0d679e7a70217ce730130ae993ab6c97/bot/fsbot/cogs/comet_cycle.py).

## Real-sky and temporal boundaries

AstrologicalClock computes a tropical Sun/Moon snapshot with the declared MOSEPH ephemeris mode at each valid heartbeat UTC. It persists/publishes only when its sign/whole-degree fingerprint changes. Therefore an older persisted observed_at_utc does not, by itself, prove the calculator stopped.

WorldMoments emits a boundary fact for each crossed **six-world-hour** interval after establishing an in-memory baseline on its first observed heartbeat. At a sustained 60× this interval corresponds to six real minutes; event arrival and tick granularity still matter. It does not mean “a meaningful scene happens every six minutes,” nor does the first baseline reconstruct every missed boundary during downtime.

Source: [astrological clock](https://github.com/karun777/future-sky/blob/f0a213ac0d679e7a70217ce730130ae993ab6c97/bot/fsbot/cogs/astrological_clock.py), [world moments](https://github.com/karun777/future-sky/blob/f0a213ac0d679e7a70217ce730130ae993ab6c97/bot/fsbot/cogs/world_moments.py).
The known observation-cadence mismatch and parked resonance work remain as recorded in the [phase closure](../current/PHASE_CLOSURE_EPISTEMIC_FOUNDATIONS_2026-10-15.md).

## Live observation — a dated sample

At 2026-10-17 08:00:46 UTC (16:00:46 AWST), sequential file reads showed:

| Store | Observed value |
| --- | --- |
| world_clock.json | world_time_seconds 1,477,005,339 |
| temporal_resolver.json | manzo; era 60 × comet 1 = effective 60; resolved at the same world second |
| comet/current_state.json | cycle 356; position 0.145191696; dormant/still; temporal factor 1 |
| pressure field | uniform_global_v0; intensity 0; still |
| astrology/current_snapshot.json | last persisted observation 07:12:34 UTC; tropical Sun Libra 23.93796°, Moon Capricorn 9.006857°; declared MOSEPH |

These files were read sequentially, not as an atomic world snapshot. Sky values are records from the stored observation time, not a claim of exact current external positions.

The sampled journal showed consecutive world values 1,477,001,739 → 1,477,005,339: +3,600 world seconds for a reported 60 real seconds at 60×. Its completed heartbeat dispatch had six subscribers, six successful outcomes and zero errors. The sky subscriber reported unchanged whole-degree fingerprint.

The service was active with PID 799778 and start time 12:50:26 AWST. This is narrow evidence, not an exhaustive health audit.

## Player-facing discrepancy

CoreCog's !time / !gtime / !worldtime uses the character's era baseline for its multiplier display, while the shared advancing clock uses the persisted effective resolver rate. The displayed 60× matches this dormant sample but may diverge when comet influence changes. No correction made.

The HUD's coherence/parallelism and display modes are not authoritative clocks. Pausing a stance or darkening a HUD does not stop world time.

Source: [CoreCog telemetry](https://github.com/karun777/future-sky/blob/f0a213ac0d679e7a70217ce730130ae993ab6c97/bot/fsbot/cogs/core.py).

## Verification and return checkpoint

Read live GameState, config/profile route, CometCycle phase calculation, TemporalResolver arithmetic, AstrologicalClock fingerprint/persistence, WorldMoments boundaries and CoreCog display. Inspected relevant durable stores, service metadata and recent heartbeat log. No gameplay command or new runtime test invoked.

Reached: shared clock, rate contributions, UTC sky, six-hour opportunities, display mismatch and narrative boundaries mapped.
Open: personal temporal experiences, calendar mapping, offline policy, long-orbit narrative coupling and telemetry/profile reconciliation.
W5 completed count: 1. W1/W2/W3/W4/W8 remain parked at 2 each.
Candidate W5-F2, not activated: verify one isolated phase-boundary → resolver → next-clock-tick sequence, preserving the separation of real and world time. No live time alteration.
