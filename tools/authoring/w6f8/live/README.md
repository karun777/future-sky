# Future Sky authenticated HUD

Current implementation: [W7-F8 — Bringing the HUD to Life](../../../../docs/wings/W7-F8_BRINGING_THE_HUD_TO_LIFE.md#seal--9-november-2026), sealed 9 November 2026. See its seal for live acceptance and retained follow-ups.
Entry: https://future-sky.net/play/ (OAuth returns to the same assets at /assets/experiments/w6-f8/live/index.html).

The directory name is retained for compatibility. This is a live authenticated client, not the isolated W6-F9 design rehearsal. The accepted layout gives the illustration its own left area and a right reading/reference column. Narrow screens stack these regions.

Type to act; click to view. Walking, inspections and clothing use existing authenticated APIs with one-use offers. Character, Inventory and Quest Log read authoritative projections. Quest Log contains discovered notices and remembered booking only. New projections require the matching W7-F8 backend; an older API is shown as unavailable rather than inventing empty records. Display settings reflect Discord preferences; no fictional instrument readings or upgrade stages are present.

Transport safeguards: same-origin credentials, no-store reads, CSRF-protected mutations, serialized commands, stale/offline gating, no automatic mutation replay, private-data cleanup on expiry. Passive browsing does not extend idle-home. Recent activity is per-tab.

Checks:
- PYTHONPATH=bot <runtime-python> -m unittest discover -s tests -p 'test_*.py'
- node --test tests/test_web_inspection_window.cjs tests/test_web_live_frame.cjs

Deploy using tools/deploy/w7f8/activate.py only after preflight. See the feather document for actual activation status, code-only rollback and live acceptance limits. Do not copy backend or static files independently into the production entry point.
