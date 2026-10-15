# Future Sky — Living World Inventory

**Version:** 0.1 — initial repository reconnaissance  
**Date:** 2026-10-15  
**Status:** Working inventory, not new canon  
**Scope:** Existing GitHub `main` content only; live deployment and content activation have not yet been verified.

## Source and authority boundaries

- **World canon:** `docs/RedBook_V7.2.md` and `docs/FutureSkyLore.pdf` (interpret via `docs/KNOWLEDGE_ATLAS.md`). Neither is rewritten here.
- **Current architecture:** `docs/current/` and `docs/KNOWLEDGE_ATLAS.md`.
- **Authored content:** JSON data and handbook passages demonstrate authored intent, not necessarily loaded runtime behaviour.
- **Implemented experience:** Must be verified against the running bot and relevant loaders, triggers and player flow. Repository presence alone is not proof.

## Existing content anchors

| Area | Evidence in repository | What we can say | Verification needed |
|---|---|---|---|
| Neptune Lounge | `data/rooms/rooms.json`, room key `neptune_lounge` | Domefront Arrival is authored as a Manzo-era social hub with exits, ambient events, return echoes, chips and a cyber-rat encounter | Confirm canonical loaded rooms file, player-facing presentation and ambient trigger behaviour |
| Surrounding Triton Central | `data/rooms/rooms.json`: `main_square`, `efiishents_office`, `sector_48` and other rooms | A connected network of authored rooms already exists | Validate links, reachability and which descriptions appear in game |
| Dark Rat Queen | `efiishents_office` room description and ambient text; `data/characters/characters.json` includes `drq_sneak_lesson` in completed Thread Node events for one character | There are concrete traces of the Queen in world text and a recorded character milestone | Locate full Queen character/story definitions and distinguish prior play from intended upcoming arrival; do not infer an arrival occurred |
| Character progression | `data/characters/characters.json` | Existing character state records include location, inventory, flags, status, mana and Thread Node history | Verify live character state independently; repository data may be stale |
| Private narrative texture | `data/narratives/internal_narratives.json` | Authored pod disorientation, Cube impressions, Lounge arrival, chips, idle whispers and future-self impressions | Verify loader, eligibility, persistence of once-per-character triggers and actual delivery |
| World opportunities | `data/world_opportunities/catalogue.json` | One enabled `manzo_low_comet_signal_test` opportunity requires Manzo era and `still` pressure band | Confirm whether test-only opportunity should remain enabled and what a player actually experiences |
| Visual assets | `assets/images/world/manzo/triton_central/neptune_lounge/rooms/dance_floor/` and `media/images/neptune-lounge-main.jpg` | Neptune Lounge visual material exists | Determine current delivery and asset mapping |
| Player-facing systems | `players-handbook/`, `bot/fsbot/cogs/narrator.py`, `bot/fsbot/cogs/world_moments.py` | Described world interactions and runtime presentation components exist | Verify implemented versus aspirational handbook features |

## First content-first feather candidate

**Neptune Lounge: an existing arrival or return experience.** Trace one already-authored moment from content definition through its trigger and actual player-facing output. Prefer an existing Lounge ambient/return echo or a private narrative; do not invent new lore until the path is proven.

**Dark Rat Queen:** retain as a nearby creative priority, but first inventory her authored Thread Nodes, room references and character state. The available references are not enough to certify her full implementation or a completed arrival.

## Open questions

1. Which room JSON path is authoritative for the running bot? Multiple room files exist.
2. Which authored narratives and Thread Nodes are currently wired into gameplay?
3. Which existing Queen-related material is canon, implemented, previously experienced or still planned?
4. What is the smallest already-authored experience we can exercise safely without changing live state?

## Next action

Inspect the **room loader and the narrative/Thread Node trigger path** for Neptune Lounge, then produce a single evidence-backed content-to-runtime walkthrough. Keep the live bot and persistent files untouched.
