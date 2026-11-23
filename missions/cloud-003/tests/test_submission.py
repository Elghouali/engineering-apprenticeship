"""Public Docker Compose contract grader; does not execute containers."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = Path(os.environ.get("APPRENTICE_SUBMISSION_PATH",
                      str(ROOT / "submissions/cloud-003/network.py")))

class NetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing cloud-003 submission")
        spec = importlib.util.spec_from_file_location("cloud003", SUBMISSION)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls.stack = mod.design_stack()

    def test_bridge_and_shared_service_network(self):
        self.assertEqual(set(self.stack["services"]), {"api", "ledger"})
        self.assertEqual(self.stack["networks"]["backend"]["driver"], "bridge")
        for service in self.stack["services"].values():
            self.assertIn("backend", service["networks"])
            self.assertNotIn("network_mode", service)
            self.assertIsNot(service.get("privileged"), True)

    def test_dns_hostname_not_localhost(self):
        self.assertEqual(self.stack["services"]["api"]["environment"]["LEDGER_URL"],
                         "http://ledger:8090")

    def test_only_loopback_api_port_exposed(self):
        self.assertFalse(self.stack["services"]["ledger"].get("ports"))
        self.assertEqual(self.stack["services"]["api"]["ports"],
                         ["127.0.0.1:18081:8080"])

    def test_runtime_is_same_checked_in_fixture(self):
        for name in ("api", "ledger"):
            svc = self.stack["services"][name]
            self.assertEqual(svc["image"], "python:3.11-alpine")
            self.assertEqual(svc["command"], ["python", "/workspace/" + name + ".py"])
            self.assertIn("./runtime:/workspace:ro", svc["volumes"])
            self.assertFalse(svc.get("secrets"))
            self.assertFalse(svc.get("devices"))

    def test_forbid_host_privilege_or_socket(self):
        text = str(self.stack)
        for banned in ("/var/run/docker.sock", "network_mode': 'host",
                       "pid': 'host", "cap_add"):
            self.assertNotIn(banned, text)

if __name__ == "__main__":
    unittest.main()
