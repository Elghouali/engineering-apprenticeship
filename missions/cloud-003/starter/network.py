"""CLOUD-003 deliberately broken Compose service discovery and exposure."""
def design_stack() -> dict:
    return {
        "services": {
            "ledger": {
                "image": "python:3.11-alpine",
                "command": ["python", "/workspace/ledger.py"],
                "volumes": ["./runtime:/workspace:ro"],
                "ports": ["8090:8090"],  # Unsafe external ledger exposure.
                "networks": ["backend"],
            },
            "api": {
                "image": "python:3.11-alpine",
                "command": ["python", "/workspace/api.py"],
                "volumes": ["./runtime:/workspace:ro"],
                "environment": {"LEDGER_URL": "http://localhost:8090"},
                "ports": ["18081:8080"],  # Unsafe all-host binding.
                "networks": ["backend"],
            },
        },
        "networks": {"backend": {"driver": "bridge"}},
    }
