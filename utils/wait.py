import time
from collections.abc import Callable


def wait_until(condition: Callable[[], bool], timeout=10.0, interval=0.5, message=""):
    """Poll a backend condition. For UI checks use expect() instead."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(interval)
    raise AssertionError(message or f"condition not met within {timeout}s")
