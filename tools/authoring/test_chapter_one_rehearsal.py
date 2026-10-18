"""Meaningful boundary cases for a proposed authoring interpretation, not gameplay."""
import tempfile
import unittest
from pathlib import Path
from chapter_one_rehearsal import (
    Rehearsal, Result, following_set, private_exchange, receipt_meaning_condition,
    allied_trade_opportunity,
)


class WindowCases(unittest.TestCase):
    def gate(self, **overrides):
        values = dict(now=20, opens=10, closes=30,
                      played_well=True, ambassador_present=True)
        values.update(overrides)
        return following_set(**values)

    def test_poor_performance_closes_opportunity(self):
        self.assertEqual(self.gate(played_well=False), Result.CLOSED)

    def test_unknown_quality_does_not_become_success(self):
        self.assertEqual(self.gate(played_well=None), Result.UNRESOLVED)

    def test_good_performance_does_not_conjure_ambassador(self):
        self.assertEqual(self.gate(ambassador_present=None), Result.UNRESOLVED)
        self.assertEqual(self.gate(ambassador_present=False), Result.CLOSED)

    def test_opening_and_closing_boundaries(self):
        self.assertEqual(self.gate(now=9), Result.UNRESOLVED)
        self.assertEqual(self.gate(now=10), Result.POSSIBLE)
        self.assertEqual(self.gate(now=29), Result.POSSIBLE)
        self.assertEqual(self.gate(now=30), Result.CLOSED)
        self.assertEqual(self.gate(now=31), Result.CLOSED)

    def test_unknown_deadline_stays_unknown(self):
        self.assertEqual(self.gate(closes=None), Result.UNRESOLVED)

    def test_invalid_interval_is_rejected(self):
        with self.assertRaises(ValueError):
            self.gate(closes=10)

    def exchange(self, **overrides):
        values = dict(opportunity=Result.POSSIBLE, private_place=True,
                      mutual_recognition=True, giver_has_item=True,
                      counterpart_willing=True)
        values.update(overrides)
        return private_exchange(**values)

    def test_public_exchange_cannot_pass_this_account(self):
        self.assertEqual(self.exchange(private_place=False), Result.CLOSED)

    def test_opportunity_does_not_override_counterpart_choice(self):
        self.assertEqual(self.exchange(counterpart_willing=False), Result.CLOSED)
        self.assertEqual(self.exchange(counterpart_willing=None), Result.UNRESOLVED)

    def test_unknown_recognition_is_not_invented(self):
        self.assertEqual(self.exchange(mutual_recognition=None), Result.UNRESOLVED)

    def test_closed_window_cannot_be_rescued_by_all_other_conditions(self):
        self.assertEqual(self.exchange(opportunity=Result.CLOSED), Result.CLOSED)


class CommonQuestCases(unittest.TestCase):
    def opportunity(self, **overrides):
        facts = dict(window_open=True, representative_present=True,
                     mutually_willing=True, exchange_available=True)
        facts.update(overrides)
        return allied_trade_opportunity(**facts)

    def test_diplomatic_trade_needs_no_romance_or_performance_fact(self):
        self.assertEqual(self.opportunity(), Result.POSSIBLE)

    def test_a_meeting_without_an_established_exchange_is_unresolved(self):
        self.assertEqual(self.opportunity(exchange_available=None), Result.UNRESOLVED)

    def test_refusal_closes_the_proposed_trade(self):
        self.assertEqual(self.opportunity(mutually_willing=False), Result.CLOSED)

    def test_expired_window_cannot_be_overridden_by_other_conditions(self):
        self.assertEqual(self.opportunity(window_open=False), Result.CLOSED)


class MemoryCases(unittest.TestCase):
    def test_shared_occurrence_different_views(self):
        world = Rehearsal()
        world.record("floor-1", 20, "encounter", participants=["efiishent", "puzzler"])
        world.observe("floor-1", "efiishent", "I recognised her.")
        world.observe("floor-1", "puzzler", "Two people caught the room's attention.")
        self.assertEqual(len(world.facts), 1)
        self.assertNotEqual(world.perspective("efiishent"), world.perspective("puzzler"))
        self.assertEqual(world.perspective("unrelated-visitor"), ())

    def test_hidden_identity_does_not_leak_into_public_account(self):
        world = Rehearsal()
        world.record("recognition-1", 21, "recognition", true_identity="dark_rat_queen")
        world.observe("recognition-1", "efiishent", "The princess is the Dark Rat Queen.")
        world.observe("recognition-1", "witness", "They seemed to recognise one another.")
        self.assertNotIn("Dark Rat Queen", str(world.perspective("witness")))

    def test_occurrence_survives_disputed_credit(self):
        world = Rehearsal()
        world.record("goal-1", 25, "objective.occurred", actor="efiishent")
        world.observe("goal-1", "witness-a", "Perhaps Efiishent did it.")
        world.observe("goal-1", "witness-b", "Perhaps the Puzzler did it.")
        self.assertEqual(world.facts[0].details["actor"], "efiishent")

    def test_duplicate_delivery_is_idempotent_conflict_rejected(self):
        world = Rehearsal()
        first = world.record("one", 1, "observed", value=1)
        self.assertEqual(first, world.record("one", 1, "observed", value=1))
        self.assertEqual(len(world.facts), 1)
        with self.assertRaises(ValueError):
            world.record("one", 1, "observed", value=2)

    def test_returned_payload_cannot_rewrite_fact(self):
        world = Rehearsal()
        fact = world.record("one", 1, "observed", value=1)
        fact.details["value"] = 99
        self.assertEqual(world.facts[0].details["value"], 1)

    def test_unique_custody_cannot_be_duplicated(self):
        world = Rehearsal()
        world.seed_custody("gift-instance-1", "princess")
        world.transfer("give-1", 25, "gift-instance-1", "princess", "efiishent")
        world.transfer("give-1", 25, "gift-instance-1", "princess", "efiishent")
        self.assertEqual(len(world.facts), 1)
        self.assertEqual(world.owner("gift-instance-1"), "efiishent")
        with self.assertRaises(ValueError):
            world.transfer("give-2", 26, "gift-instance-1", "princess", "puzzler")

    def test_new_cycle_and_reload_preserve_trace_and_custody(self):
        world = Rehearsal()
        world.seed_custody("tiny-book-fixture", "efiishent")
        world.transfer("book-1", 25, "tiny-book-fixture", "efiishent", "princess")
        world.observe("book-1", "later-visitor", "A trace of an earlier exchange.")
        world.next_cycle()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            world.save(path)
            restored = Rehearsal.load(path)
        self.assertEqual(restored.cycle, 2)
        self.assertEqual(restored.facts, world.facts)
        self.assertEqual(restored.owner("tiny-book-fixture"), "princess")
        self.assertEqual(restored.perspective("later-visitor"), world.perspective("later-visitor"))

    def test_in_game_transfer_does_not_meet_irl_condition(self):
        self.assertEqual(receipt_meaning_condition(
            recipient="efiishent", giver="dark_rat_queen", reported_irl_receipt=False), Result.CLOSED)
        self.assertEqual(receipt_meaning_condition(
            recipient="efiishent", giver="dark_rat_queen", reported_irl_receipt=None), Result.UNRESOLVED)

    def test_other_princess_gift_is_not_queen_gift(self):
        self.assertEqual(receipt_meaning_condition(
            recipient="efiishent", giver="other_princess", reported_irl_receipt=True), Result.UNRESOLVED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
