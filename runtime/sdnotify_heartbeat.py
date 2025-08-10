import os
import threading
import time
from typing import Optional

try:  # optional dependency
    from sdnotify import SystemdNotifier
except Exception:  # pragma: no cover
    SystemdNotifier = None  # type: ignore


class SdNotifyHeartbeat:
    """Systemd READY and WATCHDOG notifications."""

    def __init__(self) -> None:
        self._notifier: Optional[SystemdNotifier] = None
        self._interval: Optional[float] = None
        if SystemdNotifier and os.getenv("NOTIFY_SOCKET"):
            self._notifier = SystemdNotifier()
            watchdog = os.getenv("WATCHDOG_USEC")
            if watchdog:
                self._interval = max(int(watchdog) / 1_000_000 / 2, 1)

    def notify_ready(self) -> None:
        if self._notifier:
            self._notifier.notify("READY=1")

    def start(self) -> None:
        if self._notifier and self._interval:
            thread = threading.Thread(target=self._loop, daemon=True)
            thread.start()

    def _loop(self) -> None:
        while True:
            assert self._notifier is not None
            self._notifier.notify("WATCHDOG=1")
            time.sleep(self._interval)
