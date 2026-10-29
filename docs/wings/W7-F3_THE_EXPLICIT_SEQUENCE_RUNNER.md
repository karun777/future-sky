# W7-F3 — The Explicit Sequence Runner

Status: ACTIVE / implemented first pass, 29 October 2026. Author selected under-the-hood work to accelerate Chapter 1 playchecks. Implementation and offline verification complete; deployment recorded below.

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


## Implemented first pass

1–12 steps, maximum 1200 characters, one semicolon-separated line. Optional ! per step. Resolve aliases through the real registry, permit only canonical go with a direction, work bar, queen pay. Validate the whole script before executing. No nesting, unsupported commands, arbitrary code or embedded newlines. Character-facing results and costs remain those of the original commands.

Fresh contexts use the same routed context class, actual message author/channel/guild and copied content. Bot call-once checks plus normal Command.invoke preserve global/cog/command checks, converters, cooldowns and hooks. Normal per-step command/completion signals are emitted. Supported handlers explicitly set failed/success/choice; absence of a result stops the runner. No text matching or reimplementation of work/payment logic. Movement now restores its previous location on a save failure, and signals a committed move before later presentation; a resulting choice stops further actions without suggesting the move should be replayed.

The per-player active task blocks new player command invocations while a sequence runs, permits only that task’s internal contexts, and releases on completion/error/cancellation. It does not cancel ordinary commands that began before the sequence, lock out background world updates or persist/resume a sequence after a process restart. No cross-action transaction is claimed. The remaining list is feedback, not an automatic retry queue.

There is no new delay or time charge. Existing commands apply their current consequences; ordinary go remains outside the bounded rehearsal clock. Learned routines and unattended scripting remain later work.

## Verification

226 full-suite tests pass. Ten new tests use real discord.py command invocation and contexts on fictional temporary character JSON: six actions through payment, failed direction, failed work after movement, global and call-once checks, aliases/preflight rejection, failed movement save and recovery gate, active/new choices, simultaneous input lock, insufficient-funds stop and per-step cooldown. Existing tests also verify work/payment rollback. No live gameplay commands issued on the author’s behalf. Author playcheck remains pending.
