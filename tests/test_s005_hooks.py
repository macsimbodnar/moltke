"""S005: hook modes. Contract verified against live docs on 2026-08-01:
UserPromptSubmit exit 2 erases the prompt, so --log-prompt must always exit 0;
SessionStart context reaches Claude only via hookSpecificOutput JSON;
Stop has no documented block cap, so moltke imposes its own.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import step_file, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"


def run_moltke(cwd, *args, stdin=""):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=cwd, capture_output=True, text=True, input=stdin,
    )


def git_baseline(root):
    for args in (("init", "-q"), ("add", "-A"), ("commit", "-qm", "base")):
        subprocess.run(
            ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
            capture_output=True, text=True, check=True,
        )


class TestLogPrompt(unittest.TestCase):
    def test_prompt_appended_with_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"prompt": "first line\nsecond line"})
            result = run_moltke(root, "--log-prompt", stdin=payload)
            self.assertEqual(result.returncode, 0, result.stderr)
            worklog = (root / "project" / "worklog.md").read_text(encoding="utf-8")
            self.assertIn("> first line", worklog)
            self.assertIn("> second line", worklog)
            self.assertIn("2026-", worklog.split("> first line")[0].rsplit("##", 1)[-1])

    def test_never_blocks_even_on_bad_input(self):
        # Exit 2 would erase the user's prompt; logging must fail open.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--log-prompt", stdin="not json at all")
            self.assertEqual(result.returncode, 0, result.stderr)


class TestPreWrite(unittest.TestCase):
    def test_blocks_writes_under_plan_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-write", "project/plan_done/S001_base.md")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("plan_done", result.stderr)

    def test_blocks_step_files_outside_plan_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-write", "src/S099_rogue.md")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("S099", result.stderr)

    def test_allows_ordinary_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for path in ("src/main.py", "project/plan_todo/S009_new.md", "project/status.md"):
                result = run_moltke(root, "--pre-write", path)
                self.assertEqual(result.returncode, 0, (path, result.stderr))

    def test_reads_path_from_hook_stdin_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps(
                {"tool_input": {"file_path": str(root / "project" / "plan_done" / "S001_base.md")}})
            result = run_moltke(root, "--pre-write", stdin=payload)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class TestSessionStart(unittest.TestCase):
    def test_reports_stack_and_derived_next(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--session-start")
            self.assertEqual(result.returncode, 0, result.stderr)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("S003", context)  # active stack
            self.assertIn("S002", context)  # derived next

    def test_flags_stale_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "project" / "status.md").write_text(
                "# Status\n\n- Next: S001\n", encoding="utf-8")
            result = run_moltke(root, "--session-start")
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("stale", context.lower())


class TestPostWrite(unittest.TestCase):
    def test_clean_repo_passes_silently(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--post-write")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_violation_surfaces_without_blocking_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "project" / "plan_todo", "S003", "dupe")
            result = run_moltke(root, "--post-write")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("INV-6", result.stderr)


class TestStop(unittest.TestCase):
    def test_clean_repo_allows_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_blocks_on_invariant_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            step_file(root / "project" / "plan_todo", "S003", "dupe")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("INV-6", result.stderr)

    def test_blocks_on_stale_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "project" / "status.md").write_text(
                "# Status\n\n- Next: S001\n", encoding="utf-8")
            git_baseline(root)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("status.md", result.stderr)

    def test_blocks_source_change_without_recap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("recap", result.stderr)

    def test_recap_unblocks_source_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            worklog = root / "project" / "worklog.md"
            worklog.write_text(worklog.read_text(encoding="utf-8")
                               + "\n## 2026-08-01 recap S003\n\n- did things\n",
                               encoding="utf-8")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_block_cap_prevents_deadlock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            step_file(root / "project" / "plan_todo", "S003", "dupe")
            payload = json.dumps({"prompt_id": "p1"})
            for _ in range(3):
                result = run_moltke(root, "--stop", stdin=payload)
                self.assertEqual(result.returncode, 2, result.stderr)
            result = run_moltke(root, "--stop", stdin=payload)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
