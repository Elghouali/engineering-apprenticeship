"""Full localhost HTTP integration: source -> SQLite -> Gold -> HTTP JSON."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api import create_server, data_product
build = data_product.build

FIXTURE = ROOT / "data" / "orders.csv"


class APIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / "release"
        self.server = create_server(self.output, port=0)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def get(self, path):
        with urlopen(self.url + path, timeout=3) as response:
            return response.status, json.load(response)

    def test_unpublished_release_returns_503(self):
        with self.assertRaises(HTTPError) as exc:
            self.get("/health")
        self.assertEqual(exc.exception.code, 503)

    def test_real_data_can_be_queried_over_http(self):
        result = build(FIXTURE, self.output)
        code, health = self.get("/health")
        self.assertEqual(code, 200)
        self.assertEqual(health, {
            "status": "ok", "release_id": result["release_id"],
            "quality_passed": True,
        })
        code, revenue = self.get("/v1/revenue")
        self.assertEqual(revenue["paid_revenue_cents"], 22000)
        self.assertEqual(revenue["rows"], [{
            "order_date": "2026-11-20", "paid_orders": 3,
            "paid_revenue_cents": 22000,
        }])
        code, metadata = self.get("/v1/manifest")
        self.assertEqual(metadata["source_sha256"], result["source_sha256"])

    def test_corruption_causes_service_failure_not_fake_success(self):
        result = build(FIXTURE, self.output)
        path = self.output / "releases" / result["release_id"] / "gold.csv"
        path.write_bytes(b"incorrect,report\n")
        with self.assertRaises(HTTPError) as exc:
            self.get("/v1/revenue")
        self.assertEqual(exc.exception.code, 503)

    def test_unknown_route_404(self):
        with self.assertRaises(HTTPError) as exc:
            self.get("/not-a-route")
        self.assertEqual(exc.exception.code, 404)

    def test_server_refuses_public_network_binding(self):
        with self.assertRaisesRegex(ValueError, "loopback"):
            create_server(self.output, host="0.0.0.0", port=0)


if __name__ == "__main__":
    unittest.main()
