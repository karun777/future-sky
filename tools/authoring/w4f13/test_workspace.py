"""Fictional HTTP and text-command checks for the authoring rehearsal."""
from contextlib import AsyncExitStack
from copy import deepcopy
import asyncio
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from fsbot.web_portal import ORIGIN
from rehearsal import fictional_save, rehearsal
from workspace_scene import BOOKMARK, FIRST_OPEN, LEAVE, MARK, MEMORY, NOTE, READER, SKETCH, SLIP, USE


class WorkspaceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.files = self.enterContext(fictional_save())
        self.servers = AsyncExitStack()
        self.addAsyncCleanup(self.servers.aclose)
        await self.start()

    async def start(self):
        self.window, self.bot, self.nav = await self.servers.enter_async_context(rehearsal(self.files))
        self.auth = await self.window.sign_in(READER)

    async def commands(self, *commands):
        for command in commands:
            answer = await self.window.command(self.auth, command)
        return answer

    async def discover(self):
        await self.commands("inspect pod", "inspect berth", "inspect console")

    async def open_desk(self):
        await self.discover()
        await self.commands("inspect note", USE)

    async def offer(self, auth=None):
        return await self.window.view(self.auth if auth is None else auth)

    async def post(self, auth, view, target, **extra):
        return await self.window.post(auth, view, "inspect",
                                      {"target": target, "token": view["inspection"]["token"], **extra})

    def snapshot(self):
        return deepcopy(self.bot.storage.characters)

    async def test_progression_and_no_login_by_guess(self):
        before = self.snapshot()
        self.assertNotIn("console", (await self.offer())["inspection"]["targets"])
        for command in ("inspect note", USE, "console login underblue", "inspect probe slip", MARK):
            self.assertIn("unavailable", await self.commands(command))
        self.assertEqual(before, self.snapshot())
        await self.discover()
        self.assertIn("still folded", await self.commands(USE))
        self.assertEqual((await self.post(self.auth, await self.offer(), USE)).status, 400)
        self.assertIn(NOTE, await self.commands("!inspect note"))
        self.assertIn(FIRST_OPEN, await self.commands(USE))
        self.assertIn("Open the sketch first", await self.commands(MARK))

    async def test_passive_views_and_duplicate_read_or_mark_preserve_other_facts(self):
        await self.open_desk()
        before = self.snapshot()
        disk = self.files.read_bytes()
        for _ in range(2):
            view = await self.offer()
            self.assertNotIn(NOTE, json.dumps(view))
            self.assertNotIn(MEMORY, json.dumps(view))
            self.assertIn(SLIP, await self.commands("inspect probe slip"))
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.files.read_bytes(), disk)
        self.assertIn(SKETCH, await self.commands("inspect sketch"))
        await self.commands(MARK)
        after = self.snapshot()
        earlier = before[READER]["extra"].pop(MEMORY)
        later = deepcopy(after[READER]["extra"].pop(MEMORY))
        self.assertEqual(later, {**earlier, "sketch": True, "marked": True})
        self.assertEqual(before, after)
        with patch.object(self.bot.storage, "save_characters", side_effect=AssertionError("duplicate save")):
            self.assertIn(BOOKMARK, await self.commands(MARK))
            self.assertIn(BOOKMARK, await self.commands("inspect sketch"))

    async def test_full_discovery_never_inherits_a_grant(self):
        before = self.snapshot()
        await self.open_desk()
        await self.commands("inspect probe slip", "inspect sketch", MARK, LEAVE)
        after = self.snapshot()
        memory = after[READER]["extra"].pop(MEMORY)
        self.assertEqual(memory, dict.fromkeys(("console", "note", "visited", "sketch", "marked"), True))
        before_opening = before[READER]["extra"]["arrival"]["opening"]
        after_opening = after[READER]["extra"]["arrival"]["opening"]
        self.assertEqual(after_opening["discoveries"], [*before_opening["discoveries"], "pod", "berth"])
        after_opening["discoveries"] = before_opening["discoveries"]
        self.assertEqual(after, before)

    async def test_reader_mark_in_a_fresh_python_process(self):
        await self.open_desk()
        await self.commands("inspect sketch", MARK, LEAVE)
        await self.servers.aclose()
        script = """from pathlib import Path
import asyncio, sys
from rehearsal import rehearsal
from workspace_scene import USE, READER
async def read():
    async with rehearsal(Path(sys.argv[1])) as (window, _, _):
        print(await window.command(await window.sign_in(READER), USE))
asyncio.run(read())
"""
        # Use only the temporary JSON from this test, with a new Python process.
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([str(Path(__file__).parent), *sys.path])
        child = await asyncio.create_subprocess_exec(
            sys.executable, "-c", script, str(self.files), env=env,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        output, error = await asyncio.wait_for(child.communicate(), timeout=15)
        self.assertEqual(child.returncode, 0, error.decode())
        self.assertIn(BOOKMARK, output.decode())
        self.assertIn(SKETCH, output.decode())

    async def test_walk_away_and_return_without_a_mark(self):
        await self.open_desk()
        await self.commands("inspect probe slip", LEAVE, "go west", "go east")
        self.assertNotIn("sketch", (await self.offer())["inspection"]["targets"])
        self.assertNotIn(BOOKMARK, await self.commands(USE))
        self.assertEqual(self.snapshot()[READER]["extra"][MEMORY],
                         {"console": True, "note": True, "visited": True})

    async def test_depart_without_closing_and_restart_keep_only_deliberate_mark(self):
        await self.open_desk()
        await self.commands("inspect sketch", MARK)
        await self.commands("go west")
        self.assertEqual((await self.offer())["inspection"]["targets"], [])
        await self.commands("go east")
        self.assertNotIn("sketch", (await self.offer())["inspection"]["targets"])
        self.assertIn(BOOKMARK, await self.commands(USE))
        saved = self.snapshot()
        await self.servers.aclose()
        await self.start()  # New app, session, navigation and storage loaded from JSON.
        self.assertEqual(self.snapshot(), saved)
        self.assertNotIn("sketch", (await self.offer())["inspection"]["targets"])
        self.assertIn(BOOKMARK, await self.commands(USE))
        self.assertEqual(self.snapshot(), saved)

    async def test_abandon_before_login_or_after_inspection(self):
        await self.discover()
        await self.commands(LEAVE, "go west", "go east")
        self.assertIn("still folded", await self.commands(USE))
        await self.commands("inspect note", USE, "inspect sketch", LEAVE)
        self.assertNotIn("marked", self.snapshot()[READER]["extra"][MEMORY])
        self.assertNotIn(BOOKMARK, await self.commands(USE))

    async def test_other_signed_in_reader_same_name_room_and_supplied_selectors(self):
        await self.open_desk()
        await self.commands("inspect sketch", MARK)
        before = self.snapshot()
        other = await self.window.sign_in("456")
        own_view = await self.offer()
        response = await self.window.client.get("/play/api/me?workspace_id=123&user_id=123", headers=other)
        self.assertEqual(response.status, 200)
        second_view = await response.json()
        self.assertEqual(second_view["character"]["name"], own_view["character"]["name"])
        for label in ("probe slip", "console", MEMORY, "underblue", "crescent"):
            self.assertNotIn(label, json.dumps(second_view))
        self.assertNotIn("probe slip", await self.window.command(other, "commands"))
        self.assertEqual((await self.post(other, second_view, "probe slip")).status, 400)
        self.assertEqual((await self.post(other, second_view, MARK)).status, 400)
        self.assertEqual((await self.post(other, second_view, "probe slip", workspace_id=READER)).status, 400)
        self.assertEqual((await self.window.post(other, second_view, "inspect",
            {"target": "probe slip", "token": own_view["inspection"]["token"]})).status, 409)
        self.assertEqual((await self.post(self.auth, own_view, "probe slip", workspace_id="456")).status, 400)
        self.assertEqual(before, self.snapshot())
        self.assertNotIn("keys", (await self.window.command(other, "inspect pod")).lower())
        self.assertNotIn("space bar", await self.window.command(other, "inspect berth"))
        self.assertNotIn("console", (await self.offer(other))["inspection"]["targets"])
        self.assertEqual(self.snapshot()[READER], before[READER])

    async def test_anonymous_and_signed_out_requests_cannot_see_or_act(self):
        await self.open_desk()
        view = await self.offer()
        before = self.snapshot()
        for headers in ({}, {"Cookie": "unrecognised=fiction"}):
            response = await self.window.client.get("/play/api/me?workspace_id=123", headers=headers)
            self.assertEqual(response.status, 401)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertEqual((await self.post(headers, view, "probe slip")).status, 401)
        response = await self.window.client.post("/play/logout", headers={
            **self.auth, "Origin": ORIGIN, "X-CSRF-Token": view["session"]["csrf"]})
        self.assertEqual(response.status, 204)
        self.assertEqual((await self.post(self.auth, view, "probe slip")).status, 401)
        self.assertEqual(before, self.snapshot())

    async def test_write_failures_do_not_report_success_and_retry_is_possible(self):
        await self.commands("inspect pod", "inspect berth")
        for command, fact in (("inspect console", "console"), ("inspect note", "note"),
                              (USE, "visited"), ("inspect sketch", "sketch"), (MARK, "marked")):
            with self.subTest(command=command):
                before, disk = self.snapshot(), self.files.read_bytes()
                with patch("fsbot.storage.os.replace", side_effect=OSError("fixture write failed")):
                    with self.assertLogs("futuresky.web", level="ERROR") as logs:
                        self.assertIn("could not be saved", await self.commands(command))
                for private_text in ("underblue", FIRST_OPEN, SKETCH, SLIP):
                    self.assertNotIn(private_text, "\n".join(logs.output))
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.files.read_bytes(), disk)
                if command == USE:
                    self.assertNotIn("sketch", (await self.offer())["inspection"]["targets"])
                await self.commands(command)
                self.assertTrue(json.loads(self.files.read_text())[READER]["extra"][MEMORY][fact])

    async def test_scoped_offer_is_single_use_and_checks_origin_and_csrf(self):
        await self.discover()
        offer = await self.offer()
        before = self.snapshot()
        for origin, csrf in ((ORIGIN, "wrong"), ("https://elsewhere.invalid", offer["session"]["csrf"])):
            response = await self.window.client.post("/play/api/inspect",
                headers={**self.auth, "Origin": origin, "X-CSRF-Token": csrf},
                json={"target": "note", "token": offer["inspection"]["token"]})
            self.assertEqual(response.status, 403)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual((await self.post(self.auth, offer, "note")).status, 200)
        self.assertEqual((await self.post(self.auth, offer, "note")).status, 409)

    async def test_stale_offer_after_close_and_ordinary_exit(self):
        await self.open_desk()
        await self.commands("inspect sketch")
        second_tab = await self.window.sign_in(READER)
        old = await self.offer(second_tab)
        await self.commands(LEAVE)
        self.assertEqual((await self.post(second_tab, old, MARK)).status, 409)
        await self.commands(USE)
        old = await self.offer(second_tab)
        await self.commands("go west", "go east")
        self.assertEqual((await self.post(second_tab, old, MARK)).status, 409)
        self.assertNotIn("marked", self.snapshot()[READER]["extra"][MEMORY])

    async def test_choice_recovery_cube_and_walk_in_progress_block_scene(self):
        await self.open_desk()
        for flags, extra in (({"in_combat": True}, {}), ({}, {"recovery": {"stage": "reanimating"}}),
                             ({}, {"thread_nodes": {"active_thread_node": "choice"}})):
            character = self.bot.storage.characters[READER]
            with patch.dict(character, flags=flags), patch.dict(character["extra"], extra):
                self.assertEqual((await self.offer())["inspection"]["targets"], [])
                self.assertNotIn(SKETCH, await self.commands("inspect sketch"))
        with patch.dict(self.bot.storage.characters[READER], in_cube=True):
            self.assertEqual((await self.offer())["inspection"]["targets"], [])
        self.nav.walking.add(READER)
        self.assertEqual((await self.offer())["inspection"]["targets"], [])

    async def test_existing_pod_berth_display_hud_and_room_are_preserved(self):
        rooms = deepcopy(self.bot.storage.rooms)
        await self.commands("inspect hands", "inspect pod")
        berth = await self.commands("inspect berth")
        self.assertIn("!search panel", berth)
        self.assertIn("display behind your eyes", await self.commands("inspect hud"))
        self.assertIn("FEED7", await self.commands("inspect panels"))
        display = await self.commands("inspect display")
        self.assertIn("!feed7", display)
        self.assertIn("!inspect booking", display)
        self.assertEqual(self.bot.storage.rooms, rooms)
