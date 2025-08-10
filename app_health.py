import json
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Optional

from health.health_check import liveness_check, readiness_check


def _json_response(check_fn: Callable[[], Any]) -> tuple[str, int]:
    ok, details = check_fn()
    status = "ok" if ok else "fail"
    payload = {
        "status": status,
        "checks": details,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload), 200 if ok else 503


def _register_flask(app, host: str, port: int) -> None:
    from flask import Response

    @app.route("/healthz")
    def _health() -> Response:  # type: ignore[override]
        body, code = _json_response(liveness_check)
        return Response(body, status=code, mimetype="application/json")

    @app.route("/readyz")
    def _ready() -> Response:  # type: ignore[override]
        body, code = _json_response(lambda: readiness_check(host, port))
        return Response(body, status=code, mimetype="application/json")


def _register_fastapi(app, host: str, port: int) -> None:
    from fastapi import Response

    @app.get("/healthz")
    async def _health() -> Response:  # type: ignore[override]
        body, code = _json_response(liveness_check)
        return Response(content=body, status_code=code, media_type="application/json")

    @app.get("/readyz")
    async def _ready() -> Response:  # type: ignore[override]
        body, code = _json_response(lambda: readiness_check(host, port))
        return Response(content=body, status_code=code, media_type="application/json")


class _Handler(BaseHTTPRequestHandler):
    host = "127.0.0.1"
    port = 8030

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            body, code = _json_response(liveness_check)
        elif self.path == "/readyz":
            body, code = _json_response(lambda: readiness_check(self.host, self.port))
        else:
            self.send_error(404)
            return
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Silence default logging
        return


def setup_health(app: Optional[Any] = None, host: str = "127.0.0.1", port: int = 8030) -> Optional[HTTPServer]:
    """Register health endpoints or start an internal server."""
    if app is not None:
        if hasattr(app, "route"):
            _register_flask(app, host, port)
            return None
        if hasattr(app, "get"):
            _register_fastapi(app, host, port)
            return None

    handler = _Handler
    handler.host = host
    handler.port = port
    server = HTTPServer(("127.0.0.1", 8030), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
