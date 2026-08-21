"""S158: the reviewer fence's two dating gaps, both shipped in 0.13.0.

Red first (AGENTS.md §6). The fence dates a file against the baseline
`--audit new` records, and that baseline records only that a run *started*.

- Nothing recorded that one ended, so a reviewer spawned later — no
  `--audit new`, so no baseline of its own — was dated against a finished
  run's record and could overwrite that run's report by name, against "add
  files, never overwrite a report" (AGENTS.md §2).
- A file git cannot see at all was read as older than the run. A `tests/`
  path under `.gitignore` is absent from `git status --porcelain -uall`
  whoever wrote it, so the fence refused it as "was here before this run"
  when this run wrote it — and the correction goes to `Bash`, where nothing
  is fenced, which is exactly the F11 harm arriving through another door.

The third case S158's `accepts` inherited from its triage is not a gap, and
is anchored here rather than fixed: `worktree_state` records a recreated
rename source's own untracked line ahead of its departure, on purpose and
with a docstring saying so, so it dates as new and is permitted. That test
was green when written (S155 fast check).
"""

import datetime
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import workflow_repo
from surface import REPO

MOLTKE = REPO / "bin" / "moltke.py"
TODAY = datetime.date.today().isoformat()
SCOPED_REVIEWER = "moltke:adversarial_reviewer"


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


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class FenceCase(unittest.TestCase):
    def fence(self, root, path):
        payload = json.dumps({"agent_type": SCOPED_REVIEWER,
                              "tool_input": {"file_path": path}})
        return run_moltke(root, "--pre-write", stdin=payload)

    def opened_run(self, tmp, extra=()):
        """A committed repository with a fresh audit run opened over it."""
        root = workflow_repo(tmp)
        write(root, "src/main.py", "print('source')\n")
        for rel, text in extra:
            write(root, rel, text)
        git_baseline(root)
        opened = run_moltke(root, "--audit", "new", "adversarial")
        self.assertEqual(opened.returncode, 0, opened.stdout + opened.stderr)
        return root


class TestTheFenceKnowsWhenARunEnded(FenceCase):
    """`--audit check` is the documented end of a run — MANUAL and the audit
    skill both say to run it after the reviewer returns — and until S158 it
    left no trace, so the baseline said "a run started here" forever.
    """

    def ended_run(self, tmp):
        root = self.opened_run(tmp)
        check = run_moltke(root, "--audit", "check")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        return root

    def test_the_report_of_an_ended_run_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.ended_run(tmp)
            result = self.fence(root, f"adocs/audit/{TODAY}_adversarial.md")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_the_refusal_says_to_open_a_run_of_ones_own(self):
        # The message, not just the code: a reviewer told only "no" writes the
        # report through Bash instead, which is the failure F11 was about.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.ended_run(tmp)
            result = self.fence(root, f"adocs/audit/{TODAY}_adversarial.md")
            self.assertIn("--audit new", result.stderr)

    def test_the_report_is_still_writable_while_the_run_is_live(self):
        # Non-vacuity: the reviewer writes its report many times, and the only
        # thing separating this from the refusal above is the check in between.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.opened_run(tmp)
            result = self.fence(root, f"adocs/audit/{TODAY}_adversarial.md")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_an_ended_run_no_longer_dates_a_test_as_its_own(self):
        # The other half of ending: a finished run's snapshot cannot say that
        # this reviewer wrote the file, only that it was not there when some
        # earlier run opened. An existing test falls back to being a patch.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.opened_run(tmp)
            write(root, "tests/test_from_the_run.py", "# written by the run\n")
            live = self.fence(root, "tests/test_from_the_run.py")
            self.assertEqual(live.returncode, 0, live.stdout + live.stderr)
            check = run_moltke(root, "--audit", "check")
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            after = self.fence(root, "tests/test_from_the_run.py")
            self.assertEqual(after.returncode, 2, after.stdout + after.stderr)

    def test_a_new_run_over_an_ended_one_dates_against_itself(self):
        # Non-vacuity for every refusal above: ending a run must not wedge the
        # next one. `--audit new` records a fresh baseline, and its report and
        # its new tests are writable again.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.ended_run(tmp)
            opened = run_moltke(root, "--audit", "new", "adversarial")
            self.assertEqual(opened.returncode, 0, opened.stdout + opened.stderr)
            write(root, "tests/test_second_run.py", "# written by the second run\n")
            for path in (f"adocs/audit/{TODAY}_adversarial.2.md",
                         "tests/test_second_run.py"):
                result = self.fence(root, path)
                self.assertEqual(result.returncode, 0, (path, result.stderr))
            # And the first run's report is still evidence, now for two reasons.
            refused = self.fence(root, f"adocs/audit/{TODAY}_adversarial.md")
            self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)

    def test_the_end_is_recorded_where_the_baseline_is(self):
        # §11: watch state is derivable from the filesystem and so is this. The
        # record lives in the git directory beside the baseline it belongs to,
        # not in a session's memory.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.ended_run(tmp)
            record = Path(root) / ".git" / "moltke_audit_baseline.json"
            saved = json.loads(record.read_text(encoding="utf-8"))
            self.assertTrue(saved.get("ended"),
                            f"nothing in {record.name} says the run ended: {saved}")


class TestTheFenceDoesNotDateWhatGitCannotSee(FenceCase):
    """An ignored path is in neither snapshot for the same reason at both ends,
    so subtracting them says "was here before this run" about a file that has
    never been visible to git at all.
    """

    IGNORE = "tests/test_ignored.py\n"

    def test_an_ignored_test_this_run_wrote_is_not_called_older_than_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.opened_run(tmp, extra=[(".gitignore", self.IGNORE)])
            write(root, "tests/test_ignored.py", "# written by this run\n")
            result = self.fence(root, "tests/test_ignored.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_visible_test_that_predates_the_run_is_still_a_patch(self):
        # Non-vacuity: the widening is "git cannot see it", not "it is under
        # tests/". An untracked file the run merely found stays refused.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.opened_run(tmp, extra=[(".gitignore", self.IGNORE)])
            write(root, "tests/test_someone_elses.py", "# uncommitted, predates the run\n")
            # Written after --audit new, so only the baseline separates it from
            # the permitted case above.
            git(root, "add", "tests/test_someone_elses.py")
            git(root, "commit", "-qm", "someone else's test")
            result = self.fence(root, "tests/test_someone_elses.py")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_a_tracked_file_matching_an_ignore_pattern_is_still_visible(self):
        # git ignores patterns for tracked files, and so must this: a report
        # committed under a pattern that would otherwise hide it is evidence,
        # and overwriting it is the thing the fence exists to refuse.
        with tempfile.TemporaryDirectory() as tmp:
            # The pattern lands after the report is committed: `git add -A`
            # skips an ignored path, so writing both at once would leave the
            # report untracked and prove nothing about the index.
            root = self.opened_run(tmp, extra=[
                ("adocs/audit/2026-01-01_adversarial.md", "# an earlier run\n")])
            write(root, ".gitignore", "adocs/audit/2026-01-01_adversarial.md\n")
            git(root, "add", ".gitignore")
            git(root, "commit", "-qm", "ignore the earlier report")
            self.assertIn("adocs/audit/2026-01-01_adversarial.md",
                          git(root, "ls-files").stdout, "fixture: the report must be tracked")
            result = self.fence(root, "adocs/audit/2026-01-01_adversarial.md")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("never overwritten", result.stderr)

    def test_an_ignored_path_outside_both_directories_is_still_refused(self):
        # Invisibility is not a way out of the fence: it decides *when* a file
        # arrived, and `bin/` is refused on *where* it is, before any dating.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.opened_run(tmp, extra=[(".gitignore", "src/ignored.py\n")])
            write(root, "src/ignored.py", "# invisible and out of bounds\n")
            result = self.fence(root, "src/ignored.py")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class TestARecreatedRenameSourceIsPermitted(FenceCase):
    """Not a gap, and green when written. S158's `accepts` named this as a
    second red test, inherited from triage; the S155 fast check verified
    against the code that `worktree_state` lets a recreated source's own
    untracked line beat its departure, so it dates as new.
    """

    def test_a_rename_source_the_run_recreated_is_permitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.opened_run(tmp, extra=[("tests/test_moved.py", "# tracked\n")])
            git(root, "mv", "tests/test_moved.py", "tests/test_destination.py")
            write(root, "tests/test_moved.py", "# recreated by this run\n")
            result = self.fence(root, "tests/test_moved.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
