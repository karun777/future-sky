# W4-F9 terrace-delivery rehearsal

An offline authoring experiment from appreciating the view to collecting the USB marked **tunes**. It uses only Python's standard library. The Discord bot does not import or load it.

## Try it on Neptune Lounge

From the W4-F9 worktree:

```bash
cd /home/efiishent/future-sky-worktrees/w4-f9
python3 tools/authoring/w4f9/terrace_rehearsal.py
```

That prints a deterministic fictional walkthrough. For interactive actions:

```bash
python3 tools/authoring/w4f9/terrace_rehearsal.py --interactive
```

Type the listed actions as plain text, without Discord prefixes. Type quit to finish. Each run creates its own temporary fictional JSON save and discards it on exit. There is no save-path option and no connection to the live bot/data.

The actions can be tried in different orders. Reading the address is optional for picking up the package; picking up and opening the wrapping are separate. The lock needs the fixture's neck key. Opening the box reveals the label, and taking the USB moves it into inventory. Carried packages can be opened after leaving the terrace. Returning does not duplicate the arrival.

## Verification

```bash
python3 -m unittest discover -s tools/authoring/w4f9 -p 'test_*.py' -v
```

**18 executed tests pass.** These cover fictional eligibility, location/attention gates, separate layers and knowledge, neck-key availability, address-recognition variants, departure before pickup, opening carried material elsewhere, stable instance identifiers, re-entry/replay, isolation, temporary save/load with controller recreation, failed-save retry at every mutating step and hidden/unresolved future metadata.

The writer atomically replaces its one temporary JSON file. Injected failures occur before replacement. This is not a crash-recovery or concurrent/multiplayer test, nor an integration test of production cogs or multiple live stores.

## Review assumptions

The explicit attend → notice sky pair demonstrates a pause and attention without choosing a clock. It is not an adopted requirement for two commands, a time threshold or smoking.

Fixture enrolment and known booking select this particular passage. Neck-key availability is seeded explicitly; no live key item is invented or equated with the Key of Commotion. Name recognition can be true, false or unresolved; the default unresolved response is editorial review copy.

Instance IDs and package/box/USB custody are local experimental shapes. Each fixture player has their own synthetic delivery; this does not decide whether the eventual multiplayer scene is shared or personal.

The USB carries internal lineage, provisional temporal validity, unexamined integrity and an unresolved future condition. These metadata are not revealed in player inventory text. No sender, Queen/princess identity or later spy-work instruction is disclosed.

Queen meetings, rat messenger, fee, practice, sabotage, future Cube send, copying/transferring and disappearance are not implemented. Their detailed rules remain in the [conditions map](../../../docs/wings/W4-F9_MUSIC_CUSTODY_AND_CONDITIONS.md). The field holding future validity is an extension point, not proof of working invalidation.

No runtime room, atmosphere mechanism, artwork, inventory schema or scene command is installed. The prototype can inform a later implementation once reviewed.
