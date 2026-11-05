"""Inspection HTTP and Discord adapters share durable knowledge; fictional players only."""
import unittest
from copy import deepcopy
from types import SimpleNamespace
import test_web_walking as walking_fixture
from fsbot.web_portal import ORIGIN
from fsbot.pod_opening import OPENING, opening_state
from fsbot.pod_inspection import inspect_pod
from fsbot.cogs.inspection import InspectionCog

class WebInspectionTests(unittest.IsolatedAsyncioTestCase):
    start = walking_fixture.WebWalkingTests.start
    complete = walking_fixture.WebWalkingTests.complete
    sign_in = walking_fixture.WebWalkingTests.sign_in
    auth = walking_fixture.WebWalkingTests.auth
    offer = walking_fixture.WebWalkingTests.offer
    asyncTearDown = walking_fixture.WebWalkingTests.asyncTearDown

    async def asyncSetUp(self):
        await walking_fixture.WebWalkingTests.asyncSetUp(self)
        ch = self.bot.storage.characters["123"]
        ch["current_room"] = "pod_room"
        ch.setdefault("extra", {})["arrival"] = {"opening":{"id":OPENING,"discoveries":[]}}
        self.bot.storage.rooms["pod_room"] = {"title":"Pod","exits":{}}
        self.bot.storage.items_db = {}

    async def inspect(self, offer, target="panels", token=None, extra=None, headers=None):
        h = {**self.auth(token or self.token), "Origin":ORIGIN,
             "X-CSRF-Token":offer["session"]["csrf"]}
        h.update(headers or {})
        return await self.client.post("/play/api/inspect",headers=h,
            json={"target":target,"token":offer["inspection"]["token"],**(extra or {})})

    async def test_read_is_passive_and_sequence_is_shared_with_discord(self):
        before=deepcopy(self.bot.storage.characters)
        offer=await self.offer()
        self.assertEqual(offer["inspection"]["targets"],["panels"])
        self.assertEqual(self.saved,[])
        self.assertEqual(before,self.bot.storage.characters)
        r=await self.inspect(offer)
        self.assertEqual(r.status,200)
        self.assertEqual((await r.json())["observation"]["title"],"The side wall")
        messages=[]
        async def send(*args,**kwargs): messages.append(kwargs)
        cog=InspectionCog(self.bot)
        ctx=SimpleNamespace(author=SimpleNamespace(id=123),send=send)
        self.assertTrue(await cog._pod_view(ctx,"display"))
        self.assertEqual(messages[-1]["embed"].title,"Signal and notification")
        r=await self.inspect(await self.offer(),"booking")
        self.assertEqual(r.status,200)
        self.assertIn("booking",opening_state(self.bot.storage.characters["123"])["discoveries"])
        saves=len(self.saved)
        self.assertTrue(await cog._pod_view(ctx,"booking"))
        self.assertEqual(len(self.saved),saves)
        self.assertEqual(messages[-1]["embed"].title,"Tomorrow night")
        self.assertIsNone(inspect_pod(self.bot.storage,"123","display")["image"])

    async def test_unknown_hidden_target_and_identity_rejected(self):
        offer=await self.offer()
        for target in ["booking","wardrobe","__dict__"]:
            self.assertEqual((await self.inspect(offer,target)).status,400)
        self.assertEqual((await self.inspect(offer,extra={"user_id":"456"})).status,400)
        self.assertEqual(self.saved,[])

    async def test_token_single_use_and_two_sessions_invalidate_on_discovery(self):
        second=await self.sign_in()
        a,b=await self.offer(),await self.offer(second)
        self.assertEqual((await self.inspect(a)).status,200)
        self.assertEqual((await self.inspect(a)).status,409)
        self.assertEqual((await self.inspect(b,token=second)).status,409)
        self.assertEqual(len(self.saved),1)

    async def test_security_rejections_and_expired_offer(self):
        self.assertEqual((await self.client.post("/play/api/inspect",json={})).status,401)
        offer=await self.offer()
        for headers in [{"Origin":"https://evil.example"},{"X-CSRF-Token":"wrong"}]:
            self.assertEqual((await self.inspect(offer,headers=headers)).status,403)
        self.now+=121
        self.assertEqual((await self.inspect(offer)).status,409)
        self.assertEqual(self.saved,[])

    async def test_room_change_and_walk_revision_reject_old_intent(self):
        offer=await self.offer()
        self.bot.storage.characters["123"]["current_room"]="a"
        self.assertEqual((await self.inspect(offer)).status,409)
        self.bot.storage.characters["123"]["current_room"]="pod_room"
        offer=await self.offer()
        self.nav.walk_revisions["123"]=1
        self.assertEqual((await self.inspect(offer)).status,409)
        self.assertEqual(self.saved,[])

    async def test_discord_discovery_invalidates_web_offer(self):
        offer=await self.offer()
        inspect_pod(self.bot.storage,"123","panels")
        self.assertEqual((await self.inspect(offer)).status,409)
        self.assertIn("booking",(await self.offer())["inspection"]["targets"])

    async def test_no_opening_and_no_booking_do_not_invent_story(self):
        ch=self.bot.storage.characters["123"]
        del ch["extra"]["arrival"]
        self.assertEqual((await self.offer())["inspection"]["targets"],[])
        ch["extra"]["arrival"]={"opening":{"id":OPENING,"discoveries":["panels"]},"performance_booking":False}
        self.assertEqual((await self.offer())["inspection"]["targets"],["panels","display","wardrobe"])
        result=inspect_pod(self.bot.storage,"123","display")
        self.assertNotIn("booking",result["text"].lower())
        self.assertIsNone(result["image"])

    async def test_failed_save_rolls_back_and_does_not_leak_error(self):
        before=deepcopy(self.bot.storage.characters)
        offer=await self.offer()
        def fail(): raise OSError("PRIVATE PATH")
        self.bot.storage.save_characters=fail
        r=await self.inspect(offer)
        self.assertEqual(r.status,503)
        self.assertNotIn("PRIVATE",await r.text())
        self.assertEqual(before,self.bot.storage.characters)

    async def test_repeat_authored_observation_and_equipped_garment(self):
        first=inspect_pod(self.bot.storage,"123","brochure")
        again=inspect_pod(self.bot.storage,"123","brochure")
        self.assertIn("metallic crash",first["text"])
        self.assertNotIn("metallic crash",again["text"])
        self.bot.storage.characters["123"]["equipped"]={"chest":"outfit"}
        self.bot.storage.items_db["outfit"]={"name":"Freeform Attire"}
        self.assertEqual(inspect_pod(self.bot.storage,"123","garment")["title"],"Freeform Attire")

    async def test_movement_in_progress_blocks_inspection(self):
        offer=await self.offer()
        self.nav.walking.add("123")
        self.assertEqual((await self.inspect(offer)).status,409)
        self.assertEqual((await self.offer())["inspection"]["targets"],[])
        self.assertEqual(self.saved,[])

    async def test_recovery_and_cube_restrict_both_adapters(self):
        offer=await self.offer()
        ch=self.bot.storage.characters["123"]
        ch["extra"]["recovery"]={"stage":"reanimating"}
        self.assertEqual((await self.inspect(offer)).status,409)
        self.assertEqual((await self.offer())["inspection"]["targets"],[])
        with self.assertRaisesRegex(ValueError,"recovery"):
            inspect_pod(self.bot.storage,"123","panels")
        del ch["extra"]["recovery"]
        ch["in_cube"]=True
        self.assertEqual((await self.offer())["inspection"]["targets"],[])
        self.assertEqual(self.saved,[])

    async def test_attention_touches_idle_but_passive_reads_do_not(self):
        touched=[]
        self.cogs["IdleHomeCog"]=SimpleNamespace(observe=lambda uid:touched.append(uid),suspended=set())
        offer=await self.offer()
        await self.offer()
        self.assertEqual(touched,[])
        self.assertEqual((await self.inspect(offer)).status,200)
        self.assertEqual(touched,["123"])

    async def test_idle_save_failure_blocks_discovery(self):
        self.cogs["IdleHomeCog"]=SimpleNamespace(observe=lambda uid:None,suspended={"123"})
        offer=await self.offer()
        self.assertEqual((await self.inspect(offer)).status,503)
        self.assertEqual(opening_state(self.bot.storage.characters["123"])["discoveries"],[])
