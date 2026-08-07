"""S005: hook modes. Contract verified against live docs on 2026-08-01:
UserPromptSubmit exit 2 erases the prompt, so --log-prompt must always exit 0;
SessionStart context reaches Claude only via hookSpecificOutput JSON;
Stop has no documented block cap, so moltke imposes its own.
"""

import json
import re
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

    def test_a_relative_escape_into_plan_done_is_blocked(self):
        # S041: the plan_done and step-file rules read the same rel, so
        # normalising it has to cover them, not only the reviewer fence.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for path in ("adocs/plan_todo/../plan_done/S001_base.md",
                         "src/../adocs/plan_done/S001_base.md"):
                result = run_moltke(root, "--pre-write", path)
                self.assertEqual(result.returncode, 2, (path, result.stdout + result.stderr))
                self.assertIn("plan_done", result.stderr)

    def test_a_path_outside_the_repository_is_still_not_ours_to_police(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-write", "../elsewhere/notes.md")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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


class TestStatusStaleness(unittest.TestCase):
    """S039 (F08): only the Next: line was compared, and that is the one field
    the file and the filesystem rarely disagree about, because both derive it the
    same way. The in-progress stack is what a crashed session actually corrupts."""

    def stale_status(self, root, body):
        (root / "adocs" / "status.md").write_text(body, encoding="utf-8")

    def test_a_wrong_in_progress_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)  # S003 is in plan_current/
            self.stale_status(root, "# Status\n\n- Last done: S001\n- In progress: none\n"
                                    "- Next: S002\n- Blocked: none\n")
            context = session_context(root)
            self.assertIn("stale", context.lower())
            self.assertIn("In progress", context)

    def test_a_wrong_last_done_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.stale_status(root, "# Status\n\n- Last done: S999\n- In progress: S003 active\n"
                                    "- Next: S002\n- Blocked: none\n")
            self.assertIn("Last done", session_context(root))

    def test_stop_refuses_a_stale_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.stale_status(root, "# Status\n\n- Last done: S001\n- In progress: none\n"
                                    "- Next: S002\n- Blocked: none\n")
            git_baseline(root)
            log_prompt(root)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("status.md", result.stderr)

    def test_regenerating_clears_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.stale_status(root, "# Status\n\n- Last done: S999\n- In progress: none\n"
                                    "- Next: S002\n- Blocked: none\n")
            self.assertIn("stale", session_context(root).lower())
            run_moltke(root, "--step", "status")
            self.assertNotIn("stale", session_context(root).lower())

    def test_an_accurate_status_is_not_reported(self):
        # Non-vacuity: the fixture repo's own status.md must stay clean, or every
        # assertion above passes for the wrong reason.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "status")
            self.assertNotIn("stale", session_context(root).lower())

    def test_the_parked_block_and_the_date_are_the_humans_to_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "status")
            status = root / "adocs" / "status.md"
            text = status.read_text(encoding="utf-8")
            text = re.sub(r"^Updated:.*$", "Updated: some other day, by hand", text,
                          flags=re.M)
            status.write_text(text.rstrip("\n") + "\n  - a note nobody derived\n",
                              encoding="utf-8")
            self.assertNotIn("stale", session_context(root).lower())


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

    def test_which_paths_count_as_source(self):
        # S037 (F06): ".claude" was a bare prefix, so it also matched
        # .claude-plugin/plugin.json — the manifest whose version decides what
        # every installed copy of moltke executes, and the single
        # highest-consequence tracked file here — plus any future .claude* file.
        cases = [
            ("src/main.py", True),
            ("bin/moltke.py", True),
            (".claude-plugin/plugin.json", True),
            (".claude-plugin/marketplace.json", True),
            (".clauderc", True),
            (".claudefoo", True),
            (".claude/settings.json", False),
            ("adocs/specs.md", False),
            ("adocsfoo/notes.md", True),
        ]
        for path, blocks in cases:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                git_baseline(root)
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("changed\n", encoding="utf-8")
                log_prompt(root)
                result = run_moltke(root, "--stop", stdin="{}")
                self.assertEqual(result.returncode, 2 if blocks else 0,
                                 f"{path}: {result.stdout + result.stderr}")

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

    def test_block_cap_prevents_deadlock_in_a_linked_worktree(self):
        # S035 (F04): in a linked worktree .git is a file, so the state file had
        # nowhere to live and the cap never fired. INV-12 and DEC-006 make the
        # no-deadlock property an invariant, not a convenience.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            worktree = Path(tmp) / "linked"
            subprocess.run(["git", "-C", str(root), "worktree", "add", "-q", "-b", "wt",
                            str(worktree)], capture_output=True, text=True, check=True)
            self.assertTrue((worktree / ".git").is_file(),
                            "precondition: a linked worktree's .git is a file, not a directory")
            (worktree / "src").mkdir()
            (worktree / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")
            log_prompt(worktree)
            payload = json.dumps({"prompt_id": "p1"})
            codes = [run_moltke(worktree, "--stop", stdin=payload).returncode for _ in range(5)]
            self.assertEqual(codes, [2, 2, 2, 0, 0],
                             "the cap must fire in a worktree exactly as it does in a clone")

    def broken_repo(self, tmp):
        root = workflow_repo(tmp)
        git_baseline(root)
        step_file(root / "adocs" / "plan_todo", "S009", "orphan")  # one INV-3 violation
        return root

    def test_the_waiver_does_not_survive_into_later_turns(self):
        # S047 (.2-F01): with no prompt_id the counter was global and lived on
        # disk, so from the fourth blocked turn every Stop check was off — and
        # stayed off across sessions. A new turn must start over.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.broken_repo(tmp)
            codes = []
            for turn in range(8):
                log_prompt(root, f"turn {turn}")
                codes.append(run_moltke(root, "--stop", stdin="{}").returncode)
            self.assertEqual(codes, [2] * 8,
                             "each turn is one attempt; none of them is the fourth")

    def test_the_cap_still_fires_within_one_turn(self):
        # Non-vacuity: the no-deadlock property of INV-12 and DEC-006 is the
        # reason the waiver exists, and it must still work.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.broken_repo(tmp)
            log_prompt(root)
            codes = [run_moltke(root, "--stop", stdin="{}").returncode for _ in range(5)]
            self.assertEqual(codes, [2, 2, 2, 0, 0])

    def test_the_counter_resets_when_the_problem_set_changes(self):
        # Making progress should not count against you: two blocks on one
        # problem, then a different problem, and the cap is three away again.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.broken_repo(tmp)
            log_prompt(root)
            for _ in range(3):
                run_moltke(root, "--stop", stdin="{}")
            (root / "adocs" / "plan_todo" / "S009_orphan.md").unlink()
            (root / "adocs" / "status.md").write_text(
                "# Status\n\n- Last done: S999\n- In progress: none\n"
                "- Next: S002\n- Blocked: none\n", encoding="utf-8")
            codes = [run_moltke(root, "--stop", stdin="{}").returncode for _ in range(3)]
            self.assertEqual(codes, [2, 2, 2], "a new problem starts its own count")

    def test_the_waived_turn_still_says_what_was_wrong(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.broken_repo(tmp)
            log_prompt(root)
            for _ in range(3):
                run_moltke(root, "--stop", stdin="{}")
            waived = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(waived.returncode, 0, waived.stderr)
            self.assertIn("INV-3", waived.stderr,
                          "being waved through must not mean being told nothing")

    def test_a_payload_that_cannot_be_parsed_behaves_like_an_empty_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.broken_repo(tmp)
            codes = []
            for turn in range(5):
                log_prompt(root, f"turn {turn}")
                codes.append(run_moltke(root, "--stop", stdin="not json").returncode)
            self.assertEqual(codes, [2] * 5)

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
