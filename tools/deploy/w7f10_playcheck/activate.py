"""Three-file W7-F10 playcheck correction; never changes data or starts services."""
import argparse
import json
import os
from pathlib import Path
from tools.deploy.w7f10.activate import Deployment, check
from tools.character_reset_adapter import Refused, offline_guard, runtime_check

HERE = Path(__file__).resolve().parent
LIVE = Path("/opt/futuresky")
STATE = LIVE / "backups/w7f10-playcheck"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["check", "verify", "install", "rollback"])
    args = parser.parse_args()
    manifest = json.loads((HERE / "deployment-manifest.json").read_text())
    if args.operation in {"check", "verify"}:
        check(HERE / "delivery", LIVE, manifest, installed=args.operation == "verify")
        print("Three-file contract verified; preserved code and HUD assets match. No live changes.")
        return
    if os.geteuid() != 0:
        raise Refused("Privileged operator terminal required")
    if args.operation == "install":
        runtime_check()
    with Deployment(HERE / "delivery", LIVE, LIVE / "data", STATE, manifest, offline_guard) as deployment:
        getattr(deployment, args.operation)()
    print("Playcheck code transaction verified. Service remains stopped; no data/configuration changed.")

if __name__ == "__main__":
    main()
