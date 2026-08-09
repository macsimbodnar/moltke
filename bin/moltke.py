#!/usr/bin/env python3
"""moltke: document-driven workflow checker. Single entry point for hooks and manual runs.

Standard library only: this runs on every prompt, so startup cost matters.
INV-11: every mode exits 0 immediately when .moltke.json is absent or enabled is false.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MARKER = ".moltke.json"
DOCS = "adocs"  # agent documentation; renamed from project/ by DEC-021
SURFACE_GUARD_VALUES = ("cli", "api", "both", "none")
# The marker keys check_marker recognises. Part of the guarded public surface
# (S023): adding, renaming, or removing one fails the golden until the specs and
# MANUAL describe it. A key absent here is ignored rather than rejected, so an
# unknown key is never a violation.
MARKER_KEYS = ("schema", "enabled", "plan_active_max", "plan_stack_max",
               "surface_guard", "test_command")

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
        config = json.loads(read_file(path))
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
    # Optional (DEC-023), so schema stays 1 and no existing marker migrates. A
    # blank value is a violation rather than a no-op: silently gating nothing is
    # the failure this key exists to remove.
    if "test_command" in config:
        command = config["test_command"]
        if not isinstance(command, str) or not command.strip():
            violations.append(
                f'{MARKER}: "test_command" must be a non-empty shell command string, '
                f'got {command!r}; remove the key to leave the suite gate unconfigured'
            )
    return violations


STEP_FILE_RE = re.compile(r"^(S\d{3})_[A-Za-z0-9_]+\.md$")
PLAN_DIRS = ("plan_todo", "plan_current", "plan_done")
# The short name is the second half of a filename STEP_FILE_RE has to match, so
# the two are one rule stated twice and this is the half that is written
# (S088, 2026-08-08_adversarial.4-F01).
STEP_NAME_RE = re.compile(r"[A-Za-z0-9_]+")


def step_name_problem(name):
    """S088: the name went unchecked into `f"{step_id}_{name}.md"`. A hyphen
    produced a file STEP_FILE_RE does not match, so every scanner keyed on it
    skipped the file while plan.md listed the id — the tool that exists to keep
    those two in step creating the listed-but-absent half of INV-3 itself. A
    separator escaped the plan directory outright. `--audit new` refuses its type
    for the same reason and is the model copied here."""
    if STEP_NAME_RE.fullmatch(name):
        return None
    return (f"step name {name!r} must match [A-Za-z0-9_]+ so that {DOCS}/plan_*/S000_{{name}}.md "
            f"is a filename inside one plan directory and matches the pattern every scanner "
            f"reads; a hyphen or a dot makes a file no invariant check can see, and a separator "
            f"puts it outside the plan entirely. Use underscores: fix_parser, not fix-parser")


STEP_FIELD_RE = re.compile(r"^([a-z_]+):\s*(.*)$")


def parse_step_file(path):
    """Fields, with indented continuation lines folded into the value.

    S095: this matched per line and a continuation matches nothing, so every
    field was silently truncated to its first line. Found live during S059 — the
    Stop stamp gate reported the README and MANUAL check missing from a stamp
    that recorded it two lines down — and goal:, accepts:, touches: and
    excludes: span lines throughout the plan directories, so every reader of
    those had been seeing the opening line alone. A flush-left `word:` starts a
    new field, and a blank line ends the current one; only an indented non-empty
    line continues it.
    """
    fields, current = {}, None
    for line in read_file(path).splitlines():
        match = STEP_FIELD_RE.match(line)
        if match:
            current = match.group(1)
            fields.setdefault(current, match.group(2).strip())
            continue
        if current and line.strip() and line[:1].isspace():
            fields[current] = f"{fields[current]} {line.strip()}".strip()
            continue
        current = None
    return fields


COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE_MARKER = re.compile(r"^ {0,3}```", re.M)


def read_file(path):
    """Every repository file moltke reads, decoded one way (S064,
    2026-08-08_adversarial-F05).

    Thirteen readers decoded strictly and six replaced, and INV-14's two halves
    disagreed about the same file — the recurring shape, a rule tightened in one
    place and not its twin. One byte of latin-1 in a pasted terminal capture then
    turned every mode into a traceback, which from a Stop hook means exit 1, no
    message, and every gate off for the turn.

    Replacing rather than raising is the right default here because moltke reads
    files it did not write and must keep reporting on them: a mojibake character
    in a step file is a cosmetic problem, and a checker that cannot start is not.
    """
    return path.read_text(encoding="utf-8", errors="replace")


def strip_comments(text):
    """HTML comments out. Guidance in a template is written as one, and INV-16
    needs the same notion of "nothing written here" that strip_guidance uses."""
    return COMMENT.sub("", text)


def fence_markers(text):
    """(text without HTML comments, the fence markers in it).

    One definition, because two diverged (S055, .2-F08): INV-13 counted markers
    in the raw file while `strip_guidance` removed comments first, so a marker
    inside a comment blocked `--stop` under a message that was false for that
    file — nothing was swallowed — and following the message would have
    unbalanced a pairing that was already correct.

    Markers must open a line (S033). A marker quoted in a worklog prompt arrives
    as `> ``` `, because every prompt line is quoted, and one written inline in a
    sentence is not at the start of a line: neither is a fence.
    """
    text = strip_comments(text)
    return text, list(FENCE_MARKER.finditer(text))


def strip_guidance(text):
    """Drop fenced blocks and HTML comments.

    Templates carry their own format as an example. Every scanner in this file
    reads it through here, so guidance is never counted as data: a commented
    step is not planned, an example finding is not open, an example decision id
    is not taken.
    """
    text, marks = fence_markers(text)
    # Markers are paired in order (S033). Pairing `.*?` globally meant one stray
    # marker shifted every later pairing and deleted the real content between two
    # unrelated fences, so a rule for making guidance invisible was making
    # evidence invisible instead. An unpaired trailing marker is text: swallowing
    # to end of file is exactly the failure.
    kept, pos = [], 0
    for opener, closer in zip(marks[::2], marks[1::2]):
        line_end = text.find("\n", closer.end())
        kept.append(text[pos:opener.start()])
        pos = len(text) if line_end < 0 else line_end + 1
    kept.append(text[pos:])
    return "".join(kept)


STRIPPED_FILES = ("plan.md", "decisions.md", "worklog.md", "specs.md", "testing.md")


def stripped_files(root):
    """Every repository file read through `strip_guidance`, INV-13's scan list.

    One list, derived from the readers rather than written beside them (S063,
    2026-08-08_adversarial-F04): INV-13 scanned three files chosen by hand, S028
    added `specs.md` as a fourth consumer through `prime_directive`, and neither
    guard applied to it — a fence there hid the prime directive with every check
    green. Audit reports are found rather than listed, since their names are
    dates.
    """
    files = [f"{DOCS}/{name}" for name in STRIPPED_FILES]
    audit_dir = root / DOCS / "audit"
    if audit_dir.is_dir():
        files += [str(p.relative_to(root)) for p in sorted(audit_dir.glob("*.md"))]
    return files


def hides_content(text):
    """Whether stripping guidance would remove anything from `text`.

    The comparison INV-14 and INV-16 both make, in one place, so it stays inside
    the short list of lines allowed to call `strip_guidance` (S078).
    """
    return strip_guidance(text).strip() != text.strip()


def read_stripped(path):
    """A repository file with guidance stripped. Every whole-file read through
    `strip_guidance` goes via here, so INV-13 and the scanners cannot disagree
    about which files are guarded (S063)."""
    text = read_file(path)
    return strip_guidance(text)


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


def pauser_id(fields):
    """The step id a `paused_by` names, or None. The field carries a dated
    comment, so it is matched rather than compared."""
    found = re.search(r"S\d{3}", field_value(fields, "paused_by"))
    return found.group(0) if found else None


def unresolvable_pauses(root, steps=None):
    """{step_id: ("phantom", pauser) or ("cycle", [members])} for every pause a
    step cannot get out from under.

    A pause is what takes a step out of INV-1's active count, so a pause that
    does not resolve parks a step behind nothing while every check stays green.
    Two shapes, one rule. S090 (.4-F03) covered the pauser that is in no plan
    directory. S098 (2026-08-09_adversarial-F02) covers the rest of it: a step
    that pauses itself, or a ring of steps pausing each other, satisfies S090's
    rule — every pauser exists — and is just as stuck, with `--step done` and
    `--step unpause` naming each other.

    A pauser in `plan_done/` terminates the walk rather than continuing it: that
    is S070's stale pause, which `--step done` reports and steps over.

    Shared with `step_unpause` so "clear it with --step unpause" is true by
    construction rather than by two descriptions agreeing.
    """
    steps = plan_steps(root) if steps is None else steps
    known = {found for dirname in PLAN_DIRS for found, _p, _f in steps[dirname]}
    pauses = {step_id: pauser_id(fields)
              for step_id, _path, fields in steps["plan_current"] if pauser_id(fields)}
    problems = {}
    for step_id, pauser in pauses.items():
        if pauser not in known:
            problems[step_id] = ("phantom", pauser)
            continue
        seen, current = [step_id], pauses.get(step_id)
        while current is not None and current not in seen:
            seen.append(current)
            current = pauses.get(current)
        if current is not None:
            problems[step_id] = ("cycle", seen[seen.index(current):])
    return problems


def inv_1_active_max(root, config):
    limit = _limit(config, "plan_active_max", 1)
    steps = plan_steps(root)
    active = [s for s, _p, fields in steps["plan_current"]
              if not field_value(fields, "paused_by")]
    violations = []
    if len(active) > limit:
        violations.append(
            f"INV-1: plan_current/ holds {len(active)} non-paused steps ({', '.join(active)}), "
            f"limit {limit}; pause or complete until {limit} remain")
    # INV-3 already reports the same shape for an id plan.md lists with no file;
    # this is that rule for paused_by.
    for step_id, (kind, detail) in sorted(unresolvable_pauses(root, steps).items()):
        if kind == "phantom":
            violations.append(
                f"INV-1: {step_id} is paused by {detail}, which has no step file in any plan "
                f"directory, so it waits on work that does not exist and no completion can "
                f"reach it. Clear it with bin/moltke.py --step unpause {step_id}")
        else:
            ring = " -> ".join(detail + [detail[0]])
            violations.append(
                f"INV-1: the pause on {step_id} never resolves: {ring}. Every step in that "
                f"ring waits on another step in it, so none of them counts as active, none can "
                f"be completed, and no invariant would otherwise say so. Clear it with "
                f"bin/moltke.py --step unpause {step_id}")
    return violations


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
    # One definition of "listed", used in both directions (S048, .2-F02): a list
    # entry, exactly what plan_order and so derived_next read. Matching any
    # mention let a step named only in the description satisfy this check while
    # being invisible to the derived next step — passing validation and never
    # coming up for work. An id in prose is prose: not listed, and not a phantom.
    listed = plan_order(root) or []
    for dirname in ("plan_todo", "plan_current"):
        for step_id, path, _fields in steps[dirname]:
            if step_id not in listed:
                violations.append(f"INV-3: {path.relative_to(root)} is not listed in plan.md; "
                                  f"add {step_id} to the ordered list, since a mention in the "
                                  f"description is not the plan and never becomes the next step")
    # And the reverse (S024, F11): a mistyped entry would otherwise sit in the
    # order forever with nothing to work on.
    filed = {step_id for dirname in PLAN_DIRS for step_id, _p, _f in steps[dirname]}
    for step_id in listed:
        if step_id not in filed:
            violations.append(f"INV-3: plan.md lists {step_id} but no step file exists in "
                              f"plan_todo/, plan_current/, or plan_done/; create it with "
                              f"--step new, or fix the id in plan.md")
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
        # Through read_stripped, like every other scanner input (S085, .3-F06):
        # this ledger was the last file read raw, so a row inside a code fence —
        # guidance by the rule specs states as universal — counted as evidence
        # and completed a step.
        rows = "\n".join(l for l in read_stripped(testing_path).splitlines()
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


def git_blobs(root, specs):
    """{"<sha>:<path>": bytes} in one `git cat-file --batch`, missing keys absent.

    One process rather than one per version: DEC-026 moved these checks from
    reading a diff summary to comparing content, and --validate runs on every
    Stop.
    """
    specs = list(dict.fromkeys(specs))
    if not specs:
        return {}
    result = _git_run(["git", "-C", str(root), "cat-file", "--batch"],
                      input=("\n".join(specs) + "\n").encode())
    if result is None or result.returncode != 0:
        return {}
    blobs, out, pos = {}, result.stdout, 0
    for spec in specs:
        end = out.find(b"\n", pos)
        if end < 0:
            break
        header = out[pos:end].decode(errors="replace").split()
        pos = end + 1
        if len(header) != 3 or not header[2].isdigit():
            continue  # "<spec> missing"; the object simply is not there
        size = int(header[2])
        blobs[spec] = out[pos:pos + size]
        pos += size + 1  # the trailing newline cat-file adds after each object
    return blobs


def history_blocks(root, *args):
    """[(sha, [detail lines])] oldest first, or None without history.

    S018 (F04): HEAD is not a baseline, it is a moving target — the workflow
    commits at every step completion, so a working-tree comparison stops seeing
    tampering the moment it is committed. History is the only fixed baseline.
    --no-renames throughout, so a move into a directory reads as the addition it
    is and a move out reads as the deletion it is.
    """
    lines = _git_lines(root, "log", "--reverse", "--no-renames", "--format=%H", *args)
    if lines is None:
        return None
    blocks = []
    for line in lines:
        if "\t" in line:
            if blocks:
                blocks[-1][1].append(line)
        elif re.fullmatch(r"[0-9a-f]{7,40}", line):
            blocks.append((line, []))
    return blocks


def inv_7_done_immutable(root, config):
    # Two baselines, because they catch different things: git HEAD sees tampering
    # that is not committed yet, history sees tampering that is. Additions are
    # the one legal change (append by move only). No git history, no baseline, so
    # the check abstains.
    result = _git_run(
        ["git", "-C", str(root), "status", "--porcelain", "--", f"{DOCS}/plan_done"], text=True)
    violations = []
    if result is not None and result.returncode == 0:
        for line in result.stdout.splitlines():
            status = line[:2]
            if not any(code in status for code in ("M", "D", "R", "C", "U")):
                continue
            # Through porcelain_paths, which S050 added for exactly this and
            # which this line never learned to use (S071, .2-F05). A rename is
            # one line, `R  old -> new`, and slicing it produced a remedy that a
            # shell reads as a redirection: `git checkout -- old > new`
            # truncates the renamed file — the only remaining content of that
            # step, printed by the one invariant whose subject is immutable
            # history, and repeated to --stop as an actionable instruction.
            paths = [from_git_path(root, path) for path in porcelain_paths(line)]
            if any(path is None for path in paths):
                continue    # another package in the same repository (S081)
            entry = paths[-1]
            if len(paths) > 1:
                # A rename needs undoing, not restoring (S084, .3-F05): S071
                # made this message safe to paste and left it a no-op, because
                # `git checkout -- <new path>` restores the new path from an
                # index that already holds the rename. Following it and the
                # deletion message together wrote the old name back beside the
                # new one, which is an INV-6 duplicate id.
                violations.append(
                    f"INV-7: {entry} is {paths[0]} renamed, and plan_done/ is immutable "
                    f"history: file names there are cited from commits and reports. Undo it "
                    f"with git mv {entry} {paths[0]}")
                continue
            violations.append(f"INV-7: {entry} changed under plan_done/; history is "
                              f"immutable: restore it with git checkout -- {entry}")

    # DEC-026: judge the content, not the existence of a bad commit. A file is
    # clean when its bytes still match the version at the commit that added it,
    # so restoring the original clears the violation and history is never
    # rewritten. Judging on "an M commit exists" had no way back to green.
    landed = {}
    for sha, details in history_blocks(root, "--name-status", "--", f"{DOCS}/plan_done") or []:
        for detail in details:
            status, entry = detail.split("\t")[0], detail.split("\t")[-1]
            entry = from_git_path(root, entry)
            if entry is None:
                continue    # another package in the same repository (S081)
            if status.startswith("A") and entry not in landed:
                landed[entry] = sha
    # The blob spec is a path from the git top level; everything moltke prints
    # is a path from the marked root, and they differ whenever the two are not
    # the same directory (S081).
    blobs = git_blobs(root, [f"{sha}:{to_git_path(root, entry)}"
                             for entry, sha in landed.items()])
    for entry, sha in sorted(landed.items()):
        original = blobs.get(f"{sha}:{to_git_path(root, entry)}")
        if original is None:
            continue  # nothing to compare against; abstain rather than guess
        path = root / entry
        if not path.is_file():
            violations.append(
                f"INV-7: {entry} landed in plan_done/ at commit {sha[:8]} and is gone; "
                f"completed history is never removed. Restore it in a new commit: "
                f"git show {sha[:8]}:{to_git_path(root, entry)} > {entry}")
        elif path.read_bytes() != original:
            violations.append(
                f"INV-7: {entry} no longer matches the version that landed at commit "
                f"{sha[:8]}; plan_done/ is append by move only. Restore those bytes in a new "
                f"commit and this clears: git show {sha[:8]}:{to_git_path(root, entry)} > "
                f"{entry}. Never rewrite "
                f"the history that recorded the change")
    return violations


# decisions.md only, since DEC-025: DEC ids are cited from code comments, commit
# messages, specs.md, and step files, so a rewritten entry silently changes what
# those citations mean. worklog.md is history nothing cites by id, so it is
# append-only by convention and unchecked.
APPEND_ONLY_FILES = (f"{DOCS}/decisions.md",)
FINDING_STATUSES = ("open", "planned", "closed", "accepted")
FINDING_RE = re.compile(r"^###\s+(\S*-F\d{2})\b", re.M)


def lines_survive(past, current):
    """True when every line of `past` still appears in `current`, in order."""
    it = iter(current)
    return all(any(line == candidate for candidate in it) for line in past)


def inv_8_append_only(root, config):
    # Two baselines, same reasoning as INV-7: HEAD for the uncommitted window,
    # history for everything already committed. Untracked files have neither.
    violations = []
    # DEC-026: append-only means the current content still starts with every
    # version the file has ever had. Restoring removed text makes that true
    # again, so a repair commit clears this; "a commit removed lines" never could.
    for rel in APPEND_ONLY_FILES:
        shas = [sha for sha, _details in history_blocks(root, "--", rel) or []]
        if not shas:
            continue
        spec = to_git_path(root, rel)   # git names it from the top level (S081)
        blobs = git_blobs(root, [f"{sha}:{spec}" for sha in shas])
        path = root / rel
        if not path.is_file():
            violations.append(f"INV-8: {rel} has {len(shas)} commit(s) of history and is gone; "
                              f"it is append-only and never removed: restore it in a new commit, "
                              f"git show {shas[-1][:8]}:{spec} > {rel}")
            continue
        # The high-water mark of content that was ever legitimately in the file
        # (S046). Walk the versions oldest first: one that still contains
        # everything required becomes the new mark, one that dropped something
        # is a tampering and is skipped rather than becoming the mark. The file
        # as it stands must then contain the mark's lines, in order.
        #
        # Neither half works alone, and DEC-027 records why. Comparing against
        # every past version can never pass after a repair, because the tampered
        # version is itself history and holds text the repair rightly discarded.
        # Comparing against one fixed baseline misses any rewrite of text
        # appended after it. Skipping tampered versions is what reconciles them:
        # a repair restores the mark and clears everything at once, while a
        # removal, an in-place rewrite, and a line moved to the end are all
        # caught, because in each case a required line is no longer in order.
        required, required_sha = None, shas[0]
        for sha in shas:
            past = blobs.get(f"{sha}:{spec}")
            if past is None:
                continue
            lines = past.splitlines()
            if required is None or lines_survive(required, lines):
                required, required_sha = lines, sha
        if required is not None and not lines_survive(required, path.read_bytes().splitlines()):
            violations.append(
                f"INV-8: {rel} no longer contains, in order, the lines it had at commit "
                f"{required_sha[:8]}; nothing it has held is removed or reordered, because DEC "
                f"ids are cited from code, commits, and specs and a rewritten entry changes what "
                f"those citations mean. Put the removed content back where it was and this "
                # `spec`, not `rel` (S093, .4-F06): git show resolves from the top
                # level, so below it the root-relative path is a path git does not
                # have. S081 threaded the prefix through every other reader of this
                # file and missed this one message.
                f"clears: git show {required_sha[:8]}:{spec}. A reversal is a new entry marking "
                f"the old one VOID, never an edit")
    for rel in APPEND_ONLY_FILES:
        shown = _git_run(["git", "-C", str(root), "show", f"HEAD:{to_git_path(root, rel)}"])
        if shown is None or shown.returncode != 0:
            continue
        path = root / rel
        if not path.is_file():
            violations.append(f"INV-8: {rel} was deleted; it is append-only and never removed: "
                              f"restore it with git checkout -- {rel}")
        elif not path.read_bytes().startswith(shown.stdout):
            violations.append(f"INV-8: {rel} no longer starts with what HEAD holds, so something "
                              f"above the end changed, because DEC ids are cited from code, "
                              f"commits, and specs and a rewritten entry changes what those "
                              f"citations mean: restore the committed content and re-append. "
                              f"A reversal is a new entry marking the old one VOID")
    return violations


def inv_9_unique_dec_ids(root, config):
    path = root / DOCS / "decisions.md"
    if not path.is_file():
        return []
    seen, violations = set(), []
    text = read_stripped(path)
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
        # Through strip_guidance like every other scanner (S019, F05): a finding
        # id inside a fenced example is guidance, and the scaffolded
        # decisions.md ships exactly such an example.
        references.append(read_stripped(decisions))
    return "\n".join(references)


def own_finding_headings(text, stem):
    """Finding ids in `text` whose id carries `stem`, this report's own name.

    Scoped to the stem on purpose (S049). A foreign id is quotable evidence — the
    verdict section of every re-run is nothing but quoted headings — and the
    shipped report template fences an example finding under the placeholder stem
    `YYYY-MM-DD_type`. Both must stay guidance. Only a heading naming this file's
    own report can be a finding of this file.
    """
    return [match.group(1) for match in FINDING_RE.finditer(text)
            if re.fullmatch(rf"{re.escape(stem)}-F\d{{2}}", match.group(1))]


def hidden_findings(report):
    """Ids this report declares in its raw text but hides from every scanner.

    S049 (2026-08-07_adversarial-F02): two unclosed evidence fences are two
    markers, so they pair as one closed fence and everything between them —
    including a whole finding — is stripped before any check sees it. The count
    stays even, so INV-13 is silent. Comparing the headings the file states
    against the ones that survive stripping needs no guess about which meaning
    the markers had: either way, a finding the report names is unreadable.
    """
    # Comments come out first (S075, .2-F09): strip_guidance removes them too,
    # so a heading inside one read as hidden and the message blamed a code fence
    # that was not there, with a remedy — close the evidence blocks — that could
    # not be followed. Commented content is guidance everywhere else, the
    # shipped template's own append marker is a comment, and commenting out a
    # draft finding is a reasonable thing to do. What is left is what a fence
    # can hide, so the message is now always true of what it names.
    raw = strip_comments(read_file(report))
    visible = {finding_id for finding_id, _status in report_findings(report)}
    ids = []
    for finding_id in own_finding_headings(raw, report.stem):
        if finding_id not in visible and finding_id not in ids:
            ids.append(finding_id)
    return ids


def report_findings(report):
    """[(finding_id, status)] for a report. Fenced examples and comments in the
    template are guidance, not findings."""
    text = read_stripped(report)
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
            # Exact, not startswith: a same-day re-run is `<stem>.2`, so the first
            # report's stem is a prefix of the re-run's and a re-run id would
            # otherwise sit unnoticed in the first report (S020).
            if not re.fullmatch(rf"{re.escape(report.stem)}-F\d{{2}}", finding_id):
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


def inv_13_balanced_fences(root, config):
    """S033: two unclosed fences are indistinguishable from one closed fence, and
    the templates deliberately put headings inside fences, so no rule can tell
    them apart by content. Report the imbalance instead of guessing, because a
    guess loses a finding or a recap heading and says all checks pass."""
    violations = []
    for rel in stripped_files(root):
        path = root / rel
        if not path.is_file():
            continue
        # Through fence_markers, so this counts exactly what strip_guidance
        # pairs: a marker inside an HTML comment is neither stripped as a fence
        # nor counted as one (S055).
        count = len(fence_markers(read_file(path))[1])
        if count % 2:
            violations.append(
                f"INV-13: {rel} has {count} code-fence markers, an odd number, so one fence is "
                f"unclosed. Every scanner reads this file through strip_guidance, which pairs "
                f"markers in order: close the fence, or the content it swallows is invisible to "
                f"the checks that read this file")
    return violations


# (label, pattern, a known-bad example the pattern must catch). The examples
# travel with the shapes on purpose (DEC-032): the suite asserts each pattern
# against its own example before scanning anything, so a pattern that stopped
# matching cannot leave the check passing by failing to look. They are synthetic.
SECRET_SHAPES = [
    ("AWS access key id",
     re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
     "AKIA" + "IOSFODNN7EXAMPLE"),
    ("GitHub token",
     re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
     "ghp_" + "0123456789abcdefghijklmnopqrstuvwxyzAB"),
    ("GitHub fine-grained PAT",
     re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b"),
     "github_pat_" + "11ABCDEFG0abcdefghijklmn"),
    ("Anthropic API key",
     re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
     "sk-ant-" + "api03-Aa0Bb1Cc2Dd3Ee4Ff5Gg6"),
    ("OpenAI API key",
     re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}\b"),
     "sk-" + "Aa0Bb1Cc2Dd3Ee4Ff5Gg6Hh7Ii8Jj9Kk0Ll1"),
    ("Slack token",
     re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
     "xoxb-" + "1234567890-ABCdefGHIjkl"),
    ("Google API key",
     re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
     "AIza" + "SyA0123456789abcdefghijklmnopqrstuv"),
    ("Stripe live key",
     re.compile(r"\b[srp]k_live_[A-Za-z0-9]{16,}\b"),
     "sk_live_" + "0123456789abcdefghij"),
    ("npm token",
     re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"),
     "npm_" + "0123456789abcdefghijklmnopqrstuvwxyz"),
    ("PEM private key header",
     re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
     "-----BEGIN RSA PRIVATE KEY-----"),
    ("JSON web token",
     re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
     "eyJhbGciOiJIUzI1NiJ9." + "eyJzdWIiOiIxMjM0NTY3ODkwIn0." + "dBjftJeZ4CVPmB92K27u"),
]


def scan_secrets(text):
    """[(label, line number, first 8 characters of the match)] for every hit.

    Prefixed key shapes and PEM headers only. No entropy or bare-hex rule: a
    worklog carries a commit sha in every recap and md5 digests wherever a file
    was verified, and those rules would fire on every work turn (DEC-024). The
    trade is deliberate — catch the shapes worth catching, stay quiet otherwise.
    """
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        for label, pattern, _example in SECRET_SHAPES:
            match = pattern.search(line)
            if match:
                hits.append((label, number, match.group(0)[:8]))
    return hits


PRIME_DIRECTIVE_SECTION = re.compile(r"^##\s+Prime directive\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)


def inv_16_prime_directive_readable(root, config):
    """S063: a prime directive that is written and unreadable is worse than one
    that is missing, because the missing one is reported.

    INV-13's parity cannot reach this. Two example fences with their closers
    removed are an even count, and one closed fence around the directive is the
    same bytes — the ambiguity DEC-033 recorded. So this compares what the file
    states against what survives stripping, exactly as INV-14 does for a finding
    heading: either way, `specs.md` names a directive nothing can read, and
    `--session-start` asks for one that is already there.
    """
    specs = root / DOCS / "specs.md"
    if not specs.is_file():
        return []
    raw = PRIME_DIRECTIVE_SECTION.search(read_file(specs))
    if not raw:
        return []
    stated = strip_comments(raw.group(1)).strip()
    if not stated:
        return []   # nothing written yet: that is the planning nudge's business
    # Compare the two sides rather than testing both for emptiness (S078,
    # .2-F12). Returning clean as soon as prime_directive was non-empty passed a
    # section holding a lead-in sentence and the rule itself inside a fence: the
    # directive unreadable, nothing reporting it, and prime_directive answering
    # with the lead-in. The section is one sentence by design, so anything a
    # fence removes from it is content no check can read.
    if not hides_content(stated):
        return []
    return [f"INV-16: {DOCS}/specs.md states a prime directive that a code fence swallows, so "
            f"what every check reads is not what the file says — and --session-start may be "
            f"asking for a directive that is already there. The marker count is even, which is "
            f"why INV-13 is quiet: close the example blocks around it, or move them out of "
            f"the section"]


def inv_15_worklog_secrets(root, config):
    """DEC-032: the check travels with the plugin instead of protecting moltke
    alone. Every marked repository logs prompts verbatim into a tracked file, so
    the exposure is a property of every repository moltke is installed into, and
    the tool writing the secret to disk is the one that should say so.

    Detect, never redact (DEC-024): redaction at write time would contradict the
    verbatim guarantee, and a false positive would silently destroy the record of
    what was said. Never prints more than the first 8 characters of a match.
    """
    worklog = root / DOCS / "worklog.md"
    if not worklog.is_file():
        return []
    violations = []
    for label, number, snippet in scan_secrets(
            read_file(worklog)):
        violations.append(
            f"INV-15: {DOCS}/worklog.md line {number} holds something shaped like a "
            f"{label} (starts {snippet!r}). Prompts are recorded verbatim, so treat it as a "
            f"real leak until proven otherwise: rotate the credential first, because it is "
            f"already committed, then edit the worklog — it is append-only by convention and "
            f"not enforced, so cleaning it is an ordinary commit")
    return violations


def inv_14_findings_not_hidden(root, config):
    """S049: INV-13 catches one unclosed fence. Two are an even count and pair as
    one closed fence, which is the shape a reviewer produces by pasting two
    transcripts and closing neither, and it deletes the finding between them."""
    audit_dir = root / DOCS / "audit"
    if not audit_dir.is_dir():
        return []
    violations = []
    for report in sorted(audit_dir.glob("*.md")):
        for finding_id in hidden_findings(report):
            violations.append(
                f"INV-14: {report.name} states finding {finding_id} but a code fence swallows "
                f"it, so INV-10 and --audit list never see it. Two unclosed fences pair as one "
                f"closed fence and the marker count stays even, which is why INV-13 is quiet: "
                f"close the evidence blocks around that heading")
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
    ("INV-13", inv_13_balanced_fences),
    ("INV-14", inv_14_findings_not_hidden),
    ("INV-15", inv_15_worklog_secrets),
    ("INV-16", inv_16_prime_directive_readable),
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


def payload_str(payload, *keys):
    """A nested payload field as a string, or "" when it is anything else.

    Only the top level was checked and every consumer assumed the nested types
    (S087, .3-F08). A `PreToolUse` hook that dies exits 1, which is
    non-blocking, so the write it was judging went ahead: the reviewer fence and
    the plan_done/ refusal failing open, the direction S016 named as the wrong
    one. Nothing establishes that Claude Code sends these shapes; the fence must
    not depend on that.
    """
    value = payload
    for key in keys:
        if not isinstance(value, dict):
            return ""
        value = value.get(key)
    return value if isinstance(value, str) else ""


def plan_text(root):
    """plan.md with comments and fenced blocks stripped: commented-out
    example steps are not the plan."""
    plan_path = root / DOCS / "plan.md"
    if not plan_path.is_file():
        return None
    return read_stripped(plan_path)


# A list entry, not prose: "1. S001", "- S001", "* S001". S045 — reading every
# id in document order let a description paragraph decide the next step, since
# order lives in the list and nowhere else (DEC-008).
PLAN_ENTRY_RE = re.compile(r"^\s*(?:\d+\.|[-*])\s+(S\d{3})\b", re.M)


def plan_order(root):
    """Step ids in plan order, from plan.md's list entries, first mention wins."""
    plan = plan_text(root)
    if plan is None:
        return None
    order, seen = [], set()
    for step_id in PLAN_ENTRY_RE.findall(plan):
        if step_id not in seen:
            seen.add(step_id)
            order.append(step_id)
    return order


def derived_next(root):
    """First step in plan.md order not yet in plan_done/ (AGENTS.md §1)."""
    order = plan_order(root)
    if order is None:
        return None
    done = {s for s, _p, _f in plan_steps(root)["plan_done"]}
    for step_id in order:
        if step_id not in done:
            return step_id
    return None


STATUS_FIELDS = ("Last done", "In progress", "Next", "Blocked")


def status_fields(text):
    """{field: value} for the four derived lines of status.md.

    Everything from `- Parked:` onward is the human's to write, and the
    `Updated:` line is a timestamp, so neither is compared.
    """
    head = text.split("\n- Parked:")[0]
    found = {}
    for line in head.splitlines():
        match = re.match(r"^-\s*([A-Za-z ]+?):\s*(.*)$", line)
        if match and match.group(1) in STATUS_FIELDS:
            found.setdefault(match.group(1), match.group(2).strip())
    return found


def status_disagreements(root):
    """[(field, what status.md says, what the filesystem says)].

    S039 (F08): only `Next:` used to be compared, and that is the one field the
    file and the filesystem rarely disagree about, because both derive it the
    same way. The in-progress stack is the field a crashed session corrupts.
    """
    path = root / DOCS / "status.md"
    stated = status_fields(read_file(path)) if path.is_file() else {}
    derived = status_fields("\n".join(status_lines(root)))
    return [(field, stated.get(field, "nothing"), value)
            for field, value in derived.items() if stated.get(field) != value]


def prime_directive(root):
    """The prime directive as written, or "" while it is still the template's
    comment. Read through strip_guidance like every other scanner, so a comment
    or a fenced example is guidance rather than an answer."""
    specs = root / DOCS / "specs.md"
    if not specs.is_file():
        return ""
    text = read_stripped(specs)
    match = re.search(r"^##\s+Prime directive\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return match.group(1).strip() if match else ""


def planning_pending(root):
    """Which of the two files the planning phase has not filled yet (S028).

    `--scaffold` writes both with their content as a comment, because the prime
    directive and the plan are the two things the workflow cannot write for the
    user. Nothing said so: every check reported green on a repository that had
    adopted the workflow and not yet used it.
    """
    if not (root / DOCS).is_dir():
        return []   # not scaffolded at all; --scaffold is the advice, not this
    pending = []
    if not prime_directive(root) and not inv_16_prime_directive_readable(root, None):
        # Written-but-unreadable is INV-16's to report, not this one's: asking
        # for a directive that is already on disk sends the user to rewrite what
        # is there instead of closing the fence around it (S063).
        pending.append(f"{DOCS}/specs.md has no prime directive yet")
    if not plan_order(root):
        pending.append(f"{DOCS}/plan.md lists no steps yet")
    return pending


def mode_session_start(root, config):
    # The envelope is printed whatever happens (S068, .2-F02). Everything below
    # was built before the single print, so one unreadable path lost the whole
    # payload: exit 0 with empty stdout, the one combination a zero-exit hook
    # cannot recover from, since its stderr reaches nobody. That is why S014 put
    # the prompt-failure breadcrumb on this channel — and a session with this
    # problem is exactly the session that would not hear about it.
    lines = []
    try:
        lines = session_context_lines(root, config)
    except OSError as exc:
        lines.append(f"moltke: could not read the repository ({exc}). Nothing below is "
                     f"reliable until that path is fixed; run bin/moltke.py --validate.")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n".join(lines),
    }}))
    return EXIT_OK


def session_context_lines(root, config):
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
    stale = status_disagreements(root)
    if stale:
        disagreements = "; ".join(f"{field} says {said!r}, filesystem says {real!r}"
                                  for field, said, real in stale)
        lines.append(f"status.md is stale ({disagreements}); {_stale_remedy(root)} "
                     f"before working.")
    pending = planning_pending(root)
    if pending:
        # A nudge, never an exit (S028). Both files are the user's to write, and
        # DEC-006 makes no-deadlock a property: blocking a turn on a file only a
        # human can fill is the deadlock INV-12 exists to prevent.
        lines.append(f"Planning phase pending: {'; '.join(pending)}. The init skill drives it: "
                     f"the prime directive and the invariants first, then one --step new per "
                     f"planned step. Nothing blocks on this.")
    lost = take_log_failure(root)
    if lost:
        lines.append(lost)
    return lines


def git_dir(root):
    """Where moltke's own state files live, or None when there is no git here.

    Asking git rather than testing whether `.git` is a directory (S035, F04): in
    a linked worktree and in a submodule it is a file, and guessing lost the
    audit baseline, the prompt-failure breadcrumb, and the Stop deadlock cap all
    at once, silently, while `--validate` reported all checks pass. The path is
    per-worktree, which is what these files want to be.
    """
    lines = _git_lines(root, "rev-parse", "--absolute-git-dir")
    return Path(lines[0]) if lines else None


def _log_failure_path(root):
    resolved = git_dir(root)
    return resolved / "moltke_log_failure.json" if resolved else None


def record_log_failure(root, stamp, exc):
    """S014 (F14): a swallowed append needs a channel a zero exit still reaches.
    Nothing is written outside .git/, because an untracked file at the repo root
    reads as a source change to the Stop hook."""
    path = _log_failure_path(root)
    if path is None:
        return
    since, count = stamp, 0
    try:
        previous = json.loads(read_file(path))
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


def _peek_log_failure(root):
    """The breadcrumb without consuming it, or None. `take_log_failure` reports
    once and deletes; the Stop turn key has to be able to look every turn."""
    path = _log_failure_path(root)
    if path is None or not path.is_file():
        return None
    try:
        state = json.loads(read_file(path))
    except (OSError, ValueError):
        return None
    return state if isinstance(state, dict) else None


def take_log_failure(root):
    """Report a swallowed prompt append once, then drop the breadcrumb: a
    failure that persists rewrites it on the next prompt, one that is fixed
    goes quiet without anyone clearing it by hand."""
    path = _log_failure_path(root)
    if path is None or not path.is_file():
        return None
    try:
        state = json.loads(read_file(path))
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
    # str() rather than payload_str: a prompt of the wrong type is still
    # something the user typed, and logging must never lose it (S087).
    raw = hook_input().get("prompt", "")
    prompt = raw if isinstance(raw, str) else str(raw)
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
    path = path_arg or payload_str(payload, "tool_input", "file_path")
    if not path:
        return EXIT_OK
    # Resolve first, always (S041). pathlib does not normalise `..`, so a
    # relative path only had to start with an allowed component: tests/../bin/x
    # was permitted while its absolute form was blocked. Every rule below reads
    # this one `rel`, so normalising here covers the fence, plan_done, and the
    # step-file rule together.
    try:
        rel = (Path(path) if Path(path).is_absolute() else root / path).resolve()
        rel = rel.relative_to(root)
    except (ValueError, OSError):
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
    agent = payload_str(payload, "agent_type").split(":")[-1]
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


# INV-13 is absent on purpose: it reads the worklog, which grows without bound.
# INV-14 reads the audit reports INV-10 already reads, so a reviewer learns a
# fence swallowed a finding when the report is saved rather than at the next
# --validate — the gap 2026-08-07_adversarial.2-F04 named (S049).
CHEAP_CHECKS = ("INV-1", "INV-2", "INV-3", "INV-4", "INV-5", "INV-6", "INV-9", "INV-10",
                "INV-14")


def run_checks(root, config, only=None):
    """Every invariant, or only the named ones, with an unreadable tree reported
    rather than raised (S060, 2026-08-08_adversarial-F01).

    One place, because three call sites ran this loop and none of them handled
    an OSError: a directory where a step file belongs, or a file the index has
    and the worktree does not, killed `--validate`, `--post-write`, and `--stop`
    alike. A `Stop` hook that exits 1 enforces nothing and says nothing, which is
    worse than any violation it might have reported. S052 turned the same class
    of failure into a refusal for `--step` and stopped there.
    """
    violations = []
    for name, fn in INVARIANT_CHECKS:
        if only is not None and name not in only:
            continue
        try:
            violations.extend(fn(root, config))
        except OSError as exc:
            violations.append(f"{name} could not read the repository ({exc}). A check that "
                              f"cannot look is not a check that passed: fix the path it names, "
                              f"then run bin/moltke.py --validate")
    return violations


def mode_post_write(root, config, marker_violations):
    # Non-blocking by contract (the tool already ran); exit 2 only surfaces
    # stderr to Claude. Git-based checks are skipped to keep this cheap.
    violations = list(marker_violations) + run_checks(root, config, CHEAP_CHECKS)
    if violations:
        for violation in violations:
            print(f"moltke: {violation}", file=sys.stderr)
        return EXIT_BLOCK
    return EXIT_OK


STOP_CAP = 3


def stop_turn_key(root, payload):
    """What counts as "the same turn" for the deadlock waiver.

    S047 (.2-F01): this keyed on `prompt_id` alone, a field no observation in
    this repository establishes the Stop payload carries. When it was absent the
    key was the empty string for every turn, so the counter was global, it lived
    on disk, and from the fourth blocked turn onward every Stop check was off and
    stayed off across sessions — a deadlock-breaker turned into an off switch.

    The payload fields are used when present, and the worklog supplies the
    fallback: UserPromptSubmit appends exactly one prompt heading per turn, so
    counting them advances once per turn without depending on the payload at all.
    """
    parts = [str(payload.get("prompt_id") or ""), str(payload.get("session_id") or "")]
    worklog = root / DOCS / "worklog.md"
    prompts = 0
    try:
        text = read_stripped(worklog) if worklog.is_file() else ""
    except OSError:
        # An unreadable worklog leaves the count where it was, which is exactly
        # the frozen clock S061 was about — so the breadcrumb below is what has
        # to keep moving. Raising instead would escape past the counter and
        # wedge the turn (S067, .2-F01).
        text = ""
    if text:
        for heading in WORKLOG_HEADING.finditer(text):
            line = heading.group(0)
            if not RECAP_HEADING.search(line) and PROMPT_HEADING.search(line):
                prompts += 1
    parts.append(str(prompts))
    # S061 (2026-08-08_adversarial-F02): the heading count advances once per turn
    # only while the worklog is being written. --log-prompt swallows an OSError
    # by contract, because blocking there erases the prompt, so a worklog that
    # cannot be appended to freezes the clock — and a frozen clock makes every
    # turn look like a retry, which is the .2-F01 off switch coming back. The
    # breadcrumb S014 already writes for exactly that failure advances instead,
    # so the key keeps moving on the one path where the worklog cannot.
    failure = _peek_log_failure(root)
    if failure:
        parts.append(f"{failure.get('since')}#{failure.get('count')}")
    return "|".join(parts)


def _stop_state_path(root):
    resolved = git_dir(root)
    return resolved / "moltke_stop_state.json" if resolved else None


def _git_run(*args, **kwargs):
    """git, or None when there is no git to run.

    Every call goes through here (S067, .2-F01): `_git_lines` was made tolerant
    of a missing binary and the three direct `subprocess.run` sites were not, so
    with git off PATH the documented "the check abstains" became INV-7 and INV-8
    reporting that they could not read the repository, and every --stop blocked
    behind them.
    """
    try:
        return subprocess.run(*args, capture_output=True, **kwargs)
    except OSError:
        return None


def _git_lines(root, *args):
    result = _git_run(["git", "-C", str(root), *args], text=True)
    return result.stdout.splitlines() if result and result.returncode == 0 else None


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
    text = read_stripped(worklog)
    recapped = False
    for heading in WORKLOG_HEADING.finditer(text):
        line = heading.group(0)
        if RECAP_HEADING.search(line):
            recapped = True
        elif PROMPT_HEADING.search(line):
            recapped = False
    return not recapped


# Directories, with their separators, not a shared stem (S037). ".claude" as a
# bare prefix also matched .claude-plugin/plugin.json — the manifest whose
# version decides what every installed copy executes — and any future .claude*
# file at the repository root.
RECAP_EXEMPT = (f"{DOCS}/", ".claude/")


_GIT_PREFIX_CACHE = {}


def git_prefix(root):
    """Where the marked root sits inside the git repository, as `packages/foo/`.

    Empty when the two are the same directory, which is the ordinary case.
    Every git call is `git -C <marked root>`, but porcelain, log and show all
    speak in paths relative to the *top level*, and nothing checked the two
    agreed (S081, 2026-08-08_adversarial.3-F02): a project vendored into a
    monorepo had INV-7 calling a present file gone with a remedy that could not
    run, INV-8 abstaining on real tampering because `HEAD:adocs/decisions.md`
    does not resolve from the top level, and both `Stop` gates reading every
    path wrongly.

    Cached per root (S092, .4-F05). `from_git_path` and `to_git_path` call this
    once per path, and INV-7 and INV-8 walk every completed step and every history
    line, so one run_checks over this repository spawned 257 processes to ask a
    question whose answer cannot change while it runs — on every prompt, through
    the Stop and post-write hooks. The key is the root, so a process checking two
    roots still asks once for each.
    """
    key = str(root)
    if key not in _GIT_PREFIX_CACHE:
        result = _git_run(["git", "-C", key, "rev-parse", "--show-prefix"], text=True)
        _GIT_PREFIX_CACHE[key] = ("" if result is None or result.returncode != 0
                                  else result.stdout.strip())
    return _GIT_PREFIX_CACHE[key]


def from_git_path(root, rel):
    """A git-reported path as this repository sees it, or None if it is outside.

    A sibling package's file is git's business and not ours."""
    prefix = git_prefix(root)
    if not prefix:
        return rel
    return rel[len(prefix):] if rel.startswith(prefix) else None


def to_git_path(root, rel):
    """A repository-relative path as git names it, for `show` and `cat-file`."""
    return f"{git_prefix(root)}{rel}"


def porcelain_paths(line):
    """Every path a `git status --porcelain` line refers to.

    A staged rename is one line, `R  old -> new`, and both halves matter: the
    destination is what exists now, the source is a path that just stopped
    existing. Reading `line[3:]` whole gave the old path for renames, which is
    how `git mv` — the move AGENTS.md section 4 names for completing a step —
    walked past both `Stop` gates (S050, 2026-08-07_adversarial.2-F03). Quotes
    are git's own, around paths that need them.
    """
    entry = line[3:]
    parts = entry.split(" -> ", 1) if " -> " in entry else [entry]
    return [part.strip('"') for part in parts]


def _arrives_here(status):
    """Whether a porcelain status means the path is newly at its location.

    Untracked, added, renamed, copied. The index half is what decides, so `AM`
    and `RM` — added or renamed, then edited — count like `A ` and `R `.
    """
    return status == "??" or status[0] in ("A", "R", "C")


def _stale_remedy(root):
    """What to actually run when status.md disagrees with the filesystem.

    S052: with no `adocs/` every derived field disagrees, so both hooks named
    `--step status` — a command that cannot write into a directory that is not
    there. Steering has to name the command that works from the state observed.
    """
    if (root / DOCS).is_dir():
        return "run bin/moltke.py --step status"
    return (f"run bin/moltke.py --scaffold, because {DOCS}/ does not exist yet, then "
            f"bin/moltke.py --step status")


def porcelain_problems(root, porcelain):
    """The recap and stamp gates, as problems. Lifted out of mode_stop (S067)
    so a read failure here is caught next to what caused it and becomes a
    problem, rather than escaping past the retry counter and wedging the turn."""
    problems = []
    if porcelain is None:
        return problems
    # Both sides of a rename (S050): a file promoted out of adocs/ adds a
    # source file and a file moved into adocs/ removes one, and judging the
    # line by its old path alone made the first read as exempt.
    changed_source = [line for line in porcelain
                      if any(path is not None and not path.startswith(RECAP_EXEMPT)
                             for path in (from_git_path(root, entry)
                                          for entry in porcelain_paths(line)))]
    # No commit yet means no history a recap would sit alongside, and the
    # scaffold's own files are not work: abstain, as INV-7 and INV-8 do.
    committed = _git_lines(root, "rev-parse", "HEAD") is not None
    if changed_source and committed and recap_pending(root):
        problems.append(f"source changed but {DOCS}/worklog.md has no recap heading after "
                        f"the last logged prompt; append a recap (step id, what changed, "
                        f"files, tests, commit) before ending the turn, or commit the "
                        f"change if the turn that made it was already recapped.")
    for line in porcelain if committed else []:
        # Before the first commit every file is an arrival, including the
        # scaffold's own, which is why the recap gate abstains there too.
        # With -uall those now reach this gate individually (S060).
        entry = from_git_path(root, porcelain_paths(line)[-1])
        if entry is None:
            continue
        if _arrives_here(line[:2]) and entry.startswith(f"{DOCS}/plan_done/"):
            # The index can name a path the worktree no longer has — `AD`,
            # `RD` — and `RD` is what following this gate's own remedy
            # produces: it blocks, --pre-write forbids editing the file it
            # names, so `mv` back is the only compliant way out. Nothing
            # arrived, so there is nothing to stamp (S060).
            if not (root / entry).is_file():
                continue
            # A step file, not merely a path under plan_done/ (S069, .2-F03).
            # This was the one reader of that directory without STEP_FILE_RE, so
            # --scaffold's own .gitkeep, or any stray file, was asked for a
            # completion stamp — and in a project adopting moltke that meant
            # every Stop blocked from the moment it was scaffolded, with
            # --validate green throughout.
            if not STEP_FILE_RE.match(Path(entry).name):
                continue
            fields = parse_step_file(root / entry)
            stamp = fields.get("done", "")
            if "README" not in stamp or "MANUAL" not in stamp:
                problems.append(f"{entry} was completed without the README and MANUAL "
                                f"check recorded; check both files and note it in the "
                                f"done: stamp (checking with no change needed is valid).")
    return problems


def mode_stop(root, config, marker_violations):
    payload = hook_input()  # stdin is read once; every use below shares it
    problems = list(marker_violations) + run_checks(root, config)

    # Everything below reads paths run_checks does not, and an OSError from any
    # of them used to escape to main's backstop — which returns EXIT_BLOCK
    # before the retry counter at the bottom of this function is written. So the
    # cap never advanced, the waiver never fired, and every problem collected
    # above was dropped: a wedged session, which INV-12 and DEC-006 make the one
    # thing --stop may never do (S067, .2-F01). A failure here is a problem like
    # any other, and problems are what this function knows how to report.
    try:
        remedy = _stale_remedy(root)
        for field, said, real in status_disagreements(root):
            problems.append(f"status.md is stale or missing: {field} says {said!r}, the "
                            f"filesystem says {real!r}. {remedy[0].upper()}{remedy[1:]} before "
                            f"ending the turn.")
    except OSError as exc:
        problems.append(f"status.md could not be compared against the filesystem ({exc}); "
                        f"fix the path it names, then run bin/moltke.py --validate")

    # -uall, like worktree_state since S036 and for the same reason: plain
    # porcelain collapses a wholly untracked directory into one entry, so
    # `?? adocs/plan_done/` reached the stamp gate as a path that is a directory
    # on disk. One porcelain shape for every reader (S060).
    porcelain = _git_lines(root, "status", "--porcelain", "-uall")
    try:
        problems.extend(porcelain_problems(root, porcelain))
    except OSError as exc:
        problems.append(f"the working tree could not be read ({exc}); fix the path it names, "
                        f"then run bin/moltke.py --validate")

    state_path = _stop_state_path(root)
    if problems:
        # Print first, persist second, and let nothing here raise (S080,
        # DEC-039). The state write was the one unguarded write left in this
        # function after S067 guarded every read, so an unwritable .git escaped
        # to main's backstop — which returns before these lines run. The
        # problems were collected and thrown away, and the session could not
        # end: the third wedge found here and the second introduced fixing the
        # first. Printing before persisting means the worst case is a missing
        # cap rather than a silent turn.
        for problem in problems:
            print(f"moltke: {problem}", file=sys.stderr)
        turn = stop_turn_key(root, payload)
        fingerprint = hashlib.sha256("\n".join(sorted(problems)).encode()).hexdigest()[:16]
        count = 1
        if state_path:
            try:
                state = json.loads(read_file(state_path))
                # Same turn and the same problems: this is a retry. A new turn,
                # or a different set of problems, starts over — progress must not
                # count against you, and a stale count must not carry forward.
                if state.get("turn") == turn and state.get("fingerprint") == fingerprint:
                    count = state.get("count", 0) + 1
            except (OSError, json.JSONDecodeError):
                pass
            try:
                state_path.write_text(
                    json.dumps({"turn": turn, "fingerprint": fingerprint, "count": count}),
                    encoding="utf-8")
            except OSError as exc:
                # DEC-039 scopes the cap to wherever the state can be written,
                # which is DEC-031's accepted gap applied to its neighbour: every
                # Stop blocks until the problem is fixed, and the message says
                # why the waiver never comes rather than leaving it a mystery.
                print(f"moltke: {state_path.name} could not be written ({exc}), so the "
                      f"deadlock cap cannot count attempts and every Stop will block until "
                      f"the problems above are fixed or that path is made writable.",
                      file=sys.stderr)
        if count > STOP_CAP:
            # Live docs (2026-08-01) document no built-in cap; this one keeps
            # the no-deadlock property of DEC-006 / INV-12. The problems are
            # printed above first: being waved through must not mean being told
            # nothing (S047).
            print(f"moltke: still blocked after {STOP_CAP} attempts; allowing stop so the "
                  f"session is not deadlocked. Run bin/moltke.py --validate and fix by hand.",
                  file=sys.stderr)
            return EXIT_OK
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
    result = _git_run(["git", "-C", str(start), "rev-parse", "--show-toplevel"], text=True)
    if result is not None and result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip())
    return start


def declined(root):
    """True when the marker records a declined repository (DEC-005)."""
    path = root / MARKER
    if not path.is_file():
        return False
    try:
        config = json.loads(read_file(path))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(config, dict) and config.get("enabled") is False


# Template names, not destinations: the ruleset moltke versions and copies once
# — AGENTS.md, CLAUDE.md, .cursor/rules/moltke.mdc. Everything under adocs/
# becomes the project's own content the moment it is used, and the marker carries
# per-project keys, so comparing either would report drift on every repository
# that works (S029).
VERSIONED_TEMPLATES = ("AGENTS.md", "CLAUDE.md", "cursor_rules")


def template_drift(target, template):
    """True if a kept file differs from the installed plugin's template, False if
    it matches, None if this file is not one moltke versions."""
    if template not in VERSIONED_TEMPLATES:
        return None
    try:
        return target.read_bytes() != (TEMPLATE_ROOT / template).read_bytes()
    except OSError:
        return None


def mode_scaffold():
    # Exempt from the INV-11 gate: this mode exists to create the marker (DEC-017).
    root = scaffold_root()
    if declined(root):
        print(f"moltke: {root/MARKER} records enabled false; this repository declined the "
              f"workflow and is left untouched. Delete that file to reconsider.")
        return EXIT_OK
    created, kept = [], []
    # Dispatched before main's backstop, which it has to be — that backstop runs
    # after the marker gate this mode exists to create — so an unguarded write
    # here reached the user as a traceback, which MANUAL says no mode produces
    # (S091, .4-F04). The rollback matters as much as the message: the marker is
    # the first entry in SCAFFOLD_MAP, so a failure partway through left an
    # enabled .moltke.json over a tree that was never built, with every hook live
    # against nothing. Only files this run created are removed, and scaffolding
    # never overwrites, so nothing of the user's is at stake.
    try:
        for template, destination in SCAFFOLD_MAP:
            target = root / destination
            if target.exists():
                kept.append((destination, template_drift(target, template)))
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
    except OSError as exc:
        undone = []
        for destination in reversed(created):
            path = root / destination.rstrip("/")
            path = path / ".gitkeep" if destination.endswith("/") else path
            try:
                path.unlink()
                undone.append(destination)
            except OSError:
                continue  # reported below: what is left is what could not be removed
        left = [d for d in created if d not in undone]
        detail = (f" What this run had already created was removed, so nothing is half-applied."
                  if not left else
                  f" These could not be removed and are still there: {', '.join(left)}; delete "
                  f"them before running this again.")
        return refuse(f"could not scaffold {root} ({exc}); nothing is set up here.{detail} Fix "
                      f"the path the error names and run this again")
    print(f"moltke: scaffolded {root}")
    for path in created:
        print(f"  created  {path}")
    drifted = []
    for path, drift in kept:
        if drift is None:
            print(f"  kept     {path} (already present, not overwritten)")
            continue
        verdict = "differs from the installed template" if drift else \
                  "matches the installed template"
        print(f"  kept     {path} (already present, not overwritten; {verdict})")
        if drift:
            drifted.append(path)
    if not created:
        print("  nothing to do; the workflow is already set up here")
    elif kept:
        print("Review the kept files: moltke did not merge anything into them.")
    if drifted:
        # Reported, never acted on (S029). The ruleset is the user's file: it may
        # carry house rules deliberately, and an automatic refresh would erase
        # them. Repository state travels in git; only the plugin is per-machine,
        # so this is the one thing a fresh clone cannot already know.
        print(f"Template drift in {', '.join(drifted)}: written by an older plugin, or edited "
              f"on purpose. Nothing was changed. Compare against "
              f"{TEMPLATE_ROOT} and merge by hand if you want the newer wording.")
    return EXIT_OK


def mode_decline():
    # Exempt from the INV-11 gate for the same reason as --scaffold (DEC-017).
    root = scaffold_root()
    path = root / MARKER
    if path.is_file() and not declined(root):
        print(f"moltke: {path} already exists and is not a declined marker; leaving it alone. "
              f"Remove it first if this repository should stop using the workflow.")
        return EXIT_OK
    # Same reason as mode_scaffold: dispatched ahead of main's backstop, so its
    # one write is guarded here or not at all (S091, .4-F04).
    try:
        path.write_text(json.dumps({"schema": 1, "enabled": False}, indent=2) + "\n",
                        encoding="utf-8")
    except OSError as exc:
        return refuse(f"could not write {path} ({exc}); this repository is not recorded as "
                      f"declining the workflow, and nothing was changed. Fix the path the "
                      f"error names and run this again")
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


STEP_ID_MAX = 999


def highest_step_id(root):
    """(number, where it was found) for the highest id this repository has used.

    Ids are never reused (DEC-008), so plan.md counts even when the file is
    gone. `where` exists for the refusal in mode_step: at the ceiling the cause
    is usually a token in plan.md prose rather than a step that exists, and a
    message that cannot say which is not actionable (S097).
    """
    highest, where = 0, None
    steps = plan_steps(root)
    for dirname in PLAN_DIRS:
        for step_id, path, _f in steps[dirname]:
            if int(step_id[1:]) > highest:
                highest, where = int(step_id[1:]), f"{DOCS}/{dirname}/{path.name}"
    for number in re.findall(r"\bS(\d{3})\b", plan_text(root) or ""):
        if int(number) > highest:
            highest, where = int(number), f"{DOCS}/plan.md"
    return highest, where


def next_step_id(root):
    highest, _where = highest_step_id(root)
    return f"S{highest + 1:03d}"


def field_value_problem(operand, value):
    """S099 (2026-08-09_adversarial-F03): the writers did not honour the rule
    S095 gave the reader. `write_step`, `append_to_plan` and `with_field` each
    interpolate a value into one f-string, so a newline lands flush left — the
    one shape `parse_step_file` is documented to drop, and in `plan.md` a list
    entry nobody typed.

    Refused at the boundary rather than reflowed, because a `done:` stamp is
    evidence: silently rewriting it is the same class of quiet transformation
    the truncation was. This is the shape `step_name_problem` and the `--audit`
    type check already use.
    """
    if value is None or "\n" not in value and "\r" not in value:
        return None
    return (f"{operand} contains a line break, and a field is written as one line: the "
            f"continuation would land flush left, where the step-file parser reads it as a "
            f"new field and drops it, and where plan.md reads it as another list entry. Pass "
            f"it as a single line — long is fine, every completed step here is one line")


def step_id_ceiling_problem(root):
    """S097 (2026-08-09_adversarial-F01): past S999 the allocator produced an id
    no scanner can read. STEP_FILE_RE and PLAN_ENTRY_RE both require exactly
    three digits, so S1000_x.md matched neither: the file was on disk, the entry
    was in plan.md, and plan_steps, plan_order, derived_next, --roadmap and every
    invariant were blind to it together, with --validate green. INV-3 could not
    report it in either direction. Two triggers, both real — any S999 token in
    plan.md prose, which the shipped template invites, and the id space genuinely
    running out.
    """
    highest, where = highest_step_id(root)
    if highest < STEP_ID_MAX:
        return None
    return (f"the next id would be S{highest + 1}, past the S{STEP_ID_MAX} ceiling, and a "
            f"four-digit id is one nothing in this tool can read: step files and plan "
            f"entries are matched as exactly three digits, so the step would exist on disk, "
            f"be listed in plan.md, and be invisible to every check at once. The highest id "
            f"in use is S{highest:03d}, found in {where}. If that is a token in prose rather "
            f"than a step, change it there; if the id space is genuinely full, widening it is "
            f"a decision, not a rename")


def write_step(path, step_id, goal, blocks=""):
    template = read_file((TEMPLATE_ROOT / "step_template.md"))
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
    try:
        text = read_file(plan_path)
        if not text.endswith("\n"):
            text += "\n"
        plan_path.write_text(text + entry + "\n", encoding="utf-8")
    except OSError:
        return False
    return True


def with_field(text, key, value):
    """A step file's text with one field set, adding the line if it is absent.

    Separate from the write (S062) so a caller can decide where the result goes
    — `step_done` writes it to the destination rather than editing in place, so
    a failed move leaves nothing half-written.
    """
    rendered = f"{key}:{' ' * max(1, 11 - len(key) - 1)}{value}".rstrip()
    lines, found, replacing = [], False, False
    for line in text.splitlines():
        if line.split(":", 1)[0].strip() == key:
            lines.append(rendered)
            found, replacing = True, True
            continue
        # The lines the old value spanned go with it (S095). Now that
        # parse_step_file folds continuations into the field, leaving them here
        # would fold the replaced text straight back in — the same silent defect
        # in a new place.
        if replacing and line.strip() and line[:1].isspace():
            continue
        replacing = False
        lines.append(line)
    if not found:
        lines.append(rendered)
    return "\n".join(lines) + "\n"


def set_field(path, key, value):
    """Set a step field in place."""
    path.write_text(with_field(read_file(path), key, value), encoding="utf-8")


def step_new(root, config, name, goal):
    step_id = next_step_id(root)
    goal = goal or name.replace("_", " ")
    path = root / DOCS / "plan_todo" / f"{step_id}_{name}.md"
    # The plan entry first, the step file second (S083, .3-F04). Written the
    # other way round, a failing append left an id no list entry names, which is
    # INV-3 — the half-apply S062 and S070 fixed for --step done and left in its
    # two siblings. The listed-but-absent direction is the recoverable one:
    # INV-3 names it and --step new writes the file.
    if not append_to_plan(root, step_id, goal):
        return refuse(f"{DOCS}/plan.md could not be written, so {step_id} was not created; "
                      f"the plan is the order and a step file it does not list is a violation")
    write_step(path, step_id, goal)
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
    twin = [p for found, p, _f in current if found == step_id]
    destination = root / DOCS / "plan_current" / path.name
    if twin or destination.exists():
        held = (twin[0] if twin else destination).relative_to(root)
        return refuse(f"{step_id} is already carried by {held}, and starting the copy in "
                      f"{path.relative_to(root)} would rename onto it. Two files carrying one "
                      f"id is INV-6 and --validate reports it; resolve the duplicate by hand — "
                      f"deciding which of the two is the step is not something this command "
                      f"can do for you")
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


def step_unpause(root, config, step_id):
    """The way out of a pause naming work that exists nowhere (S090, DEC-040).

    Narrow on purpose: it clears a pause the plan cannot account for, and refuses
    one it can. A general unpause would let a step walk out of the accounting
    INV-1 keeps, which is the opposite of what this exists for."""
    dirname, path, fields = locate_step(root, step_id)
    if dirname is None:
        return refuse(f"{step_id} does not exist")
    if dirname != "plan_current":
        return refuse(f"{step_id} is in {dirname}, not plan_current/; only an in-progress "
                      f"step carries a pause")
    pauser = pauser_id(fields)
    if not pauser:
        return refuse(f"{step_id} is not paused, so there is nothing to clear")
    # Exactly what INV-1 reports, read from the same function, so the remedy the
    # violation names is the remedy that works (S098). DEC-040's rule is kept
    # rather than widened: a pause that resolves to live work someone can finish
    # is still refused, because clearing that one would be a way around the
    # accounting rather than a repair.
    if step_id not in unresolvable_pauses(root):
        return refuse(f"{step_id} is paused by {pauser}, which exists and is reachable. "
                      f"Complete {pauser} with --step done {pauser}, which unpauses {step_id} "
                      f"on its way out; this command only clears a pause that never resolves, "
                      f"which is the case --validate reports")
    set_field(path, "paused_by", "")
    print(f"moltke: {step_id} unpaused; {pauser} had no step file in any plan directory.")
    return EXIT_OK


def step_block(root, config, parent_id, name):
    dirname, parent_path, fields = locate_step(root, parent_id)
    if dirname != "plan_current":
        where = dirname or "nowhere"
        return refuse(f"{parent_id} is in {where}, not plan_current/; only an in-progress "
                      f"step can be paused by a blocking child")
    # A step can be paused by one child at a time (S082, .3-F03). This asked
    # only that the parent was in plan_current/ and then overwrote its
    # paused_by, so a second child reported success while taking the repository
    # from all checks pass to an INV-1 violation and erasing the first child's
    # pause — the parent unpaused itself while both children counted as active.
    paused_by = re.search(r"S\d{3}", field_value(fields, "paused_by"))
    if paused_by:
        return refuse(f"{parent_id} is already paused by {paused_by.group(0)}; a step is "
                      f"blocked by one child at a time. Complete {paused_by.group(0)}, which "
                      f"unpauses {parent_id}, or block {paused_by.group(0)} itself if this new "
                      f"work is what is stopping it")
    current = plan_steps(root)["plan_current"]
    limit = _limit(config, "plan_stack_max", 3)
    if len(current) + 1 > limit:
        return refuse(f"stack depth would reach {len(current) + 1}, over plan_stack_max "
                      f"{limit}. A blocker spawning its own blockers this deep means the plan "
                      f"is wrong at design level: stop, record a decision, and replan.")
    child_id = next_step_id(root)
    goal = name.replace("_", " ")
    child_path = root / DOCS / "plan_current" / f"{child_id}_{name}.md"
    # Same ordering as step_new (S083): the plan entry is the write that can
    # fail on its own, so it goes first and the rest follows only if it lands.
    if not append_to_plan(root, child_id, goal):
        return refuse(f"{DOCS}/plan.md could not be written, so {child_id} was not created and "
                      f"{parent_id} is not paused; nothing was changed")
    write_step(child_path, child_id, goal, blocks=parent_id)
    set_field(parent_path, "paused_by",
              f"{child_id}  # {datetime.date.today().isoformat()}")
    print(f"moltke: {child_id} created in plan_current/ blocking {parent_id}, "
          f"which is now paused.")
    return EXIT_OK


TEST_COMMAND_TIMEOUT = 600
TEST_OUTPUT_TAIL = 20


def run_test_command(root, config):
    """The suite gate (DEC-023). Returns an exit code to refuse with, or None to
    let completion proceed. Optional by design: AGENTS.md requires a green suite,
    and until this key existed nothing ran one, so the gate was honour-system."""
    command = config.get("test_command") if isinstance(config, dict) else None
    if not isinstance(command, str) or not command.strip():
        print(f'moltke: no "test_command" in {MARKER}, so nothing here ran the suite. '
              f'The green-suite requirement is on you; set the key to have --step done '
              f'enforce it.')
        return None
    # stderr, with the refusal it may turn into (S042). Progress, not a finding:
    # a consumer following the documented mapping reads stderr on exit 1, and
    # splitting one refusal across both streams gave it half the message.
    print(f"moltke: running the suite gate: {command}", file=sys.stderr)
    try:
        # shell=True: the value is a free-form command line, and it is trusted at
        # the same level as the hooks that already run this script. cwd is the
        # repo root, so a relative command does not depend on the caller's cwd.
        result = subprocess.run(command, shell=True, cwd=str(root),
                                capture_output=True, text=True,
                                timeout=TEST_COMMAND_TIMEOUT)
    except subprocess.TimeoutExpired:
        return refuse(f'the "test_command" gate timed out after {TEST_COMMAND_TIMEOUT}s: '
                      f'{command}. Make the suite finish, or point test_command at a '
                      f'faster subset and run the full suite yourself')
    except OSError as exc:
        return refuse(f'the "test_command" gate could not run ({exc}): {command}. '
                      f'Fix the command in {MARKER}')
    if result.returncode == 0:
        return None
    tail = "\n".join((result.stdout + result.stderr).splitlines()[-TEST_OUTPUT_TAIL:])
    return refuse(f'the "test_command" gate failed with exit {result.returncode}: {command}\n'
                  f"last {TEST_OUTPUT_TAIL} lines:\n{tail}\n"
                  f"Fix the suite. Never weaken a test to get past this")


def step_done(root, config, step_id, stamp):
    dirname, path, fields = locate_step(root, step_id)
    if dirname is None:
        return refuse(f"{step_id} does not exist")
    if dirname != "plan_current":
        return refuse(f"{step_id} is in {dirname}, not plan_current/; only a step that is "
                      f"actually in progress can be completed")
    steps = plan_steps(root)
    # The completion write is a plain write_text into plan_done/, so a duplicate
    # id — INV-6, which --validate reports rather than prevents — overwrote the
    # finished step with the one still in progress: history destroyed by the
    # command whose own message calls that directory immutable (S089, .4-F02).
    # Checked before the suite gate, so a repository in this state is told so
    # rather than after paying for a full test run.
    twin = [p for found, p, _f in steps["plan_done"] if found == step_id]
    if twin or (root / DOCS / "plan_done" / path.name).exists():
        held = (twin[0] if twin else root / DOCS / "plan_done" / path.name).relative_to(root)
        return refuse(f"{step_id} is already in plan_done/ as {held}, so completing "
                      f"{path.relative_to(root)} would overwrite finished history. Two files "
                      f"carrying one id is INV-6 and --validate reports it; ids are never "
                      f"reused (DEC-008), so one of the two is misnumbered. Resolve it by "
                      f"hand — nothing here can decide which one is the step")
    pauser = re.search(r"S\d{3}", field_value(fields, "paused_by"))
    if pauser and pauser.group(0) in {done_id for done_id, _p, _f in steps["plan_done"]}:
        # A pause naming a step that is already finished is stale, and refusing
        # on it is a dead end the CLI cannot clear — hand-editing a step file is
        # what --step exists to avoid (S070, .2-F04). Say so and go on; the
        # field is rewritten below either way.
        print(f"moltke: {step_id} was paused by {pauser.group(0)}, which is already in "
              f"plan_done/; treating the pause as stale.")
        pauser = None
    if pauser:
        return refuse(f"{step_id} is paused by {pauser.group(0)}; complete {pauser.group(0)} "
                      f"first, which unpauses this step automatically")
    for open_dir in ("plan_todo", "plan_current"):
        for other_id, _p, other_fields in steps[open_dir]:
            if other_id != step_id and step_id in field_value(other_fields, "blocks"):
                return refuse(f"{other_id} still declares blocks: {step_id}; complete or "
                              f"drop {other_id} first")
    testing = root / DOCS / "testing.md"
    rows = read_stripped(testing) if testing.is_file() else ""
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
    gate = run_test_command(root, config)
    if gate is not None:
        return gate

    # Nothing is written until the move is certain (S062,
    # 2026-08-08_adversarial-F03). The rename is the only one of the three
    # mutations that can fail, and it used to go last, so a refusal left the
    # stamp written and the parent unpaused — a transition that refused and
    # repaired half of itself, taking the repository from all checks pass to an
    # INV-1 violation. Writing the stamped content straight to the destination
    # makes the first step the failing one; the source is only unlinked once the
    # destination exists, and the parent is unpaused after both.
    # Nothing is written until every write is known to be possible (S070): the
    # parent unpause is a different file and can fail on its own, and S062 left
    # it after the point of no return, so a completion could half-apply into a
    # state neither --step done nor --step start could clear.
    parents = [parent_path for _pid, parent_path, parent_fields in steps["plan_current"]
               if step_id in field_value(parent_fields, "paused_by")]
    for parent_path in [path] + parents:
        if not os.access(parent_path, os.W_OK):
            return refuse(f"{parent_path.relative_to(root)} is not writable, and completing "
                          f"{step_id} has to rewrite it; nothing was changed. Make it writable "
                          f"and run this again")
    destination = root / DOCS / "plan_done" / path.name
    try:
        destination.write_text(with_field(read_file(path), "done", stamp),
                               encoding="utf-8")
    except OSError as exc:
        return refuse(f"could not write {destination.relative_to(root)} ({exc}); nothing was "
                      f"changed. {DOCS}/plan_done/ is where completed steps go: restore it, or "
                      f"run bin/moltke.py --scaffold, which creates what is absent and "
                      f"overwrites nothing")
    try:
        path.unlink()
    except OSError as exc:
        destination.unlink(missing_ok=True)
        return refuse(f"could not remove {path.relative_to(root)} after copying it "
                      f"({exc}); the copy was undone and nothing was changed")
    for parent_id, parent_path, parent_fields in steps["plan_current"]:
        if step_id in field_value(parent_fields, "paused_by"):
            try:
                set_field(parent_path, "paused_by", "")
            except OSError as exc:
                # Pre-flighted above, so this is a race rather than a mistake.
                # The state is recoverable: the pause now names a completed step
                # and --step done on the parent clears it (S070).
                print(f"moltke: {parent_id} could not be unpaused ({exc}); its pause now names "
                      f"a completed step, so --step done {parent_id} will clear it.",
                      file=sys.stderr)
                continue
            print(f"moltke: {parent_id} unpaused.")
    print(f"moltke: {step_id} completed and moved to plan_done/. Commit it; the move is the "
          f"last action of the step.")
    return EXIT_OK


def parked_lines(root):
    """Carry the human-written Parked list through a regeneration."""
    status_path = root / DOCS / "status.md"
    if not status_path.is_file():
        return []
    # Everything after the heading to the end of the file (S094, .4-F07). This
    # collected only lines starting with two spaces or a tab and stopped at the
    # first that did not, so a list written flush left — ordinary markdown, and
    # what the template's bare `- Parked:` invited — was dropped by a
    # regeneration that runs at every step transition and reports success.
    # Reading to the end is safe because Parked is the last thing step_status
    # writes, so nothing derived follows it; and lines are kept verbatim, so
    # what is read back next time is what was written.
    kept, collecting = [], False
    for line in read_file(status_path).splitlines():
        if not collecting:
            collecting = bool(re.match(r"^\s*-\s*Parked:", line))
            continue
        if line.strip():
            kept.append(line.rstrip())
    return kept


def status_lines(root):
    """The derived body of status.md, without the Updated: line or Parked block.

    Shared with status_disagreements so the check compares against exactly what
    a regeneration would write, rather than against a second description of it.
    """
    steps = plan_steps(root)
    done_ids = [s for s, _p, _f in steps["plan_done"]]
    # plan_order, not every id in the file: a step named in the description is
    # prose, and reading it here would pick the wrong Last done (S045).
    last_done = next((s for s in reversed(plan_order(root) or []) if s in done_ids), None)
    active, paused = [], []
    for step_id, _p, fields in steps["plan_current"]:
        pauser = field_value(fields, "paused_by")
        goal = field_value(fields, "goal")
        (paused if pauser else active).append(
            f"{step_id} {goal}" + (f" (paused by {pauser})" if pauser else ""))
    # A repository that has planned nothing and one that has finished everything
    # are different states, and the scaffolded status.md says the first of them.
    nothing = "no steps planned yet" if not plan_order(root) else "no steps left in plan.md"
    return [
        f"- Last done: {last_done or 'nothing yet'}",
        f"- In progress: {'; '.join(active) if active else 'none'}",
        f"- Next: {derived_next(root) or nothing}",
        f"- Blocked: {'; '.join(paused) if paused else 'none'}",
    ]


def step_status(root, config):
    lines = ["# Status", "",
             "Convenience view, rewritten at the end of every work turn. The filesystem "
             "beats", "this file: on disagreement, `plan_current/` wins.", "",
             f"Updated: {datetime.date.today().isoformat()} by `moltke --step status`.", ""]
    lines.extend(status_lines(root))
    lines.append("- Parked:")
    lines.extend(parked_lines(root))

    (root / DOCS / "status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"moltke: regenerated {DOCS}/status.md from the filesystem.")
    return EXIT_OK


def _audit_baseline_path(root):
    resolved = git_dir(root)
    return resolved / "moltke_audit_baseline.json" if resolved else None


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
        # The new name is what exists now. One definition of that, shared with
        # both Stop gates since S050.
        entry = from_git_path(root, porcelain_paths(line)[-1])
        if entry is None:
            continue
        state[entry] = [line[:2], _content_hash(root / entry)]
    return state


def next_report_path(root, audit_type):
    """Today's report, or the next free sequence suffix (S020, F09).

    Closure requires a re-run, so refusing a same-day re-run left no compliant
    way to close a finding fixed on the day it was found. A report is still never
    overwritten: each run gets its own file, and its own finding-id stem.
    """
    audit_dir = root / DOCS / "audit"
    stem = f"{datetime.date.today().isoformat()}_{audit_type}"
    report = audit_dir / f"{stem}.md"
    run = 1
    while report.exists():
        run += 1
        report = audit_dir / f"{stem}.{run}.md"
    return report


def audit_new(root, config, audit_type):
    report = next_report_path(root, audit_type)
    # Captured before the report exists, so the report itself shows up as part of
    # the run's footprint and is classified there rather than being invisible.
    baseline = worktree_state(root)
    template = read_file((TEMPLATE_ROOT / "audit_report_template.md"))
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(template.replace("YYYY-MM-DD_type", report.stem)
                              .replace("YYYY-MM-DD", datetime.date.today().isoformat())
                              .replace("<type>", audit_type), encoding="utf-8")
    print(f"moltke: created {report.relative_to(root)}. Write every finding before fixing "
          f"anything; finding ids are {report.stem}-F01, -F02, ...")
    baseline_path = _audit_baseline_path(root)
    if baseline is None or baseline_path is None:
        print(f"moltke: no git repository here, so --audit check cannot reconcile this run; "
              f"whatever the reviewer changes will go unnoticed.", file=sys.stderr)
        return EXIT_OK
    try:
        head = _git_lines(root, "rev-parse", "HEAD")
        baseline_path.write_text(json.dumps(
            {"report": str(report.relative_to(root)), "tree": baseline,
             "head": head[0] if head else None,
             "worklog": worklog_prefix(root)}), encoding="utf-8")
    except OSError as exc:
        print(f"moltke: could not record the audit baseline ({exc}); --audit check will "
              f"refuse until --audit new runs again.", file=sys.stderr)
    return EXIT_OK


def _is_new_file(status):
    # One definition of "newly here", shared with the Stop gates (S077, .2-F11).
    # This kept the pre-S050 predicate while _arrives_here learned that the
    # index half decides, so `AM` — a red-first test staged and then refined,
    # which is how one is actually written — was reported as contamination the
    # reviewer had to justify, when it is exactly what the fence permits.
    return _arrives_here(status)


def worklog_prefix(root):
    """[length, sha256] of the worklog as it stands, or None if there is none.

    Enough to prove later that the file only grew, without keeping a copy of it:
    hash the first `length` bytes again and compare (S036).
    """
    try:
        content = (root / DOCS / "worklog.md").read_bytes()
    except OSError:
        return None
    return [len(content), hashlib.sha256(content).hexdigest()]


def worklog_append(root, recorded):
    """What was appended to the worklog since `--audit new`, or None if the file
    did not simply grow.

    UserPromptSubmit appends to it on every prompt, so any audit spanning a
    prompt has a worklog change in its footprint — one the reviewer is fenced out
    of making. An append is what the hook does; a rewrite is what covering your
    tracks looks like, and stays reported (F05). Returning the appended text
    rather than a boolean is S056: the shape test alone said "expected" and
    printed nothing further, so an append made from Bash — the one edit that both
    passes the exemption and changes a gate's answer — was invisible.
    """
    if not (isinstance(recorded, list) and len(recorded) == 2):
        return None
    length, digest = recorded
    try:
        content = (root / DOCS / "worklog.md").read_bytes()
    except OSError:
        return None
    if len(content) < length or hashlib.sha256(content[:length]).hexdigest() != digest:
        return None
    return content[length:].decode("utf-8", errors="replace")


def foreign_worklog_lines(appended):
    """Lines in an append that `--log-prompt` would not have written.

    It writes `## <stamp> prompt`, a blank line, then the prompt with every line
    prefixed `> ` — so a prompt containing a heading, a fence, or the word recap
    arrives quoted and stays recognisable. Anything else in the appended region
    came from somewhere that is not the hook, and a recap heading there is the
    case that matters: it discharges the `Stop` recap gate for the surrounding
    turn (S056, .2-F09).
    """
    foreign = []
    for line in appended.splitlines():
        if not line.strip() or line.startswith(">"):
            continue
        if (WORKLOG_HEADING.match(line) and PROMPT_HEADING.search(line)
                and not RECAP_HEADING.search(line)):
            continue
        foreign.append(line)
    return foreign


def audit_check(root, config):
    """DEC-022: prevention gave way to detection. Report what the run actually
    changed, so a contaminated report is known before any finding is acted on."""
    baseline_path = _audit_baseline_path(root)
    saved = None
    if baseline_path is not None and baseline_path.is_file():
        try:
            saved = json.loads(read_file(baseline_path))
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

    worklog = f"{DOCS}/worklog.md"
    appended = worklog_append(root, saved.get("worklog"))
    foreign = foreign_worklog_lines(appended) if appended is not None else []
    worklog_note = None
    if appended is not None:
        added = len([line for line in appended.splitlines() if line.strip()])
        if foreign:
            worklog_note = (f"{worklog}: appended {added} line(s), {len(foreign)} of which "
                            f"--log-prompt would not have written, first {foreign[0].strip()!r}. "
                            f"A recap heading here discharges the Stop recap gate for this turn")
        else:
            worklog_note = f"{worklog}: appended {added} line(s), all prompt log entries"

    def classify(entry, note, is_new):
        if entry == worklog:
            # Named either way (S056): the exemption stays, because a gate that
            # is wrong on every audit spanning a prompt is one people learn to
            # wave through (F05), but it never passes silently again.
            note = worklog_note or note
        if (entry == report or (entry.startswith("tests/") and is_new)
                or (entry == worklog and appended is not None and not foreign)):
            expected.append(note)
        else:
            unexpected.append(note)

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
        classify(entry, note, was is None and now is not None and _is_new_file(now[0]))

    # And what the run committed (S032, F01). A clean tracked file that the run
    # patched and committed is in neither snapshot, so it was not misclassified,
    # it was absent — and DEC-022 traded the write fence away for this check, so
    # `git commit` defeated the thing that replaced the fence.
    head_before = saved.get("head")
    if head_before:
        committed = _git_lines(root, "diff", "--name-status", "--no-renames",
                               f"{head_before}..HEAD")
        if committed is None:
            unexpected.append(f"the commit {head_before[:8]} recorded at --audit new is no "
                              f"longer reachable, so what this run committed cannot be read; "
                              f"history was rewritten")
        else:
            for line in committed:
                if "\t" not in line:
                    continue
                status, entry = line.split("\t")[0], line.split("\t")[-1]
                entry = from_git_path(root, entry)
                if entry is None:
                    continue        # another package in the same repository (S081)
                classify(entry, f"{entry}: {status} in a commit made during this run",
                         status.startswith("A"))
    elif saved.get("head", "missing") is None:
        expected.append("no commit existed when --audit new ran, so commits made during the "
                        "run cannot be compared")

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
        print("no change since --audit new: nothing in the working tree, and nothing "
              "committed. The report has not been written yet.")
    return EXIT_OK


def audit_list(root, config):
    audit_dir = root / DOCS / "audit"
    reports = sorted(audit_dir.glob("*.md")) if audit_dir.is_dir() else []
    references = finding_references(root)
    steps = plan_steps(root)
    unreferenced = 0
    hidden_total = 0
    total = 0
    for report in reports:
        findings = report_findings(report)
        hidden = hidden_findings(report)
        if not findings and not hidden:
            continue
        print(f"{report.name}")
        for finding_id in hidden:
            # S049: this listing omitted them entirely, which is worse than
            # listing them unreferenced — the operator read a complete-looking
            # report. Nothing else about the finding is readable, so the status
            # and the reference are not guessed at.
            total += 1
            hidden_total += 1
            print(f"  {finding_id}  hidden  (a code fence swallows it; INV-14)")
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
    if hidden_total:
        print(f"moltke: {hidden_total} finding(s) have a heading no check can read, because a "
              f"code fence swallows them. Close the evidence blocks around them; until then "
              f"their status and their references are unknown, not absent.")
    if unreferenced:
        print(f"moltke: {unreferenced} open finding(s) have no plan step and no decision. "
              f"Every finding ends in a step whose closes: names it, or a decisions.md entry "
              f"stating why it is accepted.")
    if hidden_total or unreferenced:
        return EXIT_VIOLATIONS
    return EXIT_OK


AUDIT_OPS = ("new", "list", "check")


def mode_audit(root, config, argv):
    op, rest = argv[0], argv[1:]
    if op not in AUDIT_OPS:
        return refuse(f"unknown --audit operation {op!r}; use one of {', '.join(AUDIT_OPS)}")
    try:
        return _mode_audit(root, config, op, rest)
    except OSError as exc:
        # --audit refuses like --step does (S076, .2-F10). The S060 backstop
        # returned EXIT_BLOCK here, which README's table assigns to the three
        # hook modes only, and called every failure a read — including a write,
        # with a remedy that had nothing to do with it.
        verb = "write to" if op == "new" else "read"
        return refuse(f"--audit {op} could not {verb} {DOCS}/audit ({exc}); fix that path and "
                      f"run this again")


def _mode_audit(root, config, op, rest):
    if op == "list":
        return audit_list(root, config)
    if op == "check":
        return audit_check(root, config)
    if not rest:
        return refuse("usage: --audit new <type>   (for example: adversarial, security)")
    # Checked before anything touches the filesystem (S040). The type went
    # straight into a filename and audit_new creates the parents, so a separator
    # put the report outside the glob every check reads — filed, and counted by
    # nothing — while the printed path was computed lexically and still looked
    # contained. A dot would also collide with the `.2` namespace S020 reserved
    # for same-day re-runs.
    if not re.fullmatch(r"[A-Za-z0-9_-]+", rest[0]):
        return refuse(f"audit type {rest[0]!r} must match [A-Za-z0-9_-]+ so it stays a filename "
                      f"inside {DOCS}/audit/ and cannot collide with the .2 suffix a same-day "
                      f"re-run uses; try adversarial, security, or bugs")
    return audit_new(root, config, rest[0])


STEP_OPS = ("new", "start", "block", "unpause", "done", "status")


def mode_step(root, config, argv, goal, stamp, marker_violations=()):
    op, rest = argv[0], argv[1:]
    if op not in STEP_OPS:
        return refuse(f"unknown --step operation {op!r}; use one of {', '.join(STEP_OPS)}")
    # S038 (F07): --validate, --post-write, and --stop were given these and
    # --step was not, so a malformed test_command was reported by one command
    # while a different one completed steps green and said the key was absent.
    # The gate that decides completion cannot be the one that cannot see the
    # marker it depends on.
    if marker_violations:
        return refuse("; ".join(marker_violations) + f". Fix {MARKER} before moving the plan")
    # S052 (.2-F05): a marked repository with no `adocs/` is reachable — it is
    # the first state a new user has — and S039 made a missing `status.md`
    # maximally stale, so `--session-start` and `--stop` both steer into
    # `--step status`. That wrote into a directory that is not there and raised
    # FileNotFoundError, which is neither of the two things exit 1 means. The
    # directory is not created here on purpose: a repository that was never
    # scaffolded should say so rather than be half-built by a status write.
    if not (root / DOCS).is_dir():
        return refuse(f"{DOCS}/ does not exist, so there is no plan to move. Run "
                      f"bin/moltke.py --scaffold to create it, or set \"enabled\": false in "
                      f"{MARKER} if this repository should not use the workflow")
    try:
        # Checked here rather than inside step_new and step_block, and before
        # either touches the filesystem: both write plan.md first and the step
        # file second (S083), so a name refused halfway would leave the plan
        # naming a step that does not exist. rest is indexed inside the try so a
        # missing argument still reaches the usage handler below (S088).
        if op == "new":
            problem = (step_name_problem(rest[0]) or field_value_problem("--goal", goal)
                       or step_id_ceiling_problem(root))
            return refuse(problem) if problem else step_new(root, config, rest[0], goal)
        if op == "start":
            return step_start(root, config, rest[0])
        if op == "unpause":
            return step_unpause(root, config, rest[0])
        if op == "block":
            problem = step_name_problem(rest[1]) or step_id_ceiling_problem(root)
            return refuse(problem) if problem else step_block(root, config, rest[0], rest[1])
        if op == "done":
            problem = field_value_problem("--stamp", stamp)
            return refuse(problem) if problem else step_done(root, config, rest[0], stamp)
        return step_status(root, config)
    except IndexError:
        usage = {"new": "new <short_name> [--goal TEXT]", "start": "start <id>",
                 "block": "block <parent_id> <short_name>",
                 "unpause": "unpause <id>",
                 "done": "done <id> --stamp TEXT"}[op]
        return refuse(f"usage: --step {usage}")
    except OSError as exc:
        # A partially scaffolded tree: `adocs/` exists but a plan directory
        # inside it does not, so a rename or a write has no destination. Same
        # rule as above — name the missing path, do not create it (S052).
        return refuse(f"--step {op} could not touch the plan tree ({exc}). The workflow "
                      f"directories under {DOCS}/ are what --step moves files between; "
                      f"restore the missing one, or run bin/moltke.py --scaffold, which "
                      f"creates what is absent and overwrites nothing")


def run_validate(root, config, marker_violations):
    violations = list(marker_violations) + run_checks(root, config)
    if violations:
        for violation in violations:
            print(f"VIOLATION: {violation}")
        print(f"{len(violations)} violation(s). Fix the items above, then rerun bin/moltke.py --validate.")
        return EXIT_VIOLATIONS
    print("moltke: all checks pass")
    return EXIT_OK


STRIP_WIDTH = 46


def roadmap_cells(order, done, current, width=STRIP_WIDTH):
    """One character per bucket of consecutive steps, in plan order.

    A bucket is done only when every step in it is done, so a long plan never
    reads as further along than it is (DEC-038). Under `width` steps each cell
    is one step and the question does not arise.
    """
    if not order:
        return ""
    cells = []
    for index in range(min(width, len(order))):
        first = index * len(order) // min(width, len(order))
        last = (index + 1) * len(order) // min(width, len(order))
        bucket = order[first:last] or [order[first]]
        if any(step_id in current for step_id in bucket):
            cells.append("\u25b6")
        elif all(step_id in done for step_id in bucket):
            cells.append("\u2588")
        else:
            cells.append("\u2591")
    return "".join(cells)


def mode_roadmap(root, config):
    """Where the plan is, as one timeline strip, and never a blocking exit.

    Exit 0 always, which is what specs and both exit tables say and what a mode
    AGENTS.md tells every agent to run at the end of a unit of work has to do.
    It was dispatched inside main's try, so an unreadable path returned the
    backstop's 2 — the same defect .2-F10 reported for --audit, in its twin
    (S086, .3-F07).

    Derived from `plan.md` order and the three plan directories, like every
    other check, so it cannot report something the repository does not say
    (DEC-038). `status.md` is not read at all.
    """
    try:
        return _mode_roadmap(root, config)
    except OSError as exc:
        print(f"moltke: the plan could not be read ({exc}), so there is no roadmap to draw; "
              f"run bin/moltke.py --validate for what else that path breaks.", file=sys.stderr)
        return EXIT_OK


def _mode_roadmap(root, config):
    order = plan_order(root) or []
    if not order:
        print(f"moltke: no steps planned yet. {DOCS}/plan.md holds the ordered list, "
              f"and bin/moltke.py --step new <name> adds to it.")
        return EXIT_OK

    steps = plan_steps(root)
    done = {step_id for step_id, _p, _f in steps["plan_done"]}
    current = {step_id: fields for step_id, _p, fields in steps["plan_current"]}
    done_count = sum(1 for step_id in order if step_id in done)
    left = len(order) - done_count

    strip = roadmap_cells(order, done, current)
    print(f"{order[0]} \u258f{strip}\u2595 {order[-1]}")

    # The elbow sits under the last done cell, so the split reads at a glance.
    filled = len(strip) - strip.count("\u2591") - strip.count("\u25b6")
    done_label = f" {done_count} done "
    rule = "\u2500" * max(0, filled - len(done_label) - 1)
    tail = "nothing left" if not left else f"{left} left"
    print(f"{' ' * len(order[0])} \u2514{done_label}{rule}\u2518 \u2514 {tail}")

    active = [step_id for step_id in order if step_id in current]
    if active:
        for step_id in active:
            fields = current[step_id]
            paused = field_value(fields, "paused_by")
            mark = f" [paused by {paused}]" if paused else ""
            print(f"\n{' ' * len(order[0])} now  {step_id}  {field_value(fields, 'goal')}{mark}")
    else:
        nxt = derived_next(root)
        if nxt:
            goal = ""
            for dirname in PLAN_DIRS:
                for step_id, _path, fields in steps[dirname]:
                    if step_id == nxt:
                        goal = field_value(fields, "goal")
            print(f"\n{' ' * len(order[0])} next {nxt}  {goal}")
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
    modes.add_argument("--roadmap", action="store_true", help="print where the plan is, as one timeline strip")
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

    try:
        if args.validate:
            return run_validate(root, config, marker_violations)
        if args.roadmap:
            return mode_roadmap(root, config)
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
            return mode_step(root, config, args.step, args.goal, args.stamp, marker_violations)
        if args.audit:
            return mode_audit(root, config, args.audit)
    except OSError as exc:
        # The backstop (S060). run_checks names the invariant that could not
        # read; this catches everything else a broken tree reaches — status
        # regeneration, the plan reader, the porcelain gates — so no mode ever
        # ends in a traceback. A traceback is neither of the two things exit 1
        # means, and from a Stop hook it means every gate was off and silent.
        print(f"moltke: could not read the repository ({exc}). Fix the path named above, "
              f"then run bin/moltke.py --validate.", file=sys.stderr)
        return EXIT_OK if args.log_prompt or args.session_start else EXIT_BLOCK
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
