"""Private W4-F13 text rehearsal. Run from the worktree with PYTHONPATH=bot:tests."""
import argparse
import asyncio
from contextlib import asynccontextmanager, contextmanager
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import aiohttp
from aiohttp.test_utils import TestClient, TestServer
from fsbot.pod_opening import OPENING
from fsbot.storage import save_json
from fsbot.web_portal import create_app, WebConfig, ORIGIN, LOGIN_COOKIE, SESSION_COOKIE
from test_shared_walking import fixture
from test_web_portal import FakeOAuth
from workspace_scene import WorkspaceScene, READER, USE, MARK, LEAVE


@contextmanager
def fictional_save():
    with TemporaryDirectory(prefix="w4f13-fiction-") as directory:
        path = Path(directory) / "readers.json"
        bot, _, _, _ = fixture()
        for character in bot.storage.characters.values():
            character.update(name="Efiishent", current_room="pod_room", extra={
                "arrival": {"opening": {"id": OPENING, "discoveries": ["hands"]}}
            })
        save_json(str(path), bot.storage.characters)
        yield path


@asynccontextmanager
async def rehearsal(path):
    bot, nav, _, _ = fixture()
    storage = bot.storage
    storage.characters = json.loads(path.read_text())
    storage.save_characters = lambda: save_json(str(path), storage.characters)
    storage.rooms = {
        "pod_room": {"title": "Pod", "exits": {"west": "hall"}},
        "hall": {"title": "Hallway", "exits": {"east": "pod_room"}},
    }
    oauth = FakeOAuth()
    scene = WorkspaceScene(bot, nav)
    # Stand-ins are attached only inside this process. The real HTTP handlers
    # still own session identity, offers, validation and navigation.
    with (patch("fsbot.pod_inspection.web_targets", scene.targets),
          patch("fsbot.pod_inspection.inspect_pod", scene.inspect)):
        config = WebConfig("1000", "fixture", frozenset(storage.characters))
        server = TestServer(create_app(bot, config, oauth=oauth), host="127.0.0.1")
        async with TestClient(server, cookie_jar=aiohttp.DummyCookieJar()) as client:
            yield Window(client, oauth), bot, nav


class Window:
    def __init__(self, client, oauth):
        self.client = client
        self.oauth = oauth

    async def sign_in(self, fixture_actor):
        # Harness control. Only FakeOAuth supplies identities, never a game command.
        self.oauth.uid = fixture_actor
        start = await self.client.get("/play/auth/discord", allow_redirects=False)
        nonce = start.cookies[LOGIN_COOKIE].value
        result = await self.client.get("/play/auth/callback?code=fixture&state=test-state",
                                       headers={"Cookie": f"{LOGIN_COOKIE}={nonce}"},
                                       allow_redirects=False)
        if result.status != 302:
            raise RuntimeError("Fixture sign-in failed.")
        return {"Cookie": f"{SESSION_COOKIE}={result.cookies[SESSION_COOKIE].value}"}

    async def view(self, auth):
        response = await self.client.get("/play/api/me", headers=auth)
        response.raise_for_status()
        return await response.json()

    async def post(self, auth, view, kind, payload):
        headers = {**auth, "Origin": ORIGIN, "X-CSRF-Token": view["session"]["csrf"]}
        return await self.client.post(f"/play/api/{kind}", json=payload, headers=headers)

    async def command(self, auth, line):
        line = " ".join(line.strip().removeprefix("!").lower().split())
        view = await self.view(auth)
        inspection = view["inspection"]
        if line == "look":
            room = view["location"]
            return room["title"] + "\n" + room["description"]
        if line in {"commands", "help"}:
            choices = [t if t.startswith("console ") else "inspect " + t
                       for t in inspection["targets"]]
            choices.extend("go " + d for d in view["walking"]["exits"])
            return ", ".join(["look", *choices])
        if line.startswith("go "):
            payload = {"direction": line[3:], "token": view["walking"]["token"]}
            response = await self.post(auth, view, "walk", payload)
            if response.status == 200:
                return (await self.view(auth))["location"]["title"]
            return view["walking"]["notice"] or "That exit is unavailable."
        if line in (USE, MARK, LEAVE):
            target = line
        elif line.startswith("inspect ") and not line[8:].startswith("console "):
            target = line[8:]
        else:
            return "That command is unavailable. Type commands to see what you can do."
        if target not in inspection["targets"]:
            if inspection["notice"]:
                return inspection["notice"]
            if target == USE and "note" in inspection["targets"]:
                return "You find the slip still folded. Try inspect note."
            if target == MARK and "sketch" in inspection["targets"]:
                return "Open the sketch first with inspect sketch."
            return "That detail is unavailable. Type commands for the current choices."
        response = await self.post(auth, view, "inspect", {"target": target, "token": inspection["token"]})
        if response.status != 200:
            return await response.text()
        observation = (await response.json())["observation"]
        return "\n".join(observation[k] for k in ("title", "text", "guidance"))


DEMO = ("inspect pod", "inspect berth", "inspect console", "inspect note", USE,
        "inspect probe slip", "inspect sketch", MARK, LEAVE, "go west", "go east", USE)


async def main(interactive):
    with fictional_save() as path:
        async with rehearsal(path) as (window, _, _):
            auth = await window.sign_in(READER)
            print("Fictional pod rehearsal. Type commands for current actions, or quit.")
            if interactive:
                print(await window.command(auth, "look"))
                while True:
                    try:
                        line = input("> ")
                    except EOFError:
                        return
                    if line.strip().lower() == "quit":
                        return
                    print(await window.command(auth, line))
            else:
                for line in DEMO:
                    print(f"\n> {line}")
                    print(await window.command(auth, line))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interactive", action="store_true")
    asyncio.run(main(parser.parse_args().interactive))
