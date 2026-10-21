"""Performance tab grants/spending via real callbacks and temporary JSON."""
from copy import deepcopy
import unittest
import test_display
from fsbot.cogs.bar_shop import BarShopCog
from fsbot.performance_tab import KEY, reveal_tab, balance
from fsbot.bar_shop import buy_from_bar, BarError
from fsbot.pod_opening import prepare_observation
from fsbot.item_inspection import inspect_item

class PerformanceTabTests(unittest.IsolatedAsyncioTestCase):
    setUp = test_display.DisplayTests.setUp
    reload = test_display.DisplayTests.reload
    char = test_display.DisplayTests.char
    inspect = test_display.DisplayTests.inspect

    def performer(self):
        ch, _ = prepare_observation(self.char())
        ch["extra"]["arrival"]["opening"]["discoveries"] = ["booking"]
        ch["current_room"] = "neptune_lounge"
        ch["credits"] = 0
        self.storage.characters[self.uid] = ch
        self.storage.items_db["Triton Lager"] = {"name": "Triton Lager"}
        self.storage.save_characters()

    async def menu(self):
        self.ctx.messages.clear()
        await BarShopCog.bar.callback(BarShopCog(self.bot), self.ctx)

    async def buy(self):
        self.ctx.messages.clear()
        await BarShopCog.buy.callback(BarShopCog(self.bot), self.ctx, item="Triton Lager")

    async def test_inspection_grant_survives_reload_and_cannot_repeat(self):
        self.performer()
        others = deepcopy(self.storage.characters["other"])
        await self.inspect("counterkeeper")
        self.assertIn("For the set", self.ctx.text())
        self.assertIn("counterkeeper.webp", self.ctx.messages[-1]["embed"].image.url)
        self.assertEqual(balance(self.char()), 25)
        self.assertEqual(self.char()["credits"], 0)
        self.reload()
        before = self.path.read_text()
        await self.inspect("counterkeeper")
        self.assertNotIn("For the set", self.ctx.text())
        self.assertEqual(self.path.read_text(), before)
        self.assertEqual(self.storage.characters["other"], others)
        await self.menu()
        self.assertNotIn("For the set", self.ctx.text())
        self.assertEqual(balance(self.char()), 25)

    async def test_menu_can_reveal_without_token_then_spend_and_exhaust(self):
        self.performer()
        await self.menu()
        self.assertIn("For the set", self.ctx.text())
        self.assertIn("25 bar credits", self.ctx.text())
        for expected in [20, 15, 10, 5, 0]:
            await self.buy()
            self.assertEqual(balance(self.char()), expected)
            self.assertEqual(self.char()["credits"], 0)
            self.reload()
            self.storage.items_db["Triton Lager"] = {"name": "Triton Lager"}
        self.assertEqual(self.char()["bag"]["Triton Lager"], 5)
        before = self.path.read_text()
        await self.menu()
        self.assertNotIn("!buy Triton Lager", self.ctx.text())
        self.assertIn("not currently have enough", self.ctx.text())
        await self.inspect("counterkeeper")
        self.assertEqual(balance(self.char()), 0)
        await self.buy()
        self.assertEqual(self.path.read_text(), before)
        self.assertIn("costs 5", self.ctx.text())

    async def test_partial_tab_uses_only_remaining_cash(self):
        self.performer()
        await self.menu()
        self.char()["extra"][KEY]["balance"] = 2
        self.char()["credits"] = 7
        self.storage.save_characters()
        await self.buy()
        self.assertEqual(balance(self.char()), 0)
        self.assertEqual(self.char()["credits"], 4)
        self.assertIn("2 bar credits and 3 credits", self.ctx.text())

    async def test_failed_grant_has_no_success_and_retry_grants_once(self):
        self.performer()
        before = self.path.read_text()
        original = deepcopy(self.storage.characters)
        self.storage.fail_next = True
        await self.inspect("counterkeeper")
        self.assertIn("could not be saved", self.ctx.text())
        self.assertNotIn("For the set", self.ctx.text())
        self.assertEqual(self.path.read_text(), before)
        self.assertEqual(self.storage.characters, original)
        await self.menu()
        self.assertEqual(balance(self.char()), 25)

    async def test_failed_purchase_preserves_tab_cash_inventory_and_other(self):
        self.performer()
        await self.menu()
        before = self.path.read_text()
        original = deepcopy(self.storage.characters)
        self.storage.fail_next = True
        await self.buy()
        self.assertIn("could not be saved", self.ctx.text())
        self.assertNotIn("slides you", self.ctx.text())
        self.assertEqual(self.storage.characters, original)
        self.assertEqual(self.path.read_text(), before)
        await self.buy()
        self.assertEqual(balance(self.char()), 20)

    def test_no_grant_without_discovered_booking_or_in_cube(self):
        self.performer()
        base = deepcopy(self.char())
        cases = []
        for room in ["pod_room", "lounge_main_floor"]:
            ch = deepcopy(base); ch["current_room"] = room; cases.append(ch)
        ch = deepcopy(base); ch["in_cube"] = True; cases.append(ch)
        ch = deepcopy(base); ch["extra"]["arrival"]["performance_booking"] = False; cases.append(ch)
        ch = deepcopy(base); ch["extra"]["arrival"]["opening"]["discoveries"] = []; cases.append(ch)
        ch = deepcopy(base); ch["extra"].pop("arrival"); cases.append(ch)
        for ch in cases:
            before = deepcopy(ch)
            updated, message = reveal_tab(ch)
            self.assertEqual(updated, before)
            self.assertIsNone(message)

    async def test_corrupt_tab_cannot_refill_or_spend_cash(self):
        self.performer()
        for state in [{"granted": True, "balance": -1}, {"granted": True, "balance": True},
                      {"granted": False, "balance": 25}, {"granted": True, "balance": 26}]:
            self.char()["extra"][KEY] = state
            self.storage.save_characters()
            before = self.path.read_text()
            await self.menu()
            self.assertIn("unavailable", self.ctx.text())
            self.assertNotIn("For the set", self.ctx.text())
            await self.buy()
            self.assertEqual(self.path.read_text(), before)

    def test_lager_lore_overlay_preserves_catalogue_and_visibility(self):
        ch = {"bag": {"Triton Lager": 1}}
        item = {"name": "Triton Lager", "description": "old", "heal": 4}
        catalogue = {"Triton Lager": item}
        _, definition, _, _ = inspect_item("Triton Lager", ch, {}, catalogue)
        for word in ["blue", "non-alcoholic", "microvita", "wormhole"]:
            self.assertIn(word, definition["description"])
        self.assertEqual(definition["heal"], 4)
        self.assertEqual(item["description"], "old")
        with self.assertRaises(ValueError):
            inspect_item("Triton Lager", {"bag": {}}, {}, catalogue)

if __name__ == "__main__":
    unittest.main()
