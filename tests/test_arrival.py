"""Guided arrival uses fictional temporary storage; never connects to Discord."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
import json
from unittest.mock import patch
import test_pod_opening
from fsbot.cogs.arrival import ArrivalCog
from fsbot.cogs.core import CoreCog, build_arrival_character
from fsbot.cogs.inspection import InspectionCog
from fsbot.cogs.hud import render_panel
from fsbot.pod_opening import prepare_observation
from fsbot.pod_media import pod_image

class ArrivalTests(unittest.IsolatedAsyncioTestCase):
    setUp=test_pod_opening.PodOpeningTests.setUp
    reload=test_pod_opening.PodOpeningTests.reload
    async def act(self,text):
        if not hasattr(self,"arrival"):
            self.arrival=ArrivalCog(self.bot)
            self.ctx.guild=None
        await ArrivalCog.begin.callback(self.arrival,self.ctx,action=text)
    async def fill(self,preview=False):
        await self.act("preview" if preview else "")
        for cmd in ["class Dreamer-Technician","name Fictional Traveller","date 2000-01-01",
                    "body familiar","embodiment unfamiliar","background Music through dreams"]:
            await self.act(cmd)
    async def test_full_creation_awakens_and_inspection_persists(self):
        await self.fill()
        self.assertNotIn(str(self.ctx.author.id),self.storage.characters)
        await self.act("review");await self.act("awaken")
        uid=str(self.ctx.author.id);c=self.storage.characters[uid]
        self.assertEqual(c["extra"]["profile"]["class_id"],"dreamer_technician")
        self.assertEqual(c["extra"]["arrival"]["body_recognition"],"familiar")
        self.assertEqual(json.loads(self.path.read_text())[uid],c)
        await InspectionCog.inspect.callback(self.inspection,self.ctx,item="hands")
        self.assertIn("Yours.",self.ctx.text())
        self.assertNotIn("do not recognise",self.ctx.text())
        self.assertEqual(json.loads(self.path.read_text())[uid],self.storage.characters[uid])
    async def test_existing_character_protected_by_both_entry_points(self):
        uid=str(self.ctx.author.id);self.storage.characters[uid]={"name":"Keep","bag":{"gift":1}}
        before=deepcopy(self.storage.characters)
        await self.act("")
        await CoreCog.create_character.callback(self.core,self.ctx,"Replace","2000-01-01","dreamer_technician")
        self.assertEqual(before,self.storage.characters)
    async def test_preview_can_inspect_without_touching_saved_character(self):
        uid=str(self.ctx.author.id);self.storage.characters[uid]={"name":"Keep","bag":{"gift":1}}
        before=deepcopy(self.storage.characters);disk=self.path.read_text()
        await self.fill(preview=True);await self.act("review");await self.act("awaken")
        await self.act("inspect hands")
        self.assertIn("Yours.",self.ctx.text())
        self.assertEqual(self.storage.characters,before);self.assertEqual(self.path.read_text(),disk)
    async def test_review_required_and_edit_invalidates_it(self):
        await self.fill();await self.act("awaken")
        self.assertNotIn(str(self.ctx.author.id),self.storage.characters)
        await self.act("review");await self.act("name Changed");await self.act("awaken")
        self.assertNotIn(str(self.ctx.author.id),self.storage.characters)
    async def test_save_failure_retains_draft_and_retry_creates_once(self):
        await self.fill();await self.act("review")
        self.storage.fail_next=True;await self.act("awaken")
        uid=str(self.ctx.author.id)
        self.assertNotIn(uid,self.storage.characters);self.assertIn(uid,self.arrival.drafts)
        await self.act("awaken");before=deepcopy(self.storage.characters[uid])
        await self.act("awaken")
        self.assertEqual(self.storage.characters[uid],before)
    async def test_server_prompt_does_not_capture_draft(self):
        self.arrival=ArrivalCog(self.bot);self.ctx.guild=object()
        await self.act("name Never store")
        self.assertFalse(self.arrival.drafts)
        self.assertIn("direct message",self.ctx.text())
    async def test_invalid_values_and_cancel(self):
        await self.act("")
        for action in ["class unwritten","date invalid","body maybe","embodiment maybe","name "]:
            await self.act(action)
        self.assertEqual(self.arrival.drafts[str(self.ctx.author.id)],{"preview":False})
        await self.act("cancel");self.assertFalse(self.arrival.drafts)
    async def test_generic_arrival_has_no_unearned_booking_or_art(self):
        await self.fill();await self.act("review");await self.act("awaken")
        c=self.storage.characters[str(self.ctx.author.id)]
        for target in ["panels","display","booking"]:
            c,view=prepare_observation(c,target)
            self.assertNotIn("TOMORROW NIGHT",view[1])
        self.assertNotIn("booking",c["extra"]["arrival"]["opening"]["discoveries"])
        self.assertIsNone(pod_image(c,"display"))
        self.assertIsNone(pod_image(c,"panels"))
        panel=render_panel(c,explicit=True)
        self.assertNotIn("Unread notice",[f.name for f in panel.fields])
    def test_builder_matches_existing_derived_baseline(self):
        from fsbot.cogs.core import base_stats_for_class,hp_from_stats
        with patch("fsbot.cogs.core.ASTRO_OK",False):
            c=build_arrival_character("fiction","Fiction","2000-01-01","dreamer_technician","note",self.storage.items_db)
        expected=base_stats_for_class("dreamer_technician")
        self.assertEqual(c["stats"]["strength"],expected["strength"])
        self.assertEqual(c["stats"]["max_hp"],hp_from_stats(expected))
        self.assertEqual(c["bag"],{"itm_rusty_knife":1,"itm_leather_jacket":1})
    async def test_real_parser_accepts_multiword_background(self):
        import discord
        from discord.ext import commands
        from discord.ext.commands.view import StringView
        bot=commands.Bot(command_prefix="!",intents=discord.Intents.none())
        bot.storage=self.storage
        cog=ArrivalCog(bot);await bot.add_cog(cog)
        try:
            self.ctx.guild=None
            await ArrivalCog.begin.callback(cog,self.ctx)
            cmd=bot.get_command("begin")
            message=SimpleNamespace(_state=SimpleNamespace(),attachments=[],author=self.ctx.author,channel=self.ctx.channel)
            ctx=commands.Context(message=message,bot=bot,view=StringView("background Music in dreams"),prefix="!",command=cmd)
            ctx.send=self.ctx.send
            await cmd._parse_arguments(ctx);await cmd.callback(*ctx.args,**ctx.kwargs)
            self.assertEqual(cog.drafts[str(self.ctx.author.id)]["origin_note"],"Music in dreams")
        finally: await bot.close()
