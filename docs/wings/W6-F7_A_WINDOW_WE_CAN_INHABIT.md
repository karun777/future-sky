# W6-F7 — A Window We Can Inhabit

Status: ACTIVE — authorised 29 October 2026.
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
