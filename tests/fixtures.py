"""Fixture repositories for red-first tests.

Builders create repositories in deliberately broken states; tests observe
bin/moltke.py failing on them before the fix exists (AGENTS.md §6).
"""

import json
from pathlib import Path

MARKER = ".moltke.json"

GOOD_MARKER = {
    "schema": 1,
    "enabled": True,
    "plan_active_max": 1,
    "plan_stack_max": 3,
    "surface_guard": "cli",
}


def write_marker(root, content):
    """Write the marker verbatim (str) or as JSON (anything else)."""
    path = Path(root) / MARKER
    if isinstance(content, str):
        path.write_text(content, encoding="utf-8")
    else:
        path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
    return path


def marked_repo(root, overrides=None, remove=()):
    """A repo whose marker is GOOD_MARKER with fields overridden or removed."""
    marker = dict(GOOD_MARKER)
    marker.update(overrides or {})
    for key in remove:
        marker.pop(key, None)
    write_marker(root, marker)
    return Path(root)
