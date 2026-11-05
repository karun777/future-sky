# W7-F7 — From Attention to Agency

Status: ACTIVE — typed commands and main-panel focus revision deployed; player acceptance remains open.
Allocated 5 November 2026 on Karun's instruction “let's go W7-F7”.
Home: W7 Engine. Branch engine/w7-f7-from-attention-to-agency.
Baseline: W7-F6 seal 4ac7462216682ed9c8f08f6fa402eabf46e2bd3e.
32 sealed feathers remain; W7 six. Next unallocated W7-F8, W6-F9. Chapter 1 / W4 stays paused; Discord supported.

## Bounded outcome

In the existing fixed-screen pilot: inspect storage panels, inspect wardrobe, open wardrobe, examine an outfit, choose a first outfit or wear carried clothing, then see shared equipment in the web window and Discord.

The pod's four existing catalogue outfits are not a replenishing shop. First selection is once only; subsequent changes require carried clothing. Browsing and examining option descriptions are passive and grant no items. Opening the wardrobe observation uses existing durable discovery/attention semantics. No new clothing, canon, map, combat, FEED7 implementation, character reset, account expansion or Chapter 1 advancement.

## Implementation

- pod_inspection.web_targets adds wardrobe after panels/display discovery.
- web_wardrobe.select_outfit is the durable first-selection operation used by both WardrobeCog.uniform and HTTP; existing select_uniform rules remain authoritative.
- CoreCog.equip_item extracts the existing synchronous equip/persist operation. Discord equip_cmd remains its presentation adapter; !wear still resolves owned clothing then invokes equip. HTTP resolves the same carried clothing and calls equip_item. Slots, stat checks, two-hand behavior, bag conservation and save-failure rollback remain in the established operation.
- GET /play/api/me adds a private wardrobe projection only after wardrobe discovery and while the player can act in the pod. It includes catalogue/carried option descriptions, current fit and permitted action offers; it does not record attention or alter knowledge.
- POST /play/api/wardrobe accepts only action and one-use token. Session ownership/allowlist, exact Origin/CSRF, expiry, offered action, full-character/navigation fingerprint and current action restrictions are checked. Recovery, combat, choices, sequences, in-flight walking and room changes block it. No await separates final validation and shared mutation. Explicit changes touch IdleHome; suspended persistence blocks them.
- The frontend exposes Inspect wardrobe and Open wardrobe within observations, then a fixed-frame wardrobe dialog with examine-first garment controls and an explicit Choose and wear / Wear action. It serializes commands, refreshes saved state after responses, never retries mutations automatically, and clears private wardrobe details on location change or sign-out. Offline/error status remains visible inside the modal.
- Existing /play frontend stays unchanged. Pilot URL remains https://future-sky.net/assets/experiments/w6-f8/live/index.html.

## Verification — 5 November 2026

345 Python tests pass: prior suite, seven HTTP/shared-wardrobe cases and three additional deployment checks. 19 frontend behavior cases pass: existing inspection/transport tests plus wardrobe double-click, safe description text, fit refresh, lost-response no-retry, withdrawn actions, offline gating and session/private-detail clearing. git diff whitespace checks pass.

The HTTP tests use fictional players and fake OAuth. Deployment tests use temporary files and stubbed services; their “activated” output does not mean production was activated. No production wardrobe choice was made by the assistant. Browser visual verification and authenticated live walkthrough remain pending. The W7-F6 fresh-character discovery check is carried forward, not silently marked passed.

## Deployment

Worktree: /home/efiishent/future-sky-worktrees/w7-f7.
Read-only preflight passed: python3 tools/deploy/w7f7/activate.py --check.
Manifest selects five backend files and three static pilot assets; exact existing live hashes required. No dependencies, config, catalogue or player-data overlay.

On neptunelounge:
```bash
sudo python3 /home/efiishent/future-sky-worktrees/w7-f7/tools/deploy/w7f7/activate.py
```

Activation briefly stops the bot, validates baseline again, backs up selected code, overlays source, verifies data hashes unchanged while stopped, starts the bot, and checks Discord reconnection plus anonymous wardrobe denial and public asset hashes. Failure restores code only, removing the new module if absent before. Never restore old player data.

## Acceptance and return

Sign in again after restart. In the pod, inspect panels → wardrobe → Open wardrobe. Examine a carried garment, use Wear, check current fit and inventory, then compare !fit / !inventory in Discord. Try another carried garment to reverse the change if desired. Do not reset an existing first selection just to test it. A fresh eligible character's Choose and wear path remains an explicit live acceptance case; isolated tests cover it meanwhile.

If acceptance reveals layout or guidance issues, refine this feather before sealing. No seal or next feather activation is implied by implementation.

## Shared-wing checkpoints

W2: existing pod and authored wardrobe detail, no new room. W3: attire remains distinct from identity/class/job. W4: established clothing consequences retained; Chapter 1 paused. W5: passive browsing does not postpone idle-home; explicit inspection/change records attention. W6: existing fixed frame and reduced typography preserved, functional wardrobe overlay added. W8: one home/count, deployment/rollback limits and untested live paths explicit. W1: no new lore.


## Revised interaction contract — 5 November 2026

Karun rejected clicking to issue commands. Adopted: type to act; click to view panels and already supplied detail. A clearly labelled persistent COMMANDS field accepts Enter, with optional ! prefix. No movement, discovery, first-selection or wear button remains in the current game frame. Outfit clicks only display existing option descriptions. Nonmodal panels keep the command field available; Escape/Return close panels. Recent output is retained in a bounded per-tab command history, cleared on sign-out.

Supported commands: help/commands, look, go <offered exit>, inspect <offered detail>, wardrobe, wardrobe inspect <outfit>, uniform utility|formal|technical|freeform, wear <carried clothing>, fit, inventory, character/sheet. Unsupported commands explicitly report the web limitation. This is a bounded adapter to existing authenticated APIs, not arbitrary Discord-command dispatch or a shell. Existing stale/token/persistence checks remain authoritative.

The initial 5c95bf2 wardrobe build was independently confirmed deployed: all eight live file hashes matched. The screenshot of the older interface was /play/ after sign-in, not a proven rollback. This revision serves the current frame at /play/ with absolute asset URLs and returns OAuth login to the same fixed pilot frame. Both entry URLs show the command interface after activation.

Current verification: 347 Python tests pass, including callback destination and /play frame asset-path checks. The previous click-action UI suite is replaced by 12 command-interface tests covering optional prefix/case, offered commands only, double Enter, lost-response no-retry, offline/hidden behavior, passive panel browsing, wardrobe wear/first selection, auth cleanup and room changes. No new browser visual pass is claimed; fixed-frame layout and keyboard/panel flow require live player acceptance.

Deployment manifest has been rebased against the verified deployed initial W7-F7 build and now includes five backend files and four pilot assets. Use the same activation command for this revision. It briefly restarts the bot; no player-data/config/catalogue overlay. The initial build's activation instructions and button-oriented acceptance description above are historical; validate this command revision using the syntax in this section. Chapter 1 remains paused; W7-F7 remains active, count32 unchanged.


## Main-panel focus — 5 November 2026, 14:27 AWST

Karun requested that the main panel follow attention, reserving overlays for reference panels. Inspection and wardrobe now occupy the first two rows of the existing game frame; the command console and dock remain fixed. Room title is retained as context. Polling does not replace the chosen focus. Inventory/help/history overlays preserve it underneath; look restores the room, and authoritative room changes or session expiry clear private focus. The separate Read closely popup is removed. Outfit choices are plain text; inspect <outfit name> examines available catalogue/carried descriptions, with explicit disambiguation on duplicate names. Existing wardrobe inspect syntax remains accepted. No new mutation API or simulation behavior.

The previous ca35f2c build was independently verified: all nine deployed hashes matched and futuresky-bot.service was active. This focus pass passed 14 command/transport tests and the full 347 Python tests. Fake deployment test output is not production evidence. No automated browser visual pass or authenticated wardrobe mutation is claimed.

Four static assets were deployed without restarting the bot. All four public asset hashes verified against source; service remained active. Backup: /home/efiishent/future-sky-static-backups/w7f7-focus-20261105-062645. The deployment manifest describes this revision against the prior typed-command baseline; do not re-run activation against already-updated static files. No backend, configuration, catalogue or player data changed in this pass.

Acceptance: refresh the live frame; type inspect panels, inspect wardrobe, wardrobe, inspect Utility Uniform, then look. Confirm main-panel continuity, persistent commands, reference-panel return and room changes from Discord. Equipment mutation plus matching !fit remains outstanding before sealing. The shared web/Discord activity feed is proposed separately; current history remains per-tab and incomplete. Chapter 1 stays paused; 32 sealed feathers, W7-F7 active.
