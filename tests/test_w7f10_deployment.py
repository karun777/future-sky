"""W7-F10 deployment and pinned-router compatibility; fictional fixtures only."""
import asyncio
import base64
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, AsyncMock, patch
from tools.deploy.w7f10.activate import Deployment, check, sha, MANIFEST, ROOT
from tools.character_reset_adapter import Refused, snapshot, offline_guard, verify_runtime_files
from fsbot.reset_binding import validate_reset_binding

class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        self.source=root/"source";self.live=root/"live";self.data=root/"data";self.state=root/"backup"
        for p in (self.source,self.live,self.data):p.mkdir()
        self.manifest={"files":{},"pins":{}}
        for i in range(5):
            r=str(i)+".py"
            (self.source/r).write_text("new"+str(i))
            if i<4:(self.live/r).write_text("old"+str(i));(self.live/r).chmod(0o640)
            self.manifest["files"][r]={"source":sha(self.source/r),"live":sha(self.live/r)}
        (self.live/"router.py").write_text("unchanged")
        self.manifest["pins"]["router.py"]=sha(self.live/"router.py")
        (self.data/"players.json").write_text('{"protected":"unchanged"}')
        self.guard=Mock()
        self.before={r:snapshot(self.live/r) for r in self.manifest["files"]}

    def deploy(self):
        return Deployment(self.source,self.live,self.data,self.state,self.manifest,self.guard)

    def test_install_rollback_exact_metadata_and_missing_file(self):
        with self.deploy() as d:
            d.install();check(self.source,self.live,self.manifest,True)
            d.rollback()
            self.assertEqual(self.before,d.current())
        self.assertEqual('{"protected":"unchanged"}',(self.data/"players.json").read_text())
        self.assertEqual("unchanged",(self.live/"router.py").read_text())

    def test_reset_runtime_accepts_pinned_router_and_refuses_changed_code(self):
        with self.deploy() as d:
            with self.assertRaises(Refused):
                verify_runtime_files(self.source,self.live,self.manifest)
            d.install()
            self.assertIn("router.py",verify_runtime_files(self.source,self.live,self.manifest))
            (self.live/"router.py").write_text("strict router")
            with self.assertRaises(Refused):
                verify_runtime_files(self.source,self.live,self.manifest)

    def test_crash_each_write_reopen_and_rollback(self):
        for index in range(5):
            with self.subTest(index=index):
                def crash(i):
                    if i==index:raise RuntimeError("interrupted")
                with self.deploy() as d:
                    with self.assertRaises(RuntimeError):d.install(crash)
                with self.deploy() as d:
                    d.rollback();self.assertEqual(self.before,d.current())
                import shutil
                shutil.rmtree(self.state)

    def test_interrupted_rollback_retry(self):
        with self.deploy() as d:
            d.install()
            with self.assertRaises(RuntimeError):
                d.rollback(lambda i: (_ for _ in ()).throw(RuntimeError("stop")) if i==2 else None)
        with self.deploy() as d:
            d.rollback();self.assertEqual(self.before,d.current())

    def test_source_baseline_and_pin_drift_refused(self):
        for p in (self.source/"0.py",self.live/"0.py",self.live/"router.py"):
            old=p.read_bytes();p.write_text("changed")
            with self.assertRaises(Refused):check(self.source,self.live,self.manifest)
            p.write_bytes(old)

    def test_external_data_blocks_rollback(self):
        with self.deploy() as d:
            d.install();(self.data/"players.json").write_text("changed")
            with self.assertRaises(Refused):d.rollback()
            self.assertEqual("changed",(self.data/"players.json").read_text())

    def test_external_code_blocks_rollback(self):
        with self.deploy() as d:
            d.install();(self.live/"1.py").write_text("external")
            with self.assertRaises(Refused):d.rollback()
            self.assertEqual("external",(self.live/"1.py").read_text())

    def test_active_service_and_duplicate_install_refused(self):
        self.guard.side_effect=Refused("active")
        with self.assertRaises(Refused):
            with self.deploy():pass
        self.guard.side_effect=None
        with self.deploy() as d:
            d.install()
            with self.assertRaises(Refused):d.install()

    def test_journal_failure_no_code_changes(self):
        with self.deploy() as d,patch("tools.deploy.w7f10.activate.atomic",side_effect=OSError("disk")):
            with self.assertRaises(OSError):d.install()
            self.assertEqual(self.before,d.current())

    def test_corrupt_transaction_refused(self):
        with self.deploy() as d:
            d.install()
            p=self.state/"transaction.json";record=json.loads(p.read_text())
            record["payload"]["before"]["0.py"]["bytes"]=base64.b64encode(b"wrong").decode()
            p.write_text(json.dumps(record))
            with self.assertRaises(Refused):d.rollback()

class OfflineGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.proc=Path(self.tmp.name)
        self.patch=patch("tools.character_reset_adapter.subprocess.run",
            return_value=NS(stdout="MainPID=0\nActiveState=inactive\nSubState=dead\n"))
        self.patch.start();self.addCleanup(self.patch.stop)
    def process(self,cmd=b"other",target=None,flags="00"):
        p=self.proc/"987654";p.mkdir();(p/"cmdline").write_bytes(cmd)
        (p/"fd").mkdir();(p/"fdinfo").mkdir()
        if target:
            (p/"fd"/"3").symlink_to(target)
            (p/"fdinfo"/"3").write_text("flags:\t"+flags+"\n")
        return p
    def test_stopped_empty_and_readonly_descriptor_pass(self):
        offline_guard(self.proc)
        self.process(target="/opt/futuresky/data/characters/characters.json")
        offline_guard(self.proc)
    def test_detached_absolute_bot_refused(self):
        self.process(b"python\0/opt/futuresky/bot/run_bot.py\0")
        with self.assertRaises(Refused):offline_guard(self.proc)
    def test_detached_relative_bot_refused(self):
        p=self.process(b"python\0run_bot.py\0");(p/"cwd").symlink_to("/opt/futuresky/bot")
        with self.assertRaises(Refused):offline_guard(self.proc)
    def test_writable_descriptor_refused(self):
        self.process(target="/opt/futuresky/data/characters/characters.json",flags="0100002")
        with self.assertRaises(Refused):offline_guard(self.proc)
    def test_permission_denial_refused(self):
        self.process()
        with patch.object(Path,"read_bytes",side_effect=PermissionError):
            with self.assertRaises(Refused):offline_guard(self.proc)
    def test_disappearing_process_is_tolerated(self):
        (self.proc/"987654").mkdir()
        offline_guard(self.proc)

class PinnedRouterTests(unittest.IsolatedAsyncioTestCase):
    async def test_receipt_routes_without_category_or_creation_and_preserves_other_mapping(self):
        fixture=ROOT/"tests/fixtures/w7f10/router_pinned.py"
        manifest=json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["pins"]["fsbot/cogs/router.py"],sha(fixture))
        spec=importlib.util.spec_from_file_location("w7f10_pinned_router",fixture)
        router=importlib.util.module_from_spec(spec);spec.loader.exec_module(router)
        traveller={"id":"101","name":"New Traveller","bag":{}}
        other={"id":"202","run_channel_id":"600","special":"preserved"}
        characters={"202":other};before=deepcopy(other)
        validate_reset_binding({"version":1,"bindings":{"101":{
            "run_channel_id":"500","run_seeded_channel_id":500}}},traveller,characters)
        characters["101"]=traveller
        class Channel:
            def __init__(self,i):self.id=i;self.send=AsyncMock()
        own,queen=Channel(500),Channel(600)
        guild=NS(get_channel=lambda i:{500:own,600:queen}.get(i),create_text_channel=AsyncMock())
        bot=NS(storage=NS(characters=characters,save_characters=Mock()))
        with patch.object(router.discord,"TextChannel",Channel),patch.dict(os.environ,{"FS_PLAYERS_CATEGORY_ID":""}):
            for uid,expected in (("101",own),("202",queen)):
                self.assertIs(expected,await router.get_run_channel_by_guild_if_any(bot,guild,uid))
            ctx=NS(bot=bot,guild=guild,author=NS(id=101),channel=NS(id=900),command=NS(qualified_name="look"))
            await router.RunRoutedContext.send(ctx,"private response")
            own.send.assert_awaited_once_with(content="private response")
            queen.send.assert_not_awaited()
            self.assertTrue(router._is_seeded_for_channel(bot,"101",500))
        guild.create_text_channel.assert_not_awaited()
        bot.storage.save_characters.assert_not_called()
        self.assertEqual(before,characters["202"])
