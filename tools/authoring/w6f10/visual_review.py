"""Loopback-only W6-F10 visual fixture. No OAuth, live API or player-store access.

Run from a Git checkout:
  python3 tools/authoring/w6f10/visual_review.py --port 8766
Open /play/ for the unchanged client, /review/ for visible fixture controls.
Only the review HTML title/brand/image CSP differ from the production document.
Client scripts/CSS remain byte-for-byte source copies. Artwork is public/read-only.
"""
import argparse
from copy import deepcopy
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
CLIENT = ROOT / "tools/authoring/w6f8/live"
WARNING = "A choice or encounter needs your attention in Discord."
IMAGE = "https://future-sky.net/assets/images/world/manzo/triton_central/neptune_lounge/pod/v1/p01.png"
STATE = {"mode": "blocked", "room": "pod_room", "reads": 0, "posts": []}
BASE = {
    "session": {"csrf": "fictional-review"},
    "character": {"name": "Review Traveller (fictional)", "credits": 0},
    "sheet": {"class_id": "Dreamer Technician", "stats": {"hp": 10, "max_hp": 10}},
    "inventory": {"bag": [{"name": "Review coat", "quantity": 1}], "equipped": {}},
    "journal": {"entries": []}, "display": {"enabled": True, "state": "normal"},
    "idle_home": {"enabled": False}, "wardrobe": {"available": False, "options": []},
}

def view():
    result = deepcopy(BASE)
    blocked = STATE["mode"] == "blocked"
    distinct = STATE["mode"] == "distinct"
    pod = STATE["room"] == "pod_room"
    result["location"] = {
        "id": STATE["room"],
        "title": ("Pod Room" if pod else "Hallway") + " — Fictional review",
        "description": "Fictional review data. Your live character is not connected.\n\n"
                       "The pod image and game-window layout are the existing assets.",
        "image": IMAGE,
    }
    result["walking"] = {
        "token": "fictional-walk", "exits": [] if blocked or distinct else ["west" if pod else "east"],
        "notice": WARNING if blocked else ("Your sequence is running. Wait for it to finish." if distinct else ""),
    }
    result["inspection"] = {
        "token": "fictional-inspect", "targets": [] if blocked or distinct or not pod else ["hands", "panels"],
        "notice": WARNING if blocked else ("Inspection is unavailable while the game connection recovers." if distinct else ""),
    }
    return result

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, content_type="application/json"):
        if not isinstance(body, bytes):
            body = (json.dumps(body) if content_type == "application/json" else body).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/", "/play/"):
            html = (CLIENT / "index.html").read_text()
            html = html.replace("<title>Future Sky — Live world</title>",
                                "<title>Future Sky — FICTIONAL W6-F10 review</title>")
            html = html.replace("✧ FUTURE SKY</a>", "✧ FUTURE SKY · FICTIONAL REVIEW</a>")
            html = html.replace("img-src 'self';", "img-src 'self' https://future-sky.net;")
            return self.reply(200, html, "text/html; charset=utf-8")
        prefix = "/assets/experiments/w6-f8/live/"
        if path.startswith(prefix) and path[len(prefix):] in {"game.js", "frame.js", "frame.css"}:
            name = path[len(prefix):]
            mime = "text/css" if name.endswith(".css") else "text/javascript"
            return self.reply(200, (CLIENT / name).read_bytes(), mime)
        if path == "/play/api/me":
            STATE["reads"] += 1
            return self.reply(200, view())
        if path == "/review/":
            buttons = "".join('<button name="mode" value="' + mode + '">' + label + '</button> '
                              for mode, label in [("blocked", "Block encounter"), ("clear", "Clear encounter"),
                                                  ("distinct", "Show distinct notices")])
            return self.reply(200, '<!doctype html><meta charset="utf-8"><title>Fictional review controls</title>'
                              '<h1>W6-F10 — Fictional review controls</h1>'
                              '<p>Loopback only. No live game, Discord, OAuth or player records.</p>'
                              '<form method="post" action="/review/state">' + buttons + '</form>'
                              '<p><a href="/play/" target="_blank">Open fictional game window</a></p>'
                              '<pre>' + escape(json.dumps(STATE, indent=2)) + '</pre>',
                              "text/html; charset=utf-8")
        if path == "/favicon.ico":
            return self.reply(204, b"", "image/x-icon")
        return self.reply(404, {"error": "This route is outside the fictional review."})

    def do_POST(self):
        path = urlsplit(self.path).path
        size = int(self.headers.get("Content-Length", "0"))
        if size > 4096:
            return self.reply(413, {"error": "Request too large."})
        body = self.rfile.read(size)
        if path == "/review/state":
            mode = parse_qs(body.decode()).get("mode", [""])[0]
            if mode not in {"blocked", "clear", "distinct"}:
                return self.reply(400, {"error": "Unknown fixture."})
            STATE["mode"] = mode
            self.send_response(303)
            self.send_header("Location", "/review/")
            self.end_headers()
            return
        if path not in {"/play/api/walk", "/play/api/inspect", "/play/api/wardrobe", "/play/logout"}:
            return self.reply(404, {"error": "No external forwarding."})
        STATE["posts"].append(path)
        if path == "/play/logout":
            return self.reply(204, b"")
        if STATE["mode"] != "clear":
            return self.reply(409, {"ok": False, "message": WARNING})
        request = json.loads(body or "{}")
        if path == "/play/api/walk":
            direction = "west" if STATE["room"] == "pod_room" else "east"
            if request.get("direction") != direction:
                return self.reply(400, {"ok": False, "message": "Choose an offered direction."})
            STATE["room"] = "hallway" if direction == "west" else "pod_room"
            return self.reply(200, {"ok": True, "message": "Fictional walk completed."})
        if path == "/play/api/inspect":
            return self.reply(200, {"ok": True, "observation": {
                "title": "Fictional inspection", "text": "The command reached the local review fixture.",
                "guidance": "Type look to return.", "image": IMAGE}})
        return self.reply(409, {"ok": False, "message": "No wardrobe actions in this visual fixture."})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Fictional HUD: http://127.0.0.1:{args.port}/play/", flush=True)
    print(f"Fixture controls: http://127.0.0.1:{args.port}/review/", flush=True)
    server.serve_forever()
