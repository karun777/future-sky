"""Serve only the fictional preview assets, on loopback."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/hud.css": ("hud.css", "text/css; charset=utf-8"),
    "/scene.js": ("scene.js", "text/javascript; charset=utf-8"),
}

class PreviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ASSETS:
            self.send_error(404)
            return
        filename, content_type = ASSETS[self.path]
        body = (ROOT / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8779), PreviewHandler).serve_forever()
