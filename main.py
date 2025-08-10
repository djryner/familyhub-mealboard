"""Main entry point for FamilyHub Flask application."""

import logging
import os
import time
from werkzeug.serving import make_server

from app import app  # noqa: E402
import routes  # noqa: F401,E402
from app_health import setup_health  # noqa: E402
from bootstrap.validate_startup import validate_startup  # noqa: E402
from runtime.sdnotify_heartbeat import SdNotifyHeartbeat  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logging.Formatter.converter = time.gmtime
logger = logging.getLogger("familyhub")


def _env_bool(name: str, default: str = "true") -> bool:
    return os.getenv(name, default).lower() in {"1", "true", "yes", "on"}


def main() -> None:
    validate_startup()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    health_enabled = _env_bool("FAMILYHUB_HEALTH_ENABLED", "true")

    notifier = SdNotifyHeartbeat() if health_enabled else None
    if health_enabled:
        setup_health(app, host, port)
    logger.info(
        "FamilyHub starting host=%s port=%s health=%s watchdog=%s",
        host,
        port,
        health_enabled,
        bool(notifier and notifier._interval),
    )

    server = make_server(host, port, app)
    if notifier:
        notifier.notify_ready()
        notifier.start()
        logger.info("READY=1 sent")
    server.serve_forever()


if __name__ == "__main__":
    main()
