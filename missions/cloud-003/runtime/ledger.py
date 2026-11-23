"""Synthetic internal ledger; public fixture, not an exercise solution."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/balance":
            self.send_error(404)
            return
        body = json.dumps({"balance_cents": 12345}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        pass

HTTPServer(("0.0.0.0", 8090), Handler).serve_forever()
