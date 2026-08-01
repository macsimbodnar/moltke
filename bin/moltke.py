#!/usr/bin/env python3
"""moltke: document-driven workflow checker. Single entry point for hooks and manual runs.

Standard library only: this runs on every prompt, so startup cost matters.
INV-11: every mode exits 0 immediately when .moltke.json is absent or enabled is false.
"""

import argparse
import json
import re
import subprocess
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


STEP_FILE_RE = re.compile(r"^(S\d{3})_[A-Za-z0-9_]+\.md$")
PLAN_DIRS = ("plan_todo", "plan_current", "plan_done")


def parse_step_file(path):
    fields = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if match:
            fields.setdefault(match.group(1), match.group(2).strip())
    return fields


def plan_steps(root):
    """{plan_dir: [(step_id, path, fields)]} for the three plan directories."""
    steps = {}
    for dirname in PLAN_DIRS:
        entries = []
        directory = root / "project" / dirname
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                match = STEP_FILE_RE.match(path.name)
                if match:
                    entries.append((match.group(1), path, parse_step_file(path)))
        steps[dirname] = entries
    return steps


def _limit(config, key, default):
    # Marker damage is reported by check_marker; invariants keep working on defaults.
    value = config.get(key) if isinstance(config, dict) else None
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 1 else default


def inv_1_active_max(root, config):
    limit = _limit(config, "plan_active_max", 1)
    active = [s for s, _p, fields in plan_steps(root)["plan_current"] if not fields.get("paused_by")]
    if len(active) > limit:
        return [f"INV-1: plan_current/ holds {len(active)} non-paused steps ({', '.join(active)}), "
                f"limit {limit}; pause or complete until {limit} remain"]
    return []


def inv_2_stack_max(root, config):
    limit = _limit(config, "plan_stack_max", 3)
    stack = [s for s, _p, _f in plan_steps(root)["plan_current"]]
    if len(stack) > limit:
        return [f"INV-2: plan_current/ stack depth {len(stack)} ({', '.join(stack)}) exceeds "
                f"plan_stack_max {limit}; the plan is wrong at design level: record a decision and replan"]
    return []


def inv_3_steps_in_plan(root, config):
    plan_path = root / "project" / "plan.md"
    if not plan_path.is_file():
        return ["INV-3: project/plan.md is missing; create it and list every step"]
    plan = plan_path.read_text(encoding="utf-8")
    violations = []
    steps = plan_steps(root)
    for dirname in ("plan_todo", "plan_current"):
        for step_id, path, _fields in steps[dirname]:
            if not re.search(rf"\b{step_id}\b", plan):
                violations.append(f"INV-3: {path.relative_to(root)} is not listed in plan.md; "
                                  f"add {step_id} to the plan order or remove the file")
    return violations


def inv_4_done_not_blocked(root, config):
    steps = plan_steps(root)
    done_ids = {s for s, _p, _f in steps["plan_done"]}
    violations = []
    for dirname in PLAN_DIRS:
        for step_id, path, fields in steps[dirname]:
            blocked = fields.get("blocks", "")
            for target in re.findall(r"S\d{3}", blocked):
                if target in done_ids:
                    violations.append(f"INV-4: {target} is in plan_done/ but {step_id} "
                                      f"({path.relative_to(root)}) still declares blocks: {target}; "
                                      f"clear the blocks field or move {target} back")
    return violations


def inv_5_done_evidence(root, config):
    testing_path = root / "project" / "testing.md"
    rows = ""
    if testing_path.is_file():
        rows = "\n".join(l for l in testing_path.read_text(encoding="utf-8").splitlines()
                         if l.startswith("|"))
    violations = []
    for step_id, path, fields in plan_steps(root)["plan_done"]:
        if not fields.get("done"):
            violations.append(f"INV-5: {path.relative_to(root)} has no done: stamp; "
                              f"a completed step must carry one")
        if not re.search(rf"\b{step_id}\b", rows):
            violations.append(f"INV-5: no testing.md row references {step_id}; "
                              f"add the acceptance rows before completing the step")
    return violations


def inv_6_unique_ids(root, config):
    seen = {}
    violations = []
    for dirname in PLAN_DIRS:
        for step_id, path, _fields in plan_steps(root)[dirname]:
            if step_id in seen:
                violations.append(f"INV-6: duplicate step id {step_id} in {seen[step_id]} and "
                                  f"{dirname}; ids are allocated once, rename one file")
            else:
                seen[step_id] = dirname
    return violations


def inv_7_done_immutable(root, config):
    # Checked against git HEAD: tracked plan_done files never change or vanish;
    # additions are the one legal change (append by move only). Repos without
    # git history have no baseline, so the check abstains.
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--", "project/plan_done"],
        capture_output=True, text=True)
    if result.returncode != 0:
        return []
    violations = []
    for line in result.stdout.splitlines():
        status, _, entry = line[:2], line[2], line[3:]
        if any(code in status for code in ("M", "D", "R", "C", "U")):
            violations.append(f"INV-7: {entry.strip()} changed under plan_done/; history is "
                              f"immutable: restore it with git checkout -- {entry.strip()}")
    return violations


INVARIANT_CHECKS = [
    ("INV-1", inv_1_active_max),
    ("INV-2", inv_2_stack_max),
    ("INV-3", inv_3_steps_in_plan),
    ("INV-4", inv_4_done_not_blocked),
    ("INV-5", inv_5_done_evidence),
    ("INV-6", inv_6_unique_ids),
    ("INV-7", inv_7_done_immutable),
]


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
