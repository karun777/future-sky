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
        self.assertEqual(first["inspection"]["targets"], ["hands", "garment", "pod", "panels"])
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

    async def test_opening_choices_and_followons_preserve_fresh_progress(self):
        before = deepcopy(self.bot.storage.characters)
        first = await self.offer()
        self.assertIn("!inspect hands", first["location"]["description"])
        self.assertEqual(before, self.bot.storage.characters)
        response = await self.inspect(first, "hands")
        self.assertEqual(response.status, 200)
        observation = (await response.json())["observation"]
        self.assertIn("Yours.", observation["text"])
        offered = await self.offer()
        self.assertIn("hud", offered["inspection"]["targets"])
        self.assertIn("body", offered["inspection"]["targets"])
        self.assertFalse(offered["journal"]["entries"])
        self.assertNotIn("booking", offered["inspection"]["targets"])
        self.assertEqual((await self.inspect(offered, "garment")).status, 200)
        self.assertIn("chain", (await self.offer())["inspection"]["targets"])
        self.assertEqual((await self.inspect(await self.offer(), "pod")).status, 200)
        self.assertIn("viewport", (await self.offer())["inspection"]["targets"])
        self.assertNotIn("wardrobe", (await self.offer())["inspection"]["targets"])

    async def test_guided_outfit_departure_and_return_with_real_room_subscriber(self):
        from unittest.mock import AsyncMock
        from fsbot.cogs.threadnodes import ThreadNodesCog
        from fsbot.events import EventBus
        self.bot.state.ensure_player_records = lambda uid: None
        self.bot.storage.rooms["a"]["exits"] = {"east": "pod_room"}
        threads = ThreadNodesCog(self.bot)
        delivery = SimpleNamespace(send=AsyncMock())
        threads._event_delivery_context = AsyncMock(return_value=delivery)
        self.cogs["ThreadNodesCog"] = threads
        self.bot.events = EventBus()
        self.bot.events.subscribe("character.entered_room", threads._on_character_entered_room)
        other = deepcopy(self.bot.storage.characters["456"])
        for target in ("panels", "display", "wardrobe"):
            self.assertEqual((await self.inspect(await self.offer(), target)).status, 200)
        self.assertEqual((await self.act(await self.offer())).status, 200)
        clothed = await self.offer()
        opening = deepcopy(opening_state(self.bot.storage.characters["123"]))
        self.assertEqual((await self.move(clothed, "west")).status, 200)
        self.assertEqual(self.bot.storage.characters["123"]["current_room"], "a")
        # Discord and HUD share this actual Navigation operation.
        self.assertTrue((await self.nav.walk("123", "east"))["ok"])
        traces = self.bot.events.recent_traces(limit=2, event_type="character.entered_room")
        self.assertEqual(len(traces), 2)
        for trace in traces:
            self.assertEqual(len(trace["subscribers"]), 1)
            self.assertTrue(trace["subscribers"][0]["ok"], trace)
        self.assertEqual(traces[0]["event"]["payload"]["to_room_id"], "pod_room")
        self.assertEqual(traces[0]["subscribers"][0]["status"], "no_match")
        delivery.send.assert_not_awaited()
        saved = deepcopy(self.bot.storage.characters["123"])
        self.assertIsNone(saved["extra"]["thread_nodes"]["active_thread_node"])
        self.assertNotIn("arrival_awakening_v1", saved["extra"]["thread_nodes"]["events_completed"])
        self.assertEqual(opening_state(saved), opening)
        self.assertEqual(self.saved[-1]["123"], saved)
        self.bot.storage.characters = deepcopy(self.saved[-1])
        self.token = await self.sign_in()
        returned = await self.offer()
        self.assertEqual(returned["location"]["id"], "pod_room")
        self.assertEqual(returned["inventory"], clothed["inventory"])
        self.assertEqual(returned["walking"]["exits"], ["west"])
        self.assertEqual(saved, self.bot.storage.characters["123"])
        self.assertEqual(other, self.bot.storage.characters["456"])
        self.assertEqual((await self.move(returned, "west")).status, 200)
