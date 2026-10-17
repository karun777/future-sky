# I Have No Compass

**Status:** Authored item; mechanics awaiting implementation  
**Item ID:** `itm_i_have_no_compass`  
**Origin:** Omincron era  
**Recovered:** Efiishent's Office, Manzo era  
**Runtime item definition:** `data/items/items.json`  
**World placement:** `data/rooms/rooms.json` → `efiishents_office`

## Canonical premise

An Omincron-era pocket compass belonging to Efiishent, recovered in his office during the Manzo era. Its needle has slipped off its pivot. The bearer must reseat the needle before using it; this requires a Dexterity check. Once usable, it points seven times a day in the **left direction**.

The phrase “left direction” is deliberately preserved without interpretation.

## Player-facing initial inspection

> A small, weathered pocket compass. Its needle has slipped from the central pivot and lies awkwardly beneath the scratched glass. It looks as though a steady hand might set it right.

## Secret: The Compulsion

The bearer can give the dislodged compass to someone as a distraction. The recipient becomes compelled to reseat the needle, a deceptively tricky task, and is bound within a temporal stasis loop. They cannot turn their attention to other actions while trapped. An advanced bearer can decide how long the recipient remains caught in the compulsion.

This is facilitator/world-engine knowledge, not information exposed in the initial inspection.

## Open implementation decisions

- Dexterity check DC and consequences of failure.
- Whether and how a recipient can resist or escape.
- How bearer mastery is determined and how duration is specified.
- Whether the loop affects external elapsed time, subjective time, or both.
- What determines the seven daily activations and what “left” means.
- Item-state tracking (needle seated/dislodged) and use-action handlers.

Do not silently turn these unresolved details into canon.

## Visual asset notes

The original real-world photograph is the primary visual reference. Preserve the weathered circular casing, compass face, degree ring and dislodged needle. The previously generated journal scene and item dossier are **concepts**, not approved production assets. Do not use a text-heavy dossier as the item image.

The deferred asset pipeline specifies PNG master, WebP production, 1024px Discord WebP and 512px thumbnail, with permanent asset ID, version, attribution and explicit approval. No production image URL has been assigned yet.

## Implementation boundary

The current Discord `!inspect` command can show this item when present in the room, including its public description and known attributes. Its listed repair interaction is descriptive only; no Dexterity-check or temporal-compulsion handler has been implemented. Hidden discoveries must be granted by a future authoritative gameplay system.
