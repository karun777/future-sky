# W7-F10 playcheck correction

Installed and independently verified on 11 November 2026. The installation commands below are historical operator instructions, not a request to repeat installation. Three files only: arrival_media.py, pod_inspection.py and the live HUD game.js. All other live Python files and HUD assets are hash pinned. Historical lifecycle deployment records stay unchanged.

459 Python tests and 25 Node DOM/scheduling tests pass. These are not visual browser tests. The exact three-file package installed and rolled back in temporary code with fictional data using the existing tested transaction engine. Read-only live baseline verification passed.

## Operator installation

From /home/efiishent/future-sky-worktrees/w7-f8 in the privileged SSH terminal:

```sh
sudo systemctl stop futuresky-bot.service &&
sudo env PYTHONPATH=.:bot /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w7f10_playcheck.activate install &&
sudo systemctl start futuresky-bot.service
```

The installer checks the historical installed lifecycle contract and restart flags, requires stopped service/no detached writers, archives exact code privately under /opt/futuresky/backups/w7f10-playcheck, installs atomically and verifies unchanged canonical data. The module leaves the service stopped. The shell starts it only after success. A failure requires review before restart. This brief maintenance interrupts all players' connections.

Afterward run the same module with `verify`, check Discord reconnect and portal health, then refresh/sign in and inspect hands/garment/pod. Existing Discord messages do not change. Do not reset efiishent to test the footer.

Rollback uses the same module with `rollback` while stopped, only before further data changes. It restores this package's prior code, never player data. Data drift refuses rollback.

## Lifecycle contract

After this installation the old reset adapter intentionally refuses further reset/restore operations because two pinned dependencies changed. Review and pin a new runtime contract before another lifecycle transaction. Do not weaken the guard, rewrite the historical deployment manifest or rerun the completed reset. Receipt, archive, channel mappings, grants and player records remain untouched. W7-F10 remains REVIEW.
