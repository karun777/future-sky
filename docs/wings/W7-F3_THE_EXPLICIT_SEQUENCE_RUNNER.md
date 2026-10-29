# W7-F3 — The Explicit Sequence Runner

Status: ALLOCATED / next feather, 29 October 2026. Author selected under-the-hood work to accelerate Chapter 1 playchecks. No implementation or deployment yet.

## Proposed first-pass interface

`!sequence go north; go outside; work bar; go inside; go south; queen pay`

Execute deliberately supplied actions sequentially through normal command resolution, permissions, checks and gameplay logic. Await each completion. Preserve ordinary state persistence, outputs, costs and consequences. Do not bypass recovery, entanglement, role/command unlocks, room requirements or cooldowns.

Stop when an action fails or requires an unresolved player choice. Report the failed step and remaining unexecuted actions. Earlier successful actions remain committed; this is not a whole-sequence rollback. Do not run later actions after failed movement.

## Implementation question to resolve first

Current handlers often send a failure message and return normally. A successful Python return is not a successful game action. Establish an explicit result contract or narrowly supported adapters with trustworthy success/choice signals. Do not infer success from prose or simply loop over callback calls. Start with the small supported command set needed for the example, broaden only with verified handling.

## Scope boundaries

Explicit player instructions only. Learned routines, habit inference, automatic idle responses, arbitrary programming, nested sequences and scheduled execution are outside this first pass. Limit sequence length and serialize per-player execution; define how overlapping player input is handled. The runner does not create a new clock or claim ordinary navigation has acquired elapsed-time accounting.

## Verification target

Actual command routing/checks, ordered execution, stop on failed movement/payment/work and choices, no bypass through aliases or nested sequences, preserved costs/state, same-player concurrency and an end-to-end chapter playcheck. Selective deployment only after appropriate tests.

## Chapter return

W4-F12 sealed on live music receipt; next unallocated Play feather W4-F13 remains the sabotage continuation. W4-F9 and W4-F11 are parked functional drafts. Total sealed stays 25 while W7-F3 is allocated.
