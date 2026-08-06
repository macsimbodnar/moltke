#!/usr/bin/env python3
"""moltke: document-driven workflow checker. Single entry point for hooks and manual runs.

Standard library only: this runs on every prompt, so startup cost matters.
INV-11: every mode exits 0 immediately when .moltke.json is absent or enabled is false.
"""

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

MARKER = ".moltke.json"
DOCS = "adocs"  # agent documentation; renamed from project/ by DEC-021
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


def strip_guidance(text):
    """Drop fenced blocks and HTML comments.

    Templates carry their own format as an example. Every scanner in this file
    reads it through here, so guidance is never counted as data: a commented
    step is not planned, an example finding is not open, an example decision id
    is not taken.
    """
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def field_value(fields, key):
    """A field's real value: unfilled template placeholders read as empty."""
    return strip_guidance(fields.get(key, "")).strip()


def plan_steps(root):
    """{plan_dir: [(step_id, path, fields)]} for the three plan directories."""
    steps = {}
    for dirname in PLAN_DIRS:
        entries = []
        directory = root / DOCS / dirname
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
    active = [s for s, _p, fields in plan_steps(root)["plan_current"]
              if not field_value(fields, "paused_by")]
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
        return [f"INV-3: {DOCS}/plan.md is missing; create it and list every step"]
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
    # Only open steps block: a completed child's blocks field is history.
    for dirname in ("plan_todo", "plan_current"):
        for step_id, path, fields in steps[dirname]:
            for target in re.findall(r"S\d{3}", field_value(fields, "blocks")):
                if target in done_ids:
                    violations.append(f"INV-4: {target} is in plan_done/ but {step_id} "
                                      f"({path.relative_to(root)}) still declares blocks: {target}; "
                                      f"clear the blocks field or move {target} back")
    return violations


def inv_5_done_evidence(root, config):
    testing_path = root / DOCS / "testing.md"
    rows = ""
    if testing_path.is_file():
        rows = "\n".join(l for l in testing_path.read_text(encoding="utf-8").splitlines()
                         if l.startswith("|"))
    violations = []
    for step_id, path, fields in plan_steps(root)["plan_done"]:
        if not field_value(fields, "done"):
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
        ["git", "-C", str(root), "status", "--porcelain", "--", f"{DOCS}/plan_done"],
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


# decisions.md only, since DEC-025: DEC ids are cited from code comments, commit
# messages, specs.md, and step files, so a rewritten entry silently changes what
# those citations mean. worklog.md is history nothing cites by id, so it is
# append-only by convention and unchecked.
APPEND_ONLY_FILES = (f"{DOCS}/decisions.md",)
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
            violations.append(f"INV-8: {rel} was deleted; it is append-only and never removed: "
                              f"restore it with git checkout -- {rel}")
        elif not path.read_bytes().startswith(shown.stdout):
            violations.append(f"INV-8: {rel} changed earlier bytes; it grows only at the end, "
                              f"because DEC ids are cited from code, commits, and specs and a "
                              f"rewritten entry changes what those citations mean: restore the "
                              f"committed content and re-append. A reversal is a new entry "
                              f"marking the old one VOID")
    return violations


def inv_9_unique_dec_ids(root, config):
    path = root / DOCS / "decisions.md"
    if not path.is_file():
        return []
    seen, violations = set(), []
    text = strip_guidance(path.read_text(encoding="utf-8"))
    for dec_id in re.findall(r"^## (DEC-\d{3})\b", text, re.M):
        if dec_id in seen:
            violations.append(f"INV-9: duplicate decision id {dec_id} in decisions.md; "
                              f"renumber the new entry to the next free DEC id")
        seen.add(dec_id)
    return violations


def finding_references(root):
    """Everything that can discharge a finding: step closes: fields, decisions."""
    references = []
    for dirname in PLAN_DIRS:
        for _step_id, _path, fields in plan_steps(root)[dirname]:
            references.append(field_value(fields, "closes"))
    decisions = root / DOCS / "decisions.md"
    if decisions.is_file():
        references.append(decisions.read_text(encoding="utf-8"))
    return "\n".join(references)


def report_findings(report):
    """[(finding_id, status)] for a report. Fenced examples and comments in the
    template are guidance, not findings."""
    text = strip_guidance(report.read_text(encoding="utf-8"))
    headings = list(FINDING_RE.finditer(text))
    findings = []
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        status_match = re.search(r"^Status:\s*(\S+)", text[match.end():end], re.M | re.I)
        findings.append((match.group(1), status_match.group(1).lower() if status_match else None))
    return findings


def inv_10_audit_findings(root, config):
    audit_dir = root / DOCS / "audit"
    if not audit_dir.is_dir():
        return []
    references = finding_references(root)
    violations = []
    for report in sorted(audit_dir.glob("*.md")):
        for finding_id, status in report_findings(report):
            if not finding_id.startswith(report.stem):
                violations.append(f"INV-10: finding {finding_id} lives in {report.name}; "
                                  f"finding ids carry their own report's name, so it should "
                                  f"read {report.stem}-F<nn>")
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
    plan_path = root / DOCS / "plan.md"
    if not plan_path.is_file():
        return None
    return strip_guidance(plan_path.read_text(encoding="utf-8"))


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
    status_path = root / DOCS / "status.md"
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
            pauser = field_value(fields, "paused_by")
            paused = f" [paused by {pauser}]" if pauser else ""
            lines.append(f"  {step_id}: {field_value(fields, 'goal')}{paused}")
    else:
        lines.append("moltke: plan_current/ is empty.")
    nxt = derived_next(root)
    if nxt:
        lines.append(f"Derived next step: {nxt} (first in plan.md order not in plan_done/).")
    stated = status_next(root)
    if stated != nxt:
        lines.append(f"status.md is stale (says Next: {stated}, filesystem says {nxt}); "
                     f"regenerate it from plan_current/ before working.")
    lost = take_log_failure(root)
    if lost:
        lines.append(lost)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n".join(lines),
    }}))
    return EXIT_OK


def _log_failure_path(root):
    git_dir = root / ".git"
    return git_dir / "moltke_log_failure.json" if git_dir.is_dir() else None


def record_log_failure(root, stamp, exc):
    """S014 (F14): a swallowed append needs a channel a zero exit still reaches.
    Nothing is written outside .git/, because an untracked file at the repo root
    reads as a source change to the Stop hook."""
    path = _log_failure_path(root)
    if path is None:
        return
    since, count = stamp, 0
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(previous, dict):
            since = previous.get("since") or since
            count = previous.get("count") if isinstance(previous.get("count"), int) else 0
    except (OSError, ValueError):
        pass
    try:
        path.write_text(
            json.dumps({"since": since, "count": count + 1, "error": str(exc)}) + "\n",
            encoding="utf-8")
    except OSError:
        pass


def take_log_failure(root):
    """Report a swallowed prompt append once, then drop the breadcrumb: a
    failure that persists rewrites it on the next prompt, one that is fixed
    goes quiet without anyone clearing it by hand."""
    path = _log_failure_path(root)
    if path is None or not path.is_file():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    if not isinstance(state, dict):
        state = {}
    try:
        path.unlink()
    except OSError:
        pass
    count = state.get("count")
    what = f"{count} prompt(s)" if isinstance(count, int) and count > 0 else "at least one prompt"
    return (f"moltke: {what} not appended to {DOCS}/worklog.md since "
            f"{state.get('since') or 'an earlier turn'} "
            f"({state.get('error') or 'error unrecorded'}). UserPromptSubmit cannot report this "
            f"itself, because exit 2 there erases the prompt. The forensic log stays incomplete "
            f"until that path is writable; the lost prompts are not recoverable.")


def mode_log_prompt(root, config):
    # UserPromptSubmit exit 2 erases the user's prompt (live docs 2026-08-01):
    # logging must fail open, always exit 0.
    prompt = hook_input().get("prompt", "")
    if not prompt:
        return EXIT_OK
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    quoted = "\n".join(f"> {line}" for line in prompt.splitlines())
    try:
        # Append mode does not create parents, so a marked repo whose adocs/ is
        # missing used to discard every prompt (F14).
        (root / DOCS).mkdir(parents=True, exist_ok=True)
        with open(root / DOCS / "worklog.md", "a", encoding="utf-8") as worklog:
            worklog.write(f"\n## {stamp} prompt\n\n{quoted}\n")
    except OSError as exc:
        print(f"moltke --log-prompt: {exc}", file=sys.stderr)
        record_log_failure(root, stamp, exc)
    return EXIT_OK


REVIEWER_AGENT = "adversarial_reviewer"


def reviewer_may_write(root, rel):
    """DEC-022: the fence is a fast clear failure on the common path, not the
    guarantee — the reviewer also holds Bash, which no matcher sees. It permits
    the report, and a new regression test, which is evidence. Editing a test that
    already exists is a patch."""
    parts = rel.parts
    if parts[:2] == (DOCS, "audit"):
        return True
    return parts[:1] == ("tests",) and not (root / rel).exists()


def mode_pre_write(root, config, path_arg):
    payload = hook_input()
    path = path_arg or payload.get("tool_input", {}).get("file_path", "")
    if not path:
        return EXIT_OK
    try:
        rel = Path(path).resolve().relative_to(root) if Path(path).is_absolute() else Path(path)
    except ValueError:
        return EXIT_OK  # outside this repo, not ours to police
    parts = rel.parts
    # The reviewer produces evidence, not patches: a reviewer that can fix what
    # it finds stops recording findings and starts writing code.
    # Observed live 2026-08-06 (S016): Claude Code sends the scoped name
    # "moltke:adversarial_reviewer", and no agent_type key at all on the main
    # thread, so bare equality never matched and the fence failed open (F02).
    # Suffix match rather than an exact pair, so renaming the plugin cannot
    # silently reopen it; the cost is fencing another plugin's agent of the same
    # name, which at least blocks loudly instead of failing open.
    agent = (payload.get("agent_type") or "").split(":")[-1]
    if agent == REVIEWER_AGENT and not reviewer_may_write(root, rel):
        print(f"moltke: the {REVIEWER_AGENT} may write under {DOCS}/audit/, and may create new "
              f"files under tests/, and {rel} is neither. Record what you found as a finding in "
              f"your report; fixes are planned as steps afterwards, by someone else.",
              file=sys.stderr)
        return EXIT_BLOCK
    if parts[:2] == (DOCS, "plan_done"):
        print(f"moltke: {rel} is under plan_done/, which is immutable history. "
              f"Completed steps are moved there with mv/git mv as the last action of a step; "
              f"nothing inside is ever edited.", file=sys.stderr)
        return EXIT_BLOCK
    if STEP_FILE_RE.match(rel.name) and parts[:2] not in (
            (DOCS, "plan_todo"), (DOCS, "plan_current"), (DOCS, "plan_done")):
        print(f"moltke: {rel.name} looks like a step file but {rel} is outside the three "
              f"plan directories. Create step files only in {DOCS}/plan_todo/ or "
              f"{DOCS}/plan_current/.", file=sys.stderr)
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


WORKLOG_HEADING = re.compile(r"^##\s.*$", re.M)
RECAP_HEADING = re.compile(r"\brecap\b", re.I)
PROMPT_HEADING = re.compile(r"\bprompt\s*$", re.I)


def recap_pending(root):
    """S015 (F01): a recap is a heading after the last logged prompt, not growth.
    Growth cannot work as the signal — UserPromptSubmit appends the prompt before
    the turn begins, so the worklog has always grown by the time Stop runs.

    Recap wins over prompt when a heading reads as both: a recap whose title is
    about prompts ("recap - prompt logging never fails silently") is a recap.
    """
    worklog = root / DOCS / "worklog.md"
    if not worklog.is_file():
        return True
    text = strip_guidance(worklog.read_text(encoding="utf-8", errors="replace"))
    recapped = False
    for heading in WORKLOG_HEADING.finditer(text):
        line = heading.group(0)
        if RECAP_HEADING.search(line):
            recapped = True
        elif PROMPT_HEADING.search(line):
            recapped = False
    return not recapped


def mode_stop(root, config, marker_violations):
    problems = list(marker_violations)
    for _name, fn in INVARIANT_CHECKS:
        problems.extend(fn(root, config))

    nxt = derived_next(root)
    if nxt and status_next(root) != nxt:
        problems.append(f"status.md is stale or missing: the derived next step is {nxt}. "
                        f"Rewrite {DOCS}/status.md from plan_current/ before ending the turn.")

    porcelain = _git_lines(root, "status", "--porcelain")
    if porcelain is not None:
        changed_source = [line for line in porcelain
                          if not line[3:].startswith((f"{DOCS}/", ".claude"))]
        # No commit yet means no history a recap would sit alongside, and the
        # scaffold's own files are not work: abstain, as INV-7 and INV-8 do.
        committed = _git_lines(root, "rev-parse", "HEAD") is not None
        if changed_source and committed and recap_pending(root):
            problems.append(f"source changed but {DOCS}/worklog.md has no recap heading after "
                            f"the last logged prompt; append a recap (step id, what changed, "
                            f"files, tests, commit) before ending the turn, or commit the "
                            f"change if the turn that made it was already recapped.")
        for line in porcelain:
            entry = line[3:]
            if line[:2] in ("??", "A ") and entry.startswith(f"{DOCS}/plan_done/"):
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
    (f"{DOCS}/specs.md", f"{DOCS}/specs.md"),
    (f"{DOCS}/plan.md", f"{DOCS}/plan.md"),
    (f"{DOCS}/status.md", f"{DOCS}/status.md"),
    (f"{DOCS}/decisions.md", f"{DOCS}/decisions.md"),
    (f"{DOCS}/testing.md", f"{DOCS}/testing.md"),
    (f"{DOCS}/worklog.md", f"{DOCS}/worklog.md"),
)
SCAFFOLD_DIRS = (f"{DOCS}/plan_todo", f"{DOCS}/plan_current", f"{DOCS}/plan_done", f"{DOCS}/audit")


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


def refuse(message):
    print(f"moltke: {message}", file=sys.stderr)
    return EXIT_VIOLATIONS


def locate_step(root, step_id):
    """(plan_dir, path, fields) for a step id, or (None, None, None)."""
    steps = plan_steps(root)
    for dirname in PLAN_DIRS:
        for found, path, fields in steps[dirname]:
            if found == step_id:
                return dirname, path, fields
    return None, None, None


def next_step_id(root):
    """Highest id ever seen plus one; ids are never reused (DEC-008),
    so plan.md counts even when the file is gone."""
    highest = 0
    steps = plan_steps(root)
    for dirname in PLAN_DIRS:
        for step_id, _p, _f in steps[dirname]:
            highest = max(highest, int(step_id[1:]))
    for number in re.findall(r"\bS(\d{3})\b", plan_text(root) or ""):
        highest = max(highest, int(number))
    return f"S{highest + 1:03d}"


def write_step(path, step_id, goal, blocks=""):
    template = (TEMPLATE_ROOT / "step_template.md").read_text(encoding="utf-8")
    lines = []
    for line in template.splitlines():
        key = line.split(":", 1)[0].strip()
        if key == "id":
            line = f"id:         {step_id}"
        elif key == "goal" and goal:
            line = f"goal:       {goal}"
        elif key == "blocks":
            line = f"blocks:     {blocks}" if blocks else "blocks:"
        elif key in ("decisions", "closes", "paused_by", "done"):
            line = f"{key}:{' ' * (11 - len(key) - 1)}".rstrip()
        lines.append(line)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_to_plan(root, step_id, goal):
    plan_path = root / DOCS / "plan.md"
    numbers = [int(n) for n in re.findall(r"^\s*(\d+)\.\s", plan_text(root) or "", re.M)]
    entry = f"{max(numbers) + 1 if numbers else 1}. {step_id}  {goal}".rstrip()
    text = plan_path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    plan_path.write_text(text + entry + "\n", encoding="utf-8")


def set_field(path, key, value):
    """Set a step field, adding the line when the file does not carry it yet."""
    rendered = f"{key}:{' ' * max(1, 11 - len(key) - 1)}{value}".rstrip()
    lines, found = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.split(":", 1)[0].strip() == key:
            line, found = rendered, True
        lines.append(line)
    if not found:
        lines.append(rendered)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def step_new(root, config, name, goal):
    step_id = next_step_id(root)
    goal = goal or name.replace("_", " ")
    path = root / DOCS / "plan_todo" / f"{step_id}_{name}.md"
    write_step(path, step_id, goal)
    append_to_plan(root, step_id, goal)
    print(f"moltke: created {path.relative_to(root)} and listed {step_id} in plan.md. "
          f"Reorder plan.md if it does not belong last.")
    return EXIT_OK


def step_start(root, config, step_id):
    dirname, path, _fields = locate_step(root, step_id)
    if dirname is None:
        return refuse(f"{step_id} does not exist; create it with --step new <name>")
    if dirname == "plan_current":
        return refuse(f"{step_id} is already in plan_current/")
    if dirname == "plan_done":
        return refuse(f"{step_id} is in plan_done/, which is immutable history; "
                      f"never resume a completed step, create a new one")
    current = plan_steps(root)["plan_current"]
    active = [s for s, _p, fields in current if not field_value(fields, "paused_by")]
    if len(active) + 1 > _limit(config, "plan_active_max", 1):
        return refuse(f"{', '.join(active)} already active and plan_active_max is "
                      f"{_limit(config, 'plan_active_max', 1)}; complete it, or if it is "
                      f"blocked by this work use --step block {active[0]} <name> instead")
    if len(current) + 1 > _limit(config, "plan_stack_max", 3):
        return refuse(f"plan_current/ stack is full ({len(current)}); complete something first")
    path.rename(root / DOCS / "plan_current" / path.name)
    print(f"moltke: {step_id} is now current.")
    return EXIT_OK


def step_block(root, config, parent_id, name):
    dirname, parent_path, _fields = locate_step(root, parent_id)
    if dirname != "plan_current":
        where = dirname or "nowhere"
        return refuse(f"{parent_id} is in {where}, not plan_current/; only an in-progress "
                      f"step can be paused by a blocking child")
    current = plan_steps(root)["plan_current"]
    limit = _limit(config, "plan_stack_max", 3)
    if len(current) + 1 > limit:
        return refuse(f"stack depth would reach {len(current) + 1}, over plan_stack_max "
                      f"{limit}. A blocker spawning its own blockers this deep means the plan "
                      f"is wrong at design level: stop, record a decision, and replan.")
    child_id = next_step_id(root)
    goal = name.replace("_", " ")
    child_path = root / DOCS / "plan_current" / f"{child_id}_{name}.md"
    write_step(child_path, child_id, goal, blocks=parent_id)
    append_to_plan(root, child_id, goal)
    set_field(parent_path, "paused_by",
              f"{child_id}  # {datetime.date.today().isoformat()}")
    print(f"moltke: {child_id} created in plan_current/ blocking {parent_id}, "
          f"which is now paused.")
    return EXIT_OK


def step_done(root, config, step_id, stamp):
    dirname, path, fields = locate_step(root, step_id)
    if dirname is None:
        return refuse(f"{step_id} does not exist")
    if dirname != "plan_current":
        return refuse(f"{step_id} is in {dirname}, not plan_current/; only a step that is "
                      f"actually in progress can be completed")
    pauser = re.search(r"S\d{3}", field_value(fields, "paused_by"))
    if pauser:
        return refuse(f"{step_id} is paused by {pauser.group(0)}; complete {pauser.group(0)} "
                      f"first, which unpauses this step automatically")
    steps = plan_steps(root)
    for open_dir in ("plan_todo", "plan_current"):
        for other_id, _p, other_fields in steps[open_dir]:
            if other_id != step_id and step_id in field_value(other_fields, "blocks"):
                return refuse(f"{other_id} still declares blocks: {step_id}; complete or "
                              f"drop {other_id} first")
    testing = root / DOCS / "testing.md"
    rows = testing.read_text(encoding="utf-8") if testing.is_file() else ""
    if not re.search(rf"\b{step_id}\b", "\n".join(l for l in rows.splitlines()
                                                  if l.startswith("|"))):
        return refuse(f"no testing.md row references {step_id}; acceptance rows are added "
                      f"with the feature, before completion")
    if not stamp:
        return refuse(f"--step done needs --stamp \"<what proves this step is finished>\"")
    if "README" not in stamp or "MANUAL" not in stamp:
        return refuse(f"the completion stamp must record the README and MANUAL check "
                      f"(concluding that neither needs a change is a valid outcome, "
                      f"not checking is not)")

    set_field(path, "done", stamp)
    for parent_id, parent_path, parent_fields in steps["plan_current"]:
        if step_id in field_value(parent_fields, "paused_by"):
            set_field(parent_path, "paused_by", "")
            print(f"moltke: {parent_id} unpaused.")
    path.rename(root / DOCS / "plan_done" / path.name)
    print(f"moltke: {step_id} completed and moved to plan_done/. Commit it; the move is the "
          f"last action of the step.")
    return EXIT_OK


def parked_lines(root):
    """Carry the human-written Parked list through a regeneration."""
    status_path = root / DOCS / "status.md"
    if not status_path.is_file():
        return []
    kept, collecting = [], False
    for line in status_path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s*-\s*Parked:", line):
            collecting = True
            continue
        if collecting:
            if line.startswith(("  ", "\t")) or not line.strip():
                if line.strip():
                    kept.append(line.rstrip())
            else:
                break
    return kept


def step_status(root, config):
    steps = plan_steps(root)
    done_ids = [s for s, _p, _f in steps["plan_done"]]
    ordered = []
    for step_id in re.findall(r"\bS\d{3}\b", plan_text(root) or ""):
        if step_id not in ordered:
            ordered.append(step_id)
    last_done = next((s for s in reversed(ordered) if s in done_ids), None)

    lines = ["# Status", "",
             "Convenience view, rewritten at the end of every work turn. The filesystem "
             "beats", "this file: on disagreement, `plan_current/` wins.", "",
             f"Updated: {datetime.date.today().isoformat()} by `moltke --step status`.", ""]
    lines.append(f"- Last done: {last_done or 'nothing yet'}")

    active, paused = [], []
    for step_id, _p, fields in steps["plan_current"]:
        pauser = field_value(fields, "paused_by")
        goal = field_value(fields, "goal")
        (paused if pauser else active).append(
            f"{step_id} {goal}" + (f" (paused by {pauser})" if pauser else ""))
    lines.append(f"- In progress: {'; '.join(active) if active else 'none'}")
    lines.append(f"- Next: {derived_next(root) or 'no steps left in plan.md'}")
    lines.append(f"- Blocked: {'; '.join(paused) if paused else 'none'}")
    lines.append("- Parked:")
    lines.extend(parked_lines(root))

    (root / DOCS / "status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"moltke: regenerated {DOCS}/status.md from the filesystem.")
    return EXIT_OK


def _audit_baseline_path(root):
    git_dir = root / ".git"
    return git_dir / "moltke_audit_baseline.json" if git_dir.is_dir() else None


def _content_hash(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def worktree_state(root):
    """{path: [porcelain status, content hash]} for every changed path, or None
    without git. The hash is what catches a file edited before the audit and
    edited again during it: its status never moves."""
    # -uall, because plain porcelain collapses a wholly untracked directory into
    # one entry: adocs/audit/ would hide the report inside it.
    lines = _git_lines(root, "status", "--porcelain", "-uall")
    if lines is None:
        return None
    state = {}
    for line in lines:
        status, entry = line[:2], line[3:]
        if " -> " in entry:  # a rename; the new name is what exists now
            entry = entry.split(" -> ", 1)[1]
        entry = entry.strip('"')
        state[entry] = [status, _content_hash(root / entry)]
    return state


def audit_new(root, config, audit_type):
    report = root / DOCS / "audit" / f"{datetime.date.today().isoformat()}_{audit_type}.md"
    if report.exists():
        return refuse(f"{report.relative_to(root)} already exists; a report is evidence of one "
                      f"run and is never edited afterwards. Use a different type name, or "
                      f"re-run the audit tomorrow.")
    # Captured before the report exists, so the report itself shows up as part of
    # the run's footprint and is classified there rather than being invisible.
    baseline = worktree_state(root)
    template = (TEMPLATE_ROOT / "audit_report_template.md").read_text(encoding="utf-8")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(template.replace("YYYY-MM-DD_type", report.stem)
                              .replace("YYYY-MM-DD", datetime.date.today().isoformat())
                              .replace("<type>", audit_type), encoding="utf-8")
    print(f"moltke: created {report.relative_to(root)}. Write every finding before fixing "
          f"anything; finding ids are {report.stem}-F01, -F02, ...")
    baseline_path = _audit_baseline_path(root)
    if baseline is None or baseline_path is None:
        print(f"moltke: no git worktree here, so --audit check cannot reconcile this run; "
              f"whatever the reviewer changes will go unnoticed.", file=sys.stderr)
        return EXIT_OK
    try:
        baseline_path.write_text(json.dumps(
            {"report": str(report.relative_to(root)), "tree": baseline}), encoding="utf-8")
    except OSError as exc:
        print(f"moltke: could not record the audit baseline ({exc}); --audit check will "
              f"refuse until --audit new runs again.", file=sys.stderr)
    return EXIT_OK


def _is_new_file(status):
    return status in ("??", "A ")


def audit_check(root, config):
    """DEC-022: prevention gave way to detection. Report what the run actually
    changed, so a contaminated report is known before any finding is acted on."""
    baseline_path = _audit_baseline_path(root)
    saved = None
    if baseline_path is not None and baseline_path.is_file():
        try:
            saved = json.loads(baseline_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            saved = None
    if not isinstance(saved, dict) or not isinstance(saved.get("tree"), dict):
        return refuse("no audit baseline recorded here; run --audit new <type> first, because "
                      "check reconciles a run against the tree as it stood when the report "
                      "was opened")
    current = worktree_state(root)
    if current is None:
        return refuse("--audit check needs a git worktree: it compares git status against the "
                      "baseline recorded by --audit new")

    before, report = saved["tree"], saved.get("report", "")
    expected, unexpected = [], []
    for entry in sorted(set(before) | set(current)):
        was, now = before.get(entry), current.get(entry)
        if was == now:
            continue
        if now is None:
            note = f"{entry}: no longer reported as changed (reverted or committed)"
        elif was is None:
            note = f"{entry}: {now[0].strip() or 'changed'}"
        else:
            note = f"{entry}: changed again (was {was[0].strip()}, now {now[0].strip()})"
        if entry == report or (entry.startswith("tests/") and was is None
                               and _is_new_file(now[0])):
            expected.append(note)
        else:
            unexpected.append(note)

    if expected:
        print("expected, this run's report and new tests:")
        for note in expected:
            print(f"  {note}")
    if unexpected:
        print("unexpected, not attributable to writing the report:")
        for note in unexpected:
            print(f"  {note}")
        print(f"The reviewer holds Bash and is not fenced from mutating the repository "
              f"(DEC-022). Review each change above before acting on any finding: "
              f"git diff, then keep or revert deliberately.")
        return EXIT_VIOLATIONS
    if not expected:
        print("no change since --audit new; the report itself has not been written yet.")
    return EXIT_OK


def audit_list(root, config):
    audit_dir = root / DOCS / "audit"
    reports = sorted(audit_dir.glob("*.md")) if audit_dir.is_dir() else []
    references = finding_references(root)
    steps = plan_steps(root)
    unreferenced = 0
    total = 0
    for report in reports:
        findings = report_findings(report)
        if not findings:
            continue
        print(f"{report.name}")
        for finding_id, status in findings:
            total += 1
            closers = [s for dirname in PLAN_DIRS for s, _p, fields in steps[dirname]
                       if finding_id in field_value(fields, "closes")]
            if closers:
                where = f"closed by {', '.join(closers)}"
            elif finding_id in references:
                where = "referenced in decisions.md"
            else:
                where = "no reference"
                if status == "open":
                    unreferenced += 1
            print(f"  {finding_id}  {status}  ({where})")
    if not total:
        print("moltke: no findings recorded.")
        return EXIT_OK
    if unreferenced:
        print(f"moltke: {unreferenced} open finding(s) have no plan step and no decision. "
              f"Every finding ends in a step whose closes: names it, or a decisions.md entry "
              f"stating why it is accepted.")
        return EXIT_VIOLATIONS
    return EXIT_OK


AUDIT_OPS = ("new", "list", "check")


def mode_audit(root, config, argv):
    op, rest = argv[0], argv[1:]
    if op not in AUDIT_OPS:
        return refuse(f"unknown --audit operation {op!r}; use one of {', '.join(AUDIT_OPS)}")
    if op == "list":
        return audit_list(root, config)
    if op == "check":
        return audit_check(root, config)
    if not rest:
        return refuse("usage: --audit new <type>   (for example: adversarial, security)")
    return audit_new(root, config, rest[0])


STEP_OPS = ("new", "start", "block", "done", "status")


def mode_step(root, config, argv, goal, stamp):
    op, rest = argv[0], argv[1:]
    if op not in STEP_OPS:
        return refuse(f"unknown --step operation {op!r}; use one of {', '.join(STEP_OPS)}")
    try:
        if op == "new":
            return step_new(root, config, rest[0], goal)
        if op == "start":
            return step_start(root, config, rest[0])
        if op == "block":
            return step_block(root, config, rest[0], rest[1])
        if op == "done":
            return step_done(root, config, rest[0], stamp)
        return step_status(root, config)
    except IndexError:
        usage = {"new": "new <short_name> [--goal TEXT]", "start": "start <id>",
                 "block": "block <parent_id> <short_name>",
                 "done": "done <id> --stamp TEXT"}[op]
        return refuse(f"usage: --step {usage}")


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


def build_parser():
    """The public surface, in one place so the golden test can read it (DEC-010)."""
    parser = argparse.ArgumentParser(prog="moltke.py", description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--session-start", action="store_true", help="SessionStart hook (S005)")
    modes.add_argument("--log-prompt", action="store_true", help="UserPromptSubmit hook (S005)")
    modes.add_argument("--pre-write", metavar="PATH", nargs="?", const="",
                       help="PreToolUse hook for Write and Edit; PATH falls back to hook stdin JSON")
    modes.add_argument("--post-write", action="store_true", help="PostToolUse hook (S005)")
    modes.add_argument("--stop", action="store_true", help="Stop hook (S005)")
    modes.add_argument("--validate", action="store_true", help="run every invariant, report all violations")
    modes.add_argument("--scaffold", action="store_true", help=f"create the marker, AGENTS.md, and {DOCS}/ from templates")
    modes.add_argument("--decline", action="store_true", help="record that this repository declines the workflow, durably")
    modes.add_argument("--step", nargs="+", metavar="OP",
                       help="lifecycle: new <name> | start <id> | block <parent> <name> | done <id> | status")
    modes.add_argument("--audit", nargs="+", metavar="OP",
                       help="audit reports: new <type> | list")
    parser.add_argument("--goal", default="", help="goal line for --step new")
    parser.add_argument("--stamp", default="", help="completion stamp for --step done")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

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
    if args.step:
        return mode_step(root, config, args.step, args.goal, args.stamp)
    if args.audit:
        return mode_audit(root, config, args.audit)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
