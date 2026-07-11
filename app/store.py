"""
In-memory data store for Module 1.

Holds all task records in a plain Python dictionary keyed by UUID string.
This module is the single source of truth for task data in this module.
Data does not persist across server restarts. This is expected behaviour
per ADR-001.

Usage:
    from app.store import store
    store["some-uuid"] = {...}
"""

from typing import Dict, Any

# Central in-memory store: { str(UUID): dict }
store: Dict[str, Any] = {}