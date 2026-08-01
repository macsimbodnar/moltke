#!/usr/bin/env python3
"""moltke: document-driven workflow checker. Single entry point for hooks and manual runs.

Standard library only: this runs on every prompt, so startup cost matters.
INV-11: every mode exits 0 immediately when .moltke.json is absent or enabled is false.
"""

import argparse
import datetime
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
    plan = plan_text(root)
    if plan is None:
        return ["INV-3: project/plan.md is missing; create it and list every step"]
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


APPEND_ONLY_FILES = ("project/worklog.md", "project/decisions.md")
FINDING_STATUSES = ("open", "planned", "closed", "accepted")
FINDING_RE = re.compile(r"^###\s+(\S*-F\d{2})\b", re.M)


def inv_8_append_only(root, config):
    # Baseline is git HEAD, same reasoning as INV-7; untracked files have none.
    violations = []
    for rel in APPEND_ONLY_FILES:
        shown = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"],
                               capture_output=True)
        if shown.returncode != 0:
            continue
        path = root / rel
        if not path.is_file():
            violations.append(f"INV-8: {rel} was deleted; append-only files are never removed: "
                              f"restore it with git checkout -- {rel}")
        elif not path.read_bytes().startswith(shown.stdout):
            violations.append(f"INV-8: {rel} changed earlier bytes; append-only files grow only "
                              f"at the end: restore the committed content and re-append")
    return violations


def inv_9_unique_dec_ids(root, config):
    path = root / "project" / "decisions.md"
    if not path.is_file():
        return []
    seen, violations = set(), []
    for dec_id in re.findall(r"^## (DEC-\d{3})\b", path.read_text(encoding="utf-8"), re.M):
        if dec_id in seen:
            violations.append(f"INV-9: duplicate decision id {dec_id} in decisions.md; "
                              f"renumber the new entry to the next free DEC id")
        seen.add(dec_id)
    return violations


def inv_10_audit_findings(root, config):
    audit_dir = root / "project" / "audit"
    if not audit_dir.is_dir():
        return []
    references = []
    for dirname in PLAN_DIRS:
        for _step_id, _path, fields in plan_steps(root)[dirname]:
            references.append(fields.get("closes", ""))
    decisions = root / "project" / "decisions.md"
    if decisions.is_file():
        references.append(decisions.read_text(encoding="utf-8"))
    references = "\n".join(references)

    violations = []
    for report in sorted(audit_dir.glob("*.md")):
        text = report.read_text(encoding="utf-8")
        headings = list(FINDING_RE.finditer(text))
        for index, match in enumerate(headings):
            finding_id = match.group(1)
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            section = text[match.end():end]
            status_match = re.search(r"^Status:\s*(\S+)", section, re.M | re.I)
            status = status_match.group(1).lower() if status_match else None
            if status not in FINDING_STATUSES:
                violations.append(f"INV-10: finding {finding_id} in {report.name} has status "
                                  f"{status!r}; set one of {', '.join(FINDING_STATUSES)}")
            elif status == "open" and finding_id not in references:
                violations.append(f"INV-10: open finding {finding_id} in {report.name} has no "
                                  f"step closes: reference and no decisions.md entry; plan it "
                                  f"or record why it is accepted")
    return violations


INVARIANT_CHECKS = [
    ("INV-1", inv_1_active_max),
    ("INV-2", inv_2_stack_max),
    ("INV-3", inv_3_steps_in_plan),
    ("INV-4", inv_4_done_not_blocked),
    ("INV-5", inv_5_done_evidence),
    ("INV-6", inv_6_unique_ids),
    ("INV-7", inv_7_done_immutable),
    ("INV-8", inv_8_append_only),
    ("INV-9", inv_9_unique_dec_ids),
    ("INV-10", inv_10_audit_findings),
]


def hook_input():
    """Hook payload from stdin; {} when run manually or on damage (fail open)."""
    if sys.stdin.isatty():
        return {}
    try:
        data = json.load(sys.stdin)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def plan_text(root):
    """plan.md with comments and fenced blocks stripped: commented-out
    example steps are not the plan."""
    plan_path = root / "project" / "plan.md"
    if not plan_path.is_file():
        return None
    text = plan_path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"```.*?```", "", text, flags=re.S)


def derived_next(root):
    """First step in plan.md order not yet in plan_done/ (AGENTS.md §1)."""
    plan = plan_text(root)
    if plan is None:
        return None
    done = {s for s, _p, _f in plan_steps(root)["plan_done"]}
    seen = set()
    for step_id in re.findall(r"\bS\d{3}\b", plan):
        if step_id not in seen:
            seen.add(step_id)
            if step_id not in done:
                return step_id
    return None


def status_next(root):
    status_path = root / "project" / "status.md"
    if not status_path.is_file():
        return None
    match = re.search(r"Next:.*?\b(S\d{3})\b", status_path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def mode_session_start(root, config):
    lines = []
    current = plan_steps(root)["plan_current"]
    if current:
        lines.append("moltke stack (plan_current/):")
        for step_id, _path, fields in current:
            paused = f" [paused by {fields['paused_by']}]" if fields.get("paused_by") else ""
            lines.append(f"  {step_id}: {fields.get('goal', '')}{paused}")
    else:
        lines.append("moltke: plan_current/ is empty.")
    nxt = derived_next(root)
    if nxt:
        lines.append(f"Derived next step: {nxt} (first in plan.md order not in plan_done/).")
    stated = status_next(root)
    if stated != nxt:
        lines.append(f"status.md is stale (says Next: {stated}, filesystem says {nxt}); "
                     f"regenerate it from plan_current/ before working.")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n".join(lines),
    }}))
    return EXIT_OK


def mode_log_prompt(root, config):
    # UserPromptSubmit exit 2 erases the user's prompt (live docs 2026-08-01):
    # logging must fail open, always exit 0.
    prompt = hook_input().get("prompt", "")
    if not prompt:
        return EXIT_OK
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    quoted = "\n".join(f"> {line}" for line in prompt.splitlines())
    try:
        with open(root / "project" / "worklog.md", "a", encoding="utf-8") as worklog:
            worklog.write(f"\n## {stamp} prompt\n\n{quoted}\n")
    except OSError as exc:
        print(f"moltke --log-prompt: {exc}", file=sys.stderr)
    return EXIT_OK


def mode_pre_write(root, config, path_arg):
    path = path_arg or hook_input().get("tool_input", {}).get("file_path", "")
    if not path:
        return EXIT_OK
    try:
        rel = Path(path).resolve().relative_to(root) if Path(path).is_absolute() else Path(path)
    except ValueError:
        return EXIT_OK  # outside this repo, not ours to police
    parts = rel.parts
    if parts[:2] == ("project", "plan_done"):
        print(f"moltke: {rel} is under plan_done/, which is immutable history. "
              f"Completed steps are moved there with mv/git mv as the last action of a step; "
              f"nothing inside is ever edited.", file=sys.stderr)
        return EXIT_BLOCK
    if STEP_FILE_RE.match(rel.name) and parts[:2] not in (
            ("project", "plan_todo"), ("project", "plan_current"), ("project", "plan_done")):
        print(f"moltke: {rel.name} looks like a step file but {rel} is outside the three "
              f"plan directories. Create step files only in project/plan_todo/ or "
              f"project/plan_current/.", file=sys.stderr)
        return EXIT_BLOCK
    return EXIT_OK


CHEAP_CHECKS = ("INV-1", "INV-2", "INV-3", "INV-4", "INV-5", "INV-6", "INV-9", "INV-10")


def mode_post_write(root, config, marker_violations):
    # Non-blocking by contract (the tool already ran); exit 2 only surfaces
    # stderr to Claude. Git-based checks are skipped to keep this cheap.
    violations = list(marker_violations)
    for name, fn in INVARIANT_CHECKS:
        if name in CHEAP_CHECKS:
            violations.extend(fn(root, config))
    if violations:
        for violation in violations:
            print(f"moltke: {violation}", file=sys.stderr)
        return EXIT_BLOCK
    return EXIT_OK


STOP_CAP = 3


def _stop_state_path(root):
    git_dir = root / ".git"
    return git_dir / "moltke_stop_state.json" if git_dir.is_dir() else None


def _git_lines(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return result.stdout.splitlines() if result.returncode == 0 else None


def mode_stop(root, config, marker_violations):
    problems = list(marker_violations)
    for _name, fn in INVARIANT_CHECKS:
        problems.extend(fn(root, config))

    nxt = derived_next(root)
    if nxt and status_next(root) != nxt:
        problems.append(f"status.md is stale or missing: the derived next step is {nxt}. "
                        f"Rewrite project/status.md from plan_current/ before ending the turn.")

    porcelain = _git_lines(root, "status", "--porcelain")
    if porcelain is not None:
        changed_source = [line for line in porcelain
                          if not line[3:].startswith(("project/", ".claude"))]
        if changed_source:
            shown = subprocess.run(["git", "-C", str(root), "show", "HEAD:project/worklog.md"],
                                   capture_output=True)
            worklog = root / "project" / "worklog.md"
            current = worklog.read_bytes() if worklog.is_file() else b""
            if shown.returncode == 0 and len(current) <= len(shown.stdout):
                problems.append("source changed but project/worklog.md gained no recap; "
                                "append a recap (step id, what changed, files, tests, commit) "
                                "before ending the turn.")
        for line in porcelain:
            entry = line[3:]
            if line[:2] in ("??", "A ") and entry.startswith("project/plan_done/"):
                fields = parse_step_file(root / entry)
                stamp = fields.get("done", "")
                if "README" not in stamp or "MANUAL" not in stamp:
                    problems.append(f"{entry} was completed without the README and MANUAL "
                                    f"check recorded; check both files and note it in the "
                                    f"done: stamp (checking with no change needed is valid).")

    state_path = _stop_state_path(root)
    if problems:
        prompt_id = hook_input().get("prompt_id", "")
        count = 1
        if state_path:
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if state.get("prompt_id") == prompt_id:
                    count = state.get("count", 0) + 1
            except (OSError, json.JSONDecodeError):
                pass
            state_path.write_text(json.dumps({"prompt_id": prompt_id, "count": count}),
                                  encoding="utf-8")
        if count > STOP_CAP:
            # Live docs (2026-08-01) document no built-in cap; this one keeps
            # the no-deadlock property of DEC-006 / INV-12.
            print(f"moltke: still blocked after {STOP_CAP} attempts; allowing stop so the "
                  f"session is not deadlocked. Run bin/moltke.py --validate and fix by hand.",
                  file=sys.stderr)
            return EXIT_OK
        for problem in problems:
            print(f"moltke: {problem}", file=sys.stderr)
        return EXIT_BLOCK
    if state_path and state_path.is_file():
        try:
            state_path.unlink()
        except OSError:
            pass
    return EXIT_OK


TEMPLATE_ROOT = Path(__file__).resolve().parent.parent / "templates"

# (template path, destination path). Nothing existing is ever overwritten.
SCAFFOLD_MAP = (
    ("moltke.json", MARKER),
    ("AGENTS.md", "AGENTS.md"),
    ("CLAUDE.md", "CLAUDE.md"),
    ("cursor_rules", ".cursor/rules/moltke.mdc"),
    ("project/specs.md", "project/specs.md"),
    ("project/plan.md", "project/plan.md"),
    ("project/status.md", "project/status.md"),
    ("project/decisions.md", "project/decisions.md"),
    ("project/testing.md", "project/testing.md"),
    ("project/worklog.md", "project/worklog.md"),
)
SCAFFOLD_DIRS = ("project/plan_todo", "project/plan_current", "project/plan_done", "project/audit")


def scaffold_root(start=None):
    """Marked root if there is one, else the git top level, else cwd."""
    marked = find_root(start)
    if marked is not None:
        return marked
    start = Path(start or Path.cwd()).resolve()
    result = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip())
    return start


def declined(root):
    """True when the marker records a declined repository (DEC-005)."""
    path = root / MARKER
    if not path.is_file():
        return False
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(config, dict) and config.get("enabled") is False


def mode_scaffold():
    # Exempt from the INV-11 gate: this mode exists to create the marker (DEC-017).
    root = scaffold_root()
    if declined(root):
        print(f"moltke: {root/MARKER} records enabled false; this repository declined the "
              f"workflow and is left untouched. Delete that file to reconsider.")
        return EXIT_OK
    created, kept = [], []
    for template, destination in SCAFFOLD_MAP:
        target = root / destination
        if target.exists():
            kept.append(destination)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((TEMPLATE_ROOT / template).read_bytes())
        created.append(destination)
    for dirname in SCAFFOLD_DIRS:
        keep = root / dirname / ".gitkeep"
        if not keep.exists():
            keep.parent.mkdir(parents=True, exist_ok=True)
            keep.write_text("", encoding="utf-8")
            created.append(f"{dirname}/")
    print(f"moltke: scaffolded {root}")
    for path in created:
        print(f"  created  {path}")
    for path in kept:
        print(f"  kept     {path} (already present, not overwritten)")
    if not created:
        print("  nothing to do; the workflow is already set up here")
    elif kept:
        print("Review the kept files: moltke did not merge anything into them.")
    return EXIT_OK


def mode_decline():
    # Exempt from the INV-11 gate for the same reason as --scaffold (DEC-017).
    root = scaffold_root()
    path = root / MARKER
    if path.is_file() and not declined(root):
        print(f"moltke: {path} already exists and is not a declined marker; leaving it alone. "
              f"Remove it first if this repository should stop using the workflow.")
        return EXIT_OK
    path.write_text(json.dumps({"schema": 1, "enabled": False}, indent=2) + "\n",
                    encoding="utf-8")
    print(f"moltke: wrote {path} with enabled false. Nothing will be scaffolded or enforced "
          f"here, and you will not be asked again. Delete the file to reconsider.")
    return EXIT_OK


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
    modes.add_argument("--pre-write", metavar="PATH", nargs="?", const="",
                       help="PreToolUse hook for Write and Edit; PATH falls back to hook stdin JSON")
    modes.add_argument("--post-write", action="store_true", help="PostToolUse hook (S005)")
    modes.add_argument("--stop", action="store_true", help="Stop hook (S005)")
    modes.add_argument("--validate", action="store_true", help="run every invariant, report all violations")
    modes.add_argument("--scaffold", action="store_true", help="create the marker, AGENTS.md, and project/ from templates")
    modes.add_argument("--decline", action="store_true", help="record that this repository declines the workflow, durably")
    args = parser.parse_args(argv)

    # Setup modes run before the marker gate: they exist to create it (DEC-017).
    if args.scaffold:
        return mode_scaffold()
    if args.decline:
        return mode_decline()

    root = find_root()
    if root is None:
        return EXIT_OK  # INV-11: no marker, no friction
    config, marker_violations = load_marker(root)
    if isinstance(config, dict) and config.get("enabled") is False:
        return EXIT_OK  # INV-11: declined repo, even if other fields are junk

    if args.validate:
        return run_validate(root, config, marker_violations)
    if args.session_start:
        return mode_session_start(root, config)
    if args.log_prompt:
        return mode_log_prompt(root, config)
    if args.pre_write is not None:
        return mode_pre_write(root, config, args.pre_write)
    if args.post_write:
        return mode_post_write(root, config, marker_violations)
    if args.stop:
        return mode_stop(root, config, marker_violations)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
