"""HTTP security tests with fictional accounts; no Discord traffic or game writes."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from urllib.parse import urlsplit, parse_qs

import aiohttp
from aiohttp.test_utils import TestClient, TestServer
from fsbot.web_portal import (
    create_app, WebConfig, DiscordOAuth, ORIGIN, CALLBACK,
    LOGIN_COOKIE, SESSION_COOKIE, SESSION_SECONDS, PENDING_SECONDS)


class FakeOAuth:
    def __init__(self):
        self.uid = "123"
        self.calls = 0
        self.fail = False

    async def authorize(self):
        return "https://discord.com/oauth2/authorize?state=test-state", "test-state"

    async def identity(self, code, state):
        self.calls += 1
        if self.fail:
            raise RuntimeError("SECRET MUST NOT LEAK")
        return self.uid


class WebPortalTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.now = 100.0
        self.oauth = FakeOAuth()
        self.config = WebConfig("1348670557314482267", "fictional-secret", frozenset({"123"}))
        self.bot = SimpleNamespace(
            storage=SimpleNamespace(
                characters={"123": {"name": "Pilot", "current_room": "pod_room",
                                     "bag": {}, "equipped": {}, "extra": {}},
                            "456": {"name": "Other"}},
                rooms={"pod_room": {"title": "Pod"}}, items_db={}),
            is_ready=lambda: True)
        self.client = TestClient(TestServer(create_app(
            self.bot, self.config, oauth=self.oauth, clock=lambda: self.now)),
            cookie_jar=aiohttp.DummyCookieJar())
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()

    async def start(self):
        response = await self.client.get("/play/auth/discord", allow_redirects=False)
        self.assertEqual(response.status, 302)
        return response.cookies[LOGIN_COOKIE].value

    async def complete(self, nonce, state="test-state", extra=""):
        return await self.client.get(
            "/play/auth/callback?code=fictional-code&state=" + state + extra,
            headers={"Cookie": LOGIN_COOKIE + "=" + nonce}, allow_redirects=False)

    async def sign_in(self):
        response = await self.complete(await self.start())
        self.assertEqual(response.status, 302)
        return response.cookies[SESSION_COOKIE].value

    def auth(self, token):
        return {"Cookie": SESSION_COOKIE + "=" + token}

    async def test_anonymous_cannot_read(self):
        response = await self.client.get("/play/api/me?user_id=123")
        self.assertEqual(response.status, 401)
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    async def test_verified_identity_controls_character_not_query(self):
        before = deepcopy(vars(self.bot.storage))
        token = await self.sign_in()
        response = await self.client.get("/play/api/me?user_id=456", headers=self.auth(token))
        self.assertEqual(response.status, 200)
        self.assertEqual((await response.json())["character"]["name"], "Pilot")
        self.assertEqual(before, vars(self.bot.storage))

    async def test_login_cookie_is_secure_and_http_only(self):
        response = await self.complete(await self.start())
        value = response.cookies[SESSION_COOKIE]
        self.assertTrue(value["secure"])
        self.assertTrue(value["httponly"])
        self.assertEqual(value["samesite"], "Lax")
        self.assertEqual(value["path"], "/")
        self.assertFalse(value["domain"])

    async def test_state_mismatch_denied_before_exchange(self):
        response = await self.complete(await self.start(), "wrong")
        self.assertEqual(response.status, 400)
        self.assertEqual(self.oauth.calls, 0)

    async def test_browser_binding_required(self):
        await self.start()
        response = await self.complete("another-browser")
        self.assertEqual(response.status, 400)
        self.assertEqual(self.oauth.calls, 0)

    async def test_replayed_callback_is_denied(self):
        nonce = await self.start()
        self.assertEqual((await self.complete(nonce)).status, 302)
        self.assertEqual((await self.complete(nonce)).status, 400)
        self.assertEqual(self.oauth.calls, 1)

    async def test_expired_login_denied(self):
        nonce = await self.start()
        self.now += PENDING_SECONDS
        self.assertEqual((await self.complete(nonce)).status, 400)
        self.assertEqual(self.oauth.calls, 0)

    async def test_expired_session_denied(self):
        token = await self.sign_in()
        self.now += SESSION_SECONDS
        response = await self.client.get("/play/api/me", headers=self.auth(token))
        self.assertEqual(response.status, 401)

    async def test_non_pilot_identity_denied(self):
        self.oauth.uid = "456"
        response = await self.complete(await self.start())
        self.assertEqual(response.status, 403)
        self.assertNotIn(SESSION_COOKIE, response.cookies)

    async def test_missing_existing_character_denied_without_creation(self):
        del self.bot.storage.characters["123"]
        response = await self.complete(await self.start())
        self.assertEqual(response.status, 403)
        self.assertNotIn("123", self.bot.storage.characters)

    async def test_exchange_failure_does_not_expose_details(self):
        self.oauth.fail = True
        response = await self.complete(await self.start())
        self.assertEqual(response.status, 502)
        self.assertNotIn("SECRET", await response.text())

    async def test_duplicate_state_rejected(self):
        response = await self.complete(await self.start(), extra="&state=test-state")
        self.assertEqual(response.status, 400)
        self.assertEqual(self.oauth.calls, 0)

    async def test_cancelled_login_does_not_exchange(self):
        response = await self.complete(await self.start(), extra="&error=access_denied")
        self.assertEqual(response.status, 400)
        self.assertEqual(self.oauth.calls, 0)

    async def test_logout_requires_origin_and_csrf_then_invalidates(self):
        token = await self.sign_in()
        headers = self.auth(token)
        response = await self.client.get("/play/api/me", headers=headers)
        csrf = (await response.json())["session"]["csrf"]
        self.assertEqual((await self.client.post("/play/logout", headers=headers)).status, 403)
        headers.update({"Origin": "https://evil.example", "X-CSRF-Token": csrf})
        self.assertEqual((await self.client.post("/play/logout", headers=headers)).status, 403)
        headers["Origin"] = ORIGIN
        self.assertEqual((await self.client.post("/play/logout", headers=headers)).status, 204)
        self.assertEqual((await self.client.get("/play/api/me", headers=self.auth(token))).status, 401)

    async def test_disconnected_bot_does_not_serve_stale_state(self):
        token = await self.sign_in()
        self.bot.is_ready = lambda: False
        response = await self.client.get("/play/api/me", headers=self.auth(token))
        self.assertEqual(response.status, 503)

    async def test_no_action_endpoint_or_static_traversal(self):
        for path in ("/play/api/action", "/play/static/secrets.env"):
            response = await self.client.get(path)
            self.assertEqual(response.status, 404)

    async def test_page_and_assets_exist_under_strict_csp(self):
        for path in ("/play/", "/play/static/game.js", "/play/static/game.css"):
            response = await self.client.get(path)
            self.assertEqual(response.status, 200)
            self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])

    async def test_library_builds_correct_discord_authorization(self):
        url, state = await DiscordOAuth(self.config).authorize()
        parsed = urlsplit(url)
        params = parse_qs(parsed.query)
        self.assertEqual(parsed.netloc, "discord.com")
        self.assertEqual(params["scope"], ["identify"])
        self.assertEqual(params["redirect_uri"], [CALLBACK])
        self.assertEqual(params["response_type"], ["code"])
        self.assertEqual(params["state"], [state])
        self.assertNotIn("fictional-secret", url)
