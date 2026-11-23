"""Public Kubernetes incident contract tests; no cluster needed locally."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[3]
SUBMISSION=Path(os.environ.get("APPRENTICE_SUBMISSION_PATH",
                    str(ROOT/"submissions/cloud-006/k8s.py")))

class K8sTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing cloud-006 submission")
        spec=importlib.util.spec_from_file_location("cloud006", SUBMISSION)
        mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=mod
        spec.loader.exec_module(mod)
        cls.resources=mod.build_resources()

    def test_correct_kubernetes_objects(self):
        self.assertEqual(set(self.resources),{"deployment","service"})
        deployment=self.resources["deployment"]
        service=self.resources["service"]
        self.assertEqual((deployment["apiVersion"],deployment["kind"],
                          deployment["metadata"]["name"]),
                         ("apps/v1","Deployment","reports-api"))
        self.assertEqual((service["apiVersion"],service["kind"],
                          service["metadata"]["name"]),
                         ("v1","Service","reports-api"))

    def test_replica_and_rolling_update_strategy(self):
        spec=self.resources["deployment"]["spec"]
        self.assertEqual(spec["replicas"],2)
        self.assertEqual(spec["strategy"]["type"],"RollingUpdate")
        self.assertEqual(spec["strategy"]["rollingUpdate"],
                         {"maxSurge":1,"maxUnavailable":0})

    def test_service_selects_real_pods(self):
        spec=self.resources["deployment"]["spec"]
        labels={"app":"reports-api"}
        self.assertEqual(spec["selector"]["matchLabels"],labels)
        self.assertEqual(spec["template"]["metadata"]["labels"],labels)
        svc=self.resources["service"]["spec"]
        self.assertEqual(svc["type"],"ClusterIP")
        self.assertEqual(svc["selector"],labels)
        self.assertEqual(svc["ports"],[{"port":80,"targetPort":80}])

    def test_readiness_and_liveness_probes_work(self):
        container=self.resources["deployment"]["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["name"],"api")
        self.assertEqual(container["image"],"nginx:1.28-alpine")
        self.assertEqual(container["ports"],[{"containerPort":80}])
        self.assertEqual(container["readinessProbe"],
                         {"httpGet":{"path":"/","port":80},
                          "initialDelaySeconds":1,"periodSeconds":2})
        self.assertEqual(container["livenessProbe"],
                         {"httpGet":{"path":"/","port":80},
                          "initialDelaySeconds":5,"periodSeconds":5})

    def test_bounded_resources_no_host_escape(self):
        pod=self.resources["deployment"]["spec"]["template"]["spec"]
        self.assertFalse(pod.get("hostNetwork"))
        self.assertFalse(pod.get("hostPID"))
        container=pod["containers"][0]
        self.assertEqual(container["resources"],{
            "requests":{"cpu":"50m","memory":"32Mi"},
            "limits":{"cpu":"250m","memory":"128Mi"}
        })
        self.assertIsNot(container.get("securityContext",{}).get("privileged"), True)
        self.assertNotIn("hostPath",str(self.resources))
        self.assertEqual(len(pod["containers"]),1)

if __name__=="__main__":
    unittest.main()
