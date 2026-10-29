# Proposed W6-F6 — Time, Timing and Two Windows

Status: PROPOSAL for author review, 29 October 2026. Not allocated, implemented or deployed. W6-F5 remains in review; this proposal does not seal or replace it.

## Author direction

Retain a basic playable Discord game while exploring a richer aesthetically authored HTML experience. Consider a member-login website/game window, accounts and permissions, possibly PHP and open-source membership infrastructure. Improve both passage-of-time communication and the timing/density of presentation, particularly sequences and unattended routines. W4 chapter work remains paused.

## Proposed bounded deliverable

Use one existing home journey as a comparative interaction study: departure, a meaningful interruption and arrival. Produce a paced Discord presentation design and a small HTML/CSS/JavaScript game-pane prototype using explicitly fictional/replayed state. Compare persistent scene, compact journey progress, optional detail/history, images/ambient audio with user controls, and clear conscious-choice prompts. Keep authoritative elapsed time, deadlines and idle decisions separate from animation delays and reading/presentation cadence.

A prototype is not automatically a live second client. Before live writes, define authenticated account-to-character identity, server-side action permissions and one shared action/state authority. Existing Discord handlers are context-dependent; the current explicit runner is not a web API. A web client must not independently edit the runtime character JSON or duplicate the game's rules. Concurrent Discord/web input needs explicit handling.

## Three surfaces worth comparing

1. Existing Discord: commands retained; message components/buttons/selects/modals and editing/replacing a status panel can improve density. Supported Discord layouts remain platform-controlled.
2. Standalone web game pane: maximum HTML/CSS/JavaScript visual control; potentially placed inside our own member page, with deliberate session/frame integration.
3. Discord Activity: our web application runs inside Discord using its Embedded App SDK. This is distinct from assuming the full Discord client can be embedded in our website.

## Accounts and implementation proposal

Keep the Python simulation as the game authority. A PHP member portal or CMS can own membership/content, with a deliberate authenticated bridge to game actions. Discord OAuth2 could link web login to existing Discord identities. WordPress supplies roles/capabilities and authenticated REST facilities, but no CMS is selected and membership roles do not automatically become game permissions or factions.

Prefer a minimal branded portal plus shared game service over adopting an LMS solely to obtain login. An LMS remains a candidate if actual course/enrolment/learning-management features become requirements. Do not commit to new infrastructure on aesthetic frustration alone; make one scene tangible first.

## Current documentation checked — 29 October 2026

- Discord Activities overview: https://docs.discord.com/developers/activities/overview
- Activities architecture/lifecycle: https://github.com/discord/discord-api-docs/blob/main/developers/activities/how-activities-work.mdx
- Message/modal component reference: https://docs.discord.com/developers/components/reference
- Discord OAuth2: https://docs.discord.com/developers/topics/oauth2
- WordPress roles/capabilities: https://developer.wordpress.org/plugins/users/roles-and-capabilities/
- WordPress REST authentication: https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/

These support feasibility, not a claim that any integration is built. Third-party embeddable chat solutions, CMS plugins and LMS products have not been evaluated or selected. No hosting/account changes authorised or performed as part of this proposal.

## Decision at review

Choose a first presentation surface and scene. Keep initial effort to a concrete comparative prototype and an action/identity boundary sketch; avoid a platform migration or full rewrite. W5 retains time semantics; W7 retains simulation/action/script authority; W6 owns player-facing expression.
