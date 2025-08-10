import os
import socket
import sys
import tempfile
import logging
from typing import Iterable

logger = logging.getLogger(__name__)


def validate_startup(required_envs: Iterable[str] | None = None) -> None:
    """Validate runtime configuration and exit with explicit codes."""
    required_envs = list(required_envs or [])

    if sys.version_info < (3, 11):
        logger.error("Python 3.11+ required")
        sys.exit(2)

    missing = [env for env in required_envs if not os.getenv(env)]
    if missing:
        logger.error("Missing environment variables: %s", ",".join(missing))
        sys.exit(2)

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    sock = socket.socket()
    try:
        sock.bind((host, port))
    except OSError:
        logger.error("Port %s is unavailable on host %s", port, host)
        sys.exit(3)
    finally:
        sock.close()

    try:
        tmpdir = tempfile.gettempdir()
        testfile = os.path.join(tmpdir, "fh_perm_test")
        with open(testfile, "w"):
            pass
        os.remove(testfile)
    except Exception:
        logger.error("No write permissions for temp dir %s", tmpdir)
        sys.exit(2)

    db_path = os.getenv("DB_PATH")
    if db_path and not os.path.exists(db_path):
        logger.error("DB_PATH %s not found", db_path)
        sys.exit(4)
