# FS-W3-F4 — Vela encounter preview

Run `python3 tools/authoring/w3f4/serve.py` from this isolated worktree. Open http://127.0.0.1:8779 through the existing Mac SSH connection. This server binds only loopback and serves three explicit files. Do not serve the repository root.

Authored command rehearsal; browser-local saved memory, no requests/storage/account bindings/runtime mutations. F14 remains separate on 8778. Styles copied from the accepted F14 frame; no F14 assets changed. Source inspiration: private fs-resource-0005, translated selectively into fictional scene prose, with no private natal material included.

Review before sealing. Route furniture is provisional, not navigation simulation or mission canon.

## Choice/continuity rehearsal

Try `ask vela why`, `suggest longer route`, `ask vela why`, `defer`, `return`. The repeated question acknowledges your preference. Then inspect route/exit and suggest a wider turn to reconsider; leave/return retains the revised preference. Journal lists discussion separately from route observations. Repeated wider suggestions do not replay the first adjustment. Disagreement never accepts a job. Reload restores the saved fictional slot. All dialogue remains provisional.

## Persistent rehearsal slots

Rehearsal A and B are independent fictional copies of the same encounter, selected by URL fragment. They are not authenticated players. Saves use localStorage on this origin, versioned and keyed by slot, stable character fs-being-0007 and encounter vela-route-rehearsal-v1; partner fs-being-0001 is checked in the saved identity. Only whitelisted state fields restore. Personal resources are never read or stored. No acceptance state exists.

Closing/reopening restores observations, current preference and prior discussion. Preferences never select a route. Storage failures and incompatible records are shown and block further commands, preserving existing data. A storage event and preflight comparison guard against sequential stale-tab overwrites. This is not an atomic multi-user transaction system; simultaneous writes and cross-device sync require server authority in a later engine pass. Browser clearing/private-session expiry can remove saves.

Run Node regression checks: `node tools/authoring/w3f4/persistence.test.cjs tools/authoring/w3f4/scene.js`. These use a minimal DOM/storage harness, not a browser replacement. Cover restoration, no implicit acceptance, malformed and inconsistent records, failed writes and stale preflight.
