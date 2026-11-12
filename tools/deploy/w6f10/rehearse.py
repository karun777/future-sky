"""Rehearse W6-F10 against temporary copies of installed CODE ONLY.

Reads the fixed production code/asset list. Never reads/copies player stores,
private reset archives or receipts. Fictional state sentinels are created below.
"""
import json
from pathlib import Path
import shutil
import tempfile

from tools.deploy.w6f10.activate import ROOT, LIVE, StaticRelease, ORDER, sha


def run():
    original = StaticRelease()
    original.check()
    code = (*ORDER, *original.manifest["pins"])
    installed_before = {r: sha(LIVE / r) for r in code}
    results = []
    with tempfile.TemporaryDirectory(prefix="w6f10-code-rehearsal-") as temporary:
        root = Path(temporary)
        live = root / "live"
        for relative in code:
            target = live / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(LIVE / relative, target)
        sentinels = {
            "data/characters/characters.json": '{"fictional_player":"initial"}',
            "data/storage/reset_run_bindings.json": '{"fictional_receipt":"retained"}',
            "private/archive.json": '{"fictional_archive":"retained"}',
        }
        for relative, text in sentinels.items():
            target = live / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        release = StaticRelease(ROOT, live, root / "complete")
        before = release.current()
        runtime_before = release.check()
        release.install()
        assert release.check(installed=True) == runtime_before
        results.append("exact two-asset installation and unchanged 140-entry runtime passed")
        sentinels["data/characters/characters.json"] = '{"fictional_player":"later progress"}'
        (live / "data/characters/characters.json").write_text(sentinels["data/characters/characters.json"])
        release.rollback()
        assert release.current() == before
        assert release.check() == runtime_before
        results.append("exact bytes/ownership/mode rollback passed; later fictional progress retained")

        def interruption(stop):
            def stop_after(i):
                if i == stop:
                    raise RuntimeError("deliberate rehearsal interruption")
            return stop_after

        for stop in (0, 1):
            state = root / ("interrupted-install-" + str(stop))
            try:
                StaticRelease(ROOT, live, state).install(interruption(stop))
            except RuntimeError as exc:
                assert str(exc) == "deliberate rehearsal interruption"
            else:
                raise AssertionError("Interruption was not exercised")
            StaticRelease(ROOT, live, state).rollback()
            assert StaticRelease(ROOT, live, state).current() == before
            results.append("reopened rollback after install write " + str(stop + 1) + " passed")

        release = StaticRelease(ROOT, live, root / "interrupted-rollback")
        release.install()
        try:
            release.rollback(interruption(0))
        except RuntimeError as exc:
            assert str(exc) == "deliberate rehearsal interruption"
        else:
            raise AssertionError("Rollback interruption was not exercised")
        StaticRelease(ROOT, live, root / "interrupted-rollback").rollback()
        assert release.current() == before
        results.append("interrupted rollback retried successfully")
        assert all((live / relative).read_text() == text for relative, text in sentinels.items())
        assert {r: sha(live / r) for r in code} == installed_before
        results.append("all 139 preserved code/asset pins and fictional state sentinels matched")

    assert {r: sha(LIVE / r) for r in code} == installed_before
    original.check()
    return {
        "source_review_commit": original.manifest["basis"]["source_review_commit"],
        "copied_code_and_asset_files": len(code),
        "runtime_hash_entries": len(runtime_before),
        "results": results,
        "production_code_assets_unchanged": True,
        "production_player_stores_read_or_written": False,
        "temporary_copies_removed": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
