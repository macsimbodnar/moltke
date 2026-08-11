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


def step_file(directory, step_id, name="step", **fields):
    """Write a step file with the standard key: value layout."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    lines = [f"id:         {step_id}", f"goal:       {name}"]
    for key, value in fields.items():
        lines.append(f"{key}: {value}")
    path = directory / f"{step_id}_{name}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def workflow_repo(root):
    """A marked repo with a minimal valid plan tree: passes every invariant."""
    root = marked_repo(root)
    docs = root / "adocs"
    docs.mkdir(exist_ok=True)
    (docs / "plan.md").write_text(
        "# Plan\n\n1. S001 base\n2. S002 pending\n3. S003 active\n",
        encoding="utf-8",
    )
    step_file(docs / "plan_done", "S001", "base", done="2026-08-01 done")
    step_file(docs / "plan_todo", "S002", "pending")
    step_file(docs / "plan_current", "S003", "active")
    (docs / "testing.md").write_text(
        "# Testing ledger\n\n| Step | Criterion | Test | Result |\n"
        "|---|---|---|---|\n| S001 | base works | manual | pass |\n",
        encoding="utf-8",
    )
    (docs / "decisions.md").write_text(
        "# Decisions\n\n## DEC-001  2026-08-01  base decision\n"
        "Tags: base\nContext: fixture\nDecision: fixture\n"
        "Rejected: none\nConsequences: none\n",
        encoding="utf-8",
    )
    # Byte-for-byte what `--step status` derives for this tree. Since S039 the
    # whole body is compared, not just the Next: line, so an approximation here
    # would make every fixture repository read as stale.
    (docs / "status.md").write_text(
        "# Status\n\n- Last done: S001\n- In progress: S003 active\n"
        "- Next: S002\n- Blocked: none\n- Parked:\n",
        encoding="utf-8",
    )
    return root


def audit_report(root, findings, name="2026-08-01_adversarial.md"):
    """An audit report with (finding_id, status) sections in the S004 format."""
    audit_dir = Path(root) / "adocs" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    parts = ["# Audit\n"]
    for finding_id, status in findings:
        parts.append(f"### {finding_id}  high  fixture finding\n\nStatus: {status}\n")
    path = audit_dir / name
    path.write_text("\n".join(parts), encoding="utf-8")
    return path
