"""Regression tests for the 2026-08-19 adversarial audit.

Red when written, by design (AGENTS.md §6): each test names a defect the audit
report reproduces, and observing the failure is the evidence. Written by the
reviewer, which may create new files under tests/ and nothing else; the fixes
belong to whoever plans the steps that close these findings.

- F01  bin/moltke.py:2365, 2387, 2411 — `step_done` compares step ids with
       `in`, so any id that appears anywhere in a `paused_by:` or `blocks:`
       line matches, comment included.
- F03  bin/moltke.py:1761, 1888 — the watch subsystem reads `<root>/.git` as a
       directory instead of asking git, so nothing is registered in a linked
       worktree and no lost watcher is ever reported there.
- F04  bin/moltke.py:2567 — `worktree_state` keys each porcelain line on its
       last path, so the source half of `R  old -> new` is dropped: a staged
       `git mv` of tracked source into `tests/` reconciles as an expected new
       test and the removal is reported nowhere.
- F05  bin/moltke.py:1706, 1929 — `_pid_alive` lets `os.kill`'s `OverflowError`
       out and `main` catches `OSError` only, so a pid past `pid_t` in a record
       or in `--pid` ends the mode in a traceback; `--pid 0` and negatives are
       process-group targets that read alive forever.
- F06  bin/moltke.py:1230 — `mode_pre_command` consults MOLTKE_UNBOUNDED_OK
       ahead of both branches, so the token also switches off the
       single-match-follow refusal INV-17 says applies always.
- F07  bin/moltke.py:1690 — `mode_decline` returns early only for a marker that
       is *not* declined, so a second `--decline` rewrites an already-declined
       marker down to two keys, against INV-11's "both leave a declined
       repository untouched".
- F08  skills/audit/SKILL.md:81, 10 and tests/test_s005_hooks.py:397 — the skill
       that drives every audit still documents `adocs/worklog.md` and
       `--log-prompt`, removed in 0.11.0 (DEC-046), and cites the review model
       as AGENTS.md §10, which is Hard prohibitions; `_turn_exits` invokes the
       removed flag from nowhere.
- F09  bin/moltke.py:2228, 149 — `with_field` renders a blank line in a value
       as twelve spaces and `parse_step_file` ends the field on any line that
       strips to empty, so a paragraphed `--stamp` — documented multi-line and
       deliberately ungated — comes back as its first paragraph.
- F12  bin/moltke.py:635, 644 — `FINDING_RE` and the INV-9 scanner read a
       fixed width unanchored on the right, the shape S136's own comment calls
       worse than blind: `DEC-1000` and a hundredth finding match nothing at
       all, so INV-9 abstains and INV-10 never sees the finding's status.
- F11  bin/moltke.py:1037 — `reviewer_may_write` decides both halves on
       existence alone and gets each backwards: any path under `adocs/audit/`
       is permitted, so a `Write` at an earlier report's path destroys
       evidence, and any existing `tests/` path is refused, so correcting the
       run's own red test has to go through `Bash`, which nothing fences.
"""

import ast
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import audit_report, marked_repo, step_file, workflow_repo
from surface import REPO, moltke

MOLTKE = REPO / "bin" / "moltke.py"


def parser_flags():
    return {flag for action in moltke.build_parser()._actions
            for flag in action.option_strings}

WATCH_DIR = "moltke_watch"  # mirrors bin/moltke.py


def run_moltke(cwd, *args, stdin=None):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=str(cwd), input=stdin, capture_output=True, text=True)


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        capture_output=True, text=True, check=True)


def git_baseline(root):
    for args in (("init", "-q"), ("add", "-A"), ("commit", "-qm", "base")):
        git(root, *args)


def write_step(directory, step_id, name, **fields):
    """A step file with the fields written the way `--step block` writes them."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    lines = [f"id:         {step_id}"]
    lines.extend(f"{key}:{' ' * max(1, 11 - len(key) - 1)}{value}".rstrip()
                 for key, value in fields.items())
    path = directory / f"{step_id}_{name}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def plan_repo(tmp, entries, **marker):
    """A marked repo whose plan.md lists `entries` in order, git-committed."""
    root = marked_repo(tmp, overrides=marker)
    docs = root / "adocs"
    for name in ("plan_todo", "plan_current", "plan_done", "audit"):
        (docs / name).mkdir(parents=True, exist_ok=True)
    listing = "".join(f"{index}. {step_id}  {goal}\n"
                      for index, (step_id, goal) in enumerate(entries, start=1))
    (docs / "plan.md").write_text(f"# Plan\n\n{listing}", encoding="utf-8")
    return root


def status_regenerated(root):
    """status.md as the tool derives it, so staleness is never the failure."""
    result = run_moltke(root, "--step", "status")
    assert result.returncode == 0, result.stderr
    return result


class TestStepDoneMatchesIdsAsTokens(unittest.TestCase):
    """F01: an id is a token, and every other reader of these two fields treats
    it as one — `pauser_id` matches `STEP_ID_RE` precisely because `paused_by`
    carries a dated comment, and INV-4 reads `blocks:` with `findall`.
    `step_done` alone asks `step_id in <the whole line>`.
    """

    def test_pause_survives_completing_a_step_named_in_its_comment(self):
        # `--step block` itself writes `paused_by:  <child>  # <date>`, so a
        # comment on that line is the tool's own format, not an abuse of it.
        with tempfile.TemporaryDirectory() as tmp:
            root = plan_repo(tmp, [("S010", "unrelated work"),
                                   ("S200", "parent"),
                                   ("S201", "the real blocker")],
                             plan_active_max=1, plan_stack_max=4)
            current = root / "adocs" / "plan_current"
            write_step(current, "S010", "unrelated",
                       goal="unrelated work", paused_by="", blocks="", author="A")
            parent = write_step(current, "S200", "parent", goal="parent",
                                paused_by="S201  # 2026-08-19, after S010 lands",
                                blocks="", author="B")
            write_step(current, "S201", "blocker", goal="the real blocker",
                       paused_by="", blocks="S200", author="B")
            status_regenerated(root)
            git_baseline(root)

            # Preconditions: the tree is valid, and the pause is on S201.
            clean = run_moltke(root, "--validate")
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)

            done = run_moltke(root, "--step", "done", "S010", "--stamp", "unrelated work done")
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertNotIn("S200 unpaused", done.stdout,
                             "completing S010 must not touch a pause that names S201")
            self.assertIn("S201", parent.read_text(encoding="utf-8"),
                          "S200's pause on the still-open S201 was cleared")

            after = run_moltke(root, "--validate")
            self.assertEqual(after.returncode, 0, after.stdout + after.stderr)

    def test_four_digit_pause_survives_completing_its_three_digit_prefix(self):
        # S136 widened ids to four digits; `S100` is a prefix of `S1000`, so the
        # substring compare now collides on ids alone, with no comment involved.
        with tempfile.TemporaryDirectory() as tmp:
            root = plan_repo(tmp, [("S100", "unrelated work"),
                                   ("S200", "parent"),
                                   ("S1000", "the real blocker")],
                             plan_active_max=1, plan_stack_max=4)
            current = root / "adocs" / "plan_current"
            write_step(current, "S100", "unrelated",
                       goal="unrelated work", paused_by="", blocks="", author="A")
            parent = write_step(current, "S200", "parent", goal="parent",
                                paused_by="S1000  # 2026-08-19", blocks="", author="B")
            write_step(current, "S1000", "blocker", goal="the real blocker",
                       paused_by="", blocks="S200", author="B")
            status_regenerated(root)
            git_baseline(root)

            clean = run_moltke(root, "--validate")
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)

            done = run_moltke(root, "--step", "done", "S100", "--stamp", "unrelated work done")
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("S1000", parent.read_text(encoding="utf-8"),
                          "S200's pause on the still-open S1000 was cleared")

    def test_completion_is_not_refused_by_a_blocks_field_naming_another_id(self):
        # The same compare in the other direction: a refusal whose own message
        # quotes a `blocks:` value that does not contain the id it names.
        with tempfile.TemporaryDirectory() as tmp:
            root = plan_repo(tmp, [("S100", "the step being completed"),
                                   ("S300", "declares blocks S1000"),
                                   ("S1000", "what S300 actually blocks")],
                             plan_active_max=4, plan_stack_max=4)
            write_step(root / "adocs" / "plan_current", "S100", "target",
                       goal="the step being completed", paused_by="", blocks="")
            write_step(root / "adocs" / "plan_todo", "S300", "declarer",
                       goal="declares blocks S1000", paused_by="", blocks="S1000")
            write_step(root / "adocs" / "plan_todo", "S1000", "blockee",
                       goal="what S300 actually blocks", paused_by="", blocks="")
            status_regenerated(root)
            git_baseline(root)

            clean = run_moltke(root, "--validate")
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)

            done = run_moltke(root, "--step", "done", "S100", "--stamp", "finished")
            self.assertEqual(done.returncode, 0,
                             f"nothing declares blocks: S100, yet: {done.stderr}")


class TestWatchStateInALinkedWorktree(unittest.TestCase):
    """F03: specs and MANUAL both say every watch registers itself and that a
    session which died overnight finds the outcome the next morning. In a linked
    worktree `.git` is a file (S035, 2026-08-07_adversarial-F04), so nothing is
    written and nothing is reported — the two state files that learned this
    lesson use `git_dir()`; the watch subsystem does not.
    """

    def _worktree(self, tmp):
        (Path(tmp) / "main").mkdir()
        root = marked_repo(Path(tmp) / "main")
        docs = root / "adocs"
        for name in ("plan_todo", "plan_current", "plan_done", "audit"):
            (docs / name).mkdir(parents=True, exist_ok=True)
        (docs / "plan.md").write_text("# Plan\n\n1. S001  base\n", encoding="utf-8")
        write_step(docs / "plan_done", "S001", "base", goal="base", done="2026-08-19 stamped")
        status_regenerated(root)
        git_baseline(root)
        worktree = Path(tmp) / "linked"
        git(root, "worktree", "add", "-q", "-b", "wt", str(worktree))
        self.assertTrue((worktree / ".git").is_file(),
                        "precondition: a linked worktree's .git is a file, not a directory")
        return root, worktree

    def _watch_records(self, root, worktree):
        git_dir = Path(git(worktree, "rev-parse", "--absolute-git-dir").stdout.strip())
        records = []
        for directory in (git_dir / WATCH_DIR, root / ".git" / WATCH_DIR):
            if directory.is_dir():
                records.extend(sorted(directory.glob("*.json")))
        return records

    def test_a_watch_in_a_worktree_records_its_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, worktree = self._worktree(tmp)
            log = worktree / "run.log"
            log.write_text("RUN-DONE ok\n", encoding="utf-8")

            watch = run_moltke(worktree, "--watch", str(log), "RUN-DONE",
                               "--ceiling", "5s", "--interval", "0.05s")
            self.assertEqual(watch.returncode, 0, watch.stderr)
            self.assertNotIn("not registered", watch.stderr,
                             "the watch found no .git in a worktree that has one")

            records = self._watch_records(root, worktree)
            self.assertEqual(len(records), 1, "no watch record was written anywhere")
            record = json.loads(records[0].read_text(encoding="utf-8"))
            self.assertEqual(record["outcome"], "success marker")

    def test_stop_in_a_worktree_reports_an_unacknowledged_outcome(self):
        # The user-visible half: acting on a result is deleting its record, and
        # the turn is supposed to refuse to end until someone does.
        with tempfile.TemporaryDirectory() as tmp:
            _root, worktree = self._worktree(tmp)
            log = worktree / "run.log"
            log.write_text("RUN-DONE ok\n", encoding="utf-8")

            # Precondition: with no watch armed, this worktree ends a turn clean.
            before = run_moltke(worktree, "--stop", stdin="{}")
            self.assertEqual(before.returncode, 0, before.stdout + before.stderr)

            watch = run_moltke(worktree, "--watch", str(log), "RUN-DONE",
                               "--ceiling", "5s", "--interval", "0.05s")
            self.assertEqual(watch.returncode, 0, watch.stderr)

            after = run_moltke(worktree, "--stop", stdin="{}")
            self.assertEqual(after.returncode, 2, after.stdout + after.stderr)
            self.assertIn("unacknowledged", after.stderr)


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TestAuditCheckSeesARenameSource(unittest.TestCase):
    """F04: `porcelain_paths` returns both halves of `R  old -> new` and its
    docstring says why both matter, but `worktree_state` kept only the
    destination. `_is_new_file` treats `R` as newly here (S077), so one
    `git mv` into `tests/` removed tracked source and reconciled clean."""

    def audit_repo(self, tmp):
        root = workflow_repo(tmp)
        write(root, "src/thing.py", "print('source')\n")
        write(root, "tests/test_existing.py", "# an existing test\n")
        git_baseline(root)
        opened = run_moltke(root, "--audit", "new", "adversarial")
        self.assertEqual(opened.returncode, 0, opened.stdout + opened.stderr)
        return root

    def staged_rename(self, root, source, destination):
        git(root, "mv", source, destination)
        porcelain = git(root, "status", "--porcelain", "-uall").stdout
        self.assertIn(f"R  {source} -> {destination}", porcelain,
                      "precondition: git reports one rename line naming both halves")

    def unexpected_section(self, stdout):
        return stdout.split("unexpected,")[1] if "unexpected," in stdout else ""

    def test_a_staged_rename_into_tests_reports_the_source_it_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audit_repo(tmp)
            self.staged_rename(root, "src/thing.py", "tests/test_moved_thing.py")
            result = run_moltke(root, "--audit", "check")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("src/thing.py", self.unexpected_section(result.stdout))

    def test_the_destination_of_that_rename_is_still_reported(self):
        # The departure must be added to what the check says, not swapped for it:
        # the reviewer needs to see where the source went.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audit_repo(tmp)
            self.staged_rename(root, "src/thing.py", "tests/test_moved_thing.py")
            result = run_moltke(root, "--audit", "check")
            self.assertIn("tests/test_moved_thing.py", result.stdout)

    def test_a_rename_between_two_source_paths_is_unexpected_too(self):
        # Nothing about the departure depends on the destination being tests/.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audit_repo(tmp)
            self.staged_rename(root, "src/thing.py", "src/renamed.py")
            result = run_moltke(root, "--audit", "check")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("src/thing.py", self.unexpected_section(result.stdout))

    def test_an_ordinary_new_test_is_still_expected(self):
        # Non-vacuity: the fence permits new files under tests/, and reporting
        # departures must not turn a red-first regression test into dirt.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audit_repo(tmp)
            write(root, "tests/test_regression.py", "# red first\n")
            result = run_moltke(root, "--audit", "check")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("unexpected", result.stdout)

    def test_a_rename_staged_before_the_run_is_not_blamed_on_it(self):
        # The departure is recorded in the baseline as well, so a tree that was
        # already dirty this way reconciles unchanged.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            write(root, "src/thing.py", "print('source')\n")
            write(root, "tests/test_existing.py", "# an existing test\n")
            git_baseline(root)
            self.staged_rename(root, "src/thing.py", "tests/test_moved_thing.py")
            run_moltke(root, "--audit", "new", "adversarial")
            result = run_moltke(root, "--audit", "check")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("src/thing.py", result.stdout)


class TestPidRangeIsRefusedNotRaised(unittest.TestCase):
    """F05: `_pid_alive` catches `ProcessLookupError` and `OSError`, but
    `os.kill` raises `OverflowError` past C `pid_t` and `main`'s backstop catches
    `OSError` only. A watch record carrying such a pid is filesystem state that
    `watch_records` is written to tolerate, so `--stop` and `--session-start`
    both end in a traceback — every gate off, and from `--session-start` the
    whole additionalContext payload lost. A mistyped `--pid` does it to `--watch`
    after the record is armed, and `--pid 0` or a negative pid is a kill(2)
    process-group target that reads alive forever, so exit 3 can never fire.
    """

    OUT_OF_RANGE = 2 ** 40  # inside C long, past pid_t: os.kill overflows

    def _repo(self, tmp):
        root = workflow_repo(Path(tmp))
        git_baseline(root)
        return root

    def _arm_record(self, root, watcher_pid, **extra):
        """A watch record as `--watch` writes one, with no outcome: an obligation."""
        directory = root / ".git" / WATCH_DIR
        directory.mkdir(parents=True, exist_ok=True)
        record = {"schema": 1, "log": str(root / "run.log"), "regex": "RUN-DONE",
                  "fail_regex": None, "pid": None, "ceiling": "8h",
                  "interval": "30s", "armed_at": "2026-08-19T10:00:00+02:00",
                  "watcher_pid": watcher_pid}
        record.update(extra)
        path = directory / "1787000000_4242.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return path

    def test_stop_reports_a_watcher_pid_it_cannot_probe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            before = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(before.returncode, 0, before.stdout + before.stderr)

            self._arm_record(root, self.OUT_OF_RANGE)
            after = run_moltke(root, "--stop", stdin="{}")
            self.assertNotIn("Traceback", after.stderr)
            self.assertEqual(after.returncode, 2, after.stdout + after.stderr)
            self.assertIn("watcher died", after.stderr)

    def test_session_start_still_emits_its_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self._arm_record(root, self.OUT_OF_RANGE)
            result = run_moltke(root, "--session-start", stdin="{}")
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("hookSpecificOutput", payload)

    def test_watch_refuses_a_pid_out_of_range_before_arming_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "run.log").write_text("RUN-DONE ok\n", encoding="utf-8")
            result = run_moltke(root, "--watch", str(root / "run.log"), "RUN-DONE",
                                "--ceiling", "5s", "--interval", "0.05s",
                                "--pid", str(self.OUT_OF_RANGE))
            self.assertNotIn("Traceback", result.stderr)
            # 1, like every other --watch refusal (S129): a refusal, not a marker.
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("--pid", result.stderr)
            self.assertEqual(list((root / ".git" / WATCH_DIR).glob("*.json"))
                             if (root / ".git" / WATCH_DIR).is_dir() else [], [],
                             "a refused watch left a record blocking every stop")

    def test_watch_refuses_a_process_group_pid(self):
        # 0 and negatives are process-group targets: os.kill succeeds, the pid
        # reads alive forever, and the exit 3 the flag exists for cannot fire.
        for pid in ("0", "-1", f"-{self.OUT_OF_RANGE}"):
            with self.subTest(pid=pid), tempfile.TemporaryDirectory() as tmp:
                root = self._repo(tmp)
                (root / "run.log").write_text("nothing yet\n", encoding="utf-8")
                result = run_moltke(root, "--watch", str(root / "run.log"),
                                    "RUN-DONE", "--ceiling", "1s",
                                    "--interval", "0.05s", "--pid", pid)
                self.assertEqual(result.returncode, 1,
                                 result.stdout + result.stderr)
                self.assertIn("--pid", result.stderr)

    def test_a_pid_that_could_exist_is_still_watched(self):
        # Non-vacuity: the refusals above must not swallow the flag's own use.
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            log = root / "run.log"
            log.write_text("RUN-DONE ok\n", encoding="utf-8")
            result = run_moltke(root, "--watch", str(log), "RUN-DONE",
                                "--ceiling", "5s", "--interval", "0.05s",
                                "--pid", str(os.getpid()))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestUnboundedTokenDoesNotReachASingleMatchFollow(unittest.TestCase):
    """F06: `mode_pre_command` consults MOLTKE_UNBOUNDED_OK before either
    branch, so the token switches off the single-match-follow refusal too.
    INV-17 says that form is refused always and DEC-051 says "bounded or not",
    while the token is documented for a genuinely unbounded stream — which
    `-m N` is the opposite of. The persistent branch's own refusal teaches the
    token to every agent it blocks, so the next arm can carry it into the one
    form that leaks a `tail` forever.
    """

    SINGLE_MATCH = "tail -f run.log | grep -m1 BOOM"
    STREAM = "tail -f dev.log | grep --line-buffered ERROR"
    TOKEN = "  # MOLTKE_UNBOUNDED_OK"

    def _arm(self, root, command, persistent=True):
        payload = json.dumps({"tool_name": "Monitor",
                              "tool_input": {"command": command,
                                             "persistent": persistent}})
        return run_moltke(root, "--pre-command", stdin=payload)

    def test_the_token_does_not_arm_a_persistent_single_match_follow(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(Path(tmp))
            result = self._arm(root, self.SINGLE_MATCH + self.TOKEN)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("SIGPIPE", result.stderr)

    def test_the_refusal_states_the_token_does_not_reach_this_form(self):
        # The refusal is where the rule is taught, and INV-17's word is always.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(Path(tmp))
            result = self._arm(root, self.SINGLE_MATCH + self.TOKEN)
            self.assertIn("MOLTKE_UNBOUNDED_OK does not reach", result.stderr)

    def test_the_token_does_not_arm_a_bounded_single_match_follow_either(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(Path(tmp))
            result = self._arm(root, self.SINGLE_MATCH + self.TOKEN,
                               persistent=False)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_the_token_still_arms_a_deliberately_unbounded_stream(self):
        # Non-vacuity: the escape has to be live for the refusals above to say
        # anything, so the same stream is refused without the token first.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(Path(tmp))
            bare = self._arm(root, self.STREAM)
            self.assertEqual(bare.returncode, 2, bare.stdout + bare.stderr)
            tokened = self._arm(root, self.STREAM + self.TOKEN)
            self.assertEqual(tokened.returncode, 0, tokened.stderr)


class TestDeclineLeavesADeclinedMarkerAlone(unittest.TestCase):
    """F07: INV-11 says `--scaffold` and `--decline` both leave a declined
    repository untouched, and `--scaffold` does. `--decline` returns early only
    when the marker exists and is not declined, so a declined marker falls
    through to the write and comes back as `{"schema": 1, "enabled": false}` —
    a note saying why the repository declined, or configuration a later
    `enabled: true` would have restored, is discarded by the second run of a
    mode documented as durable.
    """

    MARKER = ('{\n  "schema": 1,\n  "enabled": false,\n'
              '  "note": "declined 2026-01-01 by the team; see docs/why.md",\n'
              '  "plan_active_max": 2\n}\n')

    def _declined(self, tmp):
        root = Path(tmp)
        (root / ".moltke.json").write_text(self.MARKER, encoding="utf-8")
        return root

    def test_a_second_decline_leaves_the_marker_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._declined(tmp)
            before = (root / ".moltke.json").read_bytes()
            result = run_moltke(root, "--decline")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((root / ".moltke.json").read_bytes(), before)

    def test_it_says_what_scaffold_says_over_the_same_marker(self):
        # The two setup modes describe one situation, so they say one thing.
        with tempfile.TemporaryDirectory() as tmp:
            root = self._declined(tmp)
            declining = run_moltke(root, "--decline")
            scaffolding = run_moltke(root, "--scaffold")
            self.assertEqual(scaffolding.returncode, 0, scaffolding.stderr)
            self.assertIn("left untouched", scaffolding.stdout)  # precondition
            self.assertEqual(declining.stdout, scaffolding.stdout)

    def test_the_first_decline_still_writes_the_marker(self):
        # Non-vacuity: the untouched marker above must be the early return, not
        # a --decline that stopped writing.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_moltke(root, "--decline")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            marker = json.loads((root / ".moltke.json").read_text(encoding="utf-8"))
            self.assertIs(marker["enabled"], False)


class TestComponentDocsNameOnlyWhatExists(unittest.TestCase):
    """F08: AGENTS.md §7 makes a doc claim a claim about code, traced to the code
    path producing it. The worklog and `--log-prompt` left in 0.11.0 (DEC-046),
    but the skill that drives every audit still tells an operator to expect a
    worklog append among `--audit check`'s expected changes and says an edit
    there turns off a `Stop` recap gate that no longer exists. The same file
    cites the review model as AGENTS.md §10, which is Hard prohibitions. A dead
    test helper invoking the removed flag is the same removal's other half.

    Skills and agent definitions are scanned whole because every command they
    quote is moltke's own; README, MANUAL and specs also quote git, whose flags
    argparse rightly refuses.
    """

    def component_docs(self):
        return sorted((REPO / "skills").glob("*/SKILL.md")) + \
            sorted((REPO / "agents").glob("*.md"))

    def flags_named_in(self, path):
        return set(re.findall(r"--[a-z][a-z0-9-]*",
                              path.read_text(encoding="utf-8")))

    def moltke_flags_in(self, path):
        """Every string constant passed to a `run_moltke(...)` call in `path`
        that looks like a flag. Read from the syntax tree, so a call spanning
        lines is one call and a flag inside a comment is not a call at all."""
        tree = ast.parse(path.read_text(encoding="utf-8"))
        flags = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if name != "run_moltke":
                continue
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                        and arg.value.startswith("--"):
                    flags.add(arg.value)
        return flags

    def test_the_scans_below_have_something_to_scan(self):
        # Non-vacuity: both checks pass trivially over an empty set, so the
        # preconditions that make them meaningful are asserted first.
        docs = self.component_docs()
        self.assertTrue(any(self.flags_named_in(path) for path in docs),
                        f"no component doc under {docs} names any flag")
        suite = sorted((REPO / "tests").glob("test_*.py"))
        self.assertTrue(any(self.moltke_flags_in(path) for path in suite),
                        "no test file invokes run_moltke with a flag")

    def test_no_component_doc_names_a_flag_the_parser_refuses(self):
        flags = parser_flags()
        stale = sorted(f"{path.relative_to(REPO)}: {flag}"
                       for path in self.component_docs()
                       for flag in self.flags_named_in(path) - flags)
        self.assertEqual(stale, [],
                         "a shipped skill or agent definition documents a flag argparse "
                         "refuses, so an operator following it gets exit 2")

    def test_no_test_invokes_moltke_with_a_flag_the_parser_refuses(self):
        flags = parser_flags()
        stale = sorted(f"{path.relative_to(REPO)}: {flag}"
                       for path in sorted((REPO / "tests").glob("test_*.py"))
                       for flag in self.moltke_flags_in(path) - flags)
        self.assertEqual(stale, [],
                         "a test invokes a mode the parser no longer has, so it either "
                         "asserts over exit 2 or is dead code the removal left behind")

    def test_no_component_doc_names_the_worklog(self):
        """Widened from the audit skill alone (S157): the init skill promised a
        recap gate over the same deleted file, so scanning one doc left the
        finding half open. Every shipped skill and agent definition is scanned,
        the same set the flag scan above reads."""
        docs = self.component_docs()
        self.assertTrue(docs, "no component doc to scan; the scan below would be vacuous")
        naming = [f"{path.relative_to(REPO)}:{number}: {line.strip()}"
                  for path in docs
                  for number, line in enumerate(
                      path.read_text(encoding="utf-8").splitlines(), 1)
                  if "worklog" in line.lower()]
        self.assertEqual(naming, [],
                         "a shipped skill or agent definition describes a file DEC-046 "
                         "deleted, so an operator following it expects a change no mode "
                         "produces and a gate no hook applies")

    def test_the_audit_skill_cites_the_section_that_holds_the_review_model(self):
        headings = re.findall(r"^## (\d+)\. (.+)$",
                              (REPO / "AGENTS.md").read_text(encoding="utf-8"),
                              flags=re.MULTILINE)
        review = [number for number, title in headings if title.startswith("Review")]
        self.assertEqual(len(review), 1,
                         f"precondition: one AGENTS.md section holds the review model, "
                         f"found {review} in {[t for _, t in headings]}")
        text = (REPO / "skills" / "audit" / "SKILL.md").read_text(encoding="utf-8")
        cited = re.findall(r"AGENTS\.md §(\d+)", text)
        self.assertEqual(cited, review,
                         "the audit skill points a reader at a section that is not the "
                         "review model it claims to be tier 3 of")


class TestABlankLineInAStampIsRefused(unittest.TestCase):
    """F09: `with_field` renders every continuation at twelve spaces, a blank
    line among them, and `parse_step_file` ends a field on the first line that
    strips to empty and then drops the indented lines below it. specs documents
    `--stamp` as multi-line and `field_value_problem` deliberately does not gate
    it, so a paragraphed stamp reached disk whole and came back as its first
    paragraph — S095's truncation narrowed to the one field documented as
    multi-line, in front of INV-5, the `Stop` arrival gate, and everything else
    that quotes a stamp.

    Refused rather than reflowed (DEC-059), which is the rule
    `field_value_problem` already applies to a line break in a one-line field: a
    stamp is evidence, and rewriting it quietly is the same class of defect as
    reading it short.
    """

    PARAGRAPHED = "first paragraph of the stamp\n\nREADME and MANUAL checked; suite green"

    def _done(self, root, stamp):
        return run_moltke(root, "--step", "done", "S003", "--stamp", stamp)

    def test_a_paragraphed_stamp_is_refused_and_nothing_moves(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self._done(root, self.PARAGRAPHED)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("blank line", result.stderr)
            self.assertIn("--stamp", result.stderr)
            self.assertTrue((root / "adocs" / "plan_current" / "S003_active.md").exists())
            self.assertEqual(list((root / "adocs" / "plan_done").glob("S003*")), [])

    def test_a_whitespace_only_line_is_the_same_line(self):
        # It renders as twelve spaces either way, so the parser cannot tell the
        # two apart and neither may the check.
        with tempfile.TemporaryDirectory() as tmp:
            result = self._done(workflow_repo(tmp), "first paragraph\n   \nsecond paragraph")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("blank line", result.stderr)

    def test_two_leading_blank_lines_are_refused_with_the_rest(self):
        # Not politeness: one leading blank line lands where the `key:` line
        # already ends, and parses; two put a twelve-space line between that key
        # and its first continuation, and the whole value is dropped. The rule
        # is one rule so that boundary is nobody's to remember.
        with tempfile.TemporaryDirectory() as tmp:
            result = self._done(workflow_repo(tmp), "\n\nthe whole stamp on one line")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("blank line", result.stderr)

    def test_the_refusal_comes_before_the_suite_gate(self):
        # The ordering specs, MANUAL and the stamp all claim: a stamp that cannot
        # be written is not worth a full test run. Every other test here runs
        # under a marker with no `test_command`, so without this one the check
        # could sit below the gate and stay green.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            marker = json.loads((root / ".moltke.json").read_text(encoding="utf-8"))
            marker["test_command"] = "touch suite_ran"  # shell=True, cwd is the root
            (root / ".moltke.json").write_text(json.dumps(marker, indent=2) + "\n",
                                               encoding="utf-8")
            refused = self._done(root, self.PARAGRAPHED)
            self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
            self.assertIn("blank line", refused.stderr)
            self.assertFalse((root / "suite_ran").exists(),
                             "the suite gate ran before the stamp was checked")
            # Non-vacuity: the same marker does reach the gate once the stamp
            # passes, so the sentinel above is absent by ordering and not because
            # nothing here ever runs a `test_command`.
            passed = self._done(root, "the whole stamp on one line")
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            self.assertTrue((root / "suite_ran").exists())

    def test_a_multi_line_stamp_without_one_completes_and_round_trips(self):
        # Non-vacuity, and the half of DEC-048 that stands: multi-line is still
        # accepted, so the refusals above are about the blank line and not about
        # the newline `field_value_problem` refuses elsewhere.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            stamp = "first line of the stamp\nREADME and MANUAL checked; suite green"
            result = self._done(root, stamp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            done = root / "adocs" / "plan_done" / "S003_active.md"
            self.assertEqual(moltke.parse_step_file(done)["done"],
                             "first line of the stamp README and MANUAL checked; suite green")


TODAY = datetime.date.today().isoformat()
SCOPED_REVIEWER = "moltke:adversarial_reviewer"


class TestReviewerFenceJudgesWhenAFileArrived(unittest.TestCase):
    """F11: the fence permits what the run produced, not what it finds lying
    there. `--audit new` records the tree as it stood when the report opened,
    so "this run wrote it" is a question the baseline can answer.
    """

    def fence(self, root, path):
        payload = json.dumps({"agent_type": SCOPED_REVIEWER,
                              "tool_input": {"file_path": path}})
        return run_moltke(root, "--pre-write", stdin=payload)

    def audited_repo(self, tmp):
        """A committed repository with an older report and a committed test,
        then a fresh audit run opened over it."""
        root = workflow_repo(tmp)
        write(root, "src/main.py", "print('source')\n")
        write(root, "tests/test_existing.py", "# committed before the run\n")
        write(root, "adocs/audit/2026-01-01_adversarial.md",
              "# Audit 2026-01-01\n\nEvidence from an earlier run.\n")
        git_baseline(root)
        opened = run_moltke(root, "--audit", "new", "adversarial")
        self.assertEqual(opened.returncode, 0, opened.stdout + opened.stderr)
        return root

    def test_an_earlier_report_cannot_be_overwritten(self):
        # AGENTS.md §2: "add files, never overwrite a report". `--audit new`
        # honours it with next_report_path; the fence did not.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audited_repo(tmp)
            result = self.fence(root, "adocs/audit/2026-01-01_adversarial.md")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            # The message, not just the code: every refusal here interpolates
            # the path, so the filename alone cannot tell this refusal from the
            # generic one for a path under neither directory.
            self.assertIn("never overwritten", result.stderr)
            self.assertIn(f"{TODAY}_adversarial.md", result.stderr)

    def test_a_test_this_run_created_can_be_corrected(self):
        # The mirror image: a typo in one's own red test had to be fixed
        # through Bash, where nothing is fenced or classified. The 2026-08-19
        # run did exactly that and disclosed it.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audited_repo(tmp)
            write(root, "tests/test_f11_red.py", "# written by this run\n")
            result = self.fence(root, "tests/test_f11_red.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_this_runs_own_report_is_still_writable(self):
        # Non-vacuity for the refusal above: the run's report exists too, and
        # the reviewer writes it many times.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audited_repo(tmp)
            result = self.fence(root, f"adocs/audit/{TODAY}_adversarial.md")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_committed_test_is_still_a_patch(self):
        # Non-vacuity for the permission above: the widening is "this run wrote
        # it", not "it is under tests/".
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audited_repo(tmp)
            result = self.fence(root, "tests/test_existing.py")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_a_test_that_was_already_sitting_untracked_is_refused(self):
        # And the baseline is what draws that line: an untracked file present
        # before the run reads as new to git and is not this run's work.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            write(root, "tests/test_someone_elses.py", "# uncommitted, predates the run\n")
            run_moltke(root, "--audit", "new", "adversarial")
            result = self.fence(root, "tests/test_someone_elses.py")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_a_new_report_path_is_still_created_freely(self):
        # Non-vacuity for every refusal above: nothing here narrows creation,
        # which is what the reviewer is spawned to do.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audited_repo(tmp)
            for path in (f"adocs/audit/{TODAY}_adversarial.2.md",
                         "tests/test_brand_new.py"):
                result = self.fence(root, path)
                self.assertEqual(result.returncode, 0, (path, result.stderr))

    def test_the_baseline_names_this_runs_report_even_once_it_is_committed(self):
        # The branch that reads `report` off the baseline, which nothing else
        # reaches: a committed report is in neither snapshot, so "arrived during
        # the run" answers no and only the name keeps it writable. The audit
        # skill commits, so this is the ordinary end of a run.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.audited_repo(tmp)
            git(root, "add", "-A")
            git(root, "commit", "-qm", "report so far")
            result = self.fence(root, f"adocs/audit/{TODAY}_adversarial.md")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_without_git_the_report_half_still_permits_and_the_tests_half_refuses(self):
        # The fallback for a repository nothing can date a run in. Each half
        # keeps what it did before S151 gave it a baseline to read: refusing the
        # report would lock the reviewer out of the one it is writing, and an
        # existing test is still a patch.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            write(root, "adocs/audit/2026-01-01_adversarial.md", "# no git here\n")
            write(root, "tests/test_existing.py", "# no git here\n")
            self.assertEqual(
                self.fence(root, "adocs/audit/2026-01-01_adversarial.md").returncode, 0)
            self.assertEqual(self.fence(root, "tests/test_existing.py").returncode, 2)

    def test_with_git_but_no_run_a_committed_report_is_still_refused(self):
        # Found by the S151 fast check. The reviewer is spawnable directly, with
        # no --audit new and so no baseline, and reading git's "untracked" as
        # "this run wrote it" waved through every file the run merely found. Git
        # can still settle one thing without a baseline: a tracked file with no
        # change against HEAD is not a report this session opened.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            write(root, "adocs/audit/2026-01-01_adversarial.md", "# an earlier run\n")
            write(root, "tests/test_existing.py", "# committed\n")
            git_baseline(root)
            for path in ("adocs/audit/2026-01-01_adversarial.md", "tests/test_existing.py"):
                self.assertEqual(self.fence(root, path).returncode, 2, path)
            # And the report a reviewer opens by hand is still writable.
            write(root, f"adocs/audit/{TODAY}_adversarial.md", "# opened by hand\n")
            self.assertEqual(
                self.fence(root, f"adocs/audit/{TODAY}_adversarial.md").returncode, 0)

    def test_a_baseline_that_cannot_date_anything_is_not_read_as_permission(self):
        # The same fast check, second half: an unreadable `tree` fell through to
        # the git-only answer, so the fence permitted what --audit check refuses
        # to reconcile at all. A record that cannot date a file abstains.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            write(root, "tests/test_existing.py", "# untracked, predates the run\n")
            git_baseline(root)
            write(root, "tests/test_untracked.py", "# untracked, predates the run\n")
            record = Path(root) / ".git" / "moltke_audit_baseline.json"
            record.write_text(json.dumps({"report": f"adocs/audit/{TODAY}_adversarial.md",
                                          "tree": None, "head": None}), encoding="utf-8")
            for path in ("tests/test_existing.py", "tests/test_untracked.py"):
                self.assertEqual(self.fence(root, path).returncode, 2, path)


class TestIdScannersReadAnyWidth(unittest.TestCase):
    """F12: the same width defect S136 fixed for step ids, left in the two
    scanners that read ids nobody allocates. There is no ceiling to refuse at,
    so a width nothing reads is a silent skip rather than a loud refusal.
    """

    def decisions(self, root, *headings):
        path = Path(root) / "adocs" / "decisions.md"
        body = ["# Decisions", "", "## Index", ""]
        for heading in headings:
            body += [f"## {heading}", "", "Tags: t", "",
                     "Decision: something.", "Why: because.", ""]
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
        return path

    def step(self, root, step_id, **fields):
        """A plan_todo step listed in plan.md, so INV-3 stays satisfied."""
        step_file(Path(root) / "adocs" / "plan_todo", step_id, "x", goal="g", **fields)
        plan = Path(root) / "adocs" / "plan.md"
        plan.write_text(plan.read_text(encoding="utf-8") + f"2. {step_id}  x\n",
                        encoding="utf-8")

    def test_a_four_digit_dec_id_is_read_by_inv_9(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.decisions(root, "DEC-1000  2026-08-20  first",
                                 "DEC-1000  2026-08-20  duplicate")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-9", result.stdout)
            self.assertIn("DEC-1000", result.stdout)
            # The word, not just the id: the malformed-heading branch below
            # reports the same id with the same INV number, so narrowing
            # DEC_ID_DIGITS back to three would still satisfy the two assertions
            # above while the duplicate went unseen (found by the S152 fast
            # check, which survived exactly that mutation).
            self.assertIn("duplicate", result.stdout)

    def test_a_three_digit_dec_id_is_still_read(self):
        # Non-vacuity anchor: the width in use today keeps working, so the test
        # above is about the width and not about the fixture.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.decisions(root, "DEC-057  2026-08-20  first",
                                 "DEC-057  2026-08-20  duplicate")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("DEC-057", result.stdout)

    def test_a_heading_that_looks_like_a_decision_and_is_not_an_id_is_reported(self):
        # The other half of "never silently skipped": a width below the form is
        # as unreadable as a width above it, and INV-9 said nothing about either.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.decisions(root, "DEC-57  2026-08-20  too narrow to be an id")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-9", result.stdout)
            self.assertIn("DEC-57", result.stdout)

    def test_an_ordinary_decisions_file_stays_silent(self):
        # Non-vacuity for the report above: the shape every decisions.md in the
        # wild has must not become a violation.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.decisions(root, "DEC-001  2026-08-20  first",
                                 "DEC-002  2026-08-20  second")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_hundredth_finding_is_seen_by_inv_10_and_audit_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            stem = "2026-08-01_adversarial"
            audit_report(root, [(f"{stem}-F01", "closed"),
                                (f"{stem}-F100", "bogus")])
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-10", result.stdout)
            self.assertIn(f"{stem}-F100", result.stdout)
            listing = run_moltke(root, "--audit", "list")
            self.assertIn(f"{stem}-F100", listing.stdout)

    def test_a_well_formed_wide_finding_is_accepted_and_can_be_closed(self):
        # The acceptance side of the widening, which nothing asserted: under a
        # stem rule still spelled two digits, a correctly named -F100 raises a
        # false "should read <stem>-F<nn>" and no test noticed (S152 fast check).
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            stem = "2026-08-01_adversarial"
            audit_report(root, [(f"{stem}-F100", "open")])
            self.step(root, "S900", closes=f"{stem}-F100")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            listing = run_moltke(root, "--audit", "list")
            self.assertIn(f"{stem}-F100  open  (closed by S900)", listing.stdout)

    def test_a_wider_id_does_not_discharge_the_finding_it_starts_with(self):
        # Found by the S152 fast check. `finding_id not in references` was a
        # substring test, safe only while every id was exactly two digits;
        # widening made -F10 a prefix of -F100, so a step closing a finding that
        # does not exist discharged an open one that does. The defect S136 and
        # S141 fixed for step ids, arriving one document over.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            stem = "2026-08-01_adversarial"
            audit_report(root, [(f"{stem}-F10", "open")])
            self.step(root, "S900", closes=f"{stem}-F100")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-10", result.stdout)
            self.assertIn(f"{stem}-F10", result.stdout)
            listing = run_moltke(root, "--audit", "list")
            self.assertIn(f"{stem}-F10  open  (no reference)", listing.stdout)

    def test_a_hidden_wide_finding_is_still_listed_as_hidden(self):
        # own_finding_headings reads the raw text with its own width; a fence
        # swallowing a -F100 left --audit list reporting a complete report.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            stem = "2026-08-01_adversarial"
            report = Path(root) / "adocs" / "audit" / f"{stem}.md"
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(f"# Audit\n\n```\n### {stem}-F100  high  swallowed\n\n"
                              f"Status: open\n```\n", encoding="utf-8")
            listing = run_moltke(root, "--audit", "list")
            self.assertIn(f"{stem}-F100  hidden", listing.stdout)

    def test_a_decision_heading_may_carry_ordinary_punctuation(self):
        # The S152 fast check again: matching the id against the whole token
        # made `## DEC-061: title` a violation, and INV-9 is a cheap check, so
        # an agent writing that heading wedged its own Stop gate. Emphasis and a
        # second space were skipped entirely, which is the blindness next door.
        for heading in ("DEC-061: with a colon", "DEC-061, and a comma",
                        "DEC-061/DEC-062  a merged pair", "**DEC-061** emphasised",
                        " DEC-061  an extra space"):
            with tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                self.decisions(root, heading)
                result = run_moltke(root, "--validate")
                self.assertEqual(result.returncode, 0, (heading, result.stdout))

    def test_the_id_is_still_read_out_of_a_punctuated_heading(self):
        # Non-vacuity for the tolerance above: tolerating the punctuation must
        # not mean skipping the entry, which is what it replaced.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.decisions(root, "DEC-061: first", "**DEC-061** duplicate")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("duplicate decision id DEC-061", result.stdout)

    def test_a_wide_finding_id_still_has_to_carry_its_own_report_name(self):
        # Widening the read does not widen what is accepted: INV-10's stem rule
        # is what a newly visible id now gets checked against.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-07-01_adversarial-F100", "closed")])
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("2026-07-01_adversarial-F100", result.stdout)


if __name__ == "__main__":
    unittest.main()
