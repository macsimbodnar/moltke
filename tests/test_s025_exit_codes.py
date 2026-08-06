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

    def test_log_prompt_never_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": "hi"}))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stderr_can_carry_a_warning_on_a_zero_exit(self):
        # Documented, because it breaks the "stderr means failure" assumption a
        # script would otherwise make: no git worktree, so --audit new warns that
        # --audit check cannot reconcile the run, and still succeeds.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--audit", "new", "probe")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("--audit check", result.stderr)
