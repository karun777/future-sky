# W7-F10 lifecycle deployment — operator runbook

Status: prepared and rehearsed, **not activated**. W7-F10 remains REVIEW.
This package installs only arrival.py, core.py, storage.py, config.py and
reset_binding.py. The manifest pins the current live Python dependencies,
including router v3.6.4. The stricter branch router is deliberately excluded.
No assets, Discord grants, category setting, credentials or shared-world files
are installed. Queen's saved mapping and existing routing behaviour are preserved.

## Preconditions and scope

Obtain the agreed maintenance approval before stopping the service or applying
the reset. The service interruption affects every connected player and may
require web reauthentication. The reset itself targets only the independently
verified Efiishent account key, its character, locker, vault and personal cube;
the prime cube, other players and existing channels/history remain intact.

Reverify Efiishent's channel ownership and exact stored name before maintenance.
Keep FS_PLAYERS_CATEGORY_ID unset; do not load the staged category env file.
Exclude external writers throughout maintenance. Do not change .env files.
Check the service unit and all environment sources for world-reset-on-boot.
The adapter checks the two deployed dotenv files plus systemd Environment;
it does not prove arbitrary external startup scripts safe.

Run from the reviewed checkout in a privileged operator terminal.
Remote privilege escalation is not part of this package.

## Read-only package check

From /home/efiishent/future-sky-worktrees/w7-f8:

    PYTHONPATH=.:bot /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w7f10.activate check

This checks source, current baseline and preserved dependencies only. It does
not assert the service is stopped, read privileged env files or authorise reset.

## Approved maintenance sequence

1. Record the reviewed Git commit and verified account/name privately.
2. Operator stops futuresky-bot.service. Do not restart until all checks finish.
3. Install the five-file overlay:

       PYTHONPATH=.:bot /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w7f10.activate install

   The installer requires inactive/dead/MainPID=0, checks for detached bot
   processes and writable live-data descriptors, and verifies all data hashes.
   It leaves the bot stopped. It retains a private code transaction at
   /opt/futuresky/backups/w7f10-lifecycle (0700, transaction files 0600).
4. Create the private reset plan using the verified numeric account key and exact
   name; substitute these deliberately rather than guessing from the display name:

       PYTHONPATH=.:bot /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.character_reset_adapter plan --account VERIFIED_ACCOUNT_ID --expect-name 'EXACT_STORED_NAME'

   Review the private plan: selected records, retained channel/seed receipt,
   preserved other entries and protected files. Do not publish its contents.
5. Apply that exact plan ID:

       PYTHONPATH=.:bot /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.character_reset_adapter apply --plan-id REVIEWED_PLAN_SHA256

   Record the private before-archive ID. The adapter verifies the installed
   five-file package and pinned old router, archives before changing data,
   and leaves the service stopped.
6. Verify transaction completion, unchanged other-player/protected data and safe
   restart configuration. Operator starts futuresky-bot.service. Check Discord
   reconnect and portal health, then sign in again.
7. Karun completes DM !begin. Verify fresh character/progression, existing channel
   and seeded marker, no duplicate channel/welcome, and Discord/HUD agreement.
   Explicitly review the other player's unchanged account/mapping; do not repair
   their parked grant issue.
8. Keep the receipt until the replacement binding is durably verified. Retire it
   deliberately during a later reviewed maintenance step; do not delete it now.
   Agree archive retention before any cleanup. Do not seal on fixture tests alone.

## Interrupted writes / rollback

Never restart with an unresolved reset journal.

- If code installation is interrupted before any reset data changes, run:

      PYTHONPATH=.:bot /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w7f10.activate rollback

  This restores exact previous bytes/metadata, including removal of the new
  reset_binding.py, and leaves the service stopped. Unexpected code, dependency
  or data changes cause refusal. The original transaction is retained; repeat
  installs deliberately refuse until an operator reviews the prior transaction.
- If reset application is interrupted, first run:

      PYTHONPATH=.:bot /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.character_reset_adapter recover

  Then review whether code rollback is needed. Recovery restores exact pre-reset
  snapshots; code rollback will only proceed if data matches its own original
  deployment snapshot. Do not bypass that guard.
- A completed reset is reversed using a new reviewed adapter plan with
  --restore ARCHIVE_ID, the verified account and current exact name. This archives
  any replacement character first. It is distinct from interrupted-write recovery.
  A semantic data restore may not match original file bytes: the code rollback
  guard may correctly refuse, requiring operator review. Prefer retaining the
  compatible lifecycle code while restoring selected data.
- No tool here automatically starts the bot. On any unexpected refusal, leave it
  stopped and inspect. No automatic deletion or shared-world restoration occurs.

## Evidence and limits

456 Python tests passed, including 17 new deployment/guard/compatibility tests.
Tests cover successful installation/rollback, interruption after each of five
writes, rollback interruption/retry, source/live/pin drift, changed data/code,
active-service refusal, duplicate install, archive failure, corrupt transaction,
stopped process fixtures, detached bot paths, writable descriptors, permission
denial and vanished processes.

The pinned router fixture is an exact hash-matched copy of live code, contains no
player data, and is never deployed. A fictional receipt and two players exercise
its saved-channel lookup and actual RunRoutedContext.send path with category unset.
No channel is created, no other player is messaged and no character record saved
by that routing path. This proves the scoped compatibility, not a repair of the
old router's known creation/access limitations.

The real read-only package check passed. Live service PID remained 1016603.
No privileged install, reset, recovery, stop/start or Discord mutation was run.
Positive stopped-process checks use fixtures; the real offline preflight remains
part of approved maintenance. Existing full reset-copy rehearsal is documented
in the feather. The new deployment rehearsal uses fictional files only.
