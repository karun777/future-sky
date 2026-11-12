"""Guided return and explicit obsolete-node release; fictional temporary records only."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from fsbot.cogs.threadnodes import ThreadNodesCog
from fsbot.pod_opening import (LEGACY_AWAKENING, guided_opening_established,
                               release_superseded_awakening)
import test_pod_opening as opening


class GuidedPodReturnTests(unittest.IsolatedAsyncioTestCase):
    setUp = opening.PodOpeningTests.setUp
    reload = opening.PodOpeningTests.reload
    disk = opening.PodOpeningTests.disk
    create = opening.PodOpeningTests.create
    awaken = opening.PodOpeningTests.awaken
    character = opening.PodOpeningTests.character

    async def stuck(self):
        await self.create()
        character = self.character()
        character["extra"]["arrival"] = {
            "origin": "guided_creation_v1", "performance_booking": False,
            "opening": {"id": "performance_arrival_v1",
                        "discoveries": ["hands", "pod", "panels", "display", "wardrobe"]},
            "pod_uniform_selected": "pod_freeform"}
        character["equipped"] = {"chest": "itm_pod_uniform_freeform"}
        character["extra"]["thread_nodes"] = {
            "active_thread_node": LEGACY_AWAKENING, "active_presented": True,
            "pending_answer": None, "events_completed": ["fictional-earlier"],
            "unrelated": {"remember": True}}
        self.storage.save_characters()
        self.ctx.messages.clear()
        return deepcopy(self.disk())

    async def test_owner_awaken_saves_only_release_and_reloads_idempotently(self):
        before = await self.stuck()
        expected = deepcopy(before)
        threads = expected[str(self.ctx.author.id)]["extra"]["thread_nodes"]
        threads.update(active_thread_node=None, active_presented=False)
        await self.awaken()
        self.assertEqual(expected, self.disk())
        self.assertEqual(expected, self.storage.characters)
        self.assertIn("FINDING YOUR BEARINGS", self.ctx.text())
        self.reload()
        calls = self.storage.save_calls
        await self.awaken()
        self.assertEqual(expected, self.disk())
        self.assertEqual(calls, self.storage.save_calls)

    async def test_failed_save_keeps_blocker_and_all_progress_then_retries(self):
        before = await self.stuck()
        self.storage.fail_next = True
        await self.awaken()
        self.assertEqual(before, self.disk())
        self.assertEqual(before, self.storage.characters)
        self.assertIn("could not remember", self.ctx.text())
        self.assertNotIn("FINDING YOUR BEARINGS", self.ctx.text())
        await self.awaken()
        self.assertIsNone(self.character()["extra"]["thread_nodes"]["active_thread_node"])
        self.assertEqual(before["other"], self.disk()["other"])

    async def test_release_refuses_unrelated_or_uncertain_state_without_writes(self):
        await self.stuck()
        initial = deepcopy(self.character())
        variants = [
            ("legacy origin", lambda c: c["extra"]["arrival"].pop("origin")),
            ("missing opening", lambda c: c["extra"]["arrival"].pop("opening")),
            ("unknown opening", lambda c: c["extra"]["arrival"]["opening"].update(id="other")),
            ("invalid discoveries", lambda c: c["extra"]["arrival"]["opening"].update(discoveries=None)),
            ("other node", lambda c: c["extra"]["thread_nodes"].update(active_thread_node="other")),
            ("pending answer", lambda c: c["extra"]["thread_nodes"].update(pending_answer="answer")),
            ("empty pending answer", lambda c: c["extra"]["thread_nodes"].update(pending_answer={})),
            ("encounter", lambda c: c["extra"]["thread_nodes"].update(active_encounter_id="encounter")),
            ("cube", lambda c: c.update(in_cube=True)),
            ("away", lambda c: c.update(current_room="hostel_hallway")),
            ("reanimation", lambda c: c["extra"].update(recovery={"stage": "reanimating"})),
            ("brain review", lambda c: c["extra"].update(recovery={"stage": "brain_review"})),
            ("combat", lambda c: c.update(in_combat=True)),
        ]
        for label, change in variants:
            with self.subTest(case=label):
                character = deepcopy(initial)
                change(character)
                self.storage.characters[str(self.ctx.author.id)] = character
                self.storage.save_characters()
                before = deepcopy(self.disk())
                calls = self.storage.save_calls
                self.assertIs(release_superseded_awakening(character), character)
                self.ctx.messages.clear()
                await self.awaken()
                self.assertEqual(before, self.disk())
                self.assertEqual(before, self.storage.characters)
                self.assertEqual(calls, self.storage.save_calls)
                self.assertIn("A moment is already open", self.ctx.text())

    async def test_selector_preserves_legacy_and_unrelated_nodes(self):
        await self.stuck()
        self.bot.state.resolve_era_for_room = lambda room: "Manzo"
        cog = ThreadNodesCog(self.bot)
        char = release_superseded_awakening(self.character())
        legacy = deepcopy(cog.nodes[LEGACY_AWAKENING])
        cog.nodes = {LEGACY_AWAKENING: legacy}
        self.assertIsNone(cog._pick_on_enter_node_id(char, "pod_room"))
        self.assertNotIn(LEGACY_AWAKENING, char["extra"]["thread_nodes"]["events_completed"])
        for origin in (None, "legacy"):
            candidate = deepcopy(char)
            candidate["extra"]["arrival"]["origin"] = origin
            self.assertEqual(cog._pick_on_enter_node_id(candidate, "pod_room"), LEGACY_AWAKENING)
        cog.nodes["unrelated"] = deepcopy(legacy)
        self.assertEqual(cog._pick_on_enter_node_id(char, "pod_room"), "unrelated")
        char["extra"]["thread_nodes"]["active_thread_node"] = "existing"
        self.assertIsNone(cog._pick_on_enter_node_id(char, "pod_room"))

    def test_missing_or_malformed_guided_origin_is_not_established(self):
        for candidate in (None, {}, {"extra": None}, {"extra": {"arrival": []}}):
            with self.subTest(candidate=candidate):
                self.assertFalse(guided_opening_established(candidate))
                self.assertIs(release_superseded_awakening(candidate), candidate)
