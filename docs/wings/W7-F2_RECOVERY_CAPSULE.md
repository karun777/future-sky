# W7-F2 — Recovery Capsule

Home: W7 Engine. Status: COMPLETE — bounded capture and disposable restore verified.
Date: 17 October 2026, verified 16:23:39 AWST.
Previous: [W7-F1](W7-F1_WHAT_IS_ACTUALLY_RUNNING.md). Return: [Wing Index](../WING_INDEX.md).
Live source HEAD: 937c007a2981d10b8e1230f293c85b6c72750425.
Captured main/document reference: 92541b5d3b5aa787a539f29b58fd28877ea4d236.
No restore over live data, service restart or runtime deployment performed.

## Capsule and result

Private on-server capsule: **/opt/futuresky/backups/capsules/w7-f2-u9ml04bx**

| Evidence | Result |
| --- | --- |
| Archive | recovery.tar.gz |
| Archive SHA-256 | c9880d69171bebabf1468aea0a6244801812b5e9b05fd5d23e3e7a5815beb029 |
| Archive size | 14,970,964 bytes |
| Files captured and restored | 165 |
| Restored bytes compared | 16,208,363 |
| JSON files parsed after restore | 21 |
| Restored room graph | 43 rooms, 100 exits, no absent targets |
| File hash comparisons | All matched captured manifest |
| Missing selected files | None |
| Bot service identity | Unchanged before/after capture and restore |

The capsule directory is mode 0700; archive, manifest and verification files are mode 0600. It contains private character/state information and stays on the authorised host. No private JSON or per-file manifest is committed to Git or uploaded elsewhere.

Manifest: manifest.json. Restore evidence: verification.json.
Disposable restore directory: /tmp/futuresky-w7f2-restore-1vhiyc2f. Temporary restore data is not the durable backup; the archive is retained.

## Scope actually captured

- Bot entrypoint and Python modules under bot/fsbot.
- Current test files.
- Atlas, reset ritual, wing index, Red Book, current/wings Markdown and the selected October handover.
- Nineteen explicitly selected JSON stores: characters, room store/baseline, items/enemies, Thread Nodes, internal narratives, configured era profiles/layers, clock/resolver, comet/astrology/pressure field, opportunity catalogue/state and cube/locker/vault stores.
- Existing artwork and metadata under assets/media, including locally untracked Compass and Tiny Book files.
- Website entry pages index.html and feed7.html.
- Installed Python distribution names/versions as reconstruction evidence; no environment contents or package-index credentials.

The 21 restored JSON files include the 19 selected stores plus selected asset metadata and the package-version inventory. These are counts of captured files, not a declaration that all project persistence is covered.

Symlink relationships bot/data → ../data and website/assets → project/assets are recorded as metadata; the rehearsal intentionally does not recreate operational links or install files into system paths.

The snapshot precedes this sealing record. W7-F2's final checkpoint/index update and recovery script are preserved by the sealing Git commit and subsequent server sync, not retroactively included in the earlier archive.

## Exclusions and limits

Excluded: credentials/environment files, SSH/TLS keys, the full event-history ledger, container/database volumes, complete virtualenv/OS packages, automatic schedules, unselected web files and off-host replication. nginx and systemd configuration were not included as installable recovery files.

Capture is **sequential while the world runs**, not an atomic cross-store snapshot. Each selected JSON file parsed at capture and restore, but this does not establish simultaneous consistency among all stores.

This archive is on the same server/filesystem. It proves a bounded file-recovery operation; it does not survive every host/disk-loss scenario or establish a complete disaster-recovery system.

No bot was started against the restore, no dependency rebuild was attempted, and no credentials were restored. A matching room graph does not validate every item reference, gameplay invariant or external service.

## Reproducible method

Script: [tools/recovery_capsule.py](../../tools/recovery_capsule.py).

Its authorised capture invocation was equivalent to:

```bash
/opt/futuresky/.venv/bin/python tools/recovery_capsule.py \
  --project /opt/futuresky \
  --output-parent /opt/futuresky/backups/capsules \
  --website /var/www/html
```

Run from a checkout containing that script. It creates a new private capsule; never reuses or replaces an older one.

The method:

1. Reads the bounded selected set and records source refs, capture times, lengths and SHA-256 hashes.
2. Parses selected JSON and copies bytes into a private staging tree.
3. Creates the compressed archive with its manifest.
4. Extracts only expected regular members into a new private temporary directory using safe extraction.
5. Compares every restored file's length/hash and parses restored JSON.
6. Checks restored room exit targets and records the verification result.
7. Removes duplicate staging data after success; retains archive, manifest and verification.

The script does not start services or write into the selected live source/data/web files. It does not provide an automatic live-restore command. Restoring live state requires a separately scoped plan based on then-current authority and backup coverage.

## Parked return — chassis first pass complete

Reached: a bounded recovery set is captured, restore-tested and provenance-recorded; selected untracked artwork is preserved in the private capsule.
Open: coherent whole-world snapshots, ledger/volume coverage, environment reconstruction, off-host retention, operational links/configuration and an actual service recovery rehearsal.
W7 completed count: 2. W7-F3 unallocated.
**All eight wings now have two completed feathers each: 16 sealed wing feathers.**
The two-feather chassis pass is complete. No next feather or deployment is automatically activated.
