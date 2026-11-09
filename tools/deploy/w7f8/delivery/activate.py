"""Selective personal-delivery correction; reuse validated code-only rollback."""
import importlib.util
from pathlib import Path
import os
import sys

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("w7f8_activation", here.parent / "activate.py")
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)
deploy.HERE = here

if __name__ == "__main__":
    manifest = deploy.preflight()
    if "--check" in sys.argv:
        print("Delivery correction preflight passed: one backend file, HTML and game.js; no writes.")
    elif os.geteuid() != 0:
        raise SystemExit("Activation requires sudo; --check is read-only.")
    else:
        deploy.activate(manifest)
