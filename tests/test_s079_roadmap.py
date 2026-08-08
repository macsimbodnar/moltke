"""S079 (DEC-038): --roadmap prints where the plan is, as one timeline strip.

Derived from plan.md order and the three plan directories, never from
status.md — the prime directive applied to the tool's own output, so the view
cannot say something the repository does not.
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import marked_repo, step_file, workflow_repo
from surface import moltke

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"


def run_moltke(cwd, *args):
    return subprocess.run([sys.executable, str(MOLTKE), *args],
                          cwd=cwd, capture_output=True, text=True, input="")


def roadmap(cwd):
    result = run_moltke(cwd, "--roadmap")
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


class TestTheStrip(unittest.TestCase):
    def test_it_names_the_first_and_last_planned_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = roadmap(workflow_repo(tmp))
            self.assertIn("S001", out)
            self.assertIn("S003", out)

    def test_it_counts_done_and_left_from_the_filesystem(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)          # S001 done, S003 current, S002 todo
            out = roadmap(root)
            self.assertIn("1 done", out)
            self.assertIn("2 left", out)

    def test_status_md_cannot_change_what_it_says(self):
        # The whole reason this is a mode and not a paragraph an agent writes:
        # it reads the same filesystem every check reads.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            before = roadmap(root)
            (root / "adocs" / "status.md").write_text(
                "# Status\n\n- Last done: S999\n- In progress: everything\n"
                "- Next: nothing\n- Blocked: none\n- Parked:\n", encoding="utf-8")
            self.assertEqual(roadmap(root), before)

    def test_the_current_step_is_named_beneath(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            out = roadmap(root)
            self.assertRegex(out, r"now\s+S003\s+active")

    def test_the_derived_next_step_is_named_when_nothing_is_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for entry in (root / "adocs" / "plan_current").iterdir():
                entry.rename(root / "adocs" / "plan_todo" / entry.name)
            out = roadmap(root)
            self.assertRegex(out, r"next\s+S002")
            self.assertNotIn("now ", out)

    def test_a_finished_plan_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for name in ("plan_todo", "plan_current"):
                for entry in (root / "adocs" / name).iterdir():
                    entry.rename(root / "adocs" / "plan_done" / entry.name)
            out = roadmap(root)
            self.assertIn("3 done", out)
            self.assertNotIn("now ", out)
            self.assertIn("nothing left", out)

    def test_a_repository_with_no_steps_says_so_rather_than_drawing_an_empty_bar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = marked_repo(tmp)
            docs = root / "adocs"
            docs.mkdir()
            (docs / "plan.md").write_text("# Plan\n\nNothing planned yet.\n", encoding="utf-8")
            out = roadmap(root)
            self.assertIn("no steps planned yet", out)
            self.assertNotIn("░", out)


class TestItStaysOneLine(unittest.TestCase):
    """A strip that grows with the plan stops being a strip."""

    def build(self, tmp, count, done):
        root = marked_repo(tmp)
        docs = root / "adocs"
        docs.mkdir()
        ids = [f"S{n:03d}" for n in range(1, count + 1)]
        (docs / "plan.md").write_text(
            "# Plan\n\n" + "".join(f"{n}. {sid} step\n" for n, sid in enumerate(ids, 1)),
            encoding="utf-8")
        for index, sid in enumerate(ids):
            where = "plan_done" if index < done else "plan_todo"
            step_file(docs / where, sid, "step", **({"done": "2026-08-01 done"}
                                                    if where == "plan_done" else {}))
        return root

    def strip_line(self, out):
        return next(line for line in out.splitlines() if "▏" in line)

    def test_a_long_plan_buckets_instead_of_widening(self):
        with tempfile.TemporaryDirectory() as tmp:
            short = self.strip_line(roadmap(self.build(tmp, 12, 6)))
        with tempfile.TemporaryDirectory() as tmp:
            long = self.strip_line(roadmap(self.build(tmp, 400, 200)))
        self.assertLessEqual(len(long), 80, long)
        self.assertGreaterEqual(len(long), len(short) - 2,
                                "a 400-step plan must still fill the strip")

    def test_a_bucket_holding_unfinished_work_reads_unfinished(self):
        # The honest direction: a cell covering several steps is only done when
        # all of them are, so the bar never claims more progress than there is.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.build(tmp, 400, 399)
            self.assertIn("░", self.strip_line(roadmap(root)),
                          "399 of 400 done must not render as a full bar")

    def test_every_line_is_narrow_enough_for_a_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = roadmap(self.build(tmp, 400, 200))
            for line in out.splitlines():
                self.assertLessEqual(len(line), 100, line)


class TestItIsPartOfTheSurface(unittest.TestCase):
    def test_the_mode_is_declared(self):
        self.assertIn("--roadmap", moltke.build_parser().format_usage())

    def test_it_is_silent_in_an_unmarked_repository(self):
        # INV-11: no marker, no friction.
        with tempfile.TemporaryDirectory() as tmp:
            result = run_moltke(tmp, "--roadmap")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
