"""Versioned code contracts and old-archive restoration; fictional stores only."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import test_character_reset_adapter as adapter_fixture
from tools.character_reset_adapter import Refused, document, runtime_code_check, runtime_check

class RuntimeContractTests(unittest.TestCase):
    setUp = adapter_fixture.AdapterTests.setUp
    put = adapter_fixture.AdapterTests.put

    def contract_fixture(self):
        repo = Path(self.tmp.name) / 'repo'
        live = Path(self.tmp.name) / 'code'
        for root in (repo / 'bot', live):
            root.mkdir(parents=True)
            (root / 'arrival.py').write_text('reviewed arrival')
            (root / 'router.py').write_text('preserved router')
        for name in ('character_reset_adapter.py', 'character_reset_rehearsal.py'):
            p = repo / 'tools' / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('reviewed operator tool')
        manifest = {'files': {'arrival.py': {'source': self.sha(live / 'arrival.py')}},
                    'pins': {'router.py': self.sha(live / 'router.py')}}
        path = repo / 'tools/deploy/w7f10/runtime-manifest.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(manifest))
        return repo, live, path

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_old_archive_restores_under_current_contract_and_archives_new_life(self):
        self.a.contract = lambda: {'historical_contract': 'v1'}
        archive = self.a.apply(self.a.plan('101', 'Test Traveller'))
        archive_path = self.state / (archive + '.archive.json')
        archive_bytes = archive_path.read_bytes()
        chars = document(self.a.read()['characters'])
        chars['101'] = {'id': '101', 'name': 'New Life', 'run_channel_id': '500',
                        'run_seeded_channel_id': 500, 'bag': {'new-item': 1}}
        chars['202']['bag']['later-progress'] = 3
        self.put('characters', chars)
        repo, live, path = self.contract_fixture()
        self.a.contract = lambda: runtime_code_check(repo, live)
        plan = self.a.plan('101', 'New Life', restore=archive)
        self.assertEqual(plan['payload']['runtime_contract'], self.a.contract())
        replacement = self.a.apply(plan)
        restored = document(self.a.read()['characters'])
        self.assertEqual(restored['101'], self.original['characters']['101'])
        self.assertEqual(restored['202'], chars['202'])
        self.assertEqual(archive_path.read_bytes(), archive_bytes)
        self.assertEqual(self.a.protected(), self.protected)
        self.a.apply(self.a.plan('101', 'Test Traveller', restore=replacement))
        self.assertEqual(document(self.a.read()['characters']), chars)

    def test_changed_contract_invalidates_pending_plan_without_data_writes(self):
        repo, live, path = self.contract_fixture()
        self.a.contract = lambda: runtime_code_check(repo, live)
        plan = self.a.plan('101', 'Test Traveller')
        value = json.loads(path.read_text()); value['review_version'] = 2
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(Refused, 'Stale or altered plan'):
            self.a.apply(plan)
        self.assertEqual(self.a.read(), self.initial)
        self.assertFalse((self.state / 'journal.json').exists())

    def test_source_installed_and_preserved_code_drift_refused(self):
        repo, live, path = self.contract_fixture()
        self.a.contract = lambda: runtime_code_check(repo, live)
        plan = self.a.plan('101', 'Test Traveller')
        for p in (repo / 'bot/arrival.py', live / 'arrival.py', live / 'router.py'):
            with self.subTest(path=str(p)):
                before = p.read_bytes(); p.write_text('unexpected change')
                with self.assertRaises(Refused): self.a.apply(plan)
                self.assertEqual(self.a.read(), self.initial)
                self.assertFalse((self.state / 'journal.json').exists())
                p.write_bytes(before)

    def test_restart_flags_still_block_before_code_check(self):
        with patch('dotenv.dotenv_values', return_value={'FS_RESET_ROOMS_ON_BOOT':'1'}), \
             patch('tools.character_reset_adapter.Path.exists', return_value=True), \
             patch('tools.character_reset_adapter.runtime_code_check') as code:
            with self.assertRaises(Refused): runtime_check()
            code.assert_not_called()
        with patch('tools.character_reset_adapter.Path.exists', return_value=False), \
             patch('tools.character_reset_adapter.subprocess.run', return_value=Mock(stdout='FS_RESET_ROOMS_ON_BOOT=1')), \
             patch('tools.character_reset_adapter.runtime_code_check') as code:
            with self.assertRaises(Refused): runtime_check()
            code.assert_not_called()

    def test_current_manifest_is_exact_reviewed_overlay(self):
        root = Path(__file__).resolve().parents[1]
        old_path = root / 'tools/deploy/w7f10/deployment-manifest.json'
        hot_path = root / 'tools/deploy/w7f10_playcheck/deployment-manifest.json'
        old = json.loads(old_path.read_text()); hot = json.loads(hot_path.read_text())
        current = json.loads((root / 'tools/deploy/w7f10/runtime-manifest.json').read_text())
        expected = deepcopy(old)
        for relative in ('fsbot/arrival_media.py', 'fsbot/pod_inspection.py'):
            entry = hot['files']['bot/' + relative]
            self.assertEqual(expected['pins'].pop(relative), entry['live'])
            expected['files'][relative] = {'source': entry['source']}
        return_path = root / 'tools/deploy/w7f9_return/deployment-manifest.json'
        baseline_path = return_path.with_name('baseline-runtime.json')
        baseline = json.loads(baseline_path.read_text())
        self.assertEqual(baseline['files'], expected['files'])
        self.assertEqual(baseline['pins'], expected['pins'])
        correction = json.loads(return_path.read_text())
        self.assertEqual(correction['basis']['baseline_runtime_sha256'], self.sha(baseline_path))
        self.assertEqual(set(correction['files']), {
            'bot/fsbot/pod_opening.py', 'bot/fsbot/cogs/threadnodes.py',
            'bot/fsbot/cogs/inspection.py'})
        for relative, entry in correction['files'].items():
            bot_relative = relative.removeprefix('bot/')
            self.assertEqual(expected['pins'].pop(bot_relative), entry['live'])
            self.assertEqual(self.sha(root / relative), entry['source'])
            self.assertEqual(self.sha(return_path.parent / 'delivery' / relative), entry['source'])
            expected['files'][bot_relative] = {'source': entry['source']}
        # Historical static pins belong to their release, not the bot-only
        # lifecycle contract. Later static packages bind their own baselines.
        self.assertFalse(any(r.startswith('assets/') for r in
                             set(current['files']) | set(current['pins'])))
        self.assertEqual(current['basis']['return_manifest_sha256'], self.sha(return_path))
        self.assertEqual(current['files'], expected['files'])
        self.assertEqual(current['pins'], expected['pins'])
        self.assertEqual(current['basis']['lifecycle_manifest_sha256'], self.sha(old_path))
        self.assertEqual(current['basis']['playcheck_manifest_sha256'], self.sha(hot_path))
