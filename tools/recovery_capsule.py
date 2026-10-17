#!/usr/bin/env python3
"""Capture a bounded private recovery set and verify a disposable restore.

Never starts the application or restores over the project. The capture is
sequential, not an atomic running-world snapshot. Credentials are excluded.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


DATA_FILES = [
    "data/characters/characters.json",
    "data/rooms/rooms.json", "data/rooms/rooms_base.json",
    "data/items/items.json", "data/enemies/enemies.json",
    "data/thread_nodes/thread_nodes.json",
    "data/narratives/internal_narratives.json",
    "data/modifiers/era_time_profiles.json", "data/modifiers/layers.json",
    "data/time/world_clock.json", "data/time/temporal_resolver.json",
    "data/comet/current_state.json", "data/astrology/current_snapshot.json",
    "data/fields/comet_pressure/current_state.json",
    "data/world_opportunities/catalogue.json",
    "data/world_opportunities/runtime_state.json",
    "data/storage/cubes.json", "data/storage/lockers.json",
    "data/storage/efiishent_vault.json",
]
DOC_FILES = [
    "docs/KNOWLEDGE_ATLAS.md", "docs/R3GPT_RESET_RITUAL_v2.0.md",
    "docs/WING_INDEX.md", "docs/RedBook_V7.2.md",
    "docs/handover/FUTURE_SKY_OCTOBER_RESEARCH_RECONCILIATION_20261015.md",
]


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def capture(project, output_parent, website=None):
    project = Path(project).resolve(strict=True)
    output_parent = Path(output_parent).resolve()
    if output_parent == project or project in output_parent.parents:
        # Only the explicitly designated backup subtree is permitted in-project.
        if output_parent != project / "backups/capsules":
            raise ValueError("In-project output must be backups/capsules")
    if output_parent == Path("/") or output_parent in project.parents:
        raise ValueError("Output cannot be an ancestor of project")
    output_parent.mkdir(parents=True, exist_ok=True)
    capsule = Path(tempfile.mkdtemp(prefix="w7-f2-", dir=output_parent))
    os.chmod(capsule, 0o700)
    staging = capsule / "captured"
    staging.mkdir(mode=0o700)
    selected = set(DATA_FILES + DOC_FILES + ["bot/run_bot.py"])
    for directory, suffixes in [
        ("bot/fsbot", {".py"}),
        ("tests", {".py"}),
        ("docs/current", {".md"}),
        ("docs/wings", {".md"}),
        ("assets", {".png", ".webp", ".jpg", ".jpeg", ".json"}),
        ("media", {".png", ".webp", ".jpg", ".jpeg"}),
    ]:
        for path in (project / directory).rglob("*"):
            rel = path.relative_to(project)
            if (path.is_file() and not path.is_symlink()
                    and path.suffix.lower() in suffixes
                    and not any(part.startswith(".") for part in rel.parts)):
                selected.add(str(rel))
    manifest = {
        "version": 1, "capture_started_utc": utc(),
        "atomic_world_snapshot": False,
        "project_head": subprocess.check_output(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            text=True).strip(),
        "main_reference": subprocess.check_output(
            ["git", "-C", str(project), "rev-parse", "origin/main"],
            text=True).strip(),
        "files": [], "missing_optional": [], "path_relationships": {
            "bot/data": "../data (recorded only; not recreated)",
            "website/assets": "project/assets (recorded only; not recreated)",
        },
        "excluded": [
            "credentials and environment files", "SSH/TLS keys",
            "event-history ledger", "container/database volumes",
            "complete virtualenv/OS packages", "automatic schedules",
            "unselected website files", "off-host backup replication",
        ],
    }

    def add(source, relative, required=False):
        if not source.is_file() or source.is_symlink():
            if required:
                raise ValueError("Missing required regular file: " + str(source))
            manifest["missing_optional"].append(str(source))
            return
        resolved = source.resolve(strict=True)
        # Never capture a project path that escapes through a parent symlink.
        if relative.startswith("project/") and project not in resolved.parents:
            raise ValueError("Project file escapes project: " + str(source))
        data = source.read_bytes()
        if source.suffix == ".json":
            json.loads(data)  # Capture must contain a whole parseable JSON file.
        dest = staging / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        os.chmod(dest, 0o600)
        manifest["files"].append({
            "path": relative, "bytes": len(data), "sha256": sha(data),
            "captured_at_utc": utc(),
        })

    for relative in sorted(selected):
        add(project / relative, "project/" + relative,
            required=relative in DATA_FILES + DOC_FILES + ["bot/run_bot.py"])
    if website is not None:
        website = Path(website).resolve(strict=True)
        for filename in ["index.html", "feed7.html"]:
            add(website / filename, "website/" + filename, required=True)

    # Record package versions without pip credentials, index URLs or env contents.
    versions = sorted(
        [{"name": dist.metadata.get("Name", "unknown"), "version": dist.version}
         for dist in importlib.metadata.distributions()],
        key=lambda x: (x["name"].lower(), x["version"]),
    )
    metadata = staging / "metadata"
    metadata.mkdir()
    package_bytes = json.dumps(versions, indent=2).encode()
    (metadata / "python-packages.json").write_bytes(package_bytes)
    os.chmod(metadata / "python-packages.json", 0o600)
    manifest["files"].append({
        "path": "metadata/python-packages.json",
        "bytes": len(package_bytes), "sha256": sha(package_bytes),
        "captured_at_utc": utc(),
    })
    manifest["capture_finished_utc"] = utc()
    manifest_path = capsule / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    os.chmod(manifest_path, 0o600)
    archive = capsule / "recovery.tar.gz"
    with tarfile.open(archive, "w:gz", dereference=False) as stream:
        for entry in manifest["files"]:
            stream.add(staging / entry["path"], arcname=entry["path"],
                       recursive=False)
        stream.add(manifest_path, arcname="manifest.json", recursive=False)
    os.chmod(archive, 0o600)

    restored = Path(tempfile.mkdtemp(prefix="futuresky-w7f2-restore-"))
    with tarfile.open(archive) as stream:
        # Only the regular files just captured are accepted.
        expected = {entry["path"] for entry in manifest["files"]} | {"manifest.json"}
        members = stream.getmembers()
        if {member.name for member in members} != expected:
            raise ValueError("Archive membership does not match manifest")
        if any(not member.isfile() for member in members):
            raise ValueError("Archive contains a non-regular member")
        stream.extractall(restored, filter="data")
    restored_manifest = json.loads((restored / "manifest.json").read_text())
    if restored_manifest != manifest:
        raise ValueError("Restored manifest differs")
    for entry in manifest["files"]:
        data = (restored / entry["path"]).read_bytes()
        if sha(data) != entry["sha256"] or len(data) != entry["bytes"]:
            raise ValueError("Restored file mismatch: " + entry["path"])
        if entry["path"].endswith(".json"):
            json.loads(data)
    room_file = restored / "project/data/rooms/rooms.json"
    rooms = json.loads(room_file.read_text())
    edges = [(src, direction, target)
             for src, value in rooms.items()
             for direction, target in value.get("exits", {}).items()]
    if any(target not in rooms for _, _, target in edges):
        raise ValueError("Restored map has missing exit targets")
    report = {
        "source_head": manifest["project_head"],
        "main_reference": manifest["main_reference"],
        "capsule_directory": str(capsule),
        "archive_sha256": sha(archive.read_bytes()),
        "archive_bytes": archive.stat().st_size,
        "restored_directory": str(restored),
        "file_count": len(manifest["files"]),
        "bytes_verified": sum(entry["bytes"] for entry in manifest["files"]),
        "json_files_parsed": sum(entry["path"].endswith(".json")
                                 for entry in manifest["files"]),
        "restored_rooms": len(rooms), "restored_exits": len(edges),
        "all_hashes_match": True, "atomic_world_snapshot": False,
        "missing_optional": manifest["missing_optional"],
        "verified_at_utc": utc(),
    }
    report_path = capsule / "verification.json"
    report_path.write_text(json.dumps(report, indent=2))
    os.chmod(report_path, 0o600)
    # Avoid retaining duplicate captured private data after archive verification.
    shutil.rmtree(staging)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--output-parent", required=True)
    parser.add_argument("--website")
    args = parser.parse_args()
    print(json.dumps(capture(args.project, args.output_parent, args.website)))


if __name__ == "__main__":
    main()
