# W6-F8 fixed-screen interface rehearsal

Published: https://future-sky.net/assets/experiments/w6-f8/index.html

V2: full-viewport game frame, internally scrolling prose/panels, prominent present context and responses. Stable scene and control strip; native dialog overlays for movement, actions, inventory, character, journal, map, implant HUD, inner voice and mode demonstrations. Booking discovery takes over most of the screen. Three local fixture rooms support rehearsal movement. Combat is a labelled manual demonstration, not live rules; inner voice is a provisional design sample.

Existing pod artwork and authored prepare_observation output from bot/fsbot/pod_opening.py are used. content.json captures first/repeat observations for seventeen targets; content.js wraps it for the browser. No dependencies, third-party scripts, cookies, API calls or persistent storage. Refresh/Restart resets the rehearsal. Previous three layouts are preserved under study-v1 after Karun rejected their webpage feel.

Deployment: index.html, window.css, window.js, content.js copied to /opt/futuresky/assets/experiments/w6-f8 (directories 755, files 644). No runtime service restart or live game replacement. The rehearsal has no access to a player's state. Chapter 1 stays paused and Discord remains supported.

Verified 4 November 2026: source/public bytes match; JavaScript syntax; browser at 1363x936 has identical viewport/document dimensions. Visually checked scene/prose/dock, panels/display/booking takeover, pod-to-hallway movement, map, Escape return, implant off retaining controls, combat guard and withdrawal. Withdrawal preserves opponent health. No mobile or live integration test claimed. Future integration must reuse authoritative action/discovery services and shared state; these local fixtures must not become a second authority.
