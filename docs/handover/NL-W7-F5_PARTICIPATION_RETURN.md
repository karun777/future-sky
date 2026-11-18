# NL-W7-F5 · Future Sky receiving return

**REVIEW · 18 November 2026.** This isolated integration belongs to NL-W7-F5 — Two Desks, One Engine. FS-W4-F14 retains the scenario. No additional FS feather ID is allocated.

## Resume here

- Device: neptunelounge, `b3786b93-367a-4c51-a8aa-558b0228140c`.
- Worktree: `/home/efiishent/future-sky-worktrees/nl-w7-f5`.
- Branch: `integration/nl-w7-f5-two-desks-one-engine`.
- Source base: `216bd0255f0c91a5f3891ea0764f2df2bbc5e4e9`.
- Shared core: NL `46326261823da66407f166d818867e32f7e993d1`; [artifact provenance](../../vendor/participation/README.md).
- Verify current branch, HEAD, upstream and working state before continuing. Preserve concurrent work.

The sole production-code edit is optional `participation=` injection into `fsbot.web_portal.create_app`, with two routes. No injection means no new routes and no participation import. The rehearsal supplies synthetic OAuth, characters, bindings and a separate realm through the normal web-session flow. No installed application or production requirements changed.

## Run on neptunelounge

Use the existing Python environment read-only; install the wheel in a separate target:

```sh
FS_REHEARSAL=/home/efiishent/future-sky-worktrees/nl-w7-f5
FS_PYTHON=/opt/futuresky/.venv-web-pilot-20261029/bin/python
"$FS_PYTHON" -m pip install --no-index --no-deps --target /tmp/nl-w7-f5-installed-package "$FS_REHEARSAL/vendor/participation/neptune_participation-0.1.0-py3-none-any.whl"
cd /tmp
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/tmp/nl-w7-f5-installed-package:$FS_REHEARSAL:$FS_REHEARSAL/bot" "$FS_PYTHON" -m tools.authoring.nl_w7_f5.rehearsal --state /home/efiishent/neptune-lounge-rehearsals/w7-f5/crew-briefing --port 8776
```

If the exact artifact is already installed, reuse it. Stop an existing rehearsal listener before starting a replacement. Do not stop the Future Sky service. The CLI binds only 127.0.0.1, refuses state inside its repository, requires a private directory, and opens existing state without reseeding.

On Karun's Mac, the verified existing SSH alias supports:

```sh
ssh -N -T -o ExitOnForwardFailure=yes -L 127.0.0.1:8775:127.0.0.1:8775 -L 127.0.0.1:8776:127.0.0.1:8776 neptunelounge
```

Then open http://127.0.0.1:8776/rehearsal/desk. Only use the local test-reader selector; it contacts no Discord provider. Rehearsal cookies are HTTP-only synthetic-session cookies local to this harness. The production cookie defaults are unchanged.

## Walkthrough

Choose Sable and send the briefing invitation. Choose Efiishent and accept or decline. If accepted, choose Sable to offer the copy. Choose Oriel to pass receipt responsibility to Tavi, then choose Tavi to verify and acknowledge the offered bytes. Efiishent's former involvement and the passing traveller are refused afterward.

The review store already contains this completed five-event sequence. Restart and sign in again to see it. A fresh private `--state` directory gives a new synthetic run; do not delete or reset the reviewed store.

The actor names and ceremony are fixtures. Reading/accepting this briefing is not accepting a crew appointment. Sender, appointment, gift, Key meaning and item equivalences remain authoring questions for FS-W4-F14 and its related wings.

## Verification

```sh
cd /home/efiishent/future-sky-worktrees/nl-w7-f5
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/nl-w7-f5-installed-package:.:bot:tests /opt/futuresky/.venv-web-pilot-20261029/bin/python -m unittest test_participation_desk -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:bot:tests /opt/futuresky/.venv-web-pilot-20261029/bin/python -m unittest test_web_portal test_shared_walking test_web_character_view -q
```

Results on 18 November: **6 adapter tests pass**, plus **42 existing browser/walking/character-view tests pass with the package absent from PYTHONPATH**. The deliberate disk-failure test logs a traceback and still passes. The adapter checks anonymous access, forged selectors, Origin/CSRF, current grants, stale views, duplicate submissions, scoped-copy succession/receipt, revocation/logout, decline and transaction rollback.

Chrome walkthrough on Karun's Mac passed request, acceptance, offer, succession, checksum receipt, former-reader refusal, visitor refusal and process restart. The restarted store retained `received`, successor holder and five attributed events. Browser console inspection returned no errors. Desktop was visually checked; mobile and a full repository test suite were not exercised in this feather.

## Return boundary

The related NL return is [W7-F5_ENGINE_RETURN](https://github.com/karun777/neptune-lounge/blob/engine/w7-f5-two-desks-one-engine/docs/handover/W7-F5_ENGINE_RETURN.md) (moving review branch). Shared architecture is documented there.

This is a bounded optional adapter and loopback rehearsal. No production security audit, deployment, live player-state action, notification delivery, private NL import, MK record use or canon decision. Existing FS-W4-F13, FS-W6-F11 and the installed service remain untouched. Review with Karun before sealing or any receiving production scope.
