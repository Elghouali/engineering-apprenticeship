"""CLOUD-001 starter: intentionally unsafe unlimited retry pattern."""
import time


def fetch_report(url, transport, attempts=3, sleep=None):
    if sleep is None:
        sleep = time.sleep
    # BUG: ignores attempts, replays all errors, and can loop forever.
    while True:
        status, body = transport(url)
        if status == 200:
            return {"status": 200, "body": body, "attempts": 1}
        sleep(0.01)
