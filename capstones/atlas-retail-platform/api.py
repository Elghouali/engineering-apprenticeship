"""Localhost-only reporting API for the Atlas Retail capstone.

No external web framework or cloud account required.
Do not expose this training server to the public internet.
"""
from __future__ import annotations
import argparse
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from platform import verify


def create_server(output: Path, host: str = "127.0.0.1", port: int = 0):
    if host != "127.0.0.1":
        raise ValueError("training_api_must_bind_loopback")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path not in ("/health", "/v1/revenue", "/v1/manifest"):
                return self.respond(404, {"error": "not_found"})
            try:
                manifest = verify(output)
                if path == "/health":
                    payload = {
                        "status": "ok",
                        "release_id": manifest["release_id"],
                        "quality_passed": manifest["quality_passed"],
                    }
                elif path == "/v1/manifest":
                    payload = {
                        "release_id": manifest["release_id"],
                        "generated_at_utc": manifest["generated_at_utc"],
                        "latest_order_date": manifest["latest_order_date"],
                        "source_sha256": manifest["source_sha256"],
                    }
                else:
                    report = output / "releases" / manifest["release_id"] / "gold.csv"
                    with report.open(newline="", encoding="utf-8") as file:
                        rows = [
                            {"order_date": row["order_date"],
                             "paid_orders": int(row["paid_orders"]),
                             "paid_revenue_cents": int(row["paid_revenue_cents"])}
                            for row in csv.DictReader(file)
                        ]
                    payload = {
                        "release_id": manifest["release_id"],
                        "paid_revenue_cents": manifest["paid_revenue_cents"],
                        "rows": rows,
                    }
                return self.respond(200, payload)
            except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError):
                return self.respond(503, {"error": "release_unavailable"})

        def respond(self, code: int, payload: dict):
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            # Default access logs include requested paths but no sensitive input data.
            return super().log_message(fmt, *args)

    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description="Atlas Retail local reporting API")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()
    with create_server(args.output, port=args.port) as server:
        print(f"Reporting API listening at http://127.0.0.1:{server.server_port}",
              flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
