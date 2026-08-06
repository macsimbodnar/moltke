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

from fixtures import marked_repo, step_file, workflow_repo

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
            worklog = (root / "adocs" / "worklog.md").read_text(encoding="utf-8")
            self.assertIn("> first line", worklog)
            self.assertIn("> second line", worklog)
            self.assertIn("2026-", worklog.split("> first line")[0].rsplit("##", 1)[-1])

    def test_never_blocks_even_on_bad_input(self):
        # Exit 2 would erase the user's prompt; logging must fail open.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--log-prompt", stdin="not json at all")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_prompt_survives_a_missing_docs_directory(self):
        # S014 (F14): append mode does not create adocs/, so a marked repo
        # without it discarded every prompt on a zero exit.
        with tempfile.TemporaryDirectory() as tmp:
            root = marked_repo(tmp)
            result = run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": "kept"}))
            self.assertEqual(result.returncode, 0, result.stderr)
            worklog = root / "adocs" / "worklog.md"
            self.assertTrue(worklog.is_file(), f"prompt lost: {worklog} was never created")
            self.assertIn("> kept", worklog.read_text(encoding="utf-8"))


def break_worklog(root):
    """Make the append fail for a reason no privilege level can bypass: a
    directory where the file belongs raises IsADirectoryError, while chmod 0
    is ignored when the suite runs as root."""
    worklog = root / "adocs" / "worklog.md"
    worklog.unlink()
    worklog.mkdir()
    return worklog


def session_context(root):
    result = run_moltke(root, "--session-start")
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


class TestLogPromptFailureIsLoud(unittest.TestCase):
    """S014: UserPromptSubmit must exit 0, so stderr reaches nobody. A swallowed
    append has to surface through SessionStart's additionalContext instead."""

    def test_failed_append_is_reported_at_session_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)  # the breadcrumb lives in .git/
            worklog = break_worklog(root)
            result = run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": "lost"}))
            self.assertEqual(result.returncode, 0, result.stderr)
            # Precondition first: without an actual failure the report below
            # would prove nothing (AGENTS.md §6, non-vacuous by construction).
            self.assertEqual(list(worklog.iterdir()), [], "the append unexpectedly succeeded")
            context = session_context(root)
            self.assertIn("not appended", context)
            self.assertIn("worklog.md", context)

    def test_report_stops_once_the_failure_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            break_worklog(root)
            run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": "lost"}))
            self.assertIn("not appended", session_context(root))
            self.assertNotIn("not appended", session_context(root))

    def test_a_healthy_append_reports_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": "fine"}))
            self.assertNotIn("not appended", session_context(root))


class TestPreWrite(unittest.TestCase):
    def test_blocks_writes_under_plan_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-write", "adocs/plan_done/S001_base.md")
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
            for path in ("src/main.py", "adocs/plan_todo/S009_new.md", "adocs/status.md"):
                result = run_moltke(root, "--pre-write", path)
                self.assertEqual(result.returncode, 0, (path, result.stderr))

    def test_reads_path_from_hook_stdin_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps(
                {"tool_input": {"file_path": str(root / "adocs" / "plan_done" / "S001_base.md")}})
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
            (root / "adocs" / "status.md").write_text(
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
            step_file(root / "adocs" / "plan_todo", "S003", "dupe")
            result = run_moltke(root, "--post-write")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("INV-6", result.stderr)


def log_prompt(root, text="a prompt"):
    """S015: every Stop fixture logs a prompt first, because UserPromptSubmit
    always has. A Stop test that skips this states a precondition no live
    session ever has (F01)."""
    result = run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": text}))
    assert result.returncode == 0, result.stderr
    return result


def append_recap(root, heading="## 2026-08-01 recap S003"):
    worklog = root / "adocs" / "worklog.md"
    worklog.write_text(worklog.read_text(encoding="utf-8") + f"\n{heading}\n\n- did things\n",
                       encoding="utf-8")


class TestStop(unittest.TestCase):
    def test_clean_repo_allows_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            log_prompt(root)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_blocks_on_invariant_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            log_prompt(root)
            step_file(root / "adocs" / "plan_todo", "S003", "dupe")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("INV-6", result.stderr)

    def test_blocks_on_stale_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "status.md").write_text(
                "# Status\n\n- Next: S001\n", encoding="utf-8")
            git_baseline(root)
            log_prompt(root)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("status.md", result.stderr)

    def test_blocks_source_change_without_recap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            log_prompt(root)  # the growth the old size comparison mistook for a recap
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("recap", result.stderr)

    def test_recap_unblocks_source_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            log_prompt(root)
            append_recap(root)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_recap_older_than_the_last_prompt_does_not_count(self):
        # A recap discharges the turn it belongs to, not every later one.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            log_prompt(root, "first prompt")
            append_recap(root)
            log_prompt(root, "second prompt")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("recap", result.stderr)

    def test_recap_inside_a_fenced_block_does_not_count(self):
        # Guidance is never data (specs, S008): a recap heading quoted inside a
        # code fence is an example, not a recap.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            log_prompt(root)
            append_recap(root, "```\n## 2026-08-01 recap S003\n```\n## not a heading")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("recap", result.stderr)

    def test_recap_about_prompts_is_still_a_recap(self):
        # This repo's own S014 recap heading ends in the word "prompt". Reading
        # it as a prompt heading would leave the turn looking unrecapped.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            log_prompt(root)
            append_recap(root, "## 2026-08-06 recap - S014 never lose a prompt")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_recap_gate_abstains_before_the_first_commit(self):
        # A repo with no HEAD has no history a recap would sit alongside, so a
        # fresh scaffold must not block. Precondition first: the same tree with
        # a commit behind it does block, or this proves nothing.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            log_prompt(root)
            self.assertEqual(run_moltke(root, "--stop", stdin="{}").returncode, 0,
                             "no commit yet: the recap gate must abstain")
            git_baseline(root)
            (root / "src" / "main.py").write_text("print('y')\n", encoding="utf-8")
            blocked = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(blocked.returncode, 2,
                             "with a commit behind it the same change must block")
            self.assertIn("recap", blocked.stderr)

    def test_block_cap_prevents_deadlock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            log_prompt(root)
            step_file(root / "adocs" / "plan_todo", "S003", "dupe")
            payload = json.dumps({"prompt_id": "p1"})
            for _ in range(3):
                result = run_moltke(root, "--stop", stdin=payload)
                self.assertEqual(result.returncode, 2, result.stderr)
            result = run_moltke(root, "--stop", stdin=payload)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
