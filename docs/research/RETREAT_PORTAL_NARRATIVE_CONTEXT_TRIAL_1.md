# Retreat Portal — Narrative Context Trial 1

**Branch:** `research/narrative-context-trial-1`  
**Base:** `main` at `ad9f851`  
**Purpose:** Explore context-rich Manzo-era authoring without changing the live runtime or canonical documentary core.

## Safety boundary

This branch:

- does not modify `main`;
- does not modify Neptune Lounge's live working tree;
- does not restart or reconfigure `futuresky-bot.service`;
- does not alter runtime code or persistent world state;
- does not promote research material to canon;
- does not implement relevance, resonance, interpretation or meaning.

The live system may continue operating from `main` independently of this work.

## Contents added

- `docs/research/NARRATIVE_CONTEXT_MODEL_v0.1.md`
- `docs/research/narrative-context-trials/MANZO_TREMBLING_GLASS_TRIAL_v0.1.md`

## Retreat

No rollback action is necessary because the work is isolated from `main`.

If the expedition is abandoned, leave the branch unmerged or delete only the branch:

```bash
git branch -D research/narrative-context-trial-1
git push origin --delete research/narrative-context-trial-1
```

Do not run those commands from the live deployment unless branch state has first been inspected.

## Return path

If the work proves useful:

1. review the prose independently of its metadata;
2. review whether the contextual envelope remained light;
3. revise research documents on this branch;
4. decide which documents, if any, deserve a pull request;
5. merge only after confirming that all material remains explicitly research or candidate content.

## Questions for the next review

1. Does the trembling-glass scene feel like Future Sky?
2. Is Sera the right initial perspective holder?
3. Did contextualization reveal possibilities without flattening the writing?
4. Which proposed identities are worth retaining?
5. Should the next trial deepen a person or broaden into a Scenario Field?
