# Next feather proposal — When the Way Is Closed

Status: PROPOSED ONLY — 13 November 2026. W6-F11 is not allocated.
Home candidate: W6 Expression; W7 retains the existing command/encounter authority.
Requested after the sealed W6-F10 review. Current Git is the authority.

## Morning connectivity checkpoint

Read the current Wing Index and W6-F10 seal/carry-forwards before inspection.
Checkout: /home/efiishent/future-sky-worktrees/w7-f8.
Expected/observed branch: engine/w7-f10-beginning-again.
Clean HEAD and independently queried origin matched
8f0d182cf4be130a310b4d603452f3d30839fd79 before this documentation checkpoint.

| Surface | Observed result |
| --- | --- |
| Remote devices | Neptune Lounge and Karun's Mac online; commands completed on both. Windows laptop listed offline. |
| Browser | Connected browser answered and listed the existing Future Sky live-window tab. No tab reload, authentication or gameplay check was performed. |
| Services, 08:58 AWST | futuresky-bot active, PID 1037793 unchanged; nginx active, PID 1024. |
| Installed release | W6-F10 read-only verify passed: two HUD assets, 139 preserved pins, unchanged 140-entry bot runtime. |
| Public delivery from Mac | /play/ and the versioned game.js returned HTTP 200 with the exact reviewed W6-F10 hashes. Anonymous /play/api/me returned HTTP 401. |

This establishes connectivity and current delivery, not a new player-state audit
or first-time OAuth result. No gameplay, restart, reset, permission change or
private archive/receipt access occurred.

## Cause inspected in current source

tools/authoring/w6f8/live/game.js formats unavailable-command feedback by appending
an offered list without checking whether the list is empty:

- Line 523: go with an unoffered direction yields an empty “Available exits:”.
- Line 529: inspect with an unoffered target ends with an empty “Available:”.
- Line 535: unavailable wardrobe suggests inspect wardrobe and appends
  “Available details:” even when no targets are offered.

The first two are the sealed W6-F10 carry-forward. The third is the same nearby
feedback problem and can suggest a step that is unavailable during a block.
The client still returns before action requests; this proposal changes feedback,
not the decision to permit an action. This is source inspection and prior fictional
visual evidence, not a fresh runtime reproduction.

## Proposed bounded outcome

**W6-F11 — When the Way Is Closed:** make the go, inspect and unavailable-wardrobe
responses useful when the current authoritative offers are empty.

- With an authoritative refusal, use that supplied reason in explicit command
  feedback. Keep W6-F10's single persistent room warning and distinct notices.
- With no reason and no offers, state that no exits/details/wardrobe action are
  currently offered; do not print an empty list or imply a route exists.
- With available alternatives, keep listing the actual current choices.
  Suggest inspect wardrobe only when that target is offered.
- Preserve command history, polling, passive reference panels and blocked-to-clear
  recovery. No new controls, layout, backend rules or encounter workflow.

Acceptance: fictional blocked, empty-without-refusal, and available-alternative
cases produce useful text; blocked commands issue zero action requests; ordinary
commands recover after refreshed offers. Existing first-outfit and carried-clothes
rules remain unchanged. Review the actual window using fictional responses.
Any later delivery requires its own reviewed static contract/cache version based
on installed W6-F10; do not rerun or rewrite the sealed W6-F10 transaction.

## First concrete step and boundaries

If accepted, allocate W6-F11 in its own chat, reproduce these three feedback cases
with the existing fictional harness/tests, then make the narrow wording correction.
No implementation, allocation, deployment or new test run is included here.

38 sealed feathers remain: W6 nine, W7 ten. W6-F11 and W7-F11 remain unallocated.
Preserve Efiishent's existing life, private archive/reset receipt and the Queen's
account, permissions and routing. Her access issue stays parked; Chapter 1 / W4
stays paused. First-time account/OAuth still needs a separate eligible participant.
