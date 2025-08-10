import datetime as _dt
import os
import socket
import sqlite3
import time
from typing import Dict, Tuple


def liveness_check() -> Tuple[bool, Dict[str, float]]:
    """Basic liveness check.

    Validates that the process is responsive and the system clock has not
    drifted excessively from UTC. Returns within ~1ms.
    """
    details: Dict[str, float] = {}
    try:
        now = time.time()
        utc_now = _dt.datetime.utcnow().timestamp()
        drift = abs(now - utc_now)
        details["clock_drift"] = drift
        ok = drift < 5  # seconds
    except Exception as exc:  # pragma: no cover - extremely unlikely
        details["error"] = str(exc)
        ok = False
    return ok, details


def _check_socket(host: str, port: int, timeout: float = 0.1) -> Tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "connected"
    except Exception as exc:
        return False, str(exc)


def _check_db(path: str) -> Tuple[bool, str]:
    try:
        if not os.path.exists(path):
            return False, "missing"
        con = sqlite3.connect(path, timeout=0.2)
        try:
            con.execute("PRAGMA quick_check")
        finally:
            con.close()
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def _check_dns(host: str) -> Tuple[bool, str]:
    try:
        socket.gethostbyname(host)
        return True, "resolved"
    except Exception as exc:
        return False, str(exc)


def readiness_check(host: str, port: int) -> Tuple[bool, Dict[str, str]]:
    """Readiness check with optional dependency probes.

    - Connect to the provided host/port if given.
    - If DB_PATH env is set, ensure the SQLite file is healthy.
    - Resolve an external hostname to verify DNS.
    """
    details: Dict[str, str] = {}
    ok = True

    if host and port:
        sock_ok, msg = _check_socket(host, port)
        details["socket"] = msg
        ok &= sock_ok

    db_path = os.environ.get("DB_PATH")
    if db_path:
        db_ok, msg = _check_db(db_path)
        details["db"] = msg
        ok &= db_ok

    dns_ok, msg = _check_dns("www.google.com")
    details["dns"] = msg
    ok &= dns_ok

    return bool(ok), details
