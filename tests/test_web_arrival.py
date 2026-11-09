"""Fresh guided creation through real HTTP adapters; fictional records/OAuth only."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
import test_web_wardrobe as wardrobe
import test_web_walking as walking
from fsbot.cogs.arrival import ArrivalCog
from fsbot.pod_opening import opening_state

class WebArrivalTests(unittest.IsolatedAsyncioTestCase):
    start = wardrobe.WebWardrobeTests.start
    complete = wardrobe.WebWardrobeTests.complete
    sign_in = wardrobe.WebWardrobeTests.sign_in
    auth = wardrobe.WebWardrobeTests.auth
    offer = wardrobe.WebWardrobeTests.offer
    inspect = wardrobe.WebWardrobeTests.inspect
    act = wardrobe.WebWardrobeTests.act
    move = walking.WebWalkingTests.move
    asyncTearDown = wardrobe.WebWardrobeTests.asyncTearDown

    async def asyncSetUp(self):
        await wardrobe.WebWardrobeTests.asyncSetUp(self)
        self.bot.storage.characters.pop("123")
        self.messages = []
        async def send(content=None, **kw): self.messages.append(content or "")
        self.ctx = SimpleNamespace(author=SimpleNamespace(id=123), guild=None, send=send)
        self.cogs["WebPortalCog"] = SimpleNamespace(allowed_ids=frozenset({"123"}))
        self.arrival = ArrivalCog(self.bot)
        for action in ["", "class dreamer technician", "name New Traveller", "date 2000-01-01",
                       "body familiar", "embodiment unfamiliar", "review", "awaken"]:
            await ArrivalCog.begin.callback(self.arrival, self.ctx, action=action)
        self.bot.storage.rooms["pod_room"]["exits"] = {"west": "a"}
        self.token = await self.sign_in()

    async def test_fresh_window_discovery_outfit_walk_and_new_session(self):
        self.assertIn("Open your game window", " ".join(self.messages))
        before = deepcopy(self.bot.storage.characters)
        first = await self.offer()
        self.assertEqual(before, self.bot.storage.characters)
        self.assertEqual(first["inspection"]["targets"], ["panels"])
        self.assertFalse(first["wardrobe"]["available"])
        self.assertFalse(first["journal"]["entries"])
        self.assertEqual((await self.inspect(first, "booking")).status, 400)
        self.assertEqual((await self.inspect(await self.offer(), "panels")).status, 200)
        offered = await self.offer()
        self.assertIn("display", offered["inspection"]["targets"])
        self.assertNotIn("booking", offered["inspection"]["targets"])
        self.assertEqual((await self.inspect(offered, "display")).status, 200)
        self.assertEqual((await self.inspect(await self.offer(), "wardrobe")).status, 200)
        outfit = await self.offer()
        self.assertTrue(outfit["wardrobe"]["first_selection"])
        self.assertEqual((await self.act(outfit)).status, 200)
        self.assertEqual((await self.act(outfit)).status, 409)
        clothed = await self.offer()
        self.assertEqual(clothed["inventory"]["equipped"]["chest"]["name"], "Freeform Attire")
        self.assertEqual((await self.move(clothed, "west")).status, 200)
        saved = deepcopy(self.bot.storage.characters["123"])
        self.token = await self.sign_in()
        returned = await self.offer()
        self.assertEqual(returned["location"]["id"], "a")
        self.assertEqual(returned["inventory"], clothed["inventory"])
        self.assertEqual(saved, self.bot.storage.characters["123"])
        self.assertNotIn("booking", opening_state(saved)["discoveries"])
