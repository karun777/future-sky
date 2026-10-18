# W4-F4 / W4-F5 deployment — 18 October 2026

Installed at approximately 18:11 Australia/Perth. Authorised by Karun's “let's go” following the combined-deployment plan.

Source: `9707200bd5874a440b6ee2c80bccc8020b6d896b`. All 94 isolated tests passed again immediately before installation. Exactly 11 bot source files differ from the live checkout's old HEAD; all 11 were installed and byte-verified against that source and the tested isolated archive.

Preserved the working checkout and local data/artwork overlays; no pull, reset, data migration or HEAD rewrite. Consequently `git rev-parse HEAD` still reports `937c007a2981d10b8e1230f293c85b6c72750425`; it is not the deployed source identifier. Use the manifest and source hashes.

## Backup and integrity

Private host backup: `/opt/futuresky/backups/w4f4-f5-deploy-20261018-181102`. Contains a pre-install snapshot of data, artwork, docs, bot and tests, plus data hashes, staged source and manifest. Permissions restrict the backup directory. Do not publish its contents.

The bot process was paused during capture and installation, then resumed. All 61 live data-file hashes remained identical across the code installation. Character-file hash also remained unchanged at the post-restart inspection. No Efiishent or other character reset was executed.

Administrator sudo was unavailable. The bot runs as the SSH user; after snapshot/install, same-user SIGKILL triggered the existing systemd `Restart=on-failure` / ten-second restart policy. This was a supervised forced restart, not a graceful shutdown. Old PID 799778; new PID 811335.

## Verified live

- Service active/running.
- All 44 extensions loaded, including Inspection, Navigation, Combat, Recovery and Rebirth.
- Discord Gateway connected and bot readiness logged at 18:11:19 AWST.
- Persisted clock loaded successfully; heartbeat ran.
- Recovery subscriber completed successfully as the seventh heartbeat subscriber.
- Existing optional voice dependencies remain unavailable; voice/audio client operation was not verified.
- No live player command or Discord UI playthrough was performed by the assistant.

## Return and rollback

Review the private manifest before any later deployment. To roll code back, pause the process, restore only the 11 source paths from the pre-install snapshot (remove the three newly introduced source modules when appropriate), then restart and verify. Preserve current data; do not overwrite post-deployment gameplay with the old snapshot. If any recovery has begun, rolling code back also removes its gate/completion path and needs a separate data-compatible recovery plan.

Efiishent's record was inspected read-only. He has no active moment or existing opening/recovery record; a physical route from his location to the pod exists. No forced reset is required merely to try W4-F4. Route: west → upstairs → up → east; narrative encounters may interrupt movement normally. At the pod use `!awaken`, then `!inspect hands`. Voluntary `!reincarnate` would instead initiate the full seven-world-day recovery after its confirmation.

This deploys existing feathers; no new feather or count increment. W4 count 4; total 18. Full player delivery/playtest remains open.
