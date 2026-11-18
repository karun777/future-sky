"""Future Sky's normal web app with synthetic identities and a separate realm.

Run with the installed code-only participation wheel on PYTHONPATH.
The fake OAuth provider and HTTP-only cookie override belong to this local harness.
"""
import argparse
import html
import os
from pathlib import Path
import secrets
from types import SimpleNamespace

from aiohttp import web
from engine.participation.desk import Binding, Desk
from engine.participation.undertakings import UndertakingStore
from fsbot import web_portal
from .fixtures import create

HERE = Path(__file__).parent
CAST = {
    "101": ("maker", "Sable · Briefing coordinator"),
    "102": ("reader", "Efiishent · Invited reader"),
    "103": ("successor", "Tavi · Nominated reader"),
    "104": ("convenor", "Oriel · Convenor"),
    "105": ("visitor", "A passing traveller"),
}


class RehearsalOAuth:
    def __init__(self):
        self.pending = set()

    async def authorize(self):
        state = secrets.token_urlsafe(24)
        if len(self.pending) >= 100:
            self.pending.clear()
        self.pending.add(state)
        return "/rehearsal/choose?state=" + state, state

    async def identity(self, code, state):
        if state not in self.pending or code not in CAST:
            raise ValueError("Unknown synthetic identity")
        self.pending.remove(state)
        return code


def make_app(store):
    bindings = {uid: Binding(actor, store.realm+"."+actor, "circle", actor, "desk", "case")
                for uid, (actor, _) in CAST.items()}
    desk = Desk(store, bindings)
    bot = SimpleNamespace(
        storage=SimpleNamespace(
            characters={uid: {"name": label.split(" · ")[0], "current_room": "pod_room",
                              "extra": {}, "bag": {}, "equipped": {}} for uid, (_, label) in CAST.items()},
            rooms={"pod_room": {"title": "Morning after · isolated scene"}}, items_db={}),
        is_ready=lambda: True, get_cog=lambda name: None)
    config = web_portal.WebConfig("123456", "synthetic-provider", frozenset(CAST))
    app = web_portal.create_app(bot, config, oauth=RehearsalOAuth(), participation=desk)

    async def page(request):
        return web.FileResponse(HERE / "page.html")

    async def asset(request):
        name = request.match_info["name"]
        if name not in {"screen.css", "screen.js"}:
            raise web.HTTPNotFound()
        return web.FileResponse(HERE / name)

    async def choose(request):
        state = request.query.get("state", "")
        links = "".join(
            '<li><a href="/play/auth/callback?code='+uid+'&amp;state='+html.escape(state, quote=True)+'">'
            +html.escape(label)+'</a></li>' for uid, (_, label) in CAST.items())
        return web.Response(text='<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<link rel="stylesheet" href="/rehearsal/static/screen.css">'
            '<title>Choose a synthetic reader</title><main class="login">'
            '<p>Local rehearsal · synthetic identities</p><h1>Choose your perspective</h1><ul>'+links+'</ul></main></html>',
            content_type="text/html")

    async def redirect(request):
        raise web.HTTPFound("/rehearsal/desk")

    app.add_routes([web.get("/rehearsal/desk", page),
                    web.get("/rehearsal/choose", choose),
                    web.get("/rehearsal/static/{name}", asset),
                    web.get("/assets/experiments/w6-f8/live/index.html", redirect)])
    return app


def main():
    parser = argparse.ArgumentParser(description="Synthetic crew briefing using Future Sky's web app")
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8776)
    args = parser.parse_args()
    args.state = args.state.resolve()
    repository = Path(__file__).resolve().parents[3]
    if args.state == repository or repository in args.state.parents:
        parser.error("Keep rehearsal state outside the repository")
    os.umask(0o077)
    args.state.mkdir(mode=0o700, parents=True, exist_ok=True)
    if args.state.stat().st_mode & 0o077:
        parser.error("Use a private state directory")
    path = args.state / "crew.sqlite3"
    if not path.exists():
        create(path, "future-sky-rehearsal", title="Dragonfly Rescue · Crew briefing",
               brief="An invitation to receive the comet-catching briefing. A crew berth is still an authoring question.",
               content="Meet for drinks and briefing at Neptune Lounge. Routine comet catch out of Triton Central.")
    store = UndertakingStore(path, "future-sky-rehearsal")
    with store.transaction():
        pass
    # This isolated process binds only to loopback and uses a synthetic OAuth provider.
    web_portal.ORIGIN = "http://127.0.0.1:" + str(args.port)
    def local_cookie(response, name, value, max_age):
        response.set_cookie(name.replace("__Host-", ""), value, max_age=max_age,
                            httponly=True, samesite="Lax", path="/")
    web_portal.LOGIN_COOKIE = "fs-rehearsal-login"
    web_portal.SESSION_COOKIE = "fs-rehearsal-session"
    web_portal.cookie = local_cookie
    web.run_app(make_app(store), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
