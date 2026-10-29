import json
import unittest
from copy import deepcopy
import test_web_walking as fixture
from fsbot.idle_home import configure


class WindowViewTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = fixture.WebWalkingTests.asyncSetUp
    asyncTearDown = fixture.WebWalkingTests.asyncTearDown
    start = fixture.WebWalkingTests.start
    complete = fixture.WebWalkingTests.complete
    sign_in = fixture.WebWalkingTests.sign_in
    auth = fixture.WebWalkingTests.auth
    offer = fixture.WebWalkingTests.offer
    move = fixture.WebWalkingTests.move

    async def test_polling_keeps_current_offer_and_never_touches_idle_state(self):
        ch = self.bot.storage.characters["123"]
        ch = configure(ch, 100, idle_seconds=60)
        ch["extra"]["idle_home_v1"].update(channel_id="private-channel", message_id="private-message")
        self.bot.storage.characters["123"] = ch
        before = deepcopy(self.bot.storage.characters)
        first = await self.offer()
        for i in range(10):
            self.now += 4
            data = await self.offer()
            self.assertEqual(data["walking"]["token"], first["walking"]["token"])
        self.assertEqual(self.bot.storage.characters, before)
        self.assertEqual(self.saved, [])
        self.assertNotIn("private-channel", json.dumps(data))
        self.assertNotIn("private-message", json.dumps(data))
        self.assertEqual(data["idle_home"], {"enabled": True, "status": "armed", "at_home": False})
        self.assertEqual((await self.move(first)).status, 200)

    async def test_poll_after_consumption_cannot_revive_used_token(self):
        first = await self.offer()
        self.assertEqual((await self.move(first)).status, 200)
        second = await self.offer()
        self.assertNotEqual(first["walking"]["token"], second["walking"]["token"])
        self.assertEqual((await self.move(first)).status, 409)
        self.assertEqual(len(self.saved), 1)

    async def test_poll_does_not_extend_original_expiry(self):
        first = await self.offer()
        self.now += 100
        self.assertEqual((await self.offer())["walking"]["token"], first["walking"]["token"])
        self.now += 21
        self.assertEqual((await self.move(first)).status, 409)
        self.assertNotEqual((await self.offer())["walking"]["token"], first["walking"]["token"])

    async def test_changed_exits_or_guard_replace_offer(self):
        first = await self.offer()
        self.bot.storage.rooms["a"]["exits"]["north"] = "c"
        second = await self.offer()
        self.assertNotEqual(first["walking"]["token"], second["walking"]["token"])
        self.bot.storage.characters["123"]["flags"] = {"in_combat": True}
        third = await self.offer()
        self.assertEqual(third["walking"]["exits"], [])
        self.assertNotEqual(second["walking"]["token"], third["walking"]["token"])

    async def test_idle_completion_status_is_curated_and_passive(self):
        ch = configure(self.bot.storage.characters["123"], 100, home="a")
        ch["extra"]["idle_home_v1"].update(status="home", pending_notice="PRIVATE INTERNAL NOTICE")
        self.bot.storage.characters["123"] = ch
        before = deepcopy(ch)
        data = await self.offer()
        self.assertEqual(data["idle_home"], {"enabled": True, "status": "home", "at_home": True})
        self.assertNotIn("PRIVATE INTERNAL NOTICE", json.dumps(data))
        self.assertEqual(ch, before)
        self.assertEqual(self.saved, [])

    async def test_malformed_idle_record_does_not_break_observation(self):
        self.bot.storage.characters["123"]["extra"]["idle_home_v1"] = {"private": "missing-schema"}
        data = await self.offer()
        self.assertFalse(data["idle_home"]["enabled"])
        self.assertNotIn("missing-schema", json.dumps(data))
        self.assertEqual(self.saved, [])
