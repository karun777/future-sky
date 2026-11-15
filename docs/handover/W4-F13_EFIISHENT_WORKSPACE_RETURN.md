# W4-F13 — Efiishent’s workspace return

15 November 2026 · **ACTIVE · isolated proof ready for author review**

[Feather and interaction treatment](../wings/W4-F13_A_WORKSPACE_ALREADY_WAITING.md) · [Wing Index](../WING_INDEX.md) · [Rehearsal](../../tools/authoring/w4f13/rehearsal.py)

## What waits beside the berth

The space bar has a hollow the width of a thumb. A folded slip catches in the hinge when Efiishent tips out the keyboard. Inside is the word *underblue*. He can use the note at the console without entering a password in the game’s command field.

> You key in the word. A pencil drawing fills the glass, open halfway down a flight of stairs. There’s an old slip pinned across one corner, headed PROBE.
>
> Yours, you suppose.

The slip says “Bring the probe back before they clear the bench.” Nobody signed it. The sketch divides at the foot of the stairs. Efiishent can leave a small crescent beside the rubbed-through branch so the console opens there on his next visit. He can also fold the keys away and walk out. The crescent is the one stroke he remembers making. The actual owner, previous user and note author remain open.

## What happened in rehearsal

Both paths ran on `neptunelounge` using an already-awake fictional stand-in. The unmarked return also ran through the interactive text loop with scripted input.

| Action | Observed result |
| --- | --- |
| Try the fictional login after finding the console, before opening the slip | “You find the slip still folded. Try inspect note.” |
| Inspect the note, use it, read the probe slip and leave without a mark. Walk west, return east and use the note. | “The sketch and the probe slip are still where you found them.” The saved scene has only console discovery, note discovery and the first visit. |
| Inspect the sketch, mark the fork, leave, walk out and return | “The little crescent you left sits beside the rubbed-through fork.” The drawing itself opens at the fork. |
| Reopen from a fresh Python process using the same temporary fictional save | The reader signs in again, uses the remembered note and gets the marked drawing. |
| Sign in as a second enrolled portal tester with the same display name in the same pod | Ordinary berth description and ordinary inspection offers. The private keyboard hint, scraps and mark belong to the first reader’s projection. |

The test compared the whole fictional character roster before and after the full interaction. Only existing pod/berth discoveries and the reader’s five scene flags were added. Inventory, money, relationships, tasks, roles and the other character match their starting state.

## Reproduce on the server

From the dedicated worktree, run the interactive rehearsal. Omit `--interactive` for the short scripted walkthrough. `commands` lists the current choices. `quit` discards the temporary fictional save.

```sh
cd /home/efiishent/future-sky-worktrees/w4-f13
PYTHONPATH=.:bot:tests /opt/futuresky/.venv-web-pilot-20261029/bin/python tools/authoring/w4f13/rehearsal.py --interactive
```

Try `inspect pod`, `inspect berth`, `inspect console`, `inspect note`, `console use note`, then `inspect probe slip` or `inspect sketch`. Only the sketch offers `console mark sketch`. Use `console leave`, `go west`, `go east` and `console use note` to see what you left behind.

| Check | Result |
| --- | --- |
| `PYTHONPATH=.:bot:tests /opt/futuresky/.venv-web-pilot-20261029/bin/python -m unittest discover -s tools/authoring/w4f13 -v` | 14 passed. Covers both returns, staged discovery, failed writes before replacement and retries, repeat actions, access boundaries, movement/encounter gates, and existing pod attention. |
| Same interpreter and environment with `-m unittest discover -s tests` | All 483 existing Python checks passed on the server. |
| `node --test tests/test_web_inspection_window.cjs tests/test_web_live_frame.cjs` | 34 existing HUD client checks passed on hash-verified worktree copies with Node 24.22.1 in the local test runtime. These exercise a minimal DOM. |
| `python3 docs/seeds/validate_pod_console_workspace.py` | Seven-record sample accepted, ten invalid variants rejected. The rehearsal never loads this documentary fixture. |

## Proof boundary and review decision

The harness starts a temporary loopback portal with a fictional OAuth provider, two synthetic identities and an atomic JSON save. The normal session, offer, Origin/CSRF, character projection, walking and inspection handlers run. Process-local adapters add the personal berth cue and private responses for one fixture reader. They carry the three typed console actions through the inspection transport **only in the rehearsal**. The CLI has no command history. A second reader, missing session, signed-out session, extra workspace selector, stale offer and mismatched token were all exercised. An open physical screen lasts for that reader’s visit, including across that same reader’s tabs. Closing it, walking away or restarting closes the view.

A production web binding still needs a reviewed way to enrol Efiishent, bind the action verbs and keep private text out of ordinary HUD command history. A Discord binding needs a private delivery path. Browser appearance, real OAuth, installed commands and actual player experience have no new evidence from this rehearsal.

The author review is whether the probe slip, sketch and optional crescent feel like traces of a life Efiishent might call his own. The invitation, archived credit claim and offered manual remain in the documentary sample. W6-F11 keeps the active HUD work, Chapter 1 remains paused and the register stays at 38 seals. There was no installation, account operation, reset or live walkthrough.

## Git return

`play/w4-f13-a-workspace-already-waiting` began clean at `984d36f`, matching its upstream. `e42e9a8` records activation, treatment and source reconciliation. `5ce65de` contains the isolated proof and its tests. This return records their review state on the same dedicated branch.
