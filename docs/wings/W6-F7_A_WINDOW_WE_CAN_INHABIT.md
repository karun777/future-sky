# W6-F7 — A Window We Can Inhabit

Status: ACTIVE — live deployment and author interface/sync feedback verified 30 October 2026; unsealed. Existing idle-home notification defect recorded below.
Home: W6 Expression. Baseline: sealed W7-F5, 784f4e2.
Branch: expression/w6-f7-window-we-can-inhabit.
W6 five sealed; project 29. W6-F8 next unallocated. Chapter 1 / W4 stays paused.

## Outcome

Refine the existing https://future-sky.net/play/ window so room art, prose and actions are comfortable to use and changes made through Discord or idle-home appear without manual Refresh. Preserve the lo-fi atmosphere and one shared character/world authority.

## Scope and boundary

Improve layout, emphasis and command-reference rendering, useful action feedback, automatic passive state refresh, connection/stale indicators and a concise account of observed location changes. Keep existing inventory/character information accessible. Maintain the single-account pilot and existing authentication/action safeguards.

No new gameplay actions, map, portrait selection, encounter modes, broad access or Chapter 1 authoring. Do not silently repair unrelated Discord rehearsal content. All gameplay remains governed by existing bot-owned state/shared walking; viewing never simulates !look, grants discovery, touches idle-home or writes player data.

## Implementation decisions

Use the existing same-origin JSON view with modest visible-tab polling rather than adding a second event transport for this small pilot. Pause polling when hidden; fetch on return; use bounded retry and request timeouts. Keep stale action controls unavailable until the current state is retrieved. Changes observed between snapshots are not a complete event history; never invent who caused a move.

Repeated reads currently rotate the single-use walking token. Reuse a still-valid offer for unchanged room/revision/exits so polling and multiple tabs do not needlessly invalidate current controls. Consumed tokens must remain single-use, expired tokens must not be prolonged, and changed state must still invalidate old offers.

Render a limited set of prose formatting (paragraphs, bold, emphasis and inline code) using DOM nodes/text only, never raw HTML. Command references remain clearly Discord commands, not buttons that pretend unsupported actions work on the website.

## Acceptance

Keep the window open: walk through Discord, walk through the website, allow idle-home to return, and see the shared state update without manual refresh. Connection loss must be visible, movement disabled while stale, and reconnection must resume updates. Passive updates must not rearm idle time. Verify safe formatting, no duplicate actions and preservation of existing Discord movement tests.

## Shared checkpoints

- W4: ordinary walking remains supported; Chapter 1 paused until this refinement is reviewed and sealed.
- W5: passive polling is observation, not conscious activity; no clock or idle policy change.
- W7: retain session/CSRF/single-use action safeguards and shared movement authority; no new infrastructure dependency.
- W8: separate source, deployment and author verification. One W6 feather, counts unchanged while active.

## Return

Allocated from the sealed W7-F5 source in an isolated worktree. Live server unchanged at allocation. Inspect current source and deployment hashes before overlaying. The existing web server reads its static assets per request; a reversible static-only overlay can avoid a restart, but backend changes require the established privileged service restart. No permission workaround is authorised by that observation.


## Implementation checkpoint

The room now uses a tighter desktop layout with a bounded-height image, readable prose, nearby exits and feedback. A compact character sidebar keeps equipment and carrying lists in collapsible sections. The inactive command-line placeholder is replaced by honest guidance that command references belong in Discord. Basic narrow-screen styling remains, without claiming a fully tested phone experience.

The browser reads /play/api/me every four seconds while visible, with an immediate read on tab return/online and a focus refresh if overdue. Requests time out after ten seconds including response body consumption. Failed reads mark the view stale and disable exits; retries back off to a maximum of thirty seconds. A twelve-second freshness guard also disables movement if updates stall. Hidden/offline tabs stop scheduled polling. Current state refreshes after every attempted web move. Movement requests are never automatically retried, including after an uncertain response. An expired/unauthorised session clears the visible private view and stops polling.

Unchanged room prose, image and exit DOM nodes are preserved across polling to avoid visual churn and loss of focus. A short Recent changes list contains at most four observations in this tab. It is explicitly not a complete event history. Location changes are described neutrally; an idle completion message appears only when the server reports enabled idle-home, home status and the current location matching home. This is current-state evidence, not invented movement attribution.

Backend GETs reuse the same unconsumed walking offer while room/revision/exits remain unchanged and more than ten seconds of its original 120-second lifetime remain. Reads do not extend that deadline. Changed state or a consumed/expiring offer produces a new token. POST identity, CSRF, origin, single-use and shared movement validation remain intact. The curated idle projection excludes source message/channel references, raw history and pending private notice text; malformed idle metadata does not break observation. No character writes or idle touches occur on GET.

Prose supports paragraphs, bold, emphasis and inline code using DOM text nodes. Raw HTML and Markdown links are not executed or rendered as links. This is a small presentation grammar, not a complete Markdown implementation. Full narrative/discovery parity and stale Elemental Sound copy remain outside this feather.

## Verification and limits

313 Python tests pass under the live runtime interpreter against isolated source/fictional state: the previous 299 plus six new passive-view/token/idle tests and eight tests for the adapted installer/readiness checks. Eleven Node tests execute the actual shipped JavaScript with a minimal DOM and controlled clock. They verify polling without commands, unchanged DOM preservation, external/idle location updates, hidden-tab return, offline/reconnect, read failure/backoff, safe formatting, duplicate-click prevention, uncertain-action non-retry, expired-session clearing, stale-clock refusal and request timeout. JavaScript syntax check also passes.

These are behavioural tests, not rendered-browser layout tests. No Chromium executable is installed in the local test environment; no automated browser rendering or phone playcheck is claimed. Author visual review and the live Discord/web/idle-home acceptance loop remain pending after activation.

## Deployment handoff

The reversible installer tools/deploy/w6f7/activate.py overlays four existing files: web_portal.py plus index.html, game.css and game.js. Source manifest baselines match the current live W7-F5 bytes at 784f4e2. Read-only preflight passed. No new dependency, nginx/OAuth change, navigation edit, player-data replacement or Chapter 1 content change is included.

The installer retains the corrected case-insensitive login check and explicit UTC journal times from W7-F5. It creates a dated code backup, stops the bot, rechecks hashes, compares both player-data trees across the overlay, restarts and checks Discord/public portal/anonymous access. Failure restores prior code without rolling back player data. Existing remote sudo restriction requires the author terminal; deployment is an access handoff, not another scope approval.

```sh
ssh -t -p 777 efiishent@future-sky.net 'sudo python3 /home/efiishent/future-sky-worktrees/w6-f7/tools/deploy/w6f7/activate.py'
```

After restart sign in again. Leave the website open, move in Discord and watch the location update without Refresh; use a web exit and verify Discord, then check an idle-home return. Check prose/layout and visibility/reconnection feedback. W6-F7 remains unsealed; W6 five and total 29. Chapter 1 stays paused until refinement acceptance and the author's decision to resume it.

## Live feedback — 30 October 2026 (Perth)

Author reports: “sync is good, nothing jumps, controls are clear”; interface looks pretty good and offers a basis for further refinement. Read-only server inspection confirms all four deployed runtime files match the W6-F7 source; futuresky-bot.service is active. Installer output and backup path were not supplied, so those are not asserted here. This feedback does not separately establish every offline/reconnection or idle-completion acceptance case.

The author also supplied repeated Discord notices: “Your usual way home is unavailable. You stay where you are.” Inspection finds the pilot at dock_gate, home pod_room, idle return enabled at 60 seconds, status blocked. dock_gate is outside idle_home.PUBLIC_ROOMS, so automatic routing refuses this start room. This is a supported-route boundary, not evidence that ordinary walking is broken.

A separate existing notification defect explains repetition: tick delivers and clears pending_notice, then retries the unsupported route; note sees the same blocked status but a missing pending_notice, queues the same notice and appends another blocked history entry. The cycle repeats on heartbeats. Passive web GETs do not cause this state transition. Follow-up should suppress repeat notices for an unchanged blocked episode while retaining route rechecks, and explicitly decide any route expansion separately. No idle policy, player data or live code was modified during this inspection.

W6-F7 remains unsealed pending author closure; counts remain W6 five and project 29. Chapter 1 remains paused.

## Author-requested idle notice repair — 30 October 2026

Author requested the repeating warning be fixed because it keeps beeping. This is a bounded repair attached to this acceptance checkpoint, with W5 idle-policy and W7 runtime impact; no new feather or sealed count is claimed.

The idle cog now persists a route-block notification episode identified by activity generation, current room and home. Delivering a notice does not clear that episode marker. Repeated heartbeats still evaluate routes but do not requeue the same warning or grow blocked history. New activity, changed room/home or a later blocked episode can produce a fresh warning. Pending notices remain available for delivery retries. The existing supported-route policy is unchanged. The repair adds one small metadata field through normal character saves, with no data migration or manual player-data edit.

All 317 Python tests pass, including four added regressions for repeated ticks and persisted restart, unavailable delivery, new activity and continued route checks, and changed blocked room. The one-file installer tools/deploy/w6f7_idle_notice/activate.py reuses the established backup/hash-check/restart/health-check/rollback workflow. Read-only preflight passes against the live idle cog. Source prepared; privileged activation still pending. No claim of live silence yet. One pending old notice may still be delivered during transition.

```sh
ssh -t -p 777 efiishent@future-sky.net 'sudo python3 /home/efiishent/future-sky-worktrees/w6-f7/tools/deploy/w6f7_idle_notice/activate.py'
```

After activation, sign in to the web window again. If idle return was temporarily switched off using !idlehome off, re-enable only when desired (the tested pilot setting was !idlehome on 60). Confirm the blocked warning does not recur over multiple heartbeats without new activity. Chapter 1 stays paused; W6-F7 remains unsealed.

## Recovery playcheck and narrow feedback repair — 30 October 2026

Author supplied combat/death/recovery transcript at 09:12–09:23 Perth. Recovery decreased from 7.000 to 6.583 in-world days, confirming timer progression in that interval. No reset, acceleration or possessions edit requested or performed. Transcript includes changing enemy instance labels (customs_eye_1#1 to customs_eye_1_1#1) and stale Elemental Sound text. Combat identity/turn behaviour needs a separate investigation; no combat patch or diagnosis of extra turns is claimed here.

Read-only live inspection now confirms the idle-notice patch matches source. The transcript's single blocked-route notice alone does not demonstrate recurrence after the patch. Its timing relative to activation is not asserted.

The confirmed recovery defect is duplicate feedback: RecoveryCog.bot_check sends its deliberate denial and returns False, then the entrypoint handles discord.py CheckFailure as a generic unexpected error. Journal output confirms that CheckFailure for look. The patch marks a successfully delivered recovery denial on the request context; the error handler suppresses only CheckFailure with that marker. Unexpected exceptions and unhandled check failures retain their normal reporting. The marker resets on each recovery check. Failed notice delivery is not marked as handled.

319 Python tests pass, including two added tests executing the actual error handler without importing the network-starting entrypoint, checking one response, retained unexpected-error reporting, reset of the marker, safe-refresh failure and failed delivery. Two-file deployment staged under tools/deploy/w6f7_recovery_notice; existing backup/hash/rollback process reused. Source fix only until privileged activation. W6-F7 unsealed; Chapter 1 paused; counts unchanged.
