"""Optional Future Sky adapter using its normal HTTP session and request handlers."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit

import aiohttp
from aiohttp.test_utils import TestClient, TestServer
from fsbot.web_portal import LOGIN_COOKIE, SESSION_COOKIE, ORIGIN
from tools.authoring.nl_w7_f5.fixtures import create
from tools.authoring.nl_w7_f5.rehearsal import make_app


class ParticipationDeskTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = create(Path(self.temp.name) / "crew.db", "future-sky-rehearsal",
                            title="Synthetic crew briefing")
        self.client = TestClient(TestServer(make_app(self.store)), cookie_jar=aiohttp.DummyCookieJar())
        await self.client.start_server()
        self.sessions = {}

    async def asyncTearDown(self):
        await self.client.close()
        self.temp.cleanup()

    async def sign_in(self, uid):
        start = await self.client.get("/play/auth/discord", allow_redirects=False)
        state = parse_qs(urlsplit(start.headers["Location"]).query)["state"][0]
        response = await self.client.get("/play/auth/callback", params={"state": state, "code": uid},
            headers={"Cookie": LOGIN_COOKIE + "=" + start.cookies[LOGIN_COOKIE].value}, allow_redirects=False)
        self.assertEqual(response.status, 302)
        headers = {"Cookie": SESSION_COOKIE + "=" + response.cookies[SESSION_COOKIE].value}
        me = await self.client.get("/play/api/me", headers=headers)
        self.assertEqual(me.status, 200)
        headers.update({"Origin": ORIGIN, "X-CSRF-Token": (await me.json())["session"]["csrf"]})
        self.sessions[uid] = headers
        return headers

    async def headers(self, uid):
        return self.sessions.get(uid) or await self.sign_in(uid)

    async def view(self, uid):
        response = await self.client.get("/play/api/undertaking", headers=await self.headers(uid))
        self.assertEqual(response.status, 200, await response.text())
        return await response.json()

    async def act(self, uid, action, revision=None, **extra):
        if revision is None:
            revision = (await self.view(uid))["revision"]
        payload = dict(action=action, revision=revision, command_id="http-"+action, **extra)
        return await self.client.post("/play/api/undertaking/action", json=payload,
                                      headers=await self.headers(uid))

    async def test_signed_in_projection_and_no_implicit_action(self):
        anonymous = await self.client.get("/play/api/undertaking?uid=101")
        self.assertEqual(anonymous.status, 401)
        before = await self.view("102")
        self.assertEqual((before["state"], before["history"]), ("open", []))
        forged = await self.client.get("/play/api/undertaking?uid=101", headers=await self.headers("102"))
        self.assertEqual(forged.status, 400)
        visitor = await self.client.get("/play/api/undertaking", headers=await self.headers("105"))
        self.assertEqual(visitor.status, 403)
        self.assertEqual(await self.view("102"), before)

    async def test_browser_request_boundaries(self):
        headers = await self.headers("101")
        body = {"action": "request", "command_id": "boundary", "revision": 0}
        for changed in [{"Origin": "https://elsewhere.invalid"}, {"X-CSRF-Token": "incorrect"}]:
            response = await self.client.post("/play/api/undertaking/action", json=body,
                                             headers={**headers, **changed})
            self.assertEqual(response.status, 403)
        for change in [{"person": "reader"}, {"key": "future-sky-rehearsal.reader"},
                       {"realm": "workshop"}, {"revision": True}]:
            response = await self.client.post("/play/api/undertaking/action", json={**body, **change}, headers=headers)
            self.assertEqual(response.status, 409)
        self.assertEqual((await self.view("101"))["history"], [])

    async def test_invitation_accept_copy_succession_and_receipt(self):
        for uid, action in [("101", "request"), ("102", "accept"), ("101", "offer")]:
            response = await self.act(uid, action)
            self.assertEqual(response.status, 200, await response.text())
        copy = (await self.view("102"))["copy"]
        self.assertEqual(set(json.loads(copy)["fields"]), {"title", "observation"})
        self.assertNotIn("WITHHELD", copy)
        self.assertEqual((await self.act("104", "succeed")).status, 200)
        denied = await self.client.get("/play/api/undertaking", headers=await self.headers("102"))
        self.assertEqual(denied.status, 403)
        self.assertEqual((await self.view("103"))["copy"], copy)
        checksum = hashlib.sha256(copy.encode()).hexdigest()
        self.assertEqual((await self.act("103", "receipt", checksum=checksum)).status, 200)
        view = await self.view("103")
        self.assertEqual(view["state"], "received")
        self.assertEqual([e["actor"] for e in view["history"]], ["maker", "reader", "maker", "convenor", "successor"])

    async def test_stale_view_and_exact_retry(self):
        self.assertEqual((await self.act("101", "request")).status, 200)
        self.assertEqual((await self.act("102", "accept", revision=0)).status, 409)
        first = await self.act("102", "accept", revision=1)
        repeated = await self.act("102", "accept", revision=1)
        self.assertEqual((first.status, repeated.status), (200, 200))
        self.assertEqual(await first.json(), await repeated.json())
        self.assertEqual(len((await self.view("101"))["history"]), 2)

    async def test_revocation_and_logout(self):
        await self.view("101")
        with self.store.transaction(True) as db:
            db.execute("UPDATE held_key SET revoked=1 WHERE holder='maker'")
        self.assertEqual((await self.act("101", "request", revision=0)).status, 409)
        response = await self.client.post("/play/logout", headers=await self.headers("101"))
        self.assertEqual(response.status, 204)
        response = await self.client.get("/play/api/undertaking", headers=self.sessions["101"])
        self.assertEqual(response.status, 401)

    async def test_decline_and_transaction_failure(self):
        self.assertEqual((await self.act("101", "request")).status, 200)
        with self.store.transaction(True) as db:
            db.execute("""CREATE TRIGGER fail_event BEFORE INSERT ON handover_event
                       BEGIN SELECT RAISE(ABORT,'synthetic fault'); END""")
        self.assertEqual((await self.act("102", "accept")).status, 503)
        self.assertEqual((await self.view("102"))["state"], "awaiting response")
        with self.store.transaction(True) as db:
            db.execute("DROP TRIGGER fail_event")
        self.assertEqual((await self.act("102", "decline")).status, 200)
        self.assertEqual((await self.act("101", "offer")).status, 409)
        self.assertEqual((await self.view("101"))["state"], "declined")
