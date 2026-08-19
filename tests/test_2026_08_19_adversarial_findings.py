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
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import marked_repo, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"

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


if __name__ == "__main__":
    unittest.main()
