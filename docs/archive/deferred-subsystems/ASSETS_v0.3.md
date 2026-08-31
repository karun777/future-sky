# ASSETS.md

## Future Sky Asset Pipeline & Production Standards

**Status:** Draft v0.3\
**Canonical Purpose:** Defines how production assets are created,
organised, attributed, curated, versioned, rendered, and ultimately
stewarded by the Future Sky community.

------------------------------------------------------------------------

# 1. Purpose

The Future Sky world is constructed from reusable production assets.

An asset is anything that contributes to the player's experience.

Assets include:

-   Room backgrounds
-   NPC portraits
-   Items
-   UI graphics
-   Ambient audio
-   Music
-   Voice recordings
-   Animation
-   Particle definitions
-   Metadata
-   Thread node illustrations
-   Maps
-   Promotional artwork
-   Curated playlists
-   Room soundtracks

Assets are treated as first-class development objects.

------------------------------------------------------------------------

# 2. Philosophy

Future Sky does not treat artwork as decoration.

Artwork **is** worldbuilding.

Sound **is** worldbuilding.

Curation **is** worldbuilding.

Every asset should communicate:

-   Mood
-   Geography
-   Architecture
-   Culture
-   Technology
-   Mythology
-   Timeline
-   Narrative clues

A player should begin feeling a place before reading a single line of
text.

------------------------------------------------------------------------

# 3. Asset Categories

``` text
assets/
    images/
    audio/
    music/
    voice/
    ui/
    video/
    maps/
    concept/
    logos/
    playlists/
```

------------------------------------------------------------------------

# 4. World Structure

``` text
assets/

images/

world/

    manzo/

        triton_central/

            neptune_lounge/

                rooms/

                    pod_room/
                    foyer/
                    dance_floor/
                    bar/
                    kitchen/
                    hostel/
                    observatory/

                characters/

                    dark_rat_queen/
                    bartender/
                    efiishent/

                objects/

                    chips/
                    jukebox/
                    stage/
                    cube/

                events/

                    arrival/
                    comet/
                    blackout/

                concepts/
```

------------------------------------------------------------------------

# 5. Room Packages

Every room owns a production package.

``` text
TC-NL-DANCE/

background_v001.webp
thumbnail.webp
metadata.json
lighting.json
music.json
curation.json

voice/
objects/
threadnodes/
```

A room package grows over time without requiring changes to game logic.

------------------------------------------------------------------------

# 6. Naming Convention

``` text
<world>_<location>_<room>_<asset>_v001.webp
```

Example:

``` text
tritoncentral_neptune_lounge_dance_floor_bg_v001.webp
```

------------------------------------------------------------------------

# 7. Asset IDs

Every significant package receives a permanent Asset ID.

``` text
TC-NL-DANCE
```

Meaning:

``` text
Triton Central
Neptune Lounge
Dance Floor
```

The identifier never changes.

Versions do.

------------------------------------------------------------------------

# 8. Versioning

Never overwrite production assets.

``` text
background_v001
background_v002
background_v003
```

Creative history is preserved.

------------------------------------------------------------------------

# 9. Metadata

``` json
{
  "asset_id": "TC-NL-DANCE",
  "title": "Neptune Lounge — Dance Floor",
  "era": "Manzo",
  "location": "Triton Central",
  "status": "Production",
  "visual_artist": "OpenAI draft",
  "curator": "Psyborg7",
  "approved": true,
  "created": "2026-07-01"
}
```

------------------------------------------------------------------------

# 10. Image Standards

**Master**

-   PNG

**Production**

-   WebP

**Discord**

-   1024px WebP

**Thumbnail**

-   512px WebP

------------------------------------------------------------------------

# 11. AI Workflow

``` text
Concept
    ↓
Prompt refinement
    ↓
AI generation
    ↓
Selection
    ↓
Editing
    ↓
Approval
    ↓
Production Asset
```

AI drafts are working artefacts.

They are not the final cultural form unless explicitly approved as such.

------------------------------------------------------------------------

# 12. Rendering Pipeline

``` text
room.json
    ↓
asset_id
    ↓
asset package
    ↓
Renderer
    ↓
Discord
Future Web
Mobile
Native Clients
```

The game references Asset IDs.

The renderer discovers everything else.

------------------------------------------------------------------------

# 13. Community Artists

Future Sky is intentionally collaborative.

AI is expected to produce many of the first visual interpretations.

Human artists are encouraged to reinterpret, challenge, replace and
expand those ideas.

Multiple canonical interpretations may coexist.

------------------------------------------------------------------------

# 14. Curation

Curation is a first-class creative role in Future Sky.

A curator chooses the atmosphere of a room or experience.

The curator may select:

-   Music
-   Ambient sound
-   Visual mood
-   Lighting direction
-   Playlist sequence
-   Seasonal variations
-   Guest artist pairings
-   Room state transitions

The curator is not necessarily the musician, visual artist or developer.

The curator's contribution is the act of meaningful selection.

Example:

``` json
{
  "room": "Neptune Lounge — Dance Floor",
  "asset_id": "TC-NL-DANCE",
  "curator": "Psyborg7",
  "curator_role": "resident room curator",
  "music": [
    {
      "title": "Black Rabbit",
      "artist": "jsuisgnou",
      "url": "https://soundcloud.com/jsuisgnou/black-rabbit",
      "platform": "SoundCloud"
    }
  ]
}
```

The player may see both:

``` text
Now Playing:
Black Rabbit — jsuisgnou
```

and:

``` text
Room curated by:
Psyborg7
```

These are separate forms of acknowledgement.

------------------------------------------------------------------------

# 15. Guest Curators

Future Sky rooms may later host guest curators.

A guest curator might temporarily reshape:

-   Music
-   Lighting
-   Room artwork
-   Ambient messages
-   Feed7 behaviour
-   Thread node frequency
-   NPC presence

This allows Future Sky to function as a living cultural venue rather
than a static game map.

Example:

``` json
{
  "guest_curator": {
    "name": "Example DJ",
    "season": "Comet Kirch",
    "start_date": "2134-03-04",
    "end_date": "2134-04-04",
    "support_url": null
  }
}
```

------------------------------------------------------------------------

# 16. Supporting Artists and Curators

Every significant production asset should eventually be attributable.

Future support mechanisms may include:

-   Donations
-   Patronage
-   Commissions
-   Revenue sharing
-   Community funding
-   Digital provenance
-   Artist pages
-   Curator pages

The architecture should make this easy.

------------------------------------------------------------------------

# 17. Tokenisation

Future Sky is designed to support future ownership technologies without
depending on them.

Metadata already provides room for:

-   payment_link
-   support_url
-   token_id

Whether the future uses NFTs, successor technologies, or something
entirely different, the asset model should already be capable of
recording provenance.

Tokenisation should not be implemented until there is a clear cultural,
legal and operational reason.

------------------------------------------------------------------------

# 18. Asset Lifecycle

Every asset has a life.

``` text
Idea
    ↓
Concept
    ↓
AI Draft
    ↓
Human Interpretation
    ↓
Production Asset
    ↓
Canon
    ↓
Legacy
```

## Idea

A feeling.

A room.

A memory.

A sketch.

The beginning of a possibility.

## Concept

The idea becomes communicable.

Words.

Reference photographs.

Mood boards.

Music.

Conversation.

## AI Draft

AI serves as a creative accelerator.

Its role is to rapidly explore visual possibility.

The AI draft is not considered the finished artwork.

It is the first conversation.

## Human Interpretation

Artists, musicians, photographers, designers and storytellers bring
lived experience.

They are encouraged to reinterpret---not merely reproduce---the AI
draft.

Future Sky becomes richer through multiple perspectives.

## Production Asset

The work is approved.

It receives:

-   Asset ID
-   Metadata
-   Version
-   Attribution

It becomes available to the renderer.

## Canon

After proving itself through use, the asset becomes part of the living
world.

Players begin associating it with memory.

Recognition itself gives an asset narrative weight.

## Legacy

Nothing is truly retired.

Older versions remain part of the historical record.

Future artists may revisit, restore or reinterpret them.

The history of Future Sky is itself an evolving artwork.

------------------------------------------------------------------------

# 19. Long-term Vision

Every room eventually becomes a complete production package containing:

-   Artwork
-   Music
-   Ambient sound
-   Lighting
-   Objects
-   NPC portraits
-   Environmental metadata
-   Thread node artwork
-   Curator notes
-   Guest curator states

The renderer assembles the experience dynamically.

------------------------------------------------------------------------

# 20. Design Principles

> The world is not built from rooms.

> The world is built from assets.

> AI helps imagine the world.

> Artists give it culture.

> Curators give it atmosphere.

> Players give it memory.
