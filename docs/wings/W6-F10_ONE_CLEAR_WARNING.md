# W6-F10 — One Clear Warning

Status: ACTIVE / STATIC DELIVERY PREPARED AND REHEARSED — 12 November 2026. Unsealed.
Home: W6 Expression. W7 supplies the unchanged encounter-gating authority.
Allocated on Karun's “let's go” following the
[bounded diagnosis and proposal](../handover/HUD_ENCOUNTER_WARNING_PROPOSAL_20261112.md).
Baseline: bcba1e0a27c1a38d7e7b7b0f376f333c1d48d15d.
Branch: engine/w7-f10-beginning-again.
Checkout: /home/efiishent/future-sky-worktrees/w7-f8 (historical folder name).
37 sealed feathers; W6 eight, W7 ten. Next unallocated W6-F11 and W7-F11.
W7-F9 and W7-F10 remain sealed. Chapter 1 / W4 remains paused.

## Current checkpoint — 12 November 2026

The isolated presentation correction and focused regressions are prepared.
An identical walking/inspection refusal now has one display in the existing
walk-notice. The matching inspection copy and otherwise empty INSPECT wrapper
are hidden. Distinct and inspection-only guidance remains visible; polling uses
the current offers, so blocks clear and return with authoritative state.

Only the live-client game.js renderer and its HTML cache tag change in production
source. The script tag now uses w6f10-b41f6e1f1619. No backend, CSS, frame, API,
command-gating, permission or player-state implementation changes are included.

The isolated browser review passes at native and compact laptop sizes. The bounded
two-asset static package is now prepared and rehearsed; 483 Python tests pass.
Its preflight preserves 139 code/asset pins and the unchanged 140-entry bot runtime
contract. This remains preparation, not deployment or live acceptance. The
installed HUD still has its original bytes; live activation and seal are pending.

## Source-preparation evidence — historical

The branch and clean baseline were rechecked before editing. This checkout remains
on engine/w7-f10-beginning-again; no older branch or attachment was used as authority.

| Check | Result and boundary |
| --- | --- |
| Client suite | 28 passing Node checks: tests/test_web_inspection_window.cjs and tests/test_web_live_frame.cjs. Exact source/test copies ran in the local Node runtime because node is absent from the server shell. These are minimal-DOM/scheduling checks, not browser rendering. |
| Duplicate refusal regression | One shared warning, hidden empty inspection wrapper, unchanged explicit command feedback across polls, zero blocked go/inspect/uniform POSTs, and passive Inventory access. |
| Other notices | Distinct and inspection-only messages remain visible, no-exits fallback survives, and ordinary offered inspection targets stay visible. |
| State transitions | Blocked to clear restores exits/inspection offers and permits one ordinary walk request; a later block restores the single refusal and prevents another request. |
| Backend adapter suite | 31 Python checks passed across test_web_walking, test_web_inspection and test_web_wardrobe in the server runtime. Expected save-failure logs came from existing failure-path fixtures. |
| Server gate regression | New test covers fictional active_thread_node and active_encounter_id separately. Previously issued walk/inspect/wardrobe offers receive HTTP 409; a fresh view withholds actions and reports the same refusal. Exact all-character fixture comparison and save count remain unchanged. |
| Defect detection control | The two duplicate/transition checks both fail against the unchanged baseline client, and pass against the corrected source. They detect the original defect. |
| Source checks | git diff --check passed; the HTML cache tag matches the corrected script hash. No full Python rerun was claimed at that source-preparation checkpoint; the later deployment checks below now record the full suite. |

Source hashes:
- game.js: b41f6e1f1619615be2d2c3639ce0f85f1ebbcf2b69f286ea9fe1c942b2da84cb
- index.html: e8a1e6df857f878031facec83b4a6c05ba0d5d9fc0ae4975a22d599c53fe8486

Read-only installed comparisons still returned the proposal's baseline:
- game.js: 4bb1d86f20371d1021596d610a8d6671384fb3c07a52a64aa13cf74e288407ce
- index.html: c5aa48b5c6feea26aab93a19fed5d9c83e9858cc9c992a7f7ce2993df0ee5356

Repeat the focused Python suite from the checkout:
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=bot:tests /opt/futuresky/.venv-web-pilot-20261029/bin/python -m unittest test_web_walking test_web_inspection test_web_wardrobe
```

Repeat the client checks where Node is available:
```sh
node --test tests/test_web_inspection_window.cjs tests/test_web_live_frame.cjs
```

## Isolated browser review passed — 12 November 2026, 20:39–20:43 AWST

Reviewed corrected source 5b1438dbb4216e5820748c64dfc04188184b127d in connected Chrome.
The [reproducible fixture](../../tools/authoring/w6f10/visual_review.py) ran on the
Mac at 127.0.0.1:8766. It serves only copied client files and fictional in-memory
responses, has no OAuth or live API forwarding, and never reads player stores.
The public existing p01 artwork was loaded read-only. Fixture HTML labels itself
FICTIONAL REVIEW and permits that image origin; game.js, frame.js and frame.css
are exact source bytes, and source index.html is copied before fixture-only edits.

| Visible check | Observed result |
| --- | --- |
| Native 1512 × 783 window | One encounter warning, no duplicate or empty INSPECT wrapper. Existing image-left/reading-right layout, typed commands and reference dock remain visible. Image loaded; document dimensions equal viewport dimensions, with no outer-page scrolling. |
| Blocked go west / inspect panels | Refused in the client. The fixture controls showed zero action POSTs. Reference Inventory opened normally while blocked. |
| Inventory close | Preserved the room and warning, returned focus to command-input. Artwork stayed unobstructed. |
| Clear encounter | Refresh removed the warning and restored west plus hands/panels inspection offers. |
| Restored commands | inspect hands opened the fictional observation; look restored the room. go west then go east completed the fictional round trip. The fixture recorded exactly one inspection POST and two walking POSTs. |
| Different refusals | Inspection-unavailable and sequence-running messages both remained visible, with the INSPECT wrapper retained for its distinct notice. |
| Reblocked state | A fresh blocked response restored one warning and no offered exits/inspection targets. |
| Compact 1366 × 600 | One warning, readable commands and dock within the viewport; document dimensions again matched the viewport. Empty inspection wrapper remained hidden. |
| Browser console and cleanup | No warning/error entries reported for the review tab. The temporary viewport override was reset and confirmed at 1512 × 783; review tabs closed and the loopback server stopped. |

The shorter-viewport override initially affected the separate controls tab; that
capture is the native-size distinct-notice screenshot. After closing controls,
the actual game window was measured at 1366 × 600 and captured separately.
No compact-size result is inferred from the initial override request.

One existing wording rough edge remains outside this correction: rejected typed
commands with no offers can end in an empty “Available exits:” or “Available:”
list. The single encounter notice remains visible in the room. Record this as a
separate wording follow-up; this review does not expand the implemented scope.

This is direct visual evidence with fictional responses. It does not establish
live deployment, new-account/OAuth onboarding, real encounter completion or a new
Efiishent journey. The backend-gating evidence remains the earlier real-adapter
Python fixtures; this local visual server is not a substitute for that authority.
The 28 Node / 31 Python results above are retained, not rerun or inflated here.

### Screenshots

| View | SHA-256 |
| --- | --- |
| [Single warning, native window](W6-F10_blocked_20261112.jpg) | 96962d809d4f2f2f3084999880bce137087ce667f540a1661ba3bfd18782aa00 |
| [Ordinary window after clearing](W6-F10_clear_20261112.jpg) | 78dcff8ed1b82b68c850fb2f4e4775fdf4745976fc88b5802260383d1d5c5e75 |
| [Inventory while blocked](W6-F10_inventory_20261112.jpg) | 498574f06c81ce11a0bdc552306aeaba152aa690bfdd60f8fddb177263933695 |
| [Distinct notices, native window](W6-F10_distinct_20261112.jpg) | f419bd9e2dbd8d10a5e4a9e200feaa2dff66db7a66f23ea649024d169b9d44f1 |
| [Single warning, 1366 × 600](W6-F10_compact_20261112.jpg) | 74c31bee81d0770243c9d1ad7f8b061d91633c3a8a4714c2c490e80b6e30d61a |

## Static delivery prepared and rehearsed — 12 November 2026

[Two-asset package and operator instructions](../../tools/deploy/w6f10/README.md)
are ready for review. The package changes only the existing game.js and index.html,
publishing the reviewed script before its cache-versioned HTML. It records exact
original bytes, modes and ownership in a private asset-only journal. Rollback
restores HTML first and script second; interrupted installation or rollback can
recover from the retained transaction. Changed sources, baselines, dependencies,
captured bytes or unknown live assets block writes.

The read-only preflight passed for both installed baselines and **139 preserved
code/asset pins**, including the existing router, frame.js and frame.css. No bot or
nginx restart is needed. The CLI has no service-control, player-store, OAuth or
reset/restore operation. A privileged operator runs the later live write.

**Runtime reconciliation:** current W7-F10 bot contract v3 explicitly excludes
static assets and remains byte-for-byte unchanged:
74a2c678be786b41ed03fc194c833e233161604e565de3e275d0833ded78327e.
Its **140-entry read-only check** passes before and after the isolated static
release. Historical manifests remain immutable; this new package owns the next
static contract. The private archive, receipt and protected player routing remain
outside its write paths.

### Deployment evidence

- **483 Python tests passed** for this prepared source, including 12 new static
  package/transaction tests. Existing deployment-test activation messages refer to
  temporary fixtures, not production. Two outdated cache/static assertions were
  reconciled: the HTTP test expects the new HTML tag, and the bot-contract test no
  longer equates a historical static pin with future source. New package tests bind
  the exact historical baseline to the reviewed static replacement.
- Tests cover exact installation/rollback order and metadata, lock and duplicate
  refusal, private journal failure, corrupted journal/foreign-asset refusal,
  source/baseline/pin drift, changes during byte capture, interrupted writes and
  untouched fictional archive/receipt/later player progress.
- The [exact-package rehearsal](../../tools/deploy/w6f10/rehearsal-20261112.json)
  copied only **141 code/asset files** into a temporary tree. It created fictional
  state sentinels; no real character records, archive or receipt were copied/read.
  Installation and rollback passed, as did reopening after interruption at either
  install write and retrying an interrupted rollback. All 139 preserved pins,
  fictional later progress and the runtime contract matched.
- Temporary rehearsal copies were removed. Production code/asset hashes matched
  before and after; bot PID **1037793** remained active. No live transaction was
  created, no service/configuration changed and no gameplay command was issued.
- bash -n passed for the ten-line install wrapper. The corrected client bytes are
  unchanged from the prior 28-check Node suite and browser review; those results
  are retained rather than counted as a new run.

The production write is still pending. This preparation does not seal the feather,
reset anyone, retire a receipt or establish first-time account/OAuth evidence.

## Next concrete step

On acceptance of the concrete live step, the operator runs the prepared
tools/deploy/w6f10/install.sh, then verifies public HTML/cache tag and script bytes.
Reload the existing authorised HUD for ordinary-window acceptance. No bot restart,
forced live encounter, reset or access expansion is needed.

The exact command and retained-transaction rollback are in the package README.
Do not rerun an old deployment package or overwrite an existing transaction.
W6-F10 remains active and unsealed until the bounded delivery/review is accepted.

## Retained boundaries and shared return

W6 owns presentation; W7 keeps the encounter authority and deployment contract.
One feather/count only. Preserve image-left/reading-right composition, typed
commands, reference panels and obvious-exit bearings.

Efiishent's last verified live state remains W7-F9's successful pod-room return,
Freeform Attire, belongings and discoveries intact. No live character re-audit,
gameplay command or reset was used here. Do not reset again. Preserve the private
archive and reset receipt. The Dark Rat Queen remains another person's protected
player character; her account, permissions and routing are untouched and her access
issue stays parked. Chapter 1 / W4 remains paused. First-time account/OAuth onboarding
still needs a separate eligible participant and remains unverified.
