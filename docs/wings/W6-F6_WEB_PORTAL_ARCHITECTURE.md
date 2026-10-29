# W6-F6 — Website identity and live character pilot
29 October 2026. SEALED as W6-F6 — Two Windows, One Character. Chapter 1 / W4 remains paused.

## Current operational summary at seal
The read-only portal is LIVE on https://future-sky.net/play/, deployed at 18:40 AWST. Author screenshots at 18:45–18:46 verified real owner login and Discord movement reflected in the website. Existing Efiishent is preserved; there are no web actions. Runtime Python is /opt/futuresky/.venv-web-pilot-20261029 via systemd drop-in; the prior environment remains available for rollback. Source is on expression/w6-f6-two-windows, not claimed merged to main. Full-suite evidence is 267 passing tests plus three separately run deployment transaction tests.

The [home feather seal](W6-F6_TIME_TIMING_AND_TWO_WINDOWS.md#seal-checkpoint--29-october-2026) owns outcome, limits, shared checkpoints and the unallocated next candidate. Total 28 sealed; W6 five. This seal changes documents only, not runtime or player state.

## Historical preparation and deployment chronology
The sections below preserve the sequence of preparation, activation and playcheck. Earlier not-deployed, outstanding-credentials or unverified-owner-login statements describe their dated stages, not current status.

## Author direction
Karun accepted the game-window sketch as a starting point and prioritised connecting
his existing Efiishent through Discord login on **future-sky.net**, on neptunelounge.
He requested firmer technical oversight: explain the architecture and open-source
choices as implementation proceeds. The domain without the hyphen was a mistake.

## Inspected foundation
- Existing Nginx HTTPS host serves /var/www/html; public home returned HTTP 200.
- Existing Discord application: Future Sky, application ID 1348670557314482267.
- Authenticated read of the application API returned an empty redirect_uris list.
- Configured bot .env contained DISCORD_TOKEN, but no OAuth client secret/config keys.
  Only key-presence information was inspected; no secret was printed.
- Efiishent is an existing record keyed by numeric Discord user ID.
- Python runtime: discord.py 2.7.1 and aiohttp 3.14.1.
- Bot owns Storage and GameState in memory. JSON paths are relative to
  /opt/futuresky/bot, including data/characters/characters.json.
- Existing room artwork is selected by pod_media/lounge_media, often overriding
  placeholder images in room JSON.

## Architecture and choices
| Layer | Choice | Responsibility |
| --- | --- | --- |
| HTTPS and public routing | Existing Nginx | Keep existing website; route /play/ to loopback |
| Game window | Plain HTML/CSS/JavaScript | Render server responses using textContent |
| Web transport | Existing aiohttp, bot-owned optional cog | Read the same live state as Discord |
| Discord OAuth2 protocol | Authlib 1.9.1, HTTPX2 2.16.0 | Authorization-code exchange, state validation, identify scope |
| Browser sessions | Opaque random identifiers in server memory | 8-hour expiry, secure HttpOnly SameSite=Lax cookie |
| Ownership | Verified Discord user ID plus server pilot allowlist | Existing account only; no character creation or browser selector |
| Game engine | Existing Python services and Discord cogs | Remains sole authority for actions/persistence |

Authlib and HTTPX2 are new dependencies, installed only in a dedicated test venv.
No runtime dependencies, Nginx configuration, live source or bot process were changed
during this preparation. requirements-web.txt pins the direct libraries and tested
cryptography/joserfc versions. Resolve and check transitive dependencies in a staged
copy of the runtime environment before installation. Test venv initially inherited
system packages, producing a pyOpenSSL/cryptography conflict; inheritance was removed,
the isolated environment then passed pip check. No live dependency change occurred.

The small custom code is Future Sky-specific projection, HTTP routing, session storage
and UI. OAuth protocol handling is delegated to Authlib. This is not a generic account
platform. Sessions deliberately expire on bot restart; the character does not reset.

## Prepared code, not deployed
- bot/fsbot/web_character_view.py: owner-only, detached projection; no Storage
  construction, saves, ensure-player calls or raw extra/flags/quest records.
- bot/fsbot/web_portal.py: login, callback, /api/me and POST logout.
- bot/fsbot/cogs/web_portal.py: optional listener on 127.0.0.1:8787.
- bot/run_bot.py: loads the cog only when FS_WEB_ENABLED=1.
- bot/fsbot/web_static/: responsive sign-in and live-character page.
- tools/deploy/web_portal/nginx-location.conf: prepared /play/ proxy fragment.
- tests/test_web_character_view.py and tests/test_web_portal.py.

The initial view exposes name, ordinary credits, current location, approved same-origin
room art and ordinary bag/equipped items. Special delivery inventories, quest notes,
map discovery, narrative, avatar art and telemetry still need their existing
presentation rules adapted. They are not copied blindly from internal state.
This view is intentionally narrower than the visual sketch.

There are no web actions. No Discord command contexts are forged. No world time,
idle timers, discoveries or player state changes occur from GET requests.
The UI refreshes on request, not by background polling. It warns that viewing does
not interrupt idle-home. This introduces an observational web view without changing
existing Discord command interruption semantics.

## Identity and session boundary
1. Browser starts at /play/auth/discord.
2. Authlib builds Discord authorization URL using identify only.
3. Server remembers state with a random browser-bound HttpOnly login cookie (5 minutes).
4. Callback consumes the pending record once, checks state and browser binding,
   exchanges code server-side and obtains /users/@me.
5. Only an allowlisted identity with an existing character receives a random session.
6. /play/api/me ignores any browser-supplied character/user ID.
7. Every read rechecks pilot membership, character existence and bot readiness.
8. Logout requires matching same-origin Origin and CSRF token, then invalidates session.

No email, friends, messages or guild-list OAuth scope. Discord access/refresh tokens
and client secret never enter page responses or persistent session storage.
Login state and sessions are capped and expire. A bot restart requires fresh login.
API responses are no-store; CSP permits only same-origin scripts/styles/images.
Aiohttp access logging is disabled and the prepared Nginx location suppresses access
logs so callback authorization codes are not recorded in URL logs.

## Remaining external setup
In https://discord.com/developers/applications/1348670557314482267/oauth2:
- Register exactly https://future-sky.net/play/auth/callback as a redirect.
- Obtain the OAuth2 client secret (distinct from the existing bot token).
- Enter it into protected server configuration, never chat, source or browser code.

Required server environment keys:
- FS_WEB_ENABLED=1 (set only at activation)
- FS_WEB_DISCORD_CLIENT_ID=1348670557314482267
- FS_WEB_DISCORD_CLIENT_SECRET=<secret entered privately on server>
- FS_WEB_ALLOWED_DISCORD_IDS=<Efiishent's existing numeric record key>

Do not select an account by name supplied from the browser. Pilot allowlist ID is
resolved from the existing Efiishent record during deployment, not committed here.

## Deployment and rollback
After credentials/redirect are ready: compare source and live baselines, stage the
new dependencies against runtime packages, back up exact changed files/config,
selectively copy only portal code/static files plus the small entrypoint change.
Do not replace live data or checkout/reset the runtime tree.
Install the /play/ HTTPS location only, run nginx -t, enable portal environment,
restart bot once, verify Discord readiness/heartbeat and loopback listener,
then reload Nginx and test anonymous denial plus real owner sign-in.
Validate owner sees the correct character and a Discord change appears after refresh.

Rollback: disable FS_WEB_ENABLED, restore changed entrypoint/source if needed,
remove only the /play/ routing fragment, validate/reload Nginx and restart bot.
No player-data rollback is part of this deployment.

## Validation
267 tests passed: existing 240 plus 27 new projection/HTTP tests.
Tests include ownership, no state mutation, hidden-data exclusion, missing character,
cookie flags, login browser binding/state/replay/expiry/cancellation, session expiry,
non-pilot denial, safe OAuth failures, authenticated logout, disconnected bot,
static assets and Authlib authorization URL construction.
Tests use fictional records and mocked Discord identity exchange. Real token exchange
and browser sign-in are not verified until application credentials are configured.
JavaScript syntax passed locally. Disabled-cog smoke check passed. Browser visual
verification remains outstanding: Playwright was available but its Chromium binary
was absent, and both browser download attempts returned invalid archives. No browser
flow, mobile visual QA or real Discord sign-in is claimed.

## Next boundary: actions
Before enabling web movement, extract shared action/result services from Discord
presentation where needed. Preserve command checks, recovery/choice guards, activity
semantics and event publication. Define per-character arbitration across web, Discord,
sequence and idle-home; a lock only around web requests is insufficient.
Website controls must not directly edit JSON or assume sequence runner is a web API.

Sources:
- https://docs.discord.com/developers/topics/oauth2
- https://docs.aiohttp.org/en/stable/web_quickstart.html
- https://docs.authlib.org/en/stable/oauth2/client/http/index.html

## Callback confirmed and secret-entry helper
Discord application API subsequently confirmed the exact callback is registered.
Run tools/deploy/web_portal/configure.py in an interactive SSH terminal to enter
the OAuth secret using a hidden getpass prompt. It derives the unique existing
Efiishent account key and stages mode-0600 configuration at
~/.config/future-sky/web-portal.env, outside Git, with FS_WEB_ENABLED=0.
This staging file is not automatically loaded by the bot. Deployment must transfer
its keys into the protected runtime environment and enable the portal only then.
The helper neither changes live .env nor restarts any service.

## Activation prepared after private credential entry
User completed configure.py; private staging file present at mode 0600.
Cloned the existing runtime environment to /opt/futuresky/.venv-web-pilot-20261029
and installed pinned web dependencies there. pip check and all 267 tests passed
in this staged environment. Original /opt/futuresky/.venv remains unchanged.
Three additional installer transaction tests pass for success, Nginx validation
failure rollback and public health-check failure rollback using temporary fixtures.
Deployment manifest pins source files, existing live entrypoint and Nginx config.
activate.py --check passes; no live files/configuration have been changed.

The remote account needs interactive sudo for privileged activation. The author
will run activate.py with sudo over SSH. It installs only the specified files,
uses a systemd drop-in for the staged Python environment and protected env file,
validates Nginx, checks data hashes while the bot is stopped, starts the bot, checks
Discord readiness and anonymous API denial, then reloads Nginx and checks HTTPS.
On failure it restores saved source/config and the previous service environment.
The script never restores or overwrites player data. Sessions require fresh login.
This step is prepared, not yet executed; real browser OAuth verification remains.

## LIVE activation — 29 October 2026, 18:40 AWST
Author ran the prepared sudo activation successfully. Backup:
/opt/futuresky/backups/web-portal-20261029-184031.
Independent checks confirmed /play/ and both static assets HTTP 200, anonymous
/api/me HTTP 401, and login HTTP 302 to discord.com with identify only and the
registered callback. Nginx and bot active; new bot PID 917022. Discord logged in
at 18:40:39; IdleHome and Recovery heartbeat subscribers successful at 18:40:41.
The installer reported player data preserved. Real owner OAuth sign-in and
character rendering remain awaiting author verification. No seal; W4 paused.

## Author browser playcheck — 29 October 2026, 18:45–18:46 AWST
Author supplied two authenticated website screenshots and the corresponding
Discord play transcript. Website shows efiishent at Hostel Hallway (18:45:42),
then Hostel Stairwell (18:46:43) following Discord !go down. Both views have the
matching approved room artwork. Website shows four credits, Freeform Attire and
Rusty Knife equipped, with the carried-items list stable across the movement.
This verifies successful real owner sign-in, character rendering and Discord
movement reflected in the refreshed web view. It does not prove background live
updates, website actions, logout/re-login, other-user login or mobile visual QA.

Presentation follow-ups: room imagery dominates the desktop viewport and pushes
text below the fold; fit scene, narrative and action area together in the next pass.
Discord still repeats the previously recorded stale rehearsal sentence about
being back at the dock windows in both hallway and stairwell. Keep this on the
presentation-fix list; no new chapter development. Recommended next bounded work:
shared room narrative and visible exits, then checked ordinary web movement.
W6-F6 remains ACTIVE, UNSEALED; Chapter 1 remains paused. No runtime changes
made while recording this playcheck.
