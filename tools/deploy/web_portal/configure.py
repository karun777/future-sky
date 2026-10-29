"""Run interactively over SSH to stage OAuth config outside Git; never activates it."""
import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def main():
    if not sys.stdin.isatty():
        raise SystemExit("Run this directly in an interactive SSH terminal.")
    characters = json.loads(Path(
        "/opt/futuresky/bot/data/characters/characters.json").read_text())
    owners = [uid for uid, c in characters.items()
              if isinstance(c, dict) and str(c.get("name", "")).casefold() == "efiishent"
              and isinstance(uid, str) and uid.isascii() and uid.isdecimal()]
    if len(owners) != 1:
        raise SystemExit("Expected one existing Efiishent account; nothing saved.")
    secret = getpass.getpass("Paste Discord OAuth2 client secret (input hidden): ").strip()
    if not re.fullmatch(r"[A-Za-z0-9._~-]{16,256}", secret):
        raise SystemExit("Secret format not recognised; nothing saved.")
    folder = Path.home() / ".config" / "future-sky"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    folder.chmod(0o700)
    destination = folder / "web-portal.env"
    content = ("FS_WEB_ENABLED=0\n"
               "FS_WEB_DISCORD_CLIENT_ID=1348670557314482267\n"
               "FS_WEB_DISCORD_CLIENT_SECRET=" + secret + "\n"
               "FS_WEB_ALLOWED_DISCORD_IDS=" + owners[0] + "\n")
    fd, temporary = tempfile.mkstemp(prefix=".web-portal-", dir=folder)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print("OAuth configuration saved privately. Portal remains disabled; bot unchanged.")


if __name__ == "__main__":
    main()
