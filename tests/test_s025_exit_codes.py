"""S025 (F06): the exit code and stream of every outcome kind.

README and MANUAL documented one rule — exit 1 with violations on stdout — and it
held for two modes out of eleven, because `refuse` prints to stderr and returns 1
for every refusal path. The documentation now states the real mapping; this pins
it, so the two cannot drift apart again without a test going red.

AGENTS.md section 7: a doc claim is a claim about code. This file is where that
claim is checked.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import audit_report, step_file, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"


def run_moltke(cwd, *args, stdin="{}"):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=cwd, capture_output=True, text=True, input=stdin,
    )


class TestFindingsGoToStdout(unittest.TestCase):
    """run_validate, audit_list, audit_check: exit 1, message on stdout."""

    def assert_findings(self, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(result.stdout.strip(), "findings must reach stdout")
        self.assertFalse(result.stderr.strip(),
                         f"findings must not go to stderr, got {result.stderr!r}")

    def test_validate_violations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_todo", "S009", "orphan")  # INV-3
            self.assert_findings(run_moltke(root, "--validate"))

    def test_audit_list_unreferenced_open_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "open")])
            self.assert_findings(run_moltke(root, "--audit", "list"))


class TestRefusalsGoToStderr(unittest.TestCase):
    """refuse(): exit 1, message on stderr. Same code, other stream — which is
    the whole point of documenting the mapping rather than one rule."""

    def assert_refusal(self, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(result.stderr.strip(), "a refusal must say why, on stderr")
        self.assertFalse(result.stdout.strip(),
                         f"a refusal must not go to stdout, got {result.stdout!r}")

    def test_step_transition_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.assert_refusal(run_moltke(root, "--step", "start", "S999"))

    def test_unknown_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.assert_refusal(run_moltke(root, "--audit", "nonsense"))

    def test_audit_check_without_a_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.assert_refusal(run_moltke(root, "--audit", "check"))

    def test_a_failing_test_command_gate(self):
        # S042 (F11): the one refusal path absent from this class, and the one
        # that would have failed its assertion — the gate printed its banner to
        # stdout while refusing on stderr. A test that states a rule and omits
        # the case that breaks it is not covering the rule.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            marker = json.loads((root / ".moltke.json").read_text(encoding="utf-8"))
            marker["test_command"] = f"{sys.executable} -c \"raise SystemExit(3)\""
            (root / ".moltke.json").write_text(json.dumps(marker, indent=2) + "\n",
                                               encoding="utf-8")
            testing = root / "adocs" / "testing.md"
            testing.write_text(testing.read_text(encoding="utf-8")
                               + "| S003 | works | manual | pass |\n", encoding="utf-8")
            self.assert_refusal(run_moltke(
                root, "--step", "done", "S003",
                "--stamp", "2026-08-07 suite green; README and MANUAL checked"))


class TestBlocksGoToStderr(unittest.TestCase):
    """Hook refusals: exit 2, reason on stderr."""

    def assert_block(self, result):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertTrue(result.stderr.strip(), "a block must state what to do, on stderr")

    def test_pre_write_into_plan_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.assert_block(run_moltke(root, "--pre-write", "adocs/plan_done/S001_base.md"))

    def test_post_write_returns_two_but_is_non_blocking_by_contract(self):
        # Documented as such because the tool it follows has already run; the
        # exit code only surfaces the text.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_todo", "S009", "orphan")
            self.assert_block(run_moltke(root, "--post-write"))


class TestCleanPathsAreQuietAndZero(unittest.TestCase):
    """Non-vacuity anchor: without this, every assertion above could be passing
    on a tool that fails no matter what it is given."""

    def test_validate_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(result.stderr.strip())

    def test_stderr_can_carry_a_warning_on_a_zero_exit(self):
        # Documented, because it breaks the "stderr means failure" assumption a
        # script would otherwise make: no git worktree, so --audit new warns that
        # --audit check cannot reconcile the run, and still succeeds.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--audit", "new", "probe")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("--audit check", result.stderr)


class TestAuditFollowsTheDocumentedTable(unittest.TestCase):
    """S076 (2026-08-08_adversarial.2-F10): the S060 backstop returned
    EXIT_BLOCK for --audit, which README's table assigns to the three hook modes
    only, and reported a failed write as "could not read the repository" with a
    remedy that had nothing to do with it. mode_step already had its own
    handler; mode_audit did not."""

    def test_a_failed_audit_write_refuses_on_stderr_with_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_dir = root / "adocs" / "audit"
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_dir.chmod(0o555)
            try:
                result = run_moltke(root, "--audit", "new", "adversarial")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "", "a refusal belongs on stderr")
                self.assertIn("write", result.stderr.lower(),
                              "a failed write must not be reported as a read")
            finally:
                audit_dir.chmod(0o755)

    def test_a_failed_audit_read_refuses_rather_than_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            report = audit_report(root, [("2026-08-01_adversarial-F01", "accepted")])
            report.chmod(0o000)
            try:
                result = run_moltke(root, "--audit", "list")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
            finally:
                report.chmod(0o644)

    def test_the_ordinary_audit_paths_are_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.assertEqual(run_moltke(root, "--audit", "new", "adversarial").returncode, 0)
            self.assertEqual(run_moltke(root, "--audit", "list").returncode, 0)


class TestRoadmapExitsAsDocumented(unittest.TestCase):
    """S086 (2026-08-08_adversarial.3-F07): specs says "Exit 0 always" for
    --roadmap and both exit tables reserve 2 for the three hook modes, while an
    unreadable path returned the backstop's 2. .2-F10 was the same defect for
    --audit; this is its twin, and AGENTS.md tells every agent to end a unit of
    work by running this mode."""

    def test_an_unreadable_plan_does_not_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            plan = root / "adocs" / "plan.md"
            plan.chmod(0o000)
            try:
                result = run_moltke(root, "--roadmap")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("plan.md", result.stdout + result.stderr)
            finally:
                plan.chmod(0o644)

    def test_the_ordinary_roadmap_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--roadmap")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("S001", result.stdout)


if __name__ == "__main__":
    unittest.main()
