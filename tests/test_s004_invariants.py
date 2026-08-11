"""S004: INV-8..INV-10 against broken fixture repositories."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import audit_report, step_file, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"
REPO = MOLTKE.parent.parent


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


def git_baseline(root):
    for args in (("init", "-q"), ("add", "-A"), ("commit", "-qm", "base")):
        git(root, *args)


class TestHistoryIsUnenforced(unittest.TestCase):
    """S105 (DEC-042): INV-8 is retired and its number is never reused. The
    documents hold current state; history lives in git. Rewriting or trimming
    decisions.md and the worklog is an ordinary edit, because the always-read
    set must be able to shrink — the enforcement was what made it unshrinkable."""

    def test_rewriting_decisions_is_not_a_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            path = root / "adocs" / "decisions.md"
            path.write_text(path.read_text(encoding="utf-8").replace(
                "base decision", "rewritten decision"), encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_trimming_decisions_is_not_a_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            path = root / "adocs" / "decisions.md"
            kept = [l for l in path.read_text(encoding="utf-8").splitlines()
                    if "Rejected" not in l]
            path.write_text("\n".join(kept) + "\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "consolidate decisions")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validate_never_mentions_inv_8(self):
        # The number is retired, not reassigned: no current check may report
        # under it, or a reader of an old audit report is pointed at the wrong
        # rule.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            for rel in ("adocs/decisions.md", "adocs/worklog.md"):
                (root / rel).write_text("rewritten wholesale\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("INV-8", result.stdout + result.stderr)

    def test_plan_done_immutability_is_untouched(self):
        # The non-vacuity anchor for the retirement: INV-7 still fires, so the
        # suite can tell "INV-8 retired" from "history checks broke".
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            done = root / "adocs" / "plan_done" / "S001_base.md"
            done.write_text(done.read_text(encoding="utf-8") + "tampered\n",
                            encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-7", result.stdout)


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


class TestWhichCommitTheViolationNames(unittest.TestCase):
    """S065 (2026-08-08_adversarial-F06): MANUAL said the violation "names the
    commit that did it". It names the commit it compares against — the one that
    added the plan_done/ file, or the high-water mark for decisions.md — and the
    tampering commit appears nowhere. A reader told otherwise runs `git show` on
    the legitimate commit that first added the file. The sentence had survived
    being named in two consecutive audits, so the claim gets a test."""

    def test_the_message_names_the_baseline_and_not_the_tampering_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            baseline = git(root, "rev-parse", "--short=8", "HEAD").stdout.strip()
            (root / "README.md").write_text("unrelated\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "unrelated work in between")
            done = root / "adocs" / "plan_done" / "S001_base.md"
            done.write_text(done.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "tamper")
            tampering = git(root, "rev-parse", "--short=8", "HEAD").stdout.strip()
            self.assertNotEqual(baseline, tampering)
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-7", result.stdout)
            self.assertIn(baseline, result.stdout)
            self.assertNotIn(tampering, result.stdout,
                             "the tampering commit is not something moltke identifies")

    def test_the_manual_does_not_claim_otherwise(self):
        manual = (REPO / "MANUAL.md").read_text(encoding="utf-8")
        self.assertNotIn("names the commit that did it", manual)
        self.assertIn("not the commit that", manual,
                      "MANUAL must say which commit is named, since the two differ")


if __name__ == "__main__":
    unittest.main()
