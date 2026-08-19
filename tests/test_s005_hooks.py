"""S005: hook modes. Contract verified against live docs on 2026-08-01:
SessionStart context reaches Claude only via hookSpecificOutput JSON;
Stop has no documented block cap, so moltke imposes its own.

The UserPromptSubmit clause left with the worklog (S120, DEC-046); no test here
invokes that event now.
"""

import json
import os
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


STAMP_COMPLAINT = "without a done: stamp"


def stamp_complaints(result):
    return [line for line in result.stderr.splitlines() if STAMP_COMPLAINT in line]


def session_context(root):
    result = run_moltke(root, "--session-start")
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


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
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("status.md", result.stderr)

    def _completed_by_hand(self, tmp, move, stamp=""):
        """A repo where S003 has just reached plan_done/ by `move`, with no
        done: stamp at all — the shape the gate blocks since S125 (DEC-048).
        Everything else is clean."""
        root = workflow_repo(tmp)
        current = root / "adocs" / "plan_current" / "S003_active.md"
        if stamp:
            current.write_text(current.read_text(encoding="utf-8")
                               + f"done:       {stamp}\n", encoding="utf-8")
        testing = root / "adocs" / "testing.md"
        testing.write_text(testing.read_text(encoding="utf-8")
                           + "| S003 | active works | manual | pass |\n", encoding="utf-8")
        git_baseline(root)
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
            kept = (done / "S001_base.md").read_text(encoding="utf-8").replace(
                "done: 2026-08-01 done", "done:")
            for entry in done.iterdir():
                entry.unlink()
            done.rmdir()
            git_baseline(root)
            done.mkdir()
            (done / "S001_base.md").write_text(kept, encoding="utf-8")
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

    def _violating_repo(self, tmp):
        root = workflow_repo(tmp)
        (root / "adocs" / "plan.md").write_text(
            "# Plan\n\n1. S001 base\n2. S002 pending\n3. S003 active\n4. S099 phantom\n",
            encoding="utf-8")
        git_baseline(root)
        return root

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
            # A violation that still blocks post-S120: a phantom pauser. The
            # recap gate this test originally leaned on left with the worklog.
            parent = worktree / "adocs" / "plan_current" / "S003_active.md"
            parent.write_text(parent.read_text(encoding="utf-8").replace(
                "goal:", "paused_by:  S999  # stranded\ngoal:", 1), encoding="utf-8")
            payload = json.dumps({"prompt_id": "p1"})
            codes = [run_moltke(worktree, "--stop", stdin=payload).returncode for _ in range(5)]
            self.assertEqual(codes, [2, 2, 2, 0, 0],
                             "the cap must fire in a worktree exactly as it does in a clone")

    def broken_repo(self, tmp):
        root = workflow_repo(tmp)
        git_baseline(root)
        step_file(root / "adocs" / "plan_todo", "S009", "orphan")  # one INV-3 violation
        return root

    def test_the_cap_still_fires_within_one_turn(self):
        # Non-vacuity: the no-deadlock property of INV-12 and DEC-006 is the
        # reason the waiver exists, and it must still work.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.broken_repo(tmp)
            codes = [run_moltke(root, "--stop", stdin="{}").returncode for _ in range(5)]
            self.assertEqual(codes, [2, 2, 2, 0, 0])

    def test_the_counter_resets_when_the_problem_set_changes(self):
        # Making progress should not count against you: two blocks on one
        # problem, then a different problem, and the cap is three away again.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.broken_repo(tmp)
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
            for _ in range(3):
                run_moltke(root, "--stop", stdin="{}")
            waived = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(waived.returncode, 0, waived.stderr)
            self.assertIn("INV-3", waived.stderr,
                          "being waved through must not mean being told nothing")

    def test_block_cap_prevents_deadlock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
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
            kept = (done / "S001_base.md").read_text(encoding="utf-8").replace(
                "done: 2026-08-01 done", "done:")
            for entry in done.iterdir():
                entry.unlink()
            done.rmdir()
            git_baseline(root)                      # commit without plan_done/
            done.mkdir()
            (done / "S001_base.md").write_text(kept, encoding="utf-8")
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

    def test_the_reviewer_fence_still_matches_a_well_formed_payload(self):
        # Non-vacuity: tolerating odd types must not stop the fence working.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"agent_type": "moltke:adversarial_reviewer",
                                  "tool_input": {"file_path": "bin/moltke.py"}})
            result = run_moltke(root, "--pre-write", stdin=payload)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class TestPreWritePathArgumentSkipsStdin(unittest.TestCase):
    """S119: --pre-write PATH read stdin before consulting PATH, so a pipe that
    never closes hung it forever. Hooks are unaffected (Claude Code closes
    stdin); MANUAL endorses manual use, where a shell with an inherited open
    pipe hangs. With a PATH argument there is nothing stdin can add."""

    def test_a_path_argument_never_touches_stdin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            # A pipe with no writer closing it: read() blocks forever. The
            # timeout is the observation — before the fix this raised
            # TimeoutExpired, after it the refusal returns immediately.
            r, w = os.pipe()
            try:
                result = subprocess.run(
                    [sys.executable, str(MOLTKE), "--pre-write",
                     "adocs/plan_done/S001_base.md"],
                    cwd=root, capture_output=True, text=True,
                    stdin=os.fdopen(r), timeout=10)
            finally:
                os.close(w)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("plan_done", result.stderr)


class TestCaseVariantPaths(unittest.TestCase):
    """S113 (2026-08-11_adversarial-F02): the deny rules compared rel.parts
    against lowercase literals, and Path.resolve() does not fold case. On the
    case-insensitive filesystem this project ships on, ADOCS/PLAN_DONE/x wrote
    into the real plan_done/ at exit 0, and a legitimate step file spelled
    Adocs/... was refused with a message that is untrue here. The rule follows
    the path's resolved identity, not its spelling; on a case-sensitive
    filesystem a case-variant path is genuinely different and stays permitted."""

    def setUp(self):
        probe = tempfile.NamedTemporaryFile(prefix="Case", suffix=".probe", delete=False)
        probe.close()
        self.insensitive = Path(probe.name.lower()).exists()
        Path(probe.name).unlink()
        if not self.insensitive:
            self.skipTest("filesystem is case-sensitive; the identity rule has nothing "
                          "to fold here and the permit direction is covered by "
                          "TestPreWrite.test_allows_ordinary_writes")

    def test_a_case_variant_of_plan_done_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"tool_input": {"file_path": "ADOCS/PLAN_DONE/notes.md"}})
            result = run_moltke(root, "--pre-write", stdin=payload)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("plan_done", result.stderr)

    def test_a_case_variant_step_file_in_a_plan_directory_is_permitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"tool_input": {"file_path": "Adocs/plan_todo/S099_probe.md"}})
            result = run_moltke(root, "--pre-write", stdin=payload)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_exact_spelling_still_behaves_as_before(self):
        # Non-vacuity anchor: folding must not loosen the straight case.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"tool_input": {"file_path": "adocs/plan_done/notes.md"}})
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

    def test_a_linked_worktree_gets_a_working_exclusion(self):
        # S112 (2026-08-11_adversarial-F01): the exclusion went to
        # --absolute-git-dir/info/exclude, which in a linked worktree is
        # .git/worktrees/<name>/info/exclude — a path git status never reads.
        # The file showed ??, the Stop gate blocked every clean turn, and its
        # remedy steered toward committing the one file DEC-043 forbids in git.
        with tempfile.TemporaryDirectory() as tmp:
            primary = Path(tmp) / "primary"
            primary.mkdir()
            root = workflow_repo(primary)
            git_baseline(root)
            linked = Path(tmp) / "linked"
            git(root, "worktree", "add", "-q", str(linked))
            result = run_moltke(linked, "--session-start")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((linked / ".moltke.local.md").is_file(),
                            "precondition: the file was created in the worktree")
            porcelain = git(linked, "status", "--porcelain").stdout
            self.assertNotIn(".moltke.local.md", porcelain,
                             "the exclusion must land where git status reads it")

    def test_a_substring_in_the_exclude_file_does_not_satisfy_the_check(self):
        # S111, from the batch's own fast check: `LOCAL_FILE not in existing`
        # is a substring test, so a line like ".moltke.local.md.bak" reads as
        # "already excluded" and the real exclusion is never appended.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            exclude = root / ".git" / "info" / "exclude"
            exclude.parent.mkdir(parents=True, exist_ok=True)
            exclude.write_text(".moltke.local.md.bak\n", encoding="utf-8")
            self.session_start(root)
            lines = exclude.read_text(encoding="utf-8").splitlines()
            self.assertIn(".moltke.local.md", lines,
                          "the exact exclusion line must be appended, not satisfied "
                          "by a superstring")
            porcelain = git(root, "status", "--porcelain").stdout
            self.assertNotIn(".moltke.local.md\n", porcelain + "\n")

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
