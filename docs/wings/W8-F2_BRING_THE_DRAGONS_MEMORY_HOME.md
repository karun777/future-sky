# W8-F2 — Bring the Dragon’s Memory Home

Home wing: W8 Stewardship.
Status: complete; documentation return route verified on Neptune Lounge on 17 October 2026.
Authorisation: Karun, “let's go w8f2”.
Previous: [W8-F1](W8-F1_GIVE_THE_DRAGON_A_MEMORY.md).
Return: [Wing Index](../WING_INDEX.md).

## Outcome

Synchronised the seven documentation paths differing between live runtime HEAD 937c007a2981d10b8e1230f293c85b6c72750425 and GitHub main d47d99c8f59f579b6132ac1a05826c3e28f0f672 into /opt/futuresky:

- docs/KNOWLEDGE_ATLAS.md
- docs/R3GPT_RESET_RITUAL_v2.0.md
- docs/WING_INDEX.md
- docs/current/EIGHT_WINGS_CHARTER.md
- docs/current/THE_ETERNAL_STRUGGLE.md
- docs/current/items/I_HAVE_NO_COMPASS.md
- docs/wings/W8-F1_GIVE_THE_DRAGON_A_MEMORY.md

The two existing entry points were backed up before replacement; new paths and every installed content hash were recorded in the manifest. The additional narrative documents are routing dependencies already on main, not canon promotions.

## Verified evidence

At 14:16 AWST, all seven installed files matched their pinned Git blobs byte for byte. All 30 relative Markdown links in the installed set resolved locally, including reset ritual → Atlas → wing index → return checkpoints and W8-F1.

The following files had identical SHA-256 hashes before and after the sync: data/characters/characters.json, data/items/items.json, data/rooms/rooms.json and data/rooms/rooms_base.json. The running world clock was not frozen, restored or written by this operation.

The bot remained active with MainPID 799778 and start time 2026-10-17 12:50:26 AWST. Runtime HEAD remained 937c007a2981d10b8e1230f293c85b6c72750425. No git index entries were staged.

Operational backup and evidence: /opt/futuresky/backups/w8-f2-20261017T141649/manifest.json.

This sealing change increments W8's completed count to 2 and adds this record. After merging, copy these two files to the live documentation overlay and compare them against their exact merged blobs before reporting completion. The completion report supplies the resulting commit identity.

## Deployment boundary

This is an intentional documentation overlay onto an older live runtime checkout. It does not fast-forward the runtime branch, deploy gameplay or reconcile data divergence. Documentation appears as modified/untracked relative to runtime HEAD; that is expected and must not be mistaken for unexplained drift.

Future pull/deploy operations must preserve this overlay or reconcile it against the matching main-branch docs before proceeding. Never use a blanket reset, restore or stash to tidy the live world.

## Rollback

If needed, first inspect the manifest and current file hashes. Restore backed-up pre-sync documentation only when it still matches this operation's ownership; remove newly created documentation only when it is unchanged and no later work depends on it. Do not roll back runtime data or move HEAD. The evidence directory records the initial seven-path sync; the final index and this record are identified by their sealing commit and verified separately.

## Return handoff

Current wing: W8. Completed count: 2. No next feather activated; W8-F3 remains unallocated. The next wing switch can start from the local reset ritual and find the same return checkpoints as GitHub.
