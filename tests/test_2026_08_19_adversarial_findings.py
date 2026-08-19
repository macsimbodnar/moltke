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
"""

import json
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


if __name__ == "__main__":
    unittest.main()
