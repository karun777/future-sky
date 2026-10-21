# Triton Lager

Status: **Author-declared lore — 21 October 2026, Australia/Perth.**  
Source: Karun's explicit clarification during W4-F8 bar-credit review.  
Home implementation record: [W4-F8](../../wings/W4-F8_INTO_THE_LOUNGE.md).

Triton Lager is blue and non-alcoholic. Served chilled, it is refreshing and exhilarating. It is infused with a particular Neptunian microvita with distinctly psychedelic effects.

Drinking in excess carries a high risk of falling through a wormhole. Other effects remain for later exploration. No dose threshold, numerical probability, destination, consequence, teleport or timing rule has been specified.

Possible venue line, accepted for the bar copy:

> Not everyone comes for the chips.

## Implementation boundary

The performance-tab build aligns menu, item inspection, serving prose and the existing effects display with this direction. A presentation overlay preserves the current catalogue's healing/use data and item visibility, rather than replacing the live item catalogue.

The existing +1 intensity per drink, cap of six, 900-real-second decay step, healing and related legacy behaviour are retained implementation, not newly adopted lore. The legacy internal namespace remains intoxication for compatibility; player-facing status reads Microvita intensity. No alcohol content is implied. Existing subjective NPC rumours remain unverified claims, not a diagnosis or evidence that the lager contains alcohol.

No wormhole mechanic is added in this build. Do not treat the absence of a roll as withdrawal of the authored risk; implementation is deferred.
