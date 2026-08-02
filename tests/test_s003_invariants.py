"""S003: INV-1..INV-7 against broken fixture repositories."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import step_file, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"


def run_validate(cwd):
    return subprocess.run(
        [sys.executable, str(MOLTKE), "--validate"],
        cwd=cwd, capture_output=True, text=True,
    )


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        capture_output=True, text=True, check=True,
    )


class TestInvariants(unittest.TestCase):
    def assert_violation(self, root, needle):
        result = run_validate(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(needle, result.stdout)

    def test_valid_tree_passes(self):
        # Non-vacuity anchor: every broken variant below starts from this tree.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv1_too_many_non_paused_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S004", "second")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            self.assert_violation(root, "INV-1")

    def test_inv1_paused_steps_do_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S004", "paused_parent",
                      paused_by="S003")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv2_stack_depth_exceeded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            current = root / "adocs" / "plan_current"
            for step_id in ("S004", "S005", "S006"):
                step_file(current, step_id, "paused", paused_by="S003")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001\n2. S002\n3. S003\n4. S004\n5. S005\n6. S006\n",
                encoding="utf-8")
            self.assert_violation(root, "INV-2")

    def test_inv3_step_missing_from_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_todo", "S009", "orphan")
            self.assert_violation(root, "INV-3")

    def test_inv4_done_step_still_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_todo", "S002", "pending", blocks="S001")
            self.assert_violation(root, "INV-4")

    def test_inv5_done_step_without_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_done", "S001", "base", done="")
            self.assert_violation(root, "INV-5")

    def test_inv5_done_step_without_testing_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "testing.md").write_text(
                "# Testing ledger\n\n| Step | Criterion | Test | Result |\n|---|---|---|---|\n",
                encoding="utf-8")
            self.assert_violation(root, "INV-5")

    def test_inv6_duplicate_step_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_todo", "S003", "dupe")
            self.assert_violation(root, "INV-6")

    def test_inv7_modified_done_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            done = root / "adocs" / "plan_done" / "S001_base.md"
            done.write_text(done.read_text(encoding="utf-8") + "tampered\n",
                            encoding="utf-8")
            self.assert_violation(root, "INV-7")

    def test_inv7_deleted_done_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            (root / "adocs" / "plan_done" / "S001_base.md").unlink()
            self.assert_violation(root, "INV-7")

    def test_inv7_added_done_step_is_allowed(self):
        # Append by move only: additions are the one legal change.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            (root / "adocs" / "plan_current" / "S003_active.md").unlink()
            step_file(root / "adocs" / "plan_done", "S003", "active",
                      done="2026-08-01 done")
            (root / "adocs" / "testing.md").write_text(
                (root / "adocs" / "testing.md").read_text(encoding="utf-8")
                + "| S003 | active works | manual | pass |\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
