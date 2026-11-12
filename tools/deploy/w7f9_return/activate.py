"""Three-file guided-pod return correction. No data edits or service control."""
import argparse
import json
import os
from pathlib import Path
from tools.deploy.w7f10.activate import Deployment, check, sha, ROOT
from tools.character_reset_adapter import Refused, offline_guard, runtime_check, runtime_code_check

HERE = Path(__file__).resolve().parent
LIVE = Path("/opt/futuresky")
STATE = LIVE / "backups/w7f9-return"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["check", "preflight", "verify", "install", "rollback"])
    args = parser.parse_args()
    manifest_path = HERE / "deployment-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    baseline = HERE / "baseline-runtime.json"
    if sha(baseline) != manifest["basis"]["baseline_runtime_sha256"]:
        raise Refused("Reviewed baseline contract changed")
    current = json.loads((ROOT / "tools/deploy/w7f10/runtime-manifest.json").read_text())
    if current["basis"]["return_manifest_sha256"] != sha(manifest_path):
        raise Refused("Current runtime contract does not bind this return correction")
    for relative, entry in manifest["files"].items():
        if sha(ROOT / relative) != entry["source"]:
            raise Refused("Source differs from reviewed delivery: " + relative)
    if args.operation in {"check", "preflight", "verify"}:
        check(HERE / "delivery", LIVE, manifest, installed=args.operation == "verify")
        contract = None if args.operation == "verify" else baseline
        runtime_code_check(manifest_path=contract)
        if args.operation == "preflight":
            if os.geteuid() != 0:
                raise Refused("Privileged preflight required to read restart configuration")
            runtime_check(manifest_path=baseline)
            print("Restart preflight passed.")
        print("Return code contract verified: three files and preserved code/assets. No live changes.")
        return
    if os.geteuid() != 0:
        raise Refused("Privileged operator terminal required")
    if args.operation == "install":
        runtime_check(manifest_path=baseline)
    with Deployment(HERE / "delivery", LIVE, LIVE / "data", STATE, manifest, offline_guard) as deployment:
        getattr(deployment, args.operation)()
    print("Return code transaction verified. Service remains stopped; no data/configuration changed.")


if __name__ == "__main__":
    main()
