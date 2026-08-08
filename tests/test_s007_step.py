"""S007: --step lifecycle operations.

Acceptance: every transition leaves INV-1..INV-7 satisfied, and completion is
refused with the specific missing condition named.
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import marked_repo, step_file, workflow_repo
from surface import moltke

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"
REPO = MOLTKE.parent.parent

STAMP = "2026-08-01 suite green; README and MANUAL checked"


def run_moltke(cwd, *args):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=cwd, capture_output=True, text=True, input="",
    )


def validate(cwd):
    return run_moltke(cwd, "--validate")


def add_testing_row(root, step_id):
    testing = root / "adocs" / "testing.md"
    testing.write_text(testing.read_text(encoding="utf-8")
                       + f"| {step_id} | works | test_{step_id} | pass |\n", encoding="utf-8")


class TestNew(unittest.TestCase):
    def test_allocates_next_free_id_and_lists_it_in_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "new", "widget", "--goal", "build the widget")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            created = root / "adocs" / "plan_todo" / "S004_widget.md"
            self.assertTrue(created.is_file(), result.stdout)
            text = created.read_text(encoding="utf-8")
            self.assertIn("id:         S004", text)
            self.assertIn("build the widget", text)
            self.assertIn("S004", (root / "adocs" / "plan.md").read_text(encoding="utf-8"))
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_ids_are_never_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "new", "one")
            (root / "adocs" / "plan_todo" / "S004_one.md").unlink()
            run_moltke(root, "--step", "new", "two")
            self.assertTrue((root / "adocs" / "plan_todo" / "S005_two.md").is_file())


class TestTemplatePlaceholders(unittest.TestCase):
    def test_unfilled_paused_by_placeholder_does_not_hide_an_active_step(self):
        # A hand-copied template keeps `paused_by: <!-- ... -->`. Treating that
        # comment as a real value would silently allow two active steps.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            template = (REPO / "templates" / "step_template.md").read_text(encoding="utf-8")
            (root / "adocs" / "plan_current" / "S004_manual.md").write_text(
                template.replace("S000", "S004"), encoding="utf-8")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001\n2. S002\n3. S003\n4. S004\n", encoding="utf-8")
            result = validate(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("INV-1", result.stdout)


class TestStart(unittest.TestCase):
    def test_promotes_todo_to_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            # Free the single active slot first.
            add_testing_row(root, "S003")
            run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            result = run_moltke(root, "--step", "start", "S002")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "adocs" / "plan_current" / "S002_pending.md").is_file())
            self.assertFalse((root / "adocs" / "plan_todo" / "S002_pending.md").exists())
            self.assertEqual(validate(root).returncode, 0)

    def test_refuses_when_the_active_slot_is_taken(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "start", "S002")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S003", result.stderr)  # names the step holding the slot
            self.assertFalse((root / "adocs" / "plan_current" / "S002_pending.md").exists())
            self.assertEqual(validate(root).returncode, 0, "refusal left the tree dirty")

    def test_refuses_an_unknown_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "start", "S099")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("S099", result.stderr)


class TestBlock(unittest.TestCase):
    def test_creates_child_and_pauses_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "block", "S003", "missing_dep")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            child = root / "adocs" / "plan_current" / "S004_missing_dep.md"
            self.assertTrue(child.is_file(), result.stdout)
            self.assertIn("blocks:     S003", child.read_text(encoding="utf-8"))
            parent = (root / "adocs" / "plan_current" / "S003_active.md").read_text(encoding="utf-8")
            self.assertRegex(parent, r"paused_by:\s*S004")
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_refuses_past_the_stack_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "block", "S003", "first")     # depth 2
            run_moltke(root, "--step", "block", "S004", "second")    # depth 3
            result = run_moltke(root, "--step", "block", "S005", "third")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("replan", result.stderr.lower())
            self.assertEqual(validate(root).returncode, 0, "refusal left the tree dirty")

    def test_refuses_when_parent_is_not_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "block", "S002", "child")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("S002", result.stderr)


class TestDone(unittest.TestCase):
    """Completion is refused with the specific missing condition named."""

    def test_refuses_without_a_testing_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("testing.md", result.stderr)
            self.assertTrue((root / "adocs" / "plan_current" / "S003_active.md").is_file())

    def test_refuses_a_paused_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            add_testing_row(root, "S003")
            run_moltke(root, "--step", "block", "S003", "dep")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("paused by S004", result.stderr)
            self.assertNotIn("#", result.stderr)  # the id, not the raw field text

    def test_refuses_when_another_step_still_blocks_it(self):
        # Blocked but not paused: a pending step declaring a dependency.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            add_testing_row(root, "S003")
            step_file(root / "adocs" / "plan_todo", "S004", "dependent", blocks="S003")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001\n2. S002\n3. S003\n4. S004\n", encoding="utf-8")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S004", result.stderr)
            self.assertIn("blocks", result.stderr)

    def test_refuses_a_step_that_is_not_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            add_testing_row(root, "S002")
            result = run_moltke(root, "--step", "done", "S002", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("plan_current", result.stderr)

    def test_refuses_a_stamp_missing_the_docs_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            add_testing_row(root, "S003")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", "2026-08-01 green")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("README", result.stderr)
            self.assertIn("MANUAL", result.stderr)

    def test_completes_and_stamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            add_testing_row(root, "S003")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            moved = root / "adocs" / "plan_done" / "S003_active.md"
            self.assertTrue(moved.is_file())
            self.assertIn(STAMP, moved.read_text(encoding="utf-8"))
            self.assertFalse((root / "adocs" / "plan_current" / "S003_active.md").exists())
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_parent_completes_once_its_child_is_done(self):
        # A completed child is history, not a live blocker.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "block", "S003", "dep")
            add_testing_row(root, "S004")
            run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
            add_testing_row(root, "S003")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_completing_a_child_unpauses_the_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "block", "S003", "dep")
            add_testing_row(root, "S004")
            result = run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            parent = (root / "adocs" / "plan_current" / "S003_active.md").read_text(encoding="utf-8")
            self.assertNotRegex(parent, r"paused_by:\s*S004")
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)


class TestDoneTestCommandGate(unittest.TestCase):
    """S021 (DEC-023, F07): the "full suite green" completion gate was
    honour-system — nothing ran or consulted a suite. Optional, so no existing
    marker needs migrating and schema stays 1."""

    def repo_with(self, tmp, command):
        root = workflow_repo(tmp)
        if command is not None:
            marker = json.loads((root / ".moltke.json").read_text(encoding="utf-8"))
            marker["test_command"] = command
            (root / ".moltke.json").write_text(json.dumps(marker, indent=2) + "\n",
                                               encoding="utf-8")
        add_testing_row(root, "S003")
        return root

    def test_a_failing_command_refuses_and_shows_the_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with(
                tmp, f"{sys.executable} -c \"print('DISTINCTIVE FAILURE'); raise SystemExit(1)\"")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("test_command", result.stderr)
            self.assertIn("DISTINCTIVE FAILURE", result.stderr)
            # Refuse, do not half-complete: the step stays where it was.
            self.assertTrue((root / "adocs" / "plan_current" / "S003_active.md").is_file())
            self.assertFalse((root / "adocs" / "plan_done" / "S003_active.md").exists())

    def test_a_passing_command_lets_the_step_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with(tmp, f"{sys.executable} -c \"raise SystemExit(0)\"")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "adocs" / "plan_done" / "S003_active.md").is_file())

    def test_without_the_key_nothing_runs_and_the_gap_is_stated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with(tmp, None)
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "adocs" / "plan_done" / "S003_active.md").is_file())
            self.assertIn("test_command", result.stdout)

    def test_a_malformed_test_command_refuses_completion(self):
        # S038 (F07): check_marker flagged these, but mode_step never received
        # marker violations, so --step done completed green while reporting that
        # the key was absent — the exact failure DEC-023 added the key to remove,
        # reached by a typo.
        for command in ("", "   ", ["python3", "-m", "unittest"], 0):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = self.repo_with(tmp, command)
                result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("test_command", result.stderr)
                self.assertTrue((root / "adocs" / "plan_current" / "S003_active.md").is_file(),
                                "a refusal must not half-complete the step")
                self.assertFalse((root / "adocs" / "plan_done" / "S003_active.md").exists())
                self.assertNotIn("no \"test_command\"", result.stdout,
                                 "the key is present, so saying it is absent is wrong")

    def test_a_malformed_marker_refuses_every_step_transition(self):
        # The gate is not special: no marker violation should be invisible to the
        # commands that move the plan around.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with(tmp, "")
            for argv in (("--step", "start", "S002"), ("--step", "new", "widget"),
                         ("--step", "status")):
                result = run_moltke(root, *argv)
                self.assertEqual(result.returncode, 1, (argv, result.stdout + result.stderr))
                self.assertIn("test_command", result.stderr, argv)

    def test_a_non_string_test_command_is_a_marker_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with(tmp, 5)
            result = validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("test_command", result.stdout)

    def test_a_blank_test_command_is_a_marker_violation(self):
        # Silently doing nothing is the failure mode this step exists to remove.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with(tmp, "   ")
            result = validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("test_command", result.stdout)

    def test_the_gate_runs_from_the_repository_root(self):
        # A relative command must not depend on the caller's working directory.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo_with(
                tmp, f"{sys.executable} -c \"import pathlib,sys; "
                     f"sys.exit(0 if pathlib.Path('.moltke.json').is_file() else 1)\"")
            sub = root / "adocs" / "plan_todo"
            result = run_moltke(sub, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestPlanOrderComesFromTheList(unittest.TestCase):
    """S045: order lives in the numbered list (DEC-008). Reading the whole file
    in document order let a description paragraph decide the next step, which is
    how this repository briefly reported Next: S028 for a list starting at S034."""

    def plan_with(self, root, text):
        (root / "adocs" / "plan.md").write_text(text, encoding="utf-8")

    def next_step(self, root):
        run_moltke(root, "--step", "status")
        status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
        return re.search(r"Next:\s*(\S+)", status).group(1)

    def test_prose_above_the_list_does_not_become_the_next_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.plan_with(root, "# Plan\n\nOrdered ahead of the feature work S002.\n\n"
                                 "1. S001  done already\n2. S003  the real next step\n")
            self.assertEqual(self.next_step(root), "S003")

    def test_an_id_inside_a_list_entrys_own_text_does_not_reorder_it(self):
        # plan.md line 22 does exactly this: S010's entry mentions S012.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.plan_with(root, "# Plan\n\n1. S001  done already\n"
                                 "2. S003  the real next step (S002 moved here)\n")
            self.assertEqual(self.next_step(root), "S003")

    def test_list_order_still_decides(self):
        # Non-vacuity: the two above must not pass by always returning the last id.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.plan_with(root, "# Plan\n\n1. S001  done already\n"
                                 "2. S002  first not done\n3. S003  after it\n")
            self.assertEqual(self.next_step(root), "S002")

    def test_a_commented_list_entry_is_still_not_the_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.plan_with(root, "# Plan\n\n<!-- 1. S099  example -->\n\n"
                                 "1. S001  done already\n2. S003  the real next step\n")
            self.assertEqual(self.next_step(root), "S003")


class TestStatus(unittest.TestCase):
    def test_regenerates_from_the_filesystem(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "status.md").write_text("# Status\n\n- Next: nonsense\n",
                                                        encoding="utf-8")
            result = run_moltke(root, "--step", "status")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            self.assertIn("S001", status)   # last done
            self.assertIn("S003", status)   # in progress
            self.assertIn("S002", status)   # derived next
            self.assertNotIn("nonsense", status)

    def test_preserves_the_parked_section(self):
        # Parked entries are human memory: regeneration must not eat them.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "status.md").write_text(
                "# Status\n\n- Next: whatever\n- Parked:\n"
                "  - ask about the licence\n  - revisit retry budget\n", encoding="utf-8")
            run_moltke(root, "--step", "status")
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            self.assertIn("ask about the licence", status)
            self.assertIn("revisit retry budget", status)

    def test_shows_the_paused_stack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "block", "S003", "dep")
            run_moltke(root, "--step", "status")
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            self.assertIn("S004", status)
            self.assertRegex(status, r"S003.*paused")


class TestAMarkedRepositoryWithNoDocsDirectory(unittest.TestCase):
    """S052 (2026-08-07_adversarial.2-F05): S039 made a missing `status.md`
    maximally stale, so `--session-start` and `--stop` both instruct
    `--step status` — which wrote into a directory that is not there and died
    with a FileNotFoundError. A traceback is neither of the two things exit 1
    means. Refusing rather than creating `adocs/` is deliberate: a repository
    that was never scaffolded must say so, not be silently half-built."""

    def marked_only(self, tmp):
        """A valid marker and nothing else — the first state a new user has."""
        root = marked_repo(tmp)
        self.assertFalse((root / "adocs").exists(), "precondition: no adocs/ here")
        return root

    def test_every_step_operation_refuses_and_names_scaffold(self):
        for argv in (["--step", "status"], ["--step", "start", "S001"],
                     ["--step", "done", "S001", "--stamp", STAMP],
                     ["--step", "new", "thing"], ["--step", "block", "S001", "dep"]):
            with self.subTest(argv=" ".join(argv)), tempfile.TemporaryDirectory() as tmp:
                root = self.marked_only(tmp)
                result = run_moltke(root, *argv)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("--scaffold", result.stderr)
                self.assertFalse((root / "adocs").exists(),
                                 "refusing must not leave a half-built adocs/ behind")

    def test_the_hooks_that_steer_here_still_work(self):
        # The instruction that leads into it must keep working, or this trades a
        # traceback for a silent repository.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.marked_only(tmp)
            for argv in (["--session-start"], ["--validate"]):
                with self.subTest(argv=" ".join(argv)):
                    result = run_moltke(root, *argv)
                    self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_the_hooks_name_scaffold_rather_than_a_command_that_cannot_work(self):
        # The finding's real damage: the staleness lines steer into --step
        # status, and with no adocs/ every derived field disagrees, so they
        # always fire here. Steering must name the command that works.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.marked_only(tmp)
            start = run_moltke(root, "--session-start")
            self.assertIn("--scaffold", start.stdout)
            stop = run_moltke(root, "--stop")
            self.assertIn("--scaffold", stop.stderr)

    def test_a_scaffolded_repository_is_still_told_to_run_step_status(self):
        # Non-vacuity for the pair above: the remedy must not become --scaffold
        # everywhere, which would be advice that does nothing.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "status.md").write_text("# Status\n\n- Next: nonsense\n",
                                                      encoding="utf-8")
            start = run_moltke(root, "--session-start")
            self.assertIn("--step status", start.stdout)
            self.assertNotIn("--scaffold", start.stdout)

    def test_a_scaffolded_repository_is_unaffected(self):
        # Non-vacuity: the refusal must be about the missing directory, not
        # about --step having stopped working.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "status")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_missing_plan_directory_refuses_instead_of_raising(self):
        # The sibling shape the finding names: adocs/ exists, a plan directory
        # inside it does not, so the rename target is missing.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for entry in (root / "adocs" / "plan_current").iterdir():
                entry.unlink()
            (root / "adocs" / "plan_current").rmdir()
            result = run_moltke(root, "--step", "start", "S002")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("plan_current", result.stderr)


class TestStepSkill(unittest.TestCase):
    def test_skill_declares_name_and_description(self):
        skill = REPO / "skills" / "step" / "SKILL.md"
        self.assertTrue(skill.is_file(), "skills/step/SKILL.md missing")
        text = skill.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: step", frontmatter)
        self.assertRegex(frontmatter, r"description:\s*\S")


if __name__ == "__main__":
    unittest.main()


class TestARefusedCompletionChangesNothing(unittest.TestCase):
    """S062 (2026-08-08_adversarial-F03): step_done wrote the stamp and unpaused
    the parent, then renamed — and the rename is the only one of the three that
    can fail. S052 turned that failure into a refusal, after two mutations were
    already on disk, so a repository went from `all checks pass` to an INV-1
    violation by way of a command that said it had refused. specs.md states the
    contract: no transition may leave INV-1..INV-7 violated."""

    def blocked_pair(self, tmp):
        """S001 active, paused by its blocking child S002, everything green."""
        root = workflow_repo(tmp)
        add_testing_row(root, "S003")
        run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
        run_moltke(root, "--step", "start", "S002")
        run_moltke(root, "--step", "block", "S002", "child")
        add_testing_row(root, "S004")
        self.assertEqual(validate(root).returncode, 0, validate(root).stdout)
        return root

    def test_a_refusal_leaves_the_repository_exactly_as_it_was(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.blocked_pair(tmp)
            before = {p.name: p.read_text(encoding="utf-8")
                      for p in (root / "adocs" / "plan_current").iterdir()}
            (root / "adocs" / "plan_done").rename(root / "adocs" / "plan_done_off")
            result = run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            after = {p.name: p.read_text(encoding="utf-8")
                     for p in (root / "adocs" / "plan_current").iterdir()}
            self.assertEqual(after, before, "a refused completion wrote to the plan tree")

    def test_the_refusal_does_not_create_an_invariant_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.blocked_pair(tmp)
            done = root / "adocs" / "plan_done"
            done.rename(root / "adocs" / "plan_done_off")
            run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
            (root / "adocs" / "plan_done_off").rename(done)   # do what the refusal said
            result = validate(root)
            self.assertEqual(result.returncode, 0,
                             f"the refusal left the tree violating something: {result.stdout}")

    def test_the_parent_is_not_unpaused_by_a_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.blocked_pair(tmp)
            (root / "adocs" / "plan_done").rename(root / "adocs" / "plan_done_off")
            run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
            parent = (root / "adocs" / "plan_current" / "S002_pending.md").read_text(
                encoding="utf-8")
            self.assertRegex(parent, r"paused_by:\s*S004",
                             "the parent was unpaused by a completion that refused")

    def test_a_successful_completion_still_does_all_three(self):
        # Non-vacuity: stamp written, parent unpaused, file moved.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.blocked_pair(tmp)
            result = run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            moved = root / "adocs" / "plan_done" / "S004_child.md"
            self.assertTrue(moved.is_file(), result.stdout)
            self.assertIn(STAMP, moved.read_text(encoding="utf-8"))
            parent = (root / "adocs" / "plan_current" / "S002_pending.md").read_text(
                encoding="utf-8")
            self.assertNotRegex(parent, r"paused_by:\s*S004")
            self.assertEqual(validate(root).returncode, 0)


class TestNoDeadEndCompletion(unittest.TestCase):
    """S070 (2026-08-08_adversarial.2-F04): S062 put the write and the unlink
    ahead of the point of no return and left the parent unpause after it. The
    unpause writes a different file and can fail on its own, and when it did the
    child was already in plan_done/ — leaving a parent paused by a completed
    step that neither --step done nor --step start could clear. Fixing it by
    hand is what --step exists to avoid."""

    def blocked_pair(self, tmp):
        root = workflow_repo(tmp)
        add_testing_row(root, "S003")
        run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
        run_moltke(root, "--step", "start", "S002")
        run_moltke(root, "--step", "block", "S002", "child")
        add_testing_row(root, "S004")
        self.assertEqual(validate(root).returncode, 0, validate(root).stdout)
        return root

    def test_an_unwritable_parent_refuses_before_anything_moves(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.blocked_pair(tmp)
            parent = root / "adocs" / "plan_current" / "S002_pending.md"
            parent.chmod(0o444)
            try:
                result = run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertTrue((root / "adocs" / "plan_current" / "S004_child.md").is_file(),
                                "the child moved despite the refusal")
                self.assertFalse((root / "adocs" / "plan_done" / "S004_child.md").exists())
            finally:
                parent.chmod(0o644)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_the_same_completion_succeeds_once_the_parent_is_writable(self):
        # Non-vacuity: the refusal is about the unwritable file, not about the
        # completion having stopped working.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.blocked_pair(tmp)
            parent = root / "adocs" / "plan_current" / "S002_pending.md"
            parent.chmod(0o444)
            run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
            parent.chmod(0o644)
            result = run_moltke(root, "--step", "done", "S004", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotRegex((root / "adocs" / "plan_current" / "S002_pending.md")
                                .read_text(encoding="utf-8"), r"paused_by:\s*S004")

    def test_a_stale_pause_can_be_cleared_by_the_cli(self):
        # The dead end itself, reached however: a parent paused by a step that is
        # already in plan_done/. Completing the parent must work rather than
        # sending the user to edit a step file by hand.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.blocked_pair(tmp)
            child = root / "adocs" / "plan_current" / "S004_child.md"
            # Set the field rather than appending one: parse_step_file keeps the
            # first occurrence, so an appended done: loses to the empty one.
            child.write_text(moltke.with_field(child.read_text(encoding="utf-8"), "done", STAMP),
                             encoding="utf-8")
            child.rename(root / "adocs" / "plan_done" / "S004_child.md")   # by hand, as Bash would
            self.assertRegex((root / "adocs" / "plan_current" / "S002_pending.md")
                             .read_text(encoding="utf-8"), r"paused_by:\s*S004")
            add_testing_row(root, "S002")
            result = run_moltke(root, "--step", "done", "S002", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("S004", result.stdout, "it should say why it went ahead")
            self.assertEqual(validate(root).returncode, 0)

    def test_a_live_pause_still_refuses(self):
        # Non-vacuity for the clause above: only a pause naming a completed step
        # is stale, and the ordinary refusal has to survive.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.blocked_pair(tmp)
            add_testing_row(root, "S002")
            result = run_moltke(root, "--step", "done", "S002", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("paused by S004", result.stderr)
