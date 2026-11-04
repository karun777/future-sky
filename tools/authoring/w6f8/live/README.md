# W6-F8 live frame pilot

URL: https://future-sky.net/assets/experiments/w6-f8/live/index.html

This is LIVE: authenticated viewing and movement use the existing /play API and affect the same character as Discord. The parent directory remains the isolated rehearsal. Original /play/ stays available unchanged.

Scope: fixed viewport, room still/prose, existing exits, character name/credits, bag/equipment overlays, observed-change history, closer-reading snapshot and fullscreen. Actions panel explains the current boundary. Journal/map controls are disabled until authoritative projections exist. No fictional character facts, combat demo, imitation HUD or fixture discoveries enter this live page. Inspection, combat and equipment commands remain in Discord in this first pilot.

Architecture: plain HTML/CSS, native dialog and small frame.js presentation script. game.js is an exact pinned copy of the deployed W6-F7 transport (SHA256 d14957c9d8ca10af3e9aed09a84bd684564c415ebd5731bcc088e8f16697a691). Retains session/CSRF, one-use walking tokens, stale/offline protection, polling, no retry of commands, passive reads, and logout behavior. Future transport changes must update this copy and rerun checks; do not let it drift into a second implementation. Server routes, permissions, secrets, player data and services are unchanged. Same-origin requests send the existing secure, HttpOnly, host-only session cookie (path /) to /play/api routes.

Sign-in uses the existing callback, returning to /play/. Reopen the pilot URL after login. No OAuth redirect change made. If already signed in in that browser, the pilot reads the same session.

Deployment 4 November 2026: four static files copied to /opt/futuresky/assets/experiments/w6-f8/live, directory755/files644. All public bytes verified against source. No service restart; original /play/ returned200; anonymous /play/api/me returned401. Live pilot browser verified signed-out state and viewport1363x936 with no document overflow. Authenticated browser playthrough remains for Karun; not claimed complete. No mobile test claimed.

Checks: existing 11 test_web_window.cjs behavioral tests pass with FS_STATIC pointed at this directory; 2 tests/test_web_live_frame.cjs tests cover panel gating, detached reading snapshot and auth-expiry cleanup. JavaScript syntax passed. Run from repo with Node: FS_STATIC=tools/authoring/w6f8/live node --test tests/test_web_window.cjs; node --test tests/test_web_live_frame.cjs.

Player test: sign in; compare character/location/inventory; walk one permitted exit and check Discord !look; move in Discord and wait for the visible pilot to update; open/close inventory and Read closely; briefly switch tabs and return; confirm no layout jumps. Server restrictions including recovery remain authoritative. Report actual vs expected, location, action and connection status.

Rollback: use original /play/. Withdraw the dedicated public live pilot directory if needed; no player-data restoration. Chapter1 stays paused. W6-F8 remains active.

## W7-F6 source update — pending deployment

This branch extends the formerly pinned game.js with authenticated panels/display/booking inspection. The unchanged-copy statement above describes the W6-F8 baseline only. Current implementation and activation evidence are owned by docs/wings/W7-F6_ATTEND_TO_THE_WORLD.md; do not publish these static files separately from the matching backend activation. No server update has happened yet.
