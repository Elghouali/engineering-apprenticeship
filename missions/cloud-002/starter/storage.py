"""CLOUD-002 intentionally broken artifact publisher."""
import hashlib
from pathlib import Path
import shutil


def publish_artifact(source: Path, store_root: Path, key: str) -> dict:
    destination = store_root / key  # BUG: no key validation / path containment
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)  # BUG: silently overwrites existing artifact
    return {"key": key, "sha256": "", "size_bytes": 0}


def fetch_artifact(store_root: Path, key: str, expected_sha256: str) -> bytes:
    return (store_root / key).read_bytes()  # BUG: no integrity verification
