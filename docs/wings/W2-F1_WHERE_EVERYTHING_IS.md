# W2-F1 — Where Everything Is

Home: W2 Worlds. Status: COMPLETE — bounded source and on-host disk-geography inspection verified.
Date: 17 October 2026, approximately 14:40–14:42 AWST.
Links: W4 Play, W7 Engine. Return: [Wing Index](../WING_INDEX.md).
This records existing geography; it does not author new places or verify a live-player walkthrough.

## Authoritative path

The live service works from /opt/futuresky/bot. Its bot/data symlink resolves to /opt/futuresky/data. In the inspected source, fsbot/config.py defines ROOMS_FILE as data/rooms/rooms.json; Storage.__init__ loads it into self.rooms; NavigationCog reads exits from that store.

The configured persistent room source therefore resolves to **/opt/futuresky/data/rooms/rooms.json**.

START_ROOM is unset in the running process environment, leaving the inspected default pod_room. FS_RESET_ROOMS_ON_BOOT is also unset; the reset branch requires exactly “1”.

Runtime checkout HEAD: 937c007a2981d10b8e1230f293c85b6c72750425.
Repository comparison: origin/main at 530809e92df928680a19df9222122d7371ea145f.
Bot active, with observed start time 2026-10-17 12:50:26 AWST.

Source anchors: [config](https://github.com/karun777/future-sky/blob/530809e92df928680a19df9222122d7371ea145f/bot/fsbot/config.py), [storage](https://github.com/karun777/future-sky/blob/530809e92df928680a19df9222122d7371ea145f/bot/fsbot/storage.py), [navigation](https://github.com/karun777/future-sky/blob/530809e92df928680a19df9222122d7371ea145f/bot/fsbot/cogs/navigation.py), [committed rooms](https://github.com/karun777/future-sky/blob/530809e92df928680a19df9222122d7371ea145f/data/rooms/rooms.json).
Source behaviour above was inspected directly on the live host, not inferred solely from these repository links.

## Observed geography

| Check on configured disk store | Result |
| --- | --- |
| Rooms | 43 |
| Era tags | All 43 are manzo |
| Directed exits | 100 |
| Exit targets absent from store | 0 |
| Rooms graph-reachable from pod_room | 43 |
| Rooms graph-reachable from neptune_lounge | 43 |
| Exit graph compared with committed main | Identical |
| SHA-256 of observed live room file | 20fc12b8573b6716a7453715fb4ee43ab35697ab38d367673d31747a0e3b661b |

These are persistent-file and static graph findings. Storage is loaded into memory; its present in-process contents were not introspected. Gameplay gating, Thread Nodes and character state may affect traversal. No character was moved and no arrival sequence was triggered.

## Existing areas and connections

These are descriptive groupings for navigation, not newly defined canonical regions.

| Area | Existing places and connections |
| --- | --- |
| Arrival and accommodation | pod_room → hostel_hallway → hostel_stairwell → neptune_lounge; hallway also connects to the balcony. |
| Lounge social spaces | Lounge entrance/hub connects inside to lounge_main_floor, which branches toward dance/stage, games/rest, conference/gym/pool, balcony and stardock overlook. |
| Food and service | Lounge west → kitchen_backline → chip_counter; kitchen also reaches cellar and staff corridor. Service gate connects the portal zone to staff corridors. |
| Private rooms and underworks | Lounge east → efiishents_office → sector_50 → dark_rat_queen_den → ratways_01 → sewer_access. Maintenance routes loop back through sectors 55 and 48. |
| City and transit | Lounge north → main_square → dock_gate → transit_pod_bay; branches lead to security/holding cell and observation dome. |
| Observation and thresholds | Catwalk joins Lounge to observation dome; portal zone links Lounge, service routes and stardock; stage reaches an arena portal and holding ring. |

Directions are authored labels, not guaranteed Euclidean coordinates. Navigation lowercases the supplied argument and matches an exit key directly: labels such as inside, upstairs and west_up matter as written.

A room description mentioning distant destinations or portals does not create loaded rooms in those destinations. This inspected store contains no Jyotzon or Omincron-tagged rooms. Wider cosmology and regions remain in lore/research sources.

## Visible seams — preserve before changing

1. **Several room files exist.** data/rooms.json also contains 43 rooms with an identical exit graph but different whole-file bytes. It is not the configured path. data/characters/data/rooms/rooms.json contains an empty object; its presence does not confer authority.
2. **Reset baseline differs.** data/rooms/rooms_base.json contains only 10 entries. Storage can copy it over the active room file when the explicit reset-on-boot setting is enabled. That setting is currently unset; this inspection did not enable it or copy either file.
3. **Four exits lack a direct return edge:** lounge_stage_edge → lounge_main_floor; lounge_rest_nook → lounge_main_floor; lounge_pool_level → lounge_portal_zone; lounge_service_corridor → sector_50. All destinations still participate in the reachable graph. These may be intentional shortcuts; do not label them defects without authorial review.
4. **Content is not geography alone.** Matching exit graphs do not imply matching items, enemies, descriptions, player experience or full deployment state.

## Verification and return checkpoint

Verification used read-only JSON parsing, directed graph reachability, target validation, graph comparison, service metadata, relevant process environment keys and source inspection. No importing the application, movement commands, writes to world data or service restarts.

Reached: configured persistent source identified; 43-room Manzo graph inspected; areas and connections summarised; boundaries recorded.
Open: runtime/player traversal, intended one-way links, reset-baseline purpose and wider-era geography.
Candidate W2-F2, not activated: make a readable local atlas from this graph, marking authored labels and unresolved shortcuts without repairing or expanding the map.
W2 completed count: 1. W1 parked with 2 approved feathers; W8 parked with 2. Existing global feather numbers unchanged.
