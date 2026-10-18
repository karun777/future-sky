# Player command language

Adopted by Karun, 18 October 2026.

Prefer spaces in player-facing commands and parameter names. Underscores are undesirable in prompts, help and examples. Internal identifiers may retain underscores. Preserve working underscore commands as compatibility paths while improving commands incrementally; no wholesale rename is required.

First implemented family:
- `!hud`
- `!hud on` / `!hud off`
- `!hud state normal`
- `!hud state signal degraded`
- `!hud state dark mode`

Consume or validate supplied arguments. Unknown or trailing arguments must produce useful guidance rather than silently executing a different action. Compatibility paths should follow the same validation principle.

This convention does not claim every existing command has been migrated. Other underscore commands remain as implemented until their families are revised.
