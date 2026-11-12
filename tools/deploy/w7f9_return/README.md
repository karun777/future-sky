# W7-F9: guided pod return correction

Installed and verified 12 November 2026 on engine/w7-f10-beginning-again.
Owner release and live departure/return/reload passed; see the current W7-F9 document.
Do not rerun the installer for acceptance. This package replaces
only bot/fsbot/pod_opening.py, bot/fsbot/cogs/threadnodes.py and
bot/fsbot/cogs/inspection.py. It preserves 138 other code/asset pins, including the
W7-F10 router and the separately reviewed HTML cache correction from ba884a9.
No reset, player-data overlay, configuration, permission or routing change.

## Before installation

Read docs/wings/W7-F9_WAKING_INTO_THE_WINDOW.md. The existing character is in the
pod, wearing Freeform Attire, blocked by arrival_awakening_v1. No story choice
has been made. Retain the private reset archive and channel receipt.

Read-only baseline check from the checkout:

```sh
PYTHONPATH=. /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w7f9_return.activate check
```

This verifies code/assets only. The operator preflight also reads protected
restart configuration and refuses FS_RESET_ROOMS_ON_BOOT=1 before stopping the
service. Remote command access blocks sudo; use the privileged server terminal:

```sh
sudo bash /home/efiishent/future-sky-worktrees/w7-f8/tools/deploy/w7f9_return/install.sh
```

The script preflights, stops the service, installs through the existing transactional
code-only installer, verifies the new contract, and starts the service. It refuses
unexpected code/data drift, keeps a private transaction at
/opt/futuresky/backups/w7f9-return, and stops on errors. Do not rerun a partially
completed installation or delete its transaction. Service start is not proof of
Discord readiness; inspect readiness before gameplay.

## Recovery and acceptance after readiness

1. Verify installed hashes, new PID, bot readiness, portal response and existing
   HUD/Discord account. Reuse the private fs-efiishent channel.
2. Capture the current owner's complete record and other-record/protected-state
   comparisons privately. Send the existing owner's !awaken once in that channel.
   Its narrowly gated release changes only active_thread_node to null and
   active_presented to false. It preserves discoveries, completed history,
   pending_answer, outfit, bag, first-choice record and routing. It does not
   complete the legacy node or choose a story option.
3. Verify persisted release, HUD exits, !fit/!inventory parity and normal bearings.
   Leave west, return east, compare Discord/HUD, reload and check persistence.
4. Save observed evidence in W7-F9. Do not call this successful live acceptance
   until those actions have actually passed. First-time account/OAuth onboarding
   is still unverified.

Recovery refuses an unrelated node, pending answer (including an empty object),
active encounter, invalid/missing guided opening, other location, cube, combat or
bodily recovery. Save failure restores the in-memory original and offers retry.

## Code-only rollback

Before any post-install play or !awaken, the existing transaction supports rollback
while the service is stopped:

```sh
cd /home/efiishent/future-sky-worktrees/w7-f8
sudo env PYTHONPATH=. /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w7f9_return.activate rollback
```

Rollback never restores data and refuses changed data. The current runtime manifest
expects corrected code; after rollback, reconcile that contract before any future
lifecycle operation. The frozen baseline-runtime.json remains available for
read-only verification. Never run a reset to clear this scene.

## Evidence

- 470 Python tests pass, including real HTTP departure, shared Navigation return
  and the actual EventBus/ThreadNodes subscriber. New fictional OAuth session
  preserves outfit/discoveries and offers usable exits.
- Disabling the new trigger guard reproduces legacy delivery in the new regression;
  this test detects the original failure.
- Explicit owner recovery: exact-record comparison, durable reload, idempotence,
  save-failure rollback/retry and refusal controls pass in temporary stores.
- Exact three-file package install and rollback rehearsed in temporary copies of
  current live code. Both 140-entry runtime contracts pass; fictional player
  records, receipt and archive unchanged. No production writes in the rehearsal.
- Historical W7-F10 deployment manifests and archive schema are unchanged.
  Current runtime-manifest.json advances to contract version 3 and intentionally
  refuses old live code until this deployment. No live archive restoration tested.
