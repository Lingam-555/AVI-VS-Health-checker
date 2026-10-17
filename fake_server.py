import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

USER = "admin"
PASSWORD = os.environ.get("FAKE_PASSWORD", "")
TOKEN = "tok-12345"

with open("vs_status.json") as f:
    VS_DATA = json.load(f)

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/login":
            self._send(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        creds = json.loads(self.rfile.read(length) or b"{}")
        if PASSWORD and creds.get("username") == USER and creds.get("password") == PASSWORD:
            self._send(200, {"token": TOKEN})
        else:
            self._send(401, {"error": "bad credentials"})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path not in ("/vs_status.json", "/vs_pages"):
            self._send(404, {"error": "not found"})
            return
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            self._send(401, {"error": "login required"})
            return
        if parsed.path == "/vs_status.json":
            self._send(200, VS_DATA)
            return
        page = int(parse_qs(parsed.query).get("page", ["1"])[0])
        items = VS_DATA["virtual_services"]
        size = 2
        chunk = items[(page - 1) * size: page * size]
        body = {"count": len(items), "results": chunk}
        if page * size < len(items):
            body["next"] = f"http://127.0.0.1:8000/vs_pages?page={page + 1}"
        self._send(200, body)

HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()