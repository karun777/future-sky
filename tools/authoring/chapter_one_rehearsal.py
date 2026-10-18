"""Offline authoring rehearsal for W4-F3. Not imported by the game.

Times are synthetic ordered ticks. Half-open intervals are a rehearsal policy,
not an adopted Manzo clock or deadline. No score decides musical quality.
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import os
import tempfile


class Result(str, Enum):
    POSSIBLE = "possible"
    CLOSED = "closed"
    UNRESOLVED = "unresolved"


def following_set(*, now, opens, closes, played_well, ambassador_present):
    """Efiishent instance: a good set is necessary, not sufficient, here."""
    if opens is None or closes is None:
        return Result.UNRESOLVED
    if closes <= opens:
        raise ValueError("Invalid rehearsal interval")
    if now >= closes or played_well is False or ambassador_present is False:
        return Result.CLOSED
    if now < opens or played_well is None or ambassador_present is None:
        return Result.UNRESOLVED
    return Result.POSSIBLE


def allied_trade_opportunity(*, window_open, representative_present,
                             mutually_willing, exchange_available):
    """Common quest: meeting/trade availability, without a romance requirement.

    These are supplied authoring facts. POSSIBLE is never a completed trade.
    The performance gate and private-room encounter belong to Efiishent's
    particular instance and are not inherited by every allied encounter.
    """
    conditions = (window_open, representative_present,
                  mutually_willing, exchange_available)
    if any(value is False for value in conditions):
        return Result.CLOSED
    if any(value is None for value in conditions):
        return Result.UNRESOLVED
    return Result.POSSIBLE


def private_exchange(*, opportunity, private_place, mutual_recognition,
                     giver_has_item, counterpart_willing):
    """Efiishent private encounter; never a universal trade/romance gate."""
    if opportunity == Result.CLOSED:
        return Result.CLOSED
    conditions = (private_place, mutual_recognition, giver_has_item,
                  counterpart_willing)
    if False in conditions:
        return Result.CLOSED
    if opportunity != Result.POSSIBLE or any(v is None for v in conditions):
        return Result.UNRESOLVED
    return Result.POSSIBLE


def receipt_meaning_condition(*, recipient, giver, reported_irl_receipt):
    """Author-supplied condition for this particular gift, not IRL verification."""
    if recipient != "efiishent" or giver != "dark_rat_queen":
        return Result.UNRESOLVED
    if reported_irl_receipt is None:
        return Result.UNRESOLVED
    return Result.POSSIBLE if reported_irl_receipt else Result.CLOSED


@dataclass(frozen=True)
class Fact:
    event_id: str
    tick: int
    kind: str
    details_json: str

    @property
    def details(self):
        return json.loads(self.details_json)


@dataclass(frozen=True)
class Observation:
    event_id: str
    observer: str
    account: str


class Rehearsal:
    """Small serial, disposable example; no concurrency or production guarantees."""
    def __init__(self):
        self._facts = {}
        self._observations = []
        self._owners = {}
        self.cycle = 1

    @property
    def facts(self):
        return tuple(self._facts.values())

    def record(self, event_id, tick, kind, **details):
        fact = Fact(event_id, tick, kind,
                    json.dumps(details, sort_keys=True, separators=(",", ":")))
        previous = self._facts.get(event_id)
        if previous is not None:
            if previous != fact:
                raise ValueError("An occurrence cannot be overwritten")
            return previous
        self._facts[event_id] = fact
        return fact

    def observe(self, event_id, observer, account):
        if event_id not in self._facts:
            raise ValueError("Unknown occurrence")
        observation = Observation(event_id, observer, account)
        if observation not in self._observations:
            self._observations.append(observation)

    def perspective(self, observer):
        # World facts never leak into a participant's view by simple presence.
        return tuple(o for o in self._observations if o.observer == observer)

    def seed_custody(self, item_instance, owner):
        if item_instance in self._owners:
            raise ValueError("Item instance already exists")
        self._owners[item_instance] = owner

    def owner(self, item_instance):
        return self._owners.get(item_instance)

    def transfer(self, event_id, tick, item_instance, giver, recipient):
        details = dict(item_instance=item_instance, giver=giver, recipient=recipient)
        previous = self._facts.get(event_id)
        if previous is not None:
            return self.record(event_id, tick, "gift.transferred", **details)
        if self.owner(item_instance) != giver:
            raise ValueError("Giver does not hold this item instance")
        fact = self.record(event_id, tick, "gift.transferred", **details)
        self._owners[item_instance] = recipient
        return fact

    def next_cycle(self):
        # Chosen rehearsal policy: renew opportunity context; preserve history.
        # Canon has not yet selected a complete reset policy.
        self.cycle += 1

    def save(self, path):
        path = Path(path)
        payload = dict(cycle=self.cycle, owners=self._owners,
                       facts=[f.__dict__ for f in self.facts],
                       observations=[o.__dict__ for o in self._observations])
        fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".rehearsal-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, ensure_ascii=False)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @classmethod
    def load(cls, path):
        # Reads only the rehearsal's own trusted fixture format.
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        result = cls()
        result.cycle = payload["cycle"]
        result._owners = payload["owners"]
        result._facts = {f["event_id"]: Fact(**f) for f in payload["facts"]}
        result._observations = [Observation(**o) for o in payload["observations"]]
        return result
