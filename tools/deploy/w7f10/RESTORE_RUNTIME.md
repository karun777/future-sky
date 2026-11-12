# W7-F10 current restore runtime

Reviewed 11 November 2026. This is a contract reconciliation, not another live reset or restore.

`runtime-manifest.json` describes the installed lifecycle code plus the two reviewed Python playcheck corrections. It derives from the immutable lifecycle and playcheck deployment manifests, whose hashes are recorded in its basis. All other Python pins, including the existing router, are preserved. Static HUD assets are outside this bot data-transaction contract.

The reset adapter now uses this current manifest by default. The historical playcheck installer explicitly retains its historical pre-install contract; do not rerun that completed installation. Neither historical deployment manifest was rewritten.

## Read-only verification

From the repository with PYTHONPATH=.:bot, call `runtime_code_check()` from `tools.character_reset_adapter`. This verifies installed/source code and preserved pins, without accessing private archives or changing data. It is not a replacement for the privileged restart and offline checks.

## Future restoration

Keep the private before-archive and receipt. Existing version-1 archives retain their selected-record schema and can be used to prepare a fresh restoration plan under the current reviewed runtime. Never reuse a pending plan made under an older contract. Review the selected account, archive scope, channel proof and maintenance impact before apply.

Actual plan/apply still requires the existing privileged operator workflow, safe restart configuration, stopped service and absence of detached writers. The adapter checks the runtime again and refuses stale plans or code drift. Restoration archives the replacement character before writing and preserves other players' intervening progress. Further runtime changes require another reviewed contract, not automatic acceptance of installed files.

## Evidence and limits

464 Python tests pass, including five new contract tests. Fictional-store rehearsal restores an archive made under an old contract, archives and restores the replacement life, preserves another player's later progress, and rejects changed manifests, source drift, installed-code drift and pinned-router drift before data writes. Restart-reset flags remain blocking.

Read-only verification of the installed bot passed with 140 hash entries. The bot remained active with the same PID. No actual private archive was restored or opened, no live lifecycle transaction or service restart occurred, and no receipt was retired. Full privileged maintenance preflight remains required for any future real restoration.


## W6-F10 static delivery preparation — 12 November 2026

[W6-F10's two-asset package](../w6f10/README.md) is prepared and rehearsed, not live.
Current bot runtime v3 remains unchanged at SHA-256
74a2c678be786b41ed03fc194c833e233161604e565de3e275d0833ded78327e.
Its 140-entry read-only verification passes before/after the isolated static
installation. Static hashes belong to the new package; this bot-only lifecycle
contract and all historical manifests retain their bytes. No private archive,
receipt, schema or restore plan is modified. Actual restoration still requires
the separate privileged offline procedure above.
