"""Backward-compatible calendar API module.

Delegates to the new service implementation in `services.calendar_service`.
Import `get_meals` from here for legacy code; new code should import from
`services.calendar_service` directly.
"""
from __future__ import annotations

from typing import Dict, List
from services.calendar_service import get_meals as service_get_meals

def get_meals() -> Dict[str, List[str]]:  # pragma: no cover - thin wrapper
    return service_get_meals()

