"""S004: INV-8..INV-10 against broken fixture repositories."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import audit_report, step_file, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"


def run_validate(cwd):
    return subprocess.run(
        [sys.executable, str(MOLTKE), "--validate"],
        cwd=cwd, capture_output=True, text=True,
    )


def git_baseline(root):
    for args in (("init", "-q"), ("add", "-A"), ("commit", "-qm", "base")):
        subprocess.run(
            ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
            capture_output=True, text=True, check=True,
        )


class TestAppendOnly(unittest.TestCase):
    """INV-8: worklog.md and decisions.md grow only at the end."""

    def assert_violation(self, root, needle):
        result = run_validate(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(needle, result.stdout)

    def test_appending_is_legal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            for rel in ("adocs/decisions.md", "adocs/worklog.md"):
                path = root / rel
                path.write_text(path.read_text(encoding="utf-8") + "\nappended\n",
                                encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rewriting_decisions_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            path = root / "adocs" / "decisions.md"
            path.write_text(path.read_text(encoding="utf-8").replace("base decision",
                            "edited decision"), encoding="utf-8")
            self.assert_violation(root, "INV-8")

    def test_rewriting_worklog_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "adocs" / "worklog.md").write_text("# Worklog\n(trimmed)\n",
                                                         encoding="utf-8")
            self.assert_violation(root, "INV-8")

    def test_deleting_append_only_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "adocs" / "decisions.md").unlink()
            self.assert_violation(root, "INV-8")


class TestDecisionIds(unittest.TestCase):
    """INV-9: every decisions.md entry has a unique DEC id."""

    def test_duplicate_dec_id_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            path = root / "adocs" / "decisions.md"
            path.write_text(path.read_text(encoding="utf-8")
                            + "\n## DEC-001  2026-08-01  duplicate\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("INV-9", result.stdout)


class TestAuditFindings(unittest.TestCase):
    """INV-10: finding statuses are valid; open findings are referenced."""

    def test_valid_statuses_pass_when_referenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "planned"),
                                ("2026-08-01_adversarial-F02", "accepted")])
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_status_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "wontfix")])
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("INV-10", result.stdout)

    def test_open_finding_without_reference_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "open")])
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("INV-10", result.stdout)

    def test_open_finding_with_closing_step_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "open")])
            step_file(root / "adocs" / "plan_todo", "S004", "fix_finding",
                      closes="2026-08-01_adversarial-F01")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001\n2. S002\n3. S003\n4. S004\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
