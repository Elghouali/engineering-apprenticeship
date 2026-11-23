"""Synthetic reporting API: reads real ledger over service DNS."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.request import urlopen

LEDGER_URL = os.environ.get("LEDGER_URL", "")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health":
            self.send_error(404)
            return
        try:
            with urlopen(LEDGER_URL + "/balance", timeout=2) as response:
                amount = json.load(response)["balance_cents"]
            status, payload = 200, {"status": "ok", "ledger_balance_cents": amount}
        except Exception:
            status, payload = 503, {"status": "unavailable"}
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        pass

HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
