"""Real HTTP-to-shared-navigation tests with fictional OAuth and character data."""
import unittest
from copy import deepcopy
import aiohttp
from aiohttp.test_utils import TestClient, TestServer
import test_web_portal as auth_fixture
from test_shared_walking import fixture
from fsbot.web_portal import create_app, WebConfig, ORIGIN, SESSION_COOKIE


class WebWalkingTests(unittest.IsolatedAsyncioTestCase):
    start = auth_fixture.WebPortalTests.start
    complete = auth_fixture.WebPortalTests.complete
    sign_in = auth_fixture.WebPortalTests.sign_in
    auth = auth_fixture.WebPortalTests.auth

    async def asyncSetUp(self):
        self.bot, self.nav, self.cogs, self.saved = fixture()
        self.now = 100
        self.oauth = auth_fixture.FakeOAuth()
        self.config = WebConfig("1348670557314482267", "fictional", frozenset({"123"}))
        self.client = TestClient(TestServer(create_app(
            self.bot, self.config, oauth=self.oauth, clock=lambda: self.now)),
            cookie_jar=aiohttp.DummyCookieJar())
        await self.client.start_server()
        self.token = await self.sign_in()

    async def asyncTearDown(self):
        await self.client.close()

    async def offer(self, token=None):
        r = await self.client.get("/play/api/me", headers=self.auth(token or self.token))
        self.assertEqual(r.status, 200)
        return await r.json()

    async def move(self, offer, direction="east", token=None, extra=None, headers=None):
        h = {**self.auth(token or self.token), "Origin": ORIGIN,
             "X-CSRF-Token": offer["session"]["csrf"]}
        if headers:
            h.update(headers)
        return await self.client.post("/play/api/walk", headers=h,
            json={"direction": direction, "token": offer["walking"]["token"], **(extra or {})})

    async def test_http_moves_shared_state_and_repeat_cannot_move_again(self):
        offer = await self.offer()
        self.assertEqual(offer["walking"]["exits"], ["east"])
        self.assertEqual(offer["location"]["description"], "Room A")
        r = await self.move(offer)
        self.assertEqual(r.status, 200)
        self.assertEqual(self.bot.storage.characters["123"]["current_room"], "b")
        r = await self.move(offer)
        self.assertEqual(r.status, 409)
        self.assertEqual(len(self.saved), 1)

    async def test_discord_style_shared_move_invalidates_web_offer(self):
        offer = await self.offer()
        await self.nav.walk("123", "east")
        r = await self.move(offer)
        self.assertEqual(r.status, 409)
        self.assertEqual(len(self.saved), 1)
        fresh = await self.offer()
        self.assertEqual(fresh["location"]["id"], "b")
        self.assertEqual((await self.move(fresh, "west")).status, 200)
        self.assertEqual(self.bot.storage.characters["123"]["current_room"], "a")

    async def test_anonymous_origin_and_csrf_fail_without_mutation(self):
        r = await self.client.post("/play/api/walk", json={})
        self.assertEqual(r.status, 401)
        offer = await self.offer()
        for h in ({"Origin": "https://evil.example"}, {"Origin": ""},
                  {"X-CSRF-Token": "wrong"}):
            self.assertEqual((await self.move(offer, headers=h)).status, 403)
        self.assertEqual(self.saved, [])

    async def test_identity_and_destination_cannot_be_supplied(self):
        offer = await self.offer()
        self.assertEqual((await self.move(offer, extra={"user_id": "456"})).status, 400)
        self.assertEqual((await self.move(offer, extra={"destination": "c"})).status, 400)
        self.assertEqual((await self.move(offer, direction="north")).status, 400)
        self.assertEqual(self.saved, [])

    async def test_two_sessions_share_stale_location_protection(self):
        second = await self.sign_in()
        first_offer, second_offer = await self.offer(), await self.offer(second)
        self.assertEqual((await self.move(first_offer)).status, 200)
        self.assertEqual((await self.move(second_offer, token=second)).status, 409)
        self.assertEqual(len(self.saved), 1)

    async def test_expired_offer_and_logged_out_session_fail(self):
        offer = await self.offer()
        self.now += 121
        self.assertEqual((await self.move(offer)).status, 409)
        offer = await self.offer()
        r = await self.client.post("/play/logout", headers={
            **self.auth(self.token), "Origin": ORIGIN,
            "X-CSRF-Token": offer["session"]["csrf"]})
        self.assertEqual(r.status, 204)
        self.assertEqual((await self.move(offer)).status, 401)
        self.assertEqual(self.saved, [])

    async def test_passive_view_does_not_save_or_change_character(self):
        before = deepcopy(self.bot.storage.characters)
        await self.offer()
        await self.offer()
        self.assertEqual(self.bot.storage.characters, before)
        self.assertEqual(self.saved, [])

    async def test_choice_after_offer_refuses_and_new_offer_has_no_exits(self):
        offer = await self.offer()
        self.bot.storage.characters["123"]["extra"]["thread_nodes"] = {"active_thread_node": "choice"}
        self.assertEqual((await self.move(offer)).status, 409)
        self.assertEqual((await self.offer())["walking"]["exits"], [])
        self.assertEqual(self.saved, [])

    async def test_save_failure_consumes_offer_but_keeps_location(self):
        offer = await self.offer()
        def fail():
            raise OSError("private detail must not reach HTTP")
        self.bot.storage.save_characters = fail
        r = await self.move(offer)
        self.assertEqual(r.status, 503)
        self.assertNotIn("private detail", await r.text())
        self.assertEqual(self.bot.storage.characters["123"]["current_room"], "a")
        self.assertEqual((await self.move(offer)).status, 409)

    async def test_readiness_and_removed_owner_are_rechecked_on_post(self):
        offer = await self.offer()
        self.bot.is_ready = lambda: False
        self.assertEqual((await self.move(offer)).status, 503)
        self.bot.is_ready = lambda: True
        del self.bot.storage.characters["123"]
        self.assertEqual((await self.move(offer)).status, 403)
        self.assertEqual(self.saved, [])
