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

_ABSENT = object()


def run_moltke(cwd, *args, stdin=""):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=cwd, capture_output=True, text=True, input=stdin,
    )


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        capture_output=True, text=True, check=True,
    )


def git_baseline(root):
    for args in (("init", "-q"), ("add", "-A"), ("commit", "-qm", "base")):
        git(root, *args)


STAMP_COMPLAINT = "README and MANUAL check recorded"


def stamp_complaints(result):
    return [line for line in result.stderr.splitlines() if STAMP_COMPLAINT in line]


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

    def _completed_by_hand(self, tmp, move, stamp="2026-08-07 suite green"):
        """A repo where S003 has just reached plan_done/ by `move`, with a stamp
        that records no README or MANUAL check. Everything else is clean."""
        root = workflow_repo(tmp)
        current = root / "adocs" / "plan_current" / "S003_active.md"
        current.write_text(current.read_text(encoding="utf-8") + f"done:       {stamp}\n",
                           encoding="utf-8")
        testing = root / "adocs" / "testing.md"
        testing.write_text(testing.read_text(encoding="utf-8")
                           + "| S003 | active works | manual | pass |\n", encoding="utf-8")
        git_baseline(root)
        log_prompt(root)
        move(root, current, root / "adocs" / "plan_done" / "S003_active.md")
        return root

    def test_the_stamp_gate_fires_when_a_step_is_moved_by_hand(self):
        # Non-vacuity anchor for the three shapes below, and the gate's first
        # test at all: it survived deletion as the only one of seventeen
        # mutations the suite did not catch (2026-08-07_adversarial.2-F03).
        def plain_mv(root, src, dst):
            src.rename(dst)

        with tempfile.TemporaryDirectory() as tmp:
            root = self._completed_by_hand(tmp, plain_mv)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(len(stamp_complaints(result)), 1, result.stderr)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_the_stamp_gate_is_not_simply_always_on(self):
        # The other half of non-vacuity: a stamp naming both files clears it, so
        # the complaints counted above are the gate deciding, not firing blindly.
        def plain_mv(root, src, dst):
            src.rename(dst)

        with tempfile.TemporaryDirectory() as tmp:
            root = self._completed_by_hand(tmp, plain_mv,
                                           stamp="2026-08-07 suite green; README and MANUAL "
                                                 "checked, no change needed")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(stamp_complaints(result), [], result.stderr)

    def test_the_stamp_gate_fires_on_git_mv(self):
        # S050: `git mv` is the command AGENTS.md section 4 and the pre-write
        # hook both name, and it produces one porcelain line, `R  old -> new`.
        # The status code is neither "??" nor "A ", and line[3:] is the *old*
        # path, so the gate saw nothing at all.
        def git_mv(root, src, dst):
            git(root, "mv", str(src.relative_to(root)), str(dst.relative_to(root)))

        with tempfile.TemporaryDirectory() as tmp:
            root = self._completed_by_hand(tmp, git_mv)
            porcelain = git(root, "status", "--porcelain").stdout
            self.assertIn(" -> ", porcelain, "precondition: git recorded this as a rename")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(len(stamp_complaints(result)), 1, result.stderr)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_the_stamp_gate_fires_on_mv_then_git_add(self):
        # The same porcelain line by the other route: every commit passes through
        # `git add -A`, so a hand-completed step reaches this state either way.
        def mv_then_add(root, src, dst):
            src.rename(dst)
            git(root, "add", "-A")

        with tempfile.TemporaryDirectory() as tmp:
            root = self._completed_by_hand(tmp, mv_then_add)
            porcelain = git(root, "status", "--porcelain").stdout
            self.assertIn(" -> ", porcelain, "precondition: git recorded this as a rename")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(len(stamp_complaints(result)), 1, result.stderr)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_a_rename_between_documentation_and_source_counts_as_source(self):
        # S050: the recap gate tested RECAP_EXEMPT against line[3:], the old
        # path, so a file promoted out of adocs/ in one `git mv` read as exempt.
        # Both directions are a source change: one adds a source file, the other
        # removes one.
        cases = [("adocs/notes.md", "src_notes.py"), ("src_notes.py", "adocs/notes.md")]
        for src_rel, dst_rel in cases:
            with self.subTest(move=f"{src_rel} -> {dst_rel}"), \
                    tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                (root / src_rel).write_text("x\n", encoding="utf-8")
                git_baseline(root)
                log_prompt(root)
                git(root, "mv", src_rel, dst_rel)
                self.assertIn(" -> ", git(root, "status", "--porcelain").stdout,
                              "precondition: git recorded this as a rename")
                result = run_moltke(root, "--stop", stdin="{}")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("recap", result.stderr)

    def test_a_rename_inside_adocs_is_still_exempt(self):
        # Non-vacuity for the pair above: judging both sides must not make every
        # rename a source change, or the recap gate fires on ordinary plan moves.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "notes.md").write_text("x\n", encoding="utf-8")
            git_baseline(root)
            log_prompt(root)
            git(root, "mv", "adocs/notes.md", "adocs/notes_renamed.md")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_stamp_gate_survives_a_staged_arrival_that_is_not_on_disk(self):
        # S060 (2026-08-08_adversarial-F01): the gate decided on the porcelain
        # status and then opened the path. `AD` and `RD` say the index has the
        # file and the worktree does not, so parse_step_file raised, mode_stop
        # had no handler, and the hook died at exit 1 with nothing printed —
        # every gate off for the turn. `RD` is reached by following the gate's
        # own remedy: it blocks, --pre-write forbids editing the file it names,
        # and `mv` back is the only compliant way out.
        def rd(root, src, dst):
            git(root, "mv", str(src.relative_to(root)), str(dst.relative_to(root)))
            dst.rename(src)     # the remedy, from Bash

        def ad(root, src, dst):
            src.rename(dst)
            git(root, "add", "-A")
            dst.rename(src)

        for name, move in (("RD", rd), ("AD", ad)):
            with self.subTest(shape=name), tempfile.TemporaryDirectory() as tmp:
                root = self._completed_by_hand(tmp, move)
                result = run_moltke(root, "--stop", stdin="{}")
                self.assertNotIn("Traceback", result.stderr)
                self.assertNotEqual(result.returncode, 1,
                                    f"a Stop hook exiting 1 enforces nothing: {result.stderr}")
                self.assertTrue(result.stderr.strip(),
                                "the turn ended with no message at all")

    def test_the_problems_found_before_the_missing_file_are_still_printed(self):
        # The crash happened before anything was written, so a real violation in
        # the same call vanished with it.
        def rd(root, src, dst):
            git(root, "mv", str(src.relative_to(root)), str(dst.relative_to(root)))
            dst.rename(src)

        with tempfile.TemporaryDirectory() as tmp:
            root = self._completed_by_hand(tmp, rd)
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 base\n2. S002 pending\n3. S003 active\n4. S099 phantom\n",
                encoding="utf-8")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("INV-3", result.stderr)
            self.assertIn("S099", result.stderr)

    def test_a_wholly_untracked_plan_done_does_not_crash_the_gate(self):
        # Porcelain without -uall collapses an untracked directory into one
        # entry, `?? adocs/plan_done/`, which startswith() accepted and which is
        # a directory on disk. worktree_state has passed -uall since S036 with a
        # comment saying exactly why; the Stop gates did not.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            done = root / "adocs" / "plan_done"
            kept = (done / "S001_base.md").read_text(encoding="utf-8")
            for entry in done.iterdir():
                entry.unlink()
            done.rmdir()
            git_baseline(root)
            done.mkdir()
            (done / "S001_base.md").write_text(kept, encoding="utf-8")
            log_prompt(root)
            porcelain = git(root, "status", "--porcelain").stdout
            self.assertIn("?? adocs/plan_done/\n", porcelain,
                          "precondition: git collapsed the untracked directory")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertNotIn("Traceback", result.stderr)
            self.assertNotEqual(result.returncode, 1, result.stderr)

    def test_an_unreadable_tree_reports_instead_of_raising(self):
        # The general case S052 fixed for --step and left everywhere else: an
        # invariant that cannot read what it is pointed at must say so, not
        # raise. A directory where a step file belongs is the cheapest way to
        # produce one; the shape does not matter, the handling does.
        for mode, expected in (("--stop", 2), ("--post-write", 2), ("--validate", 1)):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                (root / "adocs" / "plan_todo" / "S004_broken.md").mkdir()
                (root / "adocs" / "plan.md").write_text(
                    "# Plan\n\n1. S001 base\n2. S002 pending\n3. S003 active\n4. S004 broken\n",
                    encoding="utf-8")
                result = run_moltke(root, mode, stdin="{}")
                output = result.stdout + result.stderr
                self.assertNotIn("Traceback", output)
                self.assertEqual(result.returncode, expected, output)
                self.assertIn("S004_broken.md", output)

    def test_a_present_arrival_still_reaches_the_stamp_gate(self):
        # Non-vacuity: skipping what is not on disk must not skip what is.
        def git_mv(root, src, dst):
            git(root, "mv", str(src.relative_to(root)), str(dst.relative_to(root)))

        with tempfile.TemporaryDirectory() as tmp:
            root = self._completed_by_hand(tmp, git_mv)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(len(stamp_complaints(result)), 1, result.stderr)

    def _turn_exits(self, root, turns, payload="{}"):
        """--log-prompt then --stop, `turns` times: the shape of a real session."""
        exits = []
        for number in range(turns):
            run_moltke(root, "--log-prompt",
                       stdin=json.dumps({"prompt": f"turn {number}"}))
            exits.append(run_moltke(root, "--stop", stdin=payload).returncode)
        return exits

    def _violating_repo(self, tmp):
        root = workflow_repo(tmp)
        (root / "adocs" / "plan.md").write_text(
            "# Plan\n\n1. S001 base\n2. S002 pending\n3. S003 active\n4. S099 phantom\n",
            encoding="utf-8")
        git_baseline(root)
        return root

    def test_the_waiver_stays_scoped_when_the_prompt_append_fails(self):
        # S061 (2026-08-08_adversarial-F02): the turn clock is the worklog's
        # prompt-heading count, and --log-prompt swallows an OSError by contract
        # because blocking there would erase the prompt. So a worklog that
        # cannot be written freezes the clock, the key stops moving, and the
        # waiver becomes the off switch .2-F01 was about — silently, three turns
        # after a failure whose only other signal is reported once and deleted.
        with tempfile.TemporaryDirectory() as tmp:
            root = self._violating_repo(tmp)
            worklog = root / "adocs" / "worklog.md"
            worklog.chmod(0o444)
            try:
                failed = run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": "x"}))
                self.assertEqual(failed.returncode, 0, "logging must never block")
                self.assertIn("moltke --log-prompt", failed.stderr,
                              "precondition: the append really failed")
                exits = self._turn_exits(root, 8, payload=json.dumps({"session_id": "s1"}))
            finally:
                worklog.chmod(0o644)
            self.assertEqual(exits, [2] * 8,
                             "the violation stood throughout; enforcement must not switch off")

    def test_the_ordinary_per_turn_scoping_is_unchanged(self):
        # The DEC-029 property S047 restored, re-measured: eight real turns each
        # block, and eight retries inside one turn spend the cap and waive.
        with tempfile.TemporaryDirectory() as tmp:
            root = self._violating_repo(tmp)
            self.assertEqual(self._turn_exits(root, 8, payload=json.dumps({"session_id": "s1"})),
                             [2] * 8)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._violating_repo(tmp)
            run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": "one turn"}))
            retries = [run_moltke(root, "--stop", stdin="{}").returncode for _ in range(8)]
            self.assertEqual(retries, [2, 2, 2, 0, 0, 0, 0, 0],
                             "the cap must still fire within one turn, which is why it exists")

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



class TestStopNeverWedges(unittest.TestCase):
    """S067 (2026-08-08_adversarial.2-F01): S060 stopped --stop dying at exit 1
    on an unreadable path and traded it for something worse — the OSError
    escaped to main's backstop before the retry counter was written, so the
    deadlock cap never advanced and every problem already collected was thrown
    away. INV-12 and DEC-006 make no-deadlock a property of the tool, and
    MANUAL states it as one."""

    def repo_with_a_violation(self, tmp):
        root = workflow_repo(tmp)
        (root / "adocs" / "plan.md").write_text(
            "# Plan\n\n1. S001 base\n2. S002 pending\n3. S003 active\n4. S099 phantom\n",
            encoding="utf-8")
        git_baseline(root)
        log_prompt(root)
        return root

    def test_the_cap_still_fires_when_a_path_cannot_be_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with_a_violation(tmp)
            (root / "adocs" / "plan_todo" / "S050_lost.md").symlink_to("nowhere.md")
            exits = [run_moltke(root, "--stop", stdin='{"session_id":"s1"}').returncode
                     for _ in range(5)]
            self.assertEqual(exits, [2, 2, 2, 0, 0],
                             "the waiver must reach an unreadable tree too")

    def test_the_problems_collected_before_the_failure_are_printed(self):
        # --stop had these in hand and dropped them, while --post-write and
        # --validate printed all six for the identical tree.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with_a_violation(tmp)
            (root / "adocs" / "plan_todo" / "S050_thing.md").mkdir()
            stop = run_moltke(root, "--stop", stdin="{}")
            post = run_moltke(root, "--post-write", stdin="{}")
            self.assertEqual(stop.returncode, 2, stop.stderr)
            self.assertGreaterEqual(len(stop.stderr.strip().splitlines()),
                                    len(post.stderr.strip().splitlines()),
                                    "--stop must not say less than --post-write about one tree")
            self.assertIn("INV-3", stop.stderr)
            self.assertIn("S050_thing.md", stop.stderr)

    def test_an_unreadable_worklog_does_not_freeze_the_counter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with_a_violation(tmp)
            worklog = root / "adocs" / "worklog.md"
            worklog.chmod(0o000)
            try:
                exits = [run_moltke(root, "--stop", stdin="{}").returncode for _ in range(8)]
            finally:
                worklog.chmod(0o644)
            self.assertEqual(exits, [2, 2, 2, 0, 0, 0, 0, 0])

    def test_git_missing_from_path_abstains_rather_than_violating(self):
        # The documented behaviour is that the git-based checks abstain without
        # git. _git_lines raised instead of returning None, so INV-7 reported
        # that it could not read the repository and every --stop blocked.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with_a_violation(tmp)
            empty_path = Path(tmp) / "nobin"
            empty_path.mkdir()
            result = subprocess.run(
                [sys.executable, str(MOLTKE), "--validate"],
                cwd=root, capture_output=True, text=True, input="",
                env={"PATH": str(empty_path), "HOME": str(tmp)})
            self.assertNotIn("could not read the repository", result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("INV-3", result.stdout, "the non-git violation is still reported")


class TestSessionStartAlwaysSpeaks(unittest.TestCase):
    """S068 (2026-08-08_adversarial.2-F02): the whole payload was built before
    the single print, so a read failure anywhere in it lost the lot — exit 0
    with empty stdout, the one combination where nothing can be seen. A
    zero-exit hook's stderr reaches nobody, which is why S014 put the
    prompt-failure breadcrumb on this channel in the first place."""

    def test_a_broken_path_still_produces_the_json_envelope(self):
        for name, make in (("directory", lambda p: p.mkdir()),
                           ("broken symlink", lambda p: p.symlink_to("nowhere.md"))):
            with self.subTest(shape=name), tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                make(root / "adocs" / "plan_todo" / "S050_thing.md")
                result = run_moltke(root, "--session-start")
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)      # must parse at all
                context = payload["hookSpecificOutput"]["additionalContext"]
                self.assertIn("S050_thing.md", context,
                              "the agent has to be told what it cannot see")

    def test_a_healthy_repository_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            context = session_context(root)
            self.assertIn("S003", context)
            self.assertNotIn("could not", context)


class TestTheStampGateJudgesStepFiles(unittest.TestCase):
    """S069 (2026-08-08_adversarial.2-F03): the gate tested the porcelain status
    and the path prefix and nothing else, so anything arriving under plan_done/
    was asked for a completion stamp. --scaffold's own .gitkeep is such a thing,
    which made every Stop block in an existing project the moment it adopted
    moltke. plan_steps filters on STEP_FILE_RE; this was the only reader of
    plan_done/ without that filter."""

    def test_a_stray_file_under_plan_done_is_not_a_completion(self):
        for name in (".gitkeep", "notes.txt", "README.md"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                git_baseline(root)
                log_prompt(root)
                (root / "adocs" / "plan_done" / name).write_text("x\n", encoding="utf-8")
                result = run_moltke(root, "--stop", stdin="{}")
                self.assertEqual(stamp_complaints(result), [],
                                 f"{name} is not a step: {result.stderr}")

    def test_scaffolding_into_a_repository_with_history_does_not_wedge_it(self):
        # The finding's own path: the documented way an existing project adopts
        # moltke, after which every Stop blocked on a file the scaffold wrote.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# existing project\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            git(root, "add", "-A")
            git(root, "commit", "-qm", "existing history")
            run_moltke(root, "--scaffold")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(stamp_complaints(result), [], result.stderr)

    def test_a_real_step_file_still_has_to_carry_the_stamp(self):
        # Non-vacuity: the filter must not turn the gate off.
        def git_mv(root, src, dst):
            git(root, "mv", str(src.relative_to(root)), str(dst.relative_to(root)))

        with tempfile.TemporaryDirectory() as tmp:
            root = TestStop._completed_by_hand(TestStop(), tmp, git_mv)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(len(stamp_complaints(result)), 1, result.stderr)


class TestTheStampGateSeesInsideAnUntrackedPlanDone(unittest.TestCase):
    """S073 (2026-08-08_adversarial.2-F07): plain porcelain collapses a wholly
    untracked directory into one entry, so the gate saw `?? adocs/plan_done/`
    and nothing inside it. S060 passed -uall for that reason and no test held
    the flag in place — reverting it left all 308 green, and this gate plus
    worktree_state are the only -uall readers, so a later tidy-up would restore
    the blind spot silently."""

    def test_a_step_inside_a_wholly_untracked_plan_done_still_reaches_the_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            done = root / "adocs" / "plan_done"
            kept = (done / "S001_base.md").read_text(encoding="utf-8")
            for entry in done.iterdir():
                entry.unlink()
            done.rmdir()
            git_baseline(root)                      # commit without plan_done/
            done.mkdir()
            (done / "S001_base.md").write_text(kept, encoding="utf-8")
            log_prompt(root)
            plain = git(root, "status", "--porcelain").stdout
            self.assertIn("?? adocs/plan_done/\n", plain,
                          "precondition: plain porcelain collapses the directory")
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(len(stamp_complaints(result)), 1,
                             f"the step inside it must be judged: {result.stderr}")


class TestTheStopStateWriteNeverWedges(unittest.TestCase):
    """S080 (2026-08-08_adversarial.3-F01): the retry state write was the one
    unguarded write left in mode_stop. S067 guarded every read here and left it,
    so the OSError escaped to main's backstop, which returns before the problems
    are printed and before the cap is consulted — the third wedge found in this
    function and the second introduced while fixing the first. DEC-039 makes the
    crash a defect and the missing cap an accepted, stated gap."""

    STATE_FILE = "moltke_stop_state.json"

    def wedged(self, tmp):
        root = workflow_repo(tmp)
        (root / "adocs" / "plan.md").write_text(
            "# Plan\n\n1. S001 base\n2. S002 pending\n3. S003 active\n4. S099 phantom\n",
            encoding="utf-8")
        git_baseline(root)
        log_prompt(root)
        return root

    def test_an_unwritable_state_directory_does_not_crash_or_go_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.wedged(tmp)
            git_dir = root / ".git"
            git_dir.chmod(0o500)
            try:
                results = [run_moltke(root, "--stop", stdin="{}") for _ in range(3)]
            finally:
                git_dir.chmod(0o755)
            for result in results:
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("INV-3", result.stderr, "the problems must still be printed")

    def test_the_message_says_the_write_failed_and_names_the_missing_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.wedged(tmp)
            git_dir = root / ".git"
            git_dir.chmod(0o500)
            try:
                result = run_moltke(root, "--stop", stdin="{}")
            finally:
                git_dir.chmod(0o755)
            self.assertIn(self.STATE_FILE, result.stderr,
                          "the state file is what could not be written; name it")
            self.assertNotIn("could not read the repository", result.stderr)

    def test_the_cap_still_fires_where_the_state_is_writable(self):
        # Non-vacuity, and the property DEC-039 scopes rather than drops.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.wedged(tmp)
            exits = [run_moltke(root, "--stop", stdin="{}").returncode for _ in range(5)]
            self.assertEqual(exits, [2, 2, 2, 0, 0])
            self.assertTrue((root / ".git" / self.STATE_FILE).is_file(),
                            "the state file this test is about must exist by name")


class TestMalformedHookPayloads(unittest.TestCase):
    """S087 (2026-08-08_adversarial.3-F08): hook_input validated that the top
    level was a dict and the three consumers assumed the nested types. A
    PreToolUse hook that dies with exit 1 is non-blocking, so the write it was
    judging proceeded — the reviewer fence and the plan_done/ refusal both
    failing open, which S016 named as the wrong direction. Whether Claude Code
    ever sends these shapes is not established; the fence must not depend on it.
    """

    def test_pre_write_still_blocks_when_tool_input_is_not_a_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"tool_input": "adocs/plan_done/S001_base.md"})
            result = run_moltke(root, "--pre-write", "adocs/plan_done/S001_base.md",
                                stdin=payload)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_pre_write_does_not_raise_on_odd_nested_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for payload in (json.dumps({"tool_input": "a string"}),
                            json.dumps({"agent_type": ["moltke:adversarial_reviewer"],
                                        "tool_input": {"file_path": "bin/moltke.py"}}),
                            json.dumps({"tool_input": {"file_path": 12345}})):
                with self.subTest(payload=payload):
                    result = run_moltke(root, "--pre-write", stdin=payload)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn(result.returncode, (0, 2), result.stderr)

    def test_log_prompt_never_loses_a_prompt_to_a_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": 12345}))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("12345", (root / "adocs" / "worklog.md").read_text(encoding="utf-8"))

    def test_the_reviewer_fence_still_matches_a_well_formed_payload(self):
        # Non-vacuity: tolerating odd types must not stop the fence working.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"agent_type": "moltke:adversarial_reviewer",
                                  "tool_input": {"file_path": "bin/moltke.py"}})
            result = run_moltke(root, "--pre-write", stdin=payload)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class TestMachineLocalFile(unittest.TestCase):
    """S109 (DEC-043): .moltke.local.md is machine memory — tools, paths,
    directives that differ per machine and must not travel in git. The tool
    creates it so it reliably exists, excludes it through .git/info/exclude
    (itself uncommitted), and injects its content into the SessionStart
    context so an agent needs no extra read."""

    def session_start(self, root):
        return run_moltke(root, "--session-start")

    def context(self, result):
        return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_created_excluded_and_injected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            result = self.session_start(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            local = root / ".moltke.local.md"
            self.assertTrue(local.is_file(), "the file is created when absent")
            exclude = (root / ".git" / "info" / "exclude").read_text(encoding="utf-8")
            self.assertIn(".moltke.local.md", exclude)
            porcelain = git(root, "status", "--porcelain").stdout
            self.assertNotIn(".moltke.local.md", porcelain,
                             "git must not see the file at all")
            self.assertIn(".moltke.local.md", self.context(result),
                          "the injection names its source so an agent can edit it")

    def test_existing_content_is_injected_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            (root / ".moltke.local.md").write_text(
                "# This machine\n\nstockfish lives at /opt/homebrew/bin/stockfish\n",
                encoding="utf-8")
            result = self.session_start(root)
            self.assertIn("stockfish lives at /opt/homebrew/bin/stockfish",
                          self.context(result))
            self.assertIn("stockfish", (root / ".moltke.local.md").read_text(encoding="utf-8"),
                          "an existing file is the user's and is never overwritten")

    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            self.session_start(root)
            body = (root / ".moltke.local.md").read_bytes()
            exclude = (root / ".git" / "info" / "exclude").read_bytes()
            self.session_start(root)
            self.assertEqual((root / ".moltke.local.md").read_bytes(), body)
            self.assertEqual((root / ".git" / "info" / "exclude").read_bytes(), exclude,
                             "the exclude line is appended once, not once per session")

    def test_an_unmarked_repository_gets_no_file(self):
        # INV-11: a repository that did not opt in feels nothing, including no
        # file creation.
        with tempfile.TemporaryDirectory() as tmp:
            result = run_moltke(tmp, "--session-start")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((Path(tmp) / ".moltke.local.md").exists())

    def test_a_declined_repository_gets_no_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".moltke.json").write_text('{"schema": 1, "enabled": false}\n',
                                                    encoding="utf-8")
            result = run_moltke(tmp, "--session-start")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((Path(tmp) / ".moltke.local.md").exists())

    def test_without_git_the_file_still_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)   # marked, no git init
            result = self.session_start(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / ".moltke.local.md").is_file())
            self.assertNotIn("Traceback", result.stderr)


class TestAMalformedAgentTypeIsFenced(unittest.TestCase):
    """S101 (2026-08-09_adversarial-F05): S087 made `payload_str` return "" for
    anything that is not a string, which stopped the crash and left the fence
    reading a malformed `agent_type` as an absent one. Absent is the main thread
    and is never fenced (S016), so `{"agent_type": ["moltke:adversarial_reviewer"]}`
    wrote `bin/moltke.py` at exit 0 — a wrong pass, which is silent, in place of
    a wrong block, which is loud. Nothing establishes that Claude Code ever sends
    that shape, and S087's own note says the fence must not depend on it."""

    def pre_write(self, root, agent_type):
        payload = {"tool_input": {"file_path": "bin/moltke.py"}}
        if agent_type is not _ABSENT:
            payload["agent_type"] = agent_type
        return run_moltke(root, "--pre-write", stdin=json.dumps(payload))

    def test_a_list_agent_type_is_fenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, ["moltke:adversarial_reviewer"])
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("adversarial_reviewer", result.stderr)

    def test_every_malformed_shape_is_fenced(self):
        for shape in (["moltke:adversarial_reviewer"], {"name": "reviewer"}, 12345,
                      True, ["anything", "at", "all"]):
            with self.subTest(shape=shape), tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                result = self.pre_write(root, shape)
                self.assertEqual(result.returncode, 2, (shape, result.stdout, result.stderr))

    def test_an_absent_agent_type_is_still_the_main_thread(self):
        # S016's rule, and the non-vacuity anchor: the distinction is absent
        # versus malformed, not string versus everything else. A guard that
        # fenced whenever the value was not the reviewer's name would block the
        # main thread's every write.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, _ABSENT)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_null_agent_type_is_read_as_absent(self):
        # JSON null is how a payload says "no value", so it is treated as the
        # absent case rather than as a malformed one. Fencing it would block
        # every main-thread write if Claude Code ever encodes "no agent" that
        # way — a false block on the common path, against a shape nobody has
        # observed. The cheaper mistake, deliberately chosen.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, None)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_another_agents_name_is_still_not_fenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, "some-plugin:formatter")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_plan_done_rule_still_runs_for_a_malformed_payload(self):
        # S087's fix, which must not regress: the other two rules judge every
        # payload shape regardless of what agent_type holds.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"agent_type": 12345,
                                  "tool_input": {"file_path": "adocs/plan_done/S001_base.md"}})
            result = run_moltke(root, "--pre-write", stdin=payload)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("plan_done", result.stderr)


if __name__ == "__main__":
    unittest.main()
