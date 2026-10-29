# W6-F6 — Website identity and live character pilot
29 October 2026. ACTIVE, UNSEALED. Chapter 1 / W4 remains paused.

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
