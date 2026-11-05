"""Fictional HTTP wardrobe checks: no production players or OAuth."""
import unittest
from copy import deepcopy
from types import SimpleNamespace
import test_web_inspection as fixture
from fsbot.cogs.core import CoreCog
from fsbot.cogs.wardrobe import WardrobeCog, load_catalogue
from fsbot.pod_opening import opening_state
from fsbot.web_portal import ORIGIN

class WebWardrobeTests(unittest.IsolatedAsyncioTestCase):
    start = fixture.WebInspectionTests.start
    complete = fixture.WebInspectionTests.complete
    sign_in = fixture.WebInspectionTests.sign_in
    auth = fixture.WebInspectionTests.auth
    offer = fixture.WebInspectionTests.offer
    inspect = fixture.WebInspectionTests.inspect
    asyncTearDown = fixture.WebInspectionTests.asyncTearDown

    async def asyncSetUp(self):
        await fixture.WebInspectionTests.asyncSetUp(self)
        self.core = CoreCog(self.bot)
        self.cogs["CoreCog"] = self.core
        for o in load_catalogue()["uniforms"]:
            self.bot.storage.items_db[o["item_id"]] = {
                "name":o["name"],"type":"equipment",
                "equip":{"allowed_slots":["chest"]}}
        self.bot.storage.items_db["coat"] = {
            "name":"Coat","description":"A carried coat.","type":"equipment",
            "equip":{"allowed_slots":["chest"]}}
        self.bot.storage.characters["123"]["bag"] = {"coat":1}

    async def open(self):
        self.assertEqual((await self.inspect(await self.offer(),"panels")).status,200)
        self.assertEqual((await self.inspect(await self.offer(),"wardrobe")).status,200)
        return await self.offer()

    async def act(self,offer,action="select:pod_freeform",token=None,headers=None,extra=None):
        return await self.client.post("/play/api/wardrobe",headers={
            **self.auth(token or self.token),"Origin":ORIGIN,
            "X-CSRF-Token":offer["session"]["csrf"],**(headers or {})},
            json={"action":action,"token":offer["wardrobe"]["token"],**(extra or {})})

    async def test_discovery_then_first_selection_and_discord_fit(self):
        before=deepcopy(self.bot.storage.characters)
        self.assertFalse((await self.offer())["wardrobe"]["available"])
        self.assertEqual(before,self.bot.storage.characters)
        offer=await self.open()
        saves=len(self.saved)
        await self.offer()
        self.assertEqual(len(self.saved),saves)
        self.assertTrue(offer["wardrobe"]["first_selection"])
        self.assertEqual((await self.act(offer)).status,200)
        ch=self.bot.storage.characters["123"]
        self.assertEqual(ch["equipped"]["chest"],"itm_pod_uniform_freeform")
        messages=[]
        async def send(*a,**kw): messages.append(kw)
        await WardrobeCog.fit.callback(WardrobeCog(self.bot),
            SimpleNamespace(author=SimpleNamespace(id=123),send=send))
        self.assertEqual(messages[-1]["embed"].fields[0].value,"Freeform Attire")
        self.assertFalse((await self.offer())["wardrobe"]["first_selection"])
        self.assertEqual((await self.act(await self.offer(),"select:pod_formal")).status,400)

    async def test_carried_clothes_use_core_and_keep_quantity(self):
        await self.act(await self.open())
        offer=await self.offer()
        self.assertEqual((await self.act(offer,"wear:coat")).status,200)
        ch=self.bot.storage.characters["123"]
        self.assertEqual(ch["equipped"]["chest"],"coat")
        self.assertNotIn("coat",ch["bag"])
        self.assertEqual(ch["bag"]["itm_pod_uniform_freeform"],1)
        self.assertEqual((await self.act(offer,"wear:coat")).status,409)

    async def test_two_sessions_and_discord_change_invalidate_old_offer(self):
        await self.open()
        second=await self.sign_in()
        a,b=await self.offer(),await self.offer(second)
        self.assertEqual((await self.act(a)).status,200)
        self.assertEqual((await self.act(b,token=second)).status,409)
        old=await self.offer()
        self.core.equip_item("123","coat","chest")
        self.assertEqual((await self.act(old,"wear:coat")).status,409)

    async def test_security_and_expiry(self):
        self.assertEqual((await self.client.post("/play/api/wardrobe",json={})).status,401)
        offer=await self.open()
        for headers in [{"Origin":"https://evil.example"},{"X-CSRF-Token":"wrong"}]:
            self.assertEqual((await self.act(offer,headers=headers)).status,403)
        self.assertEqual((await self.act(offer,extra={"uid":"456"})).status,400)
        self.assertEqual((await self.act(offer,"wear:unowned")).status,400)
        self.now+=121
        self.assertEqual((await self.act(offer)).status,409)

    async def test_recovery_room_combat_and_choice_refuse_stale_action(self):
        await self.open()
        for mode in ["room","recovery","combat","choice","walking"]:
            original=deepcopy(self.bot.storage.characters["123"])
            offer=await self.offer()
            ch=self.bot.storage.characters["123"]
            if mode=="room": ch["current_room"]="a"
            elif mode=="recovery": ch["extra"]["recovery"]={"stage":"reanimating"}
            elif mode=="combat": ch["flags"]={"in_combat":True}
            elif mode=="choice": ch["extra"]["thread_nodes"]={"active_thread_node":"x"}
            else: self.nav.walking.add("123")
            self.assertEqual((await self.act(offer)).status,409,mode)
            self.bot.storage.characters["123"]=original
            self.nav.walking.discard("123")

    async def test_save_failure_restores_selection_and_equipment(self):
        offer=await self.open()
        original=deepcopy(self.bot.storage.characters)
        def fail(): raise OSError("secret path")
        self.bot.storage.save_characters=fail
        r=await self.act(offer)
        self.assertEqual(r.status,409)
        self.assertNotIn("secret path",await r.text())
        self.assertEqual(original,self.bot.storage.characters)
        r=await self.act(await self.offer(),"wear:coat")
        self.assertEqual(r.status,409)
        self.assertEqual(original,self.bot.storage.characters)

    async def test_discord_first_selection_uses_same_persistence(self):
        await self.open()
        offer=await self.offer()
        async def send(*a,**kw): pass
        await WardrobeCog.uniform.callback(WardrobeCog(self.bot),
            SimpleNamespace(author=SimpleNamespace(id=123),send=send),choice="formal")
        self.assertEqual((await self.act(offer)).status,409)
        self.assertEqual((await self.offer())["wardrobe"]["fit"],"Formal Uniform")
