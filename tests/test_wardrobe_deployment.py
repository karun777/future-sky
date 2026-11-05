"""Deployment safety checks use temporary directories and stubbed service commands."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

class WardrobeDeploymentTests(unittest.TestCase):
    def setUp(self):
        path=Path(__file__).resolve().parents[1]/"tools/deploy/w7f7/activate.py"
        spec=importlib.util.spec_from_file_location("wardrobe_deploy",path)
        self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name);self.m.SOURCE=root/"source";self.m.LIVE=root/"live"
        self.m.SOURCE.mkdir();self.m.LIVE.mkdir()
        (self.m.LIVE/"bot/data").mkdir(parents=True)
        (self.m.LIVE/"bot/data/characters.json").write_text('{"player":"preserve"}')
        for base in [self.m.SOURCE,self.m.LIVE]:(base/"code").mkdir()
        (self.m.SOURCE/"code/existing.py").write_text("NEW")
        (self.m.SOURCE/"code/added.py").write_text("ADDED")
        (self.m.LIVE/"code/existing.py").write_text("OLD")
        self.manifest={"files":{name:{"target":name,"source":self.m.sha(self.m.SOURCE/name),
                         "live":self.m.sha(self.m.LIVE/name)}
                         for name in ["code/existing.py","code/added.py"]}}
        self.commands=[]
        self.m.command=lambda *args:self.commands.append(args) or ""
        self.m.start_and_wait=lambda inspection:"123"
        self.m.status=lambda *args:401
        self.data=self.m.data_hashes()

    def test_success_overlays_only_code(self):
        self.m.activate(self.manifest)
        self.assertEqual((self.m.LIVE/"code/existing.py").read_text(),"NEW")
        self.assertEqual((self.m.LIVE/"code/added.py").read_text(),"ADDED")
        self.assertEqual(self.m.data_hashes(),self.data)
        result=next((self.m.LIVE/"backups").glob("*/result.json"))
        self.assertEqual(json.loads(result.read_text())["status"],"activated")

    def test_failure_restores_existing_and_removes_only_new_code(self):
        def readiness(inspection):
            if inspection:raise RuntimeError("health failure")
            return "456"
        self.m.start_and_wait=readiness
        with self.assertRaisesRegex(RuntimeError,"health failure"):
            self.m.activate(self.manifest)
        self.assertEqual((self.m.LIVE/"code/existing.py").read_text(),"OLD")
        self.assertFalse((self.m.LIVE/"code/added.py").exists())
        self.assertEqual(self.m.data_hashes(),self.data)
        result=next((self.m.LIVE/"backups").glob("*/result.json"))
        self.assertEqual(json.loads(result.read_text())["status"],"rolled_back")

    def test_changed_baseline_is_never_overwritten(self):
        (self.m.LIVE/"code/existing.py").write_text("CONCURRENT CHANGE")
        with self.assertRaisesRegex(RuntimeError,"baseline changed"):
            self.m.activate(self.manifest)
        self.assertEqual((self.m.LIVE/"code/existing.py").read_text(),"CONCURRENT CHANGE")
        self.assertFalse((self.m.LIVE/"code/added.py").exists())
        self.assertEqual(self.m.data_hashes(),self.data)
