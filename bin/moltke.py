#!/usr/bin/env python3
"""moltke: document-driven workflow checker. Single entry point for hooks and manual runs.

Standard library only: this runs on every prompt, so startup cost matters.
INV-11: every mode exits 0 immediately when .moltke.json is absent or enabled is false.
"""

import argparse
import json
import sys
from pathlib import Path

MARKER = ".moltke.json"
SURFACE_GUARD_VALUES = ("cli", "api", "both", "none")

EXIT_OK = 0
EXIT_VIOLATIONS = 1
EXIT_BLOCK = 2


def find_root(start=None):
    """Nearest ancestor (including start) containing the marker, or None."""
    start = Path(start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / MARKER).is_file():
            return candidate
    return None


def load_marker(root):
    """Return (config, violations). config is None when the file is unreadable."""
    path = root / MARKER
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{MARKER}: unreadable ({exc}); fix or delete the file, then rerun"]
    return config, check_marker(config)


def check_marker(config):
    if not isinstance(config, dict):
        return [f"{MARKER}: top level must be a JSON object"]
    violations = []
    if config.get("schema") != 1:
        violations.append(f'{MARKER}: "schema" must be 1, got {config.get("schema")!r}')
    if not isinstance(config.get("enabled"), bool):
        violations.append(f'{MARKER}: "enabled" must be true or false, got {config.get("enabled")!r}')
    for key in ("plan_active_max", "plan_stack_max"):
        value = config.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            violations.append(f'{MARKER}: "{key}" must be an integer >= 1, got {value!r}')
    if config.get("surface_guard") not in SURFACE_GUARD_VALUES:
        violations.append(
            f'{MARKER}: "surface_guard" must be one of {", ".join(SURFACE_GUARD_VALUES)}, '
            f'got {config.get("surface_guard")!r}'
        )
    return violations


# (name, fn) with fn(root, config) -> [violation strings]. INV-1..INV-10 land in S003/S004.
INVARIANT_CHECKS = []


def run_validate(root, config, marker_violations):
    violations = list(marker_violations)
    for _name, fn in INVARIANT_CHECKS:
        violations.extend(fn(root, config))
    if violations:
        for violation in violations:
            print(f"VIOLATION: {violation}")
        print(f"{len(violations)} violation(s). Fix the items above, then rerun bin/moltke.py --validate.")
        return EXIT_VIOLATIONS
    print("moltke: all checks pass")
    return EXIT_OK


def main(argv=None):
    parser = argparse.ArgumentParser(prog="moltke.py", description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--session-start", action="store_true", help="SessionStart hook (S005)")
    modes.add_argument("--log-prompt", action="store_true", help="UserPromptSubmit hook (S005)")
    modes.add_argument("--pre-write", metavar="PATH", help="PreToolUse hook for Write and Edit (S005)")
    modes.add_argument("--post-write", action="store_true", help="PostToolUse hook (S005)")
    modes.add_argument("--stop", action="store_true", help="Stop hook (S005)")
    modes.add_argument("--validate", action="store_true", help="run every invariant, report all violations")
    modes.add_argument("--scaffold", action="store_true", help="create project/ and the marker from templates (S006)")
    args = parser.parse_args(argv)

    root = find_root()
    if root is None:
        return EXIT_OK  # INV-11: no marker, no friction
    config, marker_violations = load_marker(root)
    if isinstance(config, dict) and config.get("enabled") is False:
        return EXIT_OK  # INV-11: declined repo, even if other fields are junk

    if args.validate:
        return run_validate(root, config, marker_violations)
    # Hook modes never block on a broken marker (DEC-006: no deadlock without an
    # actionable path); --validate is where marker damage must surface.
    return EXIT_OK  # remaining modes are wired in S005/S006


if __name__ == "__main__":
    sys.exit(main())
