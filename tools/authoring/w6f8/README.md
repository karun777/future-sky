# W6-F8 interface rehearsal

Published: https://future-sky.net/assets/experiments/w6-f8/index.html

Three switchable layouts over the same tab-local inspection rehearsal: adventure cabinet, Neptune terminal, illustrated storybook. Existing pod art and authored prepare_observation output from bot/fsbot/pod_opening.py are used. content.json captures first/repeat observations for seventeen targets; content.js is its browser wrapper. No dependencies, third-party scripts, cookies, player API calls or persistent storage. Refresh resets the rehearsal.

Supported: look, inspect <target>, journal, inventory, target buttons, journal revisits, recent observation history, reset and layout switching. Booking requires inspecting panels/display. Artwork with UNREAD is withheld after the booking discovery. This is a fixture comparison, not an alternate game authority or full gameplay implementation. Actual character identity, health, movement, combat, inventory manipulation, wardrobe and Discord chat are not connected.

Deployment: four static files copied to /opt/futuresky/assets/experiments/w6-f8 (directories 755, files 644). This adds a public rehearsal on the existing host, containing only authored scene material; no service restart, nginx changes or live game-file replacement. Remove that dedicated directory to withdraw the rehearsal.

Verified 4 November 2026: all four public files return matching source bytes. Cloud browser rendered the three treatments; panels/display/booking, typed chain inspection, belongings and state-preserving theme switching checked. Local browser connector failed authentication; cloud browser was used. No mobile or live-game integration test claimed.
