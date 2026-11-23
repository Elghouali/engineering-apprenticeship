"""CLOUD-001 deliberately broken but bounded starter (no infinite loop)."""
import time


def fetch_report(url, transport, attempts=3, sleep=None):
    if sleep is None:
        sleep = time.sleep
    # BUG: treats all HTTP errors the same; wrong backoff and error contract.
    # BUG: does not handle ConnectionError/TimeoutError and invalid attempts.
    for trial in range(attempts):
        status, body = transport(url)
        if status == 200:
            return {"status": 200, "body": body, "attempts": 1}
        sleep(0.01)
    raise RuntimeError("upstream_failed")
