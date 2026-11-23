"""CLOUD-006 intentionally broken Kubernetes Deployment/Service."""
def build_resources() -> dict:
    return {
        "deployment": {
            "apiVersion": "apps/v1", "kind": "Deployment",
            "metadata": {"name": "reports-api"},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "reports-api"}},
                "template": {
                    "metadata": {"labels": {"app": "reports-api"}},
                    "spec": {"containers": [{
                        "name": "api", "image": "nginx:1.28-alpine",
                        "ports": [{"containerPort": 80}],
                        "readinessProbe": {"httpGet": {"path": "/missing",
                                                       "port": 80}},
                    }]}
                }
            }
        },
        "service": {
            "apiVersion": "v1", "kind": "Service",
            "metadata": {"name": "reports-api"},
            "spec": {"type": "ClusterIP",
                     "selector": {"app": "old-api"},
                     "ports": [{"port": 80, "targetPort": 80}]}
        }
    }
