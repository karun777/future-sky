"""A character's durable observations and the ones they chose to share."""
from dataclasses import dataclass


class EncounterUnavailable(ValueError):
    pass


@dataclass(frozen=True)
class EncounterMemory:
    seen: tuple = ()
    shared: tuple = ()

    @classmethod
    def read(cls, character, encounter):
        extra = character.get("extra", {})
        if not isinstance(extra, dict):
            raise EncounterUnavailable("Your encounter record is unavailable.")
        record = extra.get(encounter, {})
        if not isinstance(record, dict):
            raise EncounterUnavailable("Your encounter record is unavailable.")
        seen, shared = record.get("seen", []), record.get("shared", [])
        if not all(isinstance(ids, list) and all(isinstance(key, str) for key in ids)
                   for ids in (seen, shared)) or not set(shared).issubset(seen):
            raise EncounterUnavailable("Your encounter record is unavailable.")
        return cls(tuple(seen), tuple(shared))

    def witness(self, fact):
        return self if fact in self.seen else EncounterMemory(self.seen + (fact,), self.shared)

    def report(self, fact):
        if fact not in self.seen:
            raise EncounterUnavailable("You have not seen that for yourself.")
        return self if fact in self.shared else EncounterMemory(self.seen, self.shared + (fact,))

    def save(self, storage, uid, encounter):
        character = storage.characters[uid]
        if self == self.read(character, encounter):
            return
        original = character.get("extra")
        record = {**(original or {}).get(encounter, {}), "seen": list(self.seen),
                  "shared": list(self.shared)}
        character["extra"] = {**(original or {}), encounter: record}
        try:
            storage.save_characters()
        except Exception:
            if original is None:
                character.pop("extra", None)
            else:
                character["extra"] = original
            raise
