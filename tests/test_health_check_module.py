from health.health_check import liveness_check, readiness_check


def test_liveness_returns_tuple():
    ok, details = liveness_check()
    assert isinstance(ok, bool)
    assert isinstance(details, dict)


def test_readiness_loopback():
    ok, details = readiness_check("127.0.0.1", 1)
    assert isinstance(ok, bool)
    assert isinstance(details, dict)
