# W6-F3 deployment — 18 October 2026

Authorised by Karun: “ok let's go deploy”. Installed approximately 19:44 AWST.

Source `cbab82763e7453d63d0ba54792b7ab04c4809935`; prior runtime source `9707200bd5874a440b6ee2c80bccc8020b6d896b`. Selected six bot files only: Activity, Ambient, HUD, Navigation, Router and pod_opening. Live pre-install files matched the prior source; candidate matched the isolated tested archive. **112 tests passed again** before installation.

Private backup `/opt/futuresky/backups/w6f3-deploy-20261018-194402` contains data/assets/docs/bot/tests snapshot, staged files, hashes and manifest. Do not publish its contents. Bot paused during capture/install, then resumed and terminated as same service user to trigger existing systemd Restart=on-failure (ten seconds). This was a supervised forced restart, not a graceful stop. PID 811335 → 812193.

All **61 data files** unchanged across install; character-file hash also unchanged at post-restart inspection. No reset or discovery clearing. Existing Efiishent brochure inspection remains seen; the new HUD-presence notice can appear on a later hands inspection if not yet recorded and HUD is visible.

Post-start checks: service active/running; **44 cogs loaded**; no extension-load failure; Discord readiness true; Recovery heartbeat successful. All six installed source files byte-match the tested Git target. No live player commands were executed by the assistant.

Runtime checkout HEAD remains its older baseline by design; selected code overlays identify the deployed source. Live data, artwork and configuration overlays preserved. Deployment documentation updated separately.

Player check: `!hud` → `!hud_off` → `!look` (no automatic telemetry) → `!hud_on`. Try `!hud_state signal_degraded` then `!look`; return with `!hud_state normal`. In the pod, `!inspect hands` can introduce the display, then `!inspect hud`. Previously seen brochure should not replay its crash. Preserve all existing records rather than manufacture a fresh character for this check.

Rollback: snapshot has prior six code paths. Restore only those code files with process paused, restart and verify; do not roll live data back. Added per-character discovery flags can remain; no migration was performed.

W6-F3 stays REVIEW until player delivery evidence. Total sealed remains 18; no new feather count.

## Functional follow-up — 20:19 AWST

Authorised by Karun's “ok let's go” following the functional close-out plan. Tested source `3ccfd56248258f407fff8c839153f877e98c8690`; **119 isolated tests pass**, including 25 HUD/pod/activity cases. Actual argument parser tests cover space-separated commands and states, legacy compatibility and invalid suffixes.

Installed three code files only: HUD, pod_opening and Help. Live files matched previous deployed source `cbab82763e7453d63d0ba54792b7ab04c4809935`; all new files matched the tested candidate. Private snapshot `/opt/futuresky/backups/w6f3-functional-20261018-201856` contains pre-install state, manifests and staged files. Permissions restrict access; do not publish backup contents.

Same paused-snapshot/install and supervised on-failure forced-restart procedure as prior deployment. All **61 data files** hash-identical across installation. Character-file hash unchanged after restart. PID 812193 → 812667. All **44 cogs loaded**, Discord readiness true, no extension-load failures, Recovery heartbeat successful. Three installed source paths byte-match the tested commit.

Explicit `!hud` now presents only discoveries; no automatic telemetry panels in any mode. On/off and state changes use spaces. Old underscore commands remain hidden compatibility entries. Preferences, possessions and discoveries were not reset or migrated.

A short player check remains before sealing: `!look`, `!hud`, `!hud off`, `!hud on`. Ambient tests are automated, not a fresh live idle-pacing trial. No full calibration, sensory-return, subtle perception or upgrade engine is claimed. Next creative work: agree pod layout/visible props and improve cinematic presentation.

Rollback only these three code files from this snapshot if needed; preserve current gameplay data. Runtime HEAD remains historical; deployed source is the manifest's target. W6-F3 REVIEW; sealed count unchanged at 18.
