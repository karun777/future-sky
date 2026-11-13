# W6-F11 — When the Way Is Closed

Status: ACTIVE / SOURCE PREPARED — 13 November 2026. Unsealed; not deployed.
Home: W6 Expression. W7 supplies unchanged authoritative offers and gates.
Allocated on Karun's “ok let's go” after the bounded proposal and wing/trajectory context.
Baseline: 9acb8a9af6c44295cdf0cfb1ddd83ef4d2db18b6.
Branch: engine/w7-f10-beginning-again.
Checkout: /home/efiishent/future-sky-worktrees/w7-f8 (historical folder name).
38 sealed feathers; W6 nine, W7 ten. Next unallocated W6-F12 and W7-F11.
W6-F10, W7-F9 and W7-F10 remain sealed. Chapter 1 / W4 remains paused.

## Current checkpoint — 13 November 2026

The three unavailable-command paths now use their own supplied server refusal.
When no refusal or offers exist, they give a complete fallback sentence. Available
alternatives remain listed; the wardrobe hint suggests inspect wardrobe only when
that target is currently offered.

Only the live-client command-feedback branches and HTML cache tag change in
production source. The persistent room-warning renderer, command gates, requests,
first-outfit/carried-clothing rules, frame and CSS are unchanged. W6-F10's single
persistent warning remains distinct from explicit feedback/history for a command.

This advances W6's coherent player-facing presentation over W7's verified state.
It supports understandable player agency while W4 remains paused; it adds no new
encounter control, story content, interpretation system or live-player journey.

The source correction passes **34 client checks and 483 Python tests**.
The live host still matches sealed W6-F10: two assets plus 139 preserved pins,
unchanged 140-entry bot runtime, active bot PID 1037793. No W6-F11 deployment occurred.

## Cause and corrected responses

[Accepted proposal and morning connectivity](../handover/HUD_COMMAND_REFUSAL_PROPOSAL_20261113.md)
record the inspected cause: issueCommand appended offered lists even when empty,
and ignored existing walking/inspection/wardrobe notice values.

| Situation | Corrected explicit feedback |
| --- | --- |
| Refused go, inspect or wardrobe with a supplied notice | Uses that action's authoritative notice, including encounter/connection reasons. |
| No exits and no reason | No exits are available from here right now. |
| No inspection targets and no reason | No details are available to inspect here right now. |
| Unavailable wardrobe, no reason or targets | The wardrobe is not available here right now. |
| Alternatives offered | Retains the actual exit/detail list. |
| Wardrobe not yet available | Suggests inspect wardrobe only if wardrobe appears in current inspection targets; otherwise gives availability guidance and any actual details. |

The permission predicates and early returns are unchanged. Browsing a supplied
outfit remains passive; this correction does not broaden wardrobe access.

## Evidence and test boundary

[Machine-readable source checkpoint](W6-F11_SOURCE_CHECKS_20261113.json).

- Clean branch/HEAD and independently queried origin matched the baseline before
  editing. No local AGENTS.md files were found on the relevant ancestry/paths.
- Exact Git source/test copies were hash-compared before the local Node run,
  because Node is absent from the server shell.
- **All six new regression cases failed against the old client**, including each
  of the three refusal paths, empty offers, wardrobe alternatives and reblocking.
  Failures were the expected misleading/empty feedback, not test setup failures.
- **34 client checks passed** against the corrected source and cache-tagged HTML:
  six new checks plus the existing 28. They cover current per-action reasons,
  history and polling preservation, zero blocked action POSTs, passive Inventory,
  empty/absent offers, truthful wardrobe hints, ordinary recovery and reblocking.
  Existing first-selection, carried-clothes, observation and frame tests pass.
- **483 Python tests passed** in the server virtual environment. Expected failure
  logs and deployment messages come from temporary fictional fixtures, not live
  actions. No new backend implementation or test-count increase is claimed.
- The HTTP frame test now verifies the current script's actual hash suffix.
  The sealed W6-F10 package test binds its original reviewed asset hashes instead
  of assuming that every future client source must equal W6-F10. Its source/baseline,
  dependency, interruption and rollback checks remain. No historical manifest,
  installer or transaction was rewritten.
- git diff --check passed. These are behavior/contract checks, not a new browser
  visual review. No live command, account login, reset or deployment was used.

Source hashes:
- game.js: baf9b84ce3342de4bd671b3de0bd15828c2d91ce8bd545cc7c75f524f896e502
- index.html: 103d149be45bf0232b182bb3f4888e714fe08ba47ea191a777cca6ec87dc3d0b
- Cache tag: game.js?v=w6f11-baf9b84ce334

## Installed baseline and delivery boundary

Live code remains W6-F10:
- game.js: b41f6e1f1619615be2d2c3639ce0f85f1ebbcf2b69f286ea9fe1c942b2da84cb
- index.html: e8a1e6df857f878031facec83b4a6c05ba0d5d9fc0ae4975a22d599c53fe8486

The W6-F10 CLI verify passed before edits. After edits, all 141 installed code/asset
hashes were compared directly with the unchanged W6-F10 manifest, and the bot-only
runtime check again passed. W6-F10's source guard intentionally rejects a later
draft in this checkout; do not rerun its install or treat its refusal of new source
as evidence of a production fault. Its retained journal and sealed source remain
the W6-F10 rollback contract.

A later W6-F11 static delivery must bind the new source to this exact installed
baseline, retain protected pins and leave the bot-only runtime contract unchanged.
No W6-F11 release package or operator activation is prepared at this checkpoint.

## Next concrete step

Review the corrected window with clearly fictional blocked, empty and alternative
offers. Check feedback/history, unchanged persistent warning, Inventory, compact
layout and blocked-to-clear recovery. Only then prepare/rehearse bounded static
delivery. Keep this feather short; after sealing, reassess the next substantial
play-readiness milestone.

Do not reset Efiishent again. Preserve the private archive/reset receipt and the
Queen's account, permissions and routing; her access issue remains parked.
First-time account/OAuth still requires a separate eligible participant. No
manufactured live encounter, access expansion or Chapter 1 resumption is implied.
