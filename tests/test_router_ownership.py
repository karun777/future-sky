"""Fictional Discord surfaces: no API calls, channels or messages."""
import asyncio
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, Mock, patch
import discord
from fsbot.cogs import router
from fsbot.cogs.speech import SpeechCog


class Member:
    def __init__(self, ident, bot=False):
        self.id, self.bot = ident, bot
        self.guild_permissions = NS(administrator=False)
        self.send = AsyncMock()


class Role:
    def __init__(self, ident, admin=False):
        self.id = ident
        self.permissions = NS(administrator=admin)


class Category:
    def __init__(self):
        self.id = 99
        self.channels = []


class Channel:
    def __init__(self, guild, ident, name, overwrites):
        self.guild, self.id, self.name = guild, ident, name
        self.category_id = guild.category.id
        self.overwrites = overwrites
        self.send = AsyncMock()

    def overwrites_for(self, target):
        return self.overwrites.get(target, discord.PermissionOverwrite())

    def permissions_for(self, member):
        return NS(view_channel=(member.guild_permissions.administrator
                  or getattr(self.guild, "owner_id", None) == member.id
                  or self.overwrites_for(member).view_channel is True))


class RouterOwnershipTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        for name, fake in (("Member", Member), ("Role", Role),
                           ("TextChannel", Channel), ("CategoryChannel", Category)):
            patcher = patch.object(router.discord, name, fake)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(router, "_players_category_id", return_value=99)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.seed = AsyncMock()
        patcher = patch.object(router, "_seed_run_channel_once", self.seed)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.a, self.b, self.robot = Member(101), Member(202), Member(303, bot=True)
        self.category = Category()
        self.guild = NS(id=9, default_role=Role(9), me=self.robot, category=self.category)
        self.guild.get_member = lambda uid: {101:self.a, 202:self.b, 303:self.robot}.get(uid)
        self.guild.get_channel = lambda cid: self.category if cid == 99 else next(
            (ch for ch in self.category.channels if ch.id == cid), None)
        self.guild.create_text_channel = AsyncMock(side_effect=self.create)
        self.storage = NS(characters={"101":{"name":"Same"}, "202":{"name":"Same"}},
                          save_characters=Mock())
        self.bot = NS(storage=self.storage)
        self.ctx = NS(guild=self.guild, author=self.a)

    async def create(self, *, name, category, overwrites, reason):
        await asyncio.sleep(0)
        ch = Channel(self.guild, 400+len(category.channels), name, overwrites)
        category.channels.append(ch)
        return ch

    def existing(self, owner, ident=500, name="fs-old-name"):
        ch = Channel(self.guild, ident, name, {
            self.guild.default_role:discord.PermissionOverwrite(view_channel=False),
            owner:discord.PermissionOverwrite(view_channel=True),
            self.robot:discord.PermissionOverwrite(view_channel=True)})
        self.category.channels.append(ch)
        return ch

    async def ensure(self, uid="202", name="Same"):
        return await router.ensure_player_run_channel(self.bot,self.ctx,uid,name)

    async def test_saved_channel_allows_admin_operator_grant(self):
        ch = self.existing(self.b)
        self.storage.characters["202"]["run_channel_id"] = str(ch.id)
        self.a.guild_permissions.administrator = True
        ch.overwrites[self.a] = discord.PermissionOverwrite(view_channel=True)
        self.assertIs(ch, await self.ensure())
        self.assertIs(ch, await router.get_run_channel_by_guild_if_any(self.bot,self.guild,"202"))

    async def test_saved_channel_allows_guild_owner_operator_grant(self):
        ch = self.existing(self.b)
        self.storage.characters["202"]["run_channel_id"] = str(ch.id)
        self.guild.owner_id = self.a.id
        ch.overwrites[self.a] = discord.PermissionOverwrite(view_channel=True)
        self.assertIs(ch, await self.ensure())

    async def test_saved_admin_recipient_needs_no_individual_grant(self):
        ch = self.existing(self.robot)
        self.storage.characters["202"]["run_channel_id"] = str(ch.id)
        self.b.guild_permissions.administrator = True
        self.assertIs(ch, await self.ensure())

    async def test_admin_access_alone_never_adopts_channel(self):
        other = self.existing(self.a)
        self.b.guild_permissions.administrator = True
        result = await self.ensure()
        self.assertIsNot(other, result)
        self.assertEqual(2, len(self.category.channels))

    async def test_developer_label_does_not_grant_access(self):
        ch = self.existing(self.a)
        self.guild.owner_id = self.a.id
        self.b.roles = [NS(name="DPC")]
        self.storage.characters["202"]["run_channel_id"] = str(ch.id)
        self.assertIsNone(await self.ensure())
        self.guild.create_text_channel.assert_not_awaited()

    async def test_saved_nonadmin_visitor_still_refused(self):
        ch = self.existing(self.b)
        self.storage.characters["202"]["run_channel_id"] = str(ch.id)
        ch.overwrites[self.a] = discord.PermissionOverwrite(view_channel=True)
        self.assertIsNone(await self.ensure())

    async def test_admin_cannot_override_conflicting_saved_claim(self):
        ch = self.existing(self.b)
        self.b.guild_permissions.administrator = True
        for record in self.storage.characters.values():
            record["run_channel_id"] = str(ch.id)
        self.assertIsNone(await self.ensure())

    async def test_broadcast_creation_grants_recipient_not_speaker(self):
        ch = await self.ensure()
        self.assertIs(ch.overwrites_for(self.b).view_channel, True)
        self.assertIsNone(ch.overwrites_for(self.a).view_channel)
        self.assertEqual(str(ch.id),self.storage.characters["202"]["run_channel_id"])

    async def test_same_name_does_not_adopt_other_players_channel(self):
        other = self.existing(self.a, name="fs-same")
        ch = await self.ensure()
        self.assertIsNot(other,ch)
        self.assertEqual(2,len(self.category.channels))

    async def test_reset_and_rename_reattach_by_owner_permissions(self):
        old = self.existing(self.b)
        old.send.reset_mock()
        self.assertIs(old,await self.ensure(name="New life"))
        self.guild.create_text_channel.assert_not_awaited()
        old.send.assert_not_awaited()

    async def test_wrong_saved_owner_blocks_lookup_and_creation(self):
        other = self.existing(self.a)
        self.storage.characters["202"]["run_channel_id"]=str(other.id)
        self.assertIsNone(await self.ensure())
        self.assertIsNone(await router.get_run_channel_by_guild_if_any(self.bot,self.guild,"202"))
        self.guild.create_text_channel.assert_not_awaited()
        self.seed.assert_not_awaited()

    async def test_duplicate_claim_blocks_adoption(self):
        ch = self.existing(self.b)
        self.storage.characters["101"]["run_channel_id"]=str(ch.id)
        self.assertIsNone(await self.ensure())
        self.guild.create_text_channel.assert_not_awaited()

    async def test_ambiguous_channels_block_adoption(self):
        self.existing(self.b,500)
        self.existing(self.b,501)
        self.assertIsNone(await self.ensure())
        self.guild.create_text_channel.assert_not_awaited()

    async def test_extra_human_grant_is_not_owner_proof(self):
        ch = self.existing(self.a)
        ch.overwrites[self.b]=discord.PermissionOverwrite(view_channel=True)
        self.assertIsNone(await self.ensure())

    async def test_public_or_role_visible_channel_refused(self):
        ch = self.existing(self.b)
        self.storage.characters["202"]["run_channel_id"]=str(ch.id)
        ch.overwrites[self.guild.default_role]=discord.PermissionOverwrite(view_channel=True)
        self.assertIsNone(await self.ensure())
        ch.overwrites[self.guild.default_role]=discord.PermissionOverwrite(view_channel=False)
        ch.overwrites[Role(77)]=discord.PermissionOverwrite(view_channel=True)
        self.assertIsNone(await self.ensure())

    async def test_wrong_category_and_guild_refused(self):
        ch=self.existing(self.b)
        self.storage.characters["202"]["run_channel_id"]=str(ch.id)
        ch.category_id=88
        self.assertIsNone(await self.ensure())
        ch.category_id=99
        ch.guild=NS(id=8)
        self.assertIsNone(await self.ensure())

    async def test_missing_category_preserves_verified_saved_route_only(self):
        ch=self.existing(self.b)
        self.storage.characters["202"]["run_channel_id"]=str(ch.id)
        with patch.object(router,"_players_category_id",return_value=0):
            self.assertIs(ch,await self.ensure())
            self.assertIs(ch,await router.get_run_channel_by_guild_if_any(self.bot,self.guild,"202"))
            del self.storage.characters["202"]["run_channel_id"]
            self.assertIsNone(await self.ensure())
            self.guild.create_text_channel.assert_not_awaited()

    async def test_missing_member_or_character_never_creates(self):
        self.guild.get_member=lambda uid: None
        self.assertIsNone(await self.ensure())
        self.guild.create_text_channel.assert_not_awaited()
        self.assertIsNone(await self.ensure(uid="404"))

    async def test_failed_save_retains_no_mapping_and_retries_same_channel(self):
        self.storage.save_characters.side_effect=OSError("full")
        self.assertIsNone(await self.ensure())
        self.assertNotIn("run_channel_id",self.storage.characters["202"])
        self.seed.assert_not_awaited()
        self.storage.save_characters.side_effect=None
        ch=await self.ensure()
        self.assertEqual(1,len(self.category.channels))
        self.assertIs(ch,self.category.channels[0])

    async def test_concurrent_delivery_creates_one_channel(self):
        results=await asyncio.gather(self.ensure(),self.ensure())
        self.assertIs(results[0],results[1])
        self.guild.create_text_channel.assert_awaited_once()

    async def test_speech_still_delivers_into_each_recipient_space(self):
        cog=SpeechCog(self.bot)
        await cog._send_to_player_run(self.ctx,"101",self.storage.characters["101"],"shared scene")
        await cog._send_to_player_run(self.ctx,"202",self.storage.characters["202"],"shared scene")
        self.assertEqual(2,len(self.category.channels))
        for uid in ("101","202"):
            ch=await router.get_run_channel_by_guild_if_any(self.bot,self.guild,uid)
            ch.send.assert_awaited_once_with("shared scene")

    async def test_say_keeps_room_and_cube_audience_boundaries(self):
        self.storage.characters["404"]={"name":"Elsewhere"}
        self.storage.characters["505"]={"name":"In cube","in_cube":True}
        rooms={"101":"lounge","202":"lounge","404":"dock","505":"lounge"}
        self.bot.state=NS(ensure_player_records=lambda uid:None,
                          resolve_room_for_user=lambda uid:rooms[uid])
        self.ctx.author.display_name="Speaker"
        await SpeechCog.say.callback(SpeechCog(self.bot),self.ctx,message="Hello room")
        self.assertEqual(2,len(self.category.channels))
        for uid in ("101","202"):
            ch=await router.get_run_channel_by_guild_if_any(self.bot,self.guild,uid)
            ch.send.assert_awaited_once()
            self.assertIn("Hello room",ch.send.await_args.args[0])
        self.assertNotIn("run_channel_id",self.storage.characters["404"])
        self.assertNotIn("run_channel_id",self.storage.characters["505"])

    async def test_background_delivery_refuses_foreign_channel(self):
        other=self.existing(self.a)
        self.storage.characters["202"]["run_channel_id"]=str(other.id)
        self.assertFalse(await router.send_to_player_run_channel_if_any(
            self.bot,self.guild,"202","private"))
        other.send.assert_not_awaited()

    async def test_private_output_falls_back_to_own_dm_not_public_channel(self):
        ctx=NS(guild=self.guild, author=self.a,bot=self.bot,channel=NS(id=1),
               command=NS(qualified_name="inventory"))
        with patch.object(router,"get_run_channel_by_guild_if_any",AsyncMock(return_value=None)), \
             patch.object(router,"ensure_player_run_channel",AsyncMock(return_value=None)), \
             patch.object(router.commands.Context,"send",AsyncMock()) as public:
            await router.RunRoutedContext.send(ctx,"private inventory")
            self.a.send.assert_awaited_once_with(content="private inventory")
            public.assert_not_awaited()
            self.a.send.side_effect=RuntimeError("DM closed")
            await router.RunRoutedContext.send(ctx,"private inventory")
            public.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
