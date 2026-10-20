"""W4-F7: real callbacks with fictional temporary character storage."""
from copy import deepcopy
import unittest
from unittest.mock import Mock
import test_display
from fsbot.cogs.core import CoreCog
from fsbot.cogs.wardrobe import WardrobeCog
from fsbot.dressing import resolve_clothing

class DressingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        test_display.DisplayTests.setUp(self)
        self.core=CoreCog(self.bot)
        self.wardrobe=WardrobeCog(self.bot)
        self.bot.get_cog=lambda name: self.core if name=="CoreCog" else None
        self.storage.items_db={
            "coat":{"name":"Travel Coat","type":"equipment","equip":{"allowed_slots":["chest"]}},
            "shirt":{"name":"Plain Shirt","type":"equipment","equip":{"allowed_slots":["chest"]}},
            "knife":{"name":"Knife","type":"weapon","equip":{"allowed_slots":["main_hand"]}},
        }
        self.storage.characters[self.uid]["bag"]={"coat":1,"knife":1,"keepsake":2}
        self.storage.characters[self.uid]["equipped"]={"chest":"shirt","main_hand":"knife"}
        self.storage.save_characters()
    reload=test_display.DisplayTests.reload
    def char(self):
        return self.storage.characters[self.uid]
    async def test_wear_remove_rewear_persists_and_preserves_other_possessions(self):
        other=deepcopy(self.storage.characters["other"])
        await WardrobeCog.wear.callback(self.wardrobe,self.ctx,garment="  TRAVEL coat ")
        self.assertEqual(self.char()["equipped"]["chest"],"coat")
        self.assertEqual(self.char()["bag"]["shirt"],1)
        self.assertNotIn("coat",self.char()["bag"])
        await WardrobeCog.remove.callback(self.wardrobe,self.ctx,garment="Travel Coat")
        self.assertIsNone(self.char()["equipped"]["chest"])
        self.assertEqual(self.char()["bag"]["coat"],1)
        await WardrobeCog.wear.callback(self.wardrobe,self.ctx,garment="Travel Coat")
        self.assertEqual(self.char()["bag"]["keepsake"],2)
        self.assertEqual(self.char()["equipped"]["main_hand"],"knife")
        self.assertEqual(self.storage.characters["other"],other)
        import json
        self.assertEqual(json.loads(self.path.read_text())[self.uid],self.char())
    async def test_save_failure_rolls_back_wear_and_remove_without_success_message(self):
        before=deepcopy(self.char())
        self.storage.save_characters=Mock(side_effect=OSError("fictional disk failure"))
        await WardrobeCog.wear.callback(self.wardrobe,self.ctx,garment="Travel Coat")
        self.assertEqual(self.char(),before)
        self.assertIn("could not be saved",self.ctx.text())
        self.ctx.messages.clear()
        await WardrobeCog.remove.callback(self.wardrobe,self.ctx,garment="Plain Shirt")
        self.assertEqual(self.char(),before)
        self.assertIn("could not be saved",self.ctx.text())
    async def test_unknown_or_unowned_garment_does_not_grant_anything(self):
        before=deepcopy(self.char())
        for name in ["Formal Uniform","Knife","Travel Coat trailing"]:
            await WardrobeCog.wear.callback(self.wardrobe,self.ctx,garment=name)
        self.assertEqual(self.char(),before)
    async def test_existing_requirements_are_enforced(self):
        self.storage.items_db["coat"]["equip"]["requirements"]={"stat_requirements":{"str":100}}
        before=deepcopy(self.char())
        await WardrobeCog.wear.callback(self.wardrobe,self.ctx,garment="Travel Coat")
        self.assertEqual(self.char(),before)
        self.assertIn("Requires strength",self.ctx.text())
    async def test_browse_and_inspect_are_text_only_and_nonmutating(self):
        before=deepcopy(self.char())
        await WardrobeCog.wardrobe.callback(self.wardrobe,self.ctx)
        await WardrobeCog.wardrobe.callback(self.wardrobe,self.ctx,action="inspect formal")
        self.assertEqual(self.char(),before)
        self.assertEqual(self.ctx.messages[-1]["embed"].title,"Formal Uniform")
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
    async def test_returning_player_is_not_offered_a_second_grant(self):
        self.char().setdefault("extra",{}).setdefault("arrival",{})["pod_uniform_selected"]="pod_formal"
        before=deepcopy(self.char())
        await WardrobeCog.wardrobe.callback(self.wardrobe,self.ctx)
        self.assertIn("first outfit has already",self.ctx.text())
        await WardrobeCog.uniform.callback(self.wardrobe,self.ctx,choice="utility")
        self.assertEqual(self.char(),before)
        self.assertIn("!wear",self.ctx.text())
    def test_duplicate_names_are_rejected(self):
        self.storage.items_db["coat2"]=deepcopy(self.storage.items_db["coat"])
        self.char()["bag"]["coat2"]=1
        with self.assertRaisesRegex(ValueError,"More than one"):
            resolve_clothing(self.char(),self.storage.items_db,"Travel Coat")
    async def test_fit_after_removal_is_truthful(self):
        await WardrobeCog.remove.callback(self.wardrobe,self.ctx,garment="Plain Shirt")
        await WardrobeCog.fit.callback(self.wardrobe,self.ctx)
        self.assertIn("No chest garment",self.ctx.text())

    async def test_multiword_names_and_trailing_input_through_real_parser(self):
        import discord
        from discord.ext import commands
        from discord.ext.commands.view import StringView
        from types import SimpleNamespace
        bot=commands.Bot(command_prefix="!", intents=discord.Intents.none())
        bot.storage=self.storage
        await bot.add_cog(CoreCog(bot))
        await bot.add_cog(WardrobeCog(bot))
        try:
            for command_name, argument in [("wear","Travel Coat"),("remove","Travel Coat")]:
                cmd=bot.get_command(command_name)
                message=SimpleNamespace(_state=SimpleNamespace(), attachments=[],author=self.ctx.author,channel=self.ctx.channel)
                context=commands.Context(message=message,bot=bot,view=StringView(argument),prefix="!",command=cmd)
                context.send=self.ctx.send
                await cmd._parse_arguments(context)
                await cmd.callback(*context.args,**context.kwargs)
            self.assertIsNone(self.char()["equipped"]["chest"])
            self.assertEqual(self.char()["bag"]["coat"],1)
        finally:
            await bot.close()

    def test_new_commands_route_to_run_channel(self):
        from types import SimpleNamespace
        from fsbot.cogs.router import _should_route_ctx
        for name in ["wear","remove","wardrobe"]:
            self.assertTrue(_should_route_ctx(SimpleNamespace(command=SimpleNamespace(qualified_name=name))))
