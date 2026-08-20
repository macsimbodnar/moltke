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

    def test_completes_without_a_testing_row_since_dec_048(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "done", "S003", "--stamp",
                                "2026-08-11: verified by the suite gate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_any_nonempty_stamp_completes_since_dec_048(self):
        # The substring gate verified mention, not truth; a stamp is free text.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "done", "S003", "--stamp",
                                "shipped, docs untouched on purpose")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_preserves_an_unindented_parked_entry(self):
        # S094 (2026-08-08_adversarial.4-F07): the collector stopped at the first
        # line that did not start with two spaces or a tab, so a Parked list
        # written flush left — the ordinary markdown for a nested list, and what
        # the shipped template's bare `- Parked:` invites — was silently dropped
        # by a regeneration that runs at every step transition and reports
        # success. Human memory, deleted by a convenience view.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "status.md").write_text(
                "# Status\n\n- Next: whatever\n- Parked:\n"
                "- ask about the licence\n- revisit retry budget\n", encoding="utf-8")
            result = run_moltke(root, "--step", "status")
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            if result.returncode == 0:
                self.assertIn("ask about the licence", status)
                self.assertIn("revisit retry budget", status)
            else:
                # The other outcome this step allows: refuse, say what could not
                # be read, and change nothing.
                self.assertIn("Parked", result.stderr)
                self.assertIn("ask about the licence", status)

    def test_preserves_a_mixed_parked_list(self):
        # Indented continuation under a flush-left entry: both shapes at once,
        # which is what a hand-written list actually looks like.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "status.md").write_text(
                "# Status\n\n- Next: whatever\n- Parked:\n"
                "- ask about the licence\n"
                "  which the vendor has not answered\n"
                "  - revisit retry budget\n", encoding="utf-8")
            self.assertEqual(run_moltke(root, "--step", "status").returncode, 0)
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            for kept in ("ask about the licence", "which the vendor has not answered",
                         "revisit retry budget"):
                self.assertIn(kept, status)

    def test_a_parked_list_survives_repeated_regeneration(self):
        # Carrying it through once is not enough: --step status runs at every
        # transition, so the shape it writes has to be one it can read back.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "status.md").write_text(
                "# Status\n\n- Next: whatever\n- Parked:\n"
                "- ask about the licence\n", encoding="utf-8")
            for _ in range(3):
                self.assertEqual(run_moltke(root, "--step", "status").returncode, 0)
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            self.assertEqual(status.count("ask about the licence"), 1,
                             "the entry must survive without being duplicated")

    def test_blank_lines_inside_the_parked_block_survive(self):
        # S100 (2026-08-09_adversarial-F04): S094 carried the block to the end of
        # the file and still dropped every blank line in it, while specs and the
        # step skill both say "verbatim". Blank lines are markdown structure:
        # paragraphs merge and a heading below the list loses its separation.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            block = ("# Status\n\n- Next: whatever\n- Parked:\n"
                     "  - first note\n"
                     "\n"
                     "  - second note, separated for readability\n"
                     "\n"
                     "## Notes for humans\n"
                     "\n"
                     "  something else entirely\n")
            (root / "adocs" / "status.md").write_text(block, encoding="utf-8")
            self.assertEqual(run_moltke(root, "--step", "status").returncode, 0)
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            tail = status.split("- Parked:\n", 1)[1]
            self.assertEqual(
                tail,
                "  - first note\n"
                "\n"
                "  - second note, separated for readability\n"
                "\n"
                "## Notes for humans\n"
                "\n"
                "  something else entirely\n")

    def test_regeneration_is_idempotent_and_does_not_grow_the_file(self):
        # Trailing blank lines are trimmed, so keeping blank lines cannot make
        # the file grow a line per transition.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "status.md").write_text(
                "# Status\n\n- Next: whatever\n- Parked:\n"
                "  - a note\n\n\n", encoding="utf-8")
            run_moltke(root, "--step", "status")
            once = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            for _ in range(2):
                run_moltke(root, "--step", "status")
            self.assertEqual((root / "adocs" / "status.md").read_text(encoding="utf-8"), once,
                             "a second and third regeneration must be byte-identical")

    def test_the_shipped_template_shows_a_parked_entry(self):
        template = (REPO / "templates" / "adocs" / "status.md").read_text(encoding="utf-8")
        parked = template.split("- Parked:", 1)[1].strip()
        self.assertTrue(parked, "the template's Parked list must show the shape, not just "
                                "the heading, so it is visible rather than inferred")

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


class TestBlockOnAnAlreadyPausedParent(unittest.TestCase):
    """S082 (2026-08-08_adversarial.3-F03): step_block asked only that the
    parent was in plan_current/, never whether it was already paused, and then
    overwrote its paused_by. The second child reported success while taking the
    repository from all checks pass to an INV-1 violation, and the first child's
    pause vanished from the file."""

    def test_a_second_blocking_child_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "block", "S003", "first_child")
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)
            result = run_moltke(root, "--step", "block", "S003", "second_child")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S004", result.stderr, "it should name the child already blocking it")
            self.assertEqual(validate(root).returncode, 0,
                             "a refusal must leave the tree as it was")

    def test_the_first_childs_pause_survives_the_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "block", "S003", "first_child")
            run_moltke(root, "--step", "block", "S003", "second_child")
            parent = (root / "adocs" / "plan_current" / "S003_active.md").read_text(
                encoding="utf-8")
            self.assertRegex(parent, r"paused_by:\s*S004")
            self.assertFalse((root / "adocs" / "plan_current" / "S005_second_child.md").exists(),
                             "the refused child must not have been created")

    def test_blocking_the_child_itself_still_works(self):
        # Non-vacuity: the stack is legal, and deepening it is how blocking work
        # discovered inside blocking work is meant to be recorded.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--step", "block", "S003", "first_child")
            result = run_moltke(root, "--step", "block", "S004", "grandchild")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(validate(root).returncode, 0)


class TestNewAndBlockWriteLast(unittest.TestCase):
    """S083 (2026-08-08_adversarial.3-F04): step_new and step_block wrote the
    step file before the plan entry, so a failure appending to plan.md left an
    id no list entry names, which is INV-3 — and for block, an unpaused parent
    too. The half-apply class S062 and S070 fixed for done, unfixed for its two
    siblings."""

    def unwritable_plan(self, root):
        plan = root / "adocs" / "plan.md"
        plan.chmod(0o444)
        return plan

    def test_step_new_leaves_nothing_behind_when_the_plan_cannot_be_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            plan = self.unwritable_plan(root)
            try:
                result = run_moltke(root, "--step", "new", "widget")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertFalse((root / "adocs" / "plan_todo" / "S004_widget.md").exists(),
                                 "a step file with no plan entry is INV-3")
            finally:
                plan.chmod(0o644)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_step_block_leaves_nothing_behind_when_the_plan_cannot_be_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            plan = self.unwritable_plan(root)
            try:
                result = run_moltke(root, "--step", "block", "S003", "dep")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertFalse((root / "adocs" / "plan_current" / "S004_dep.md").exists())
                parent = (root / "adocs" / "plan_current" / "S003_active.md").read_text(
                    encoding="utf-8")
                self.assertNotRegex(parent, r"paused_by:\s*S004")
            finally:
                plan.chmod(0o644)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_both_still_work_normally(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.assertEqual(run_moltke(root, "--step", "new", "widget").returncode, 0)
            self.assertEqual(run_moltke(root, "--step", "block", "S003", "dep").returncode, 0)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)
            self.assertTrue((root / "adocs" / "plan_todo" / "S004_widget.md").is_file())
            self.assertTrue((root / "adocs" / "plan_current" / "S005_dep.md").is_file())


class TestStepNameValidation(unittest.TestCase):
    """S088 (2026-08-08_adversarial.4-F01): the short name went straight into a
    filename. STEP_FILE_RE accepts `[A-Za-z0-9_]+`, so a hyphen produced a file
    every scanner keyed on that pattern skips while plan.md listed the id — the
    listed-but-absent half of INV-3, created by the tool that exists to keep the
    two in step. `--audit new` already refuses its type for the same reason."""

    def plan_ids(self, root):
        return re.findall(r"S\d{3}", (root / "adocs" / "plan.md").read_text(encoding="utf-8"))

    def test_new_refuses_a_hyphenated_name_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            before = self.plan_ids(root)
            result = run_moltke(root, "--step", "new", "fix-parser")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("A-Za-z0-9_", result.stderr)
            self.assertEqual(list((root / "adocs" / "plan_todo").glob("*fix*")), [],
                             "a refused name may not leave a step file behind")
            self.assertEqual(self.plan_ids(root), before,
                             "a refused name may not leave an id listed in plan.md")
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_block_refuses_a_hyphenated_name_and_leaves_the_parent_unpaused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            before = self.plan_ids(root)
            result = run_moltke(root, "--step", "block", "S003", "fix-parser")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("A-Za-z0-9_", result.stderr)
            parent = (root / "adocs" / "plan_current" / "S003_active.md").read_text(
                encoding="utf-8")
            self.assertNotIn("S004", parent, "the parent may not be paused by a refused child")
            self.assertEqual(
                [p.name for p in (root / "adocs" / "plan_current").iterdir()],
                ["S003_active.md"])
            self.assertEqual(self.plan_ids(root), before)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_a_traversing_name_stays_inside_the_marked_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "new", "../../../escaped")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(list(Path(tmp).glob("**/*escaped*")), [],
                             "nothing may be created outside the plan directory")
            self.assertFalse((root.parent / "escaped").exists())
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_awkward_names_are_refused_before_they_reach_the_filesystem(self):
        for name in ("with space", "sub/dir", "..", ".", "", "tab\there", "rm;ls",
                     "trailing.md", "dot.name"):
            for argv in (("new", name), ("block", "S003", name)):
                with self.subTest(name=name, op=argv[0]), tempfile.TemporaryDirectory() as tmp:
                    root = workflow_repo(tmp)
                    result = run_moltke(root, "--step", *argv)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertEqual(validate(root).returncode, 0)

    def test_ordinary_names_still_work(self):
        # Non-vacuity: the guard must not refuse the names the workflow uses.
        # Without this a rule refusing everything would pass every case above.
        for name in ("fix_parser", "S095_like_name", "step2", "UPPER_case"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                result = run_moltke(root, "--step", "new", name)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue((root / "adocs" / "plan_todo" / f"S004_{name}.md").is_file())
                self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_block_still_creates_an_ordinary_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "block", "S003", "fix_parser")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "adocs" / "plan_current" / "S004_fix_parser.md").is_file())
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_a_missing_name_still_prints_usage(self):
        # The guard reads rest[0]; reading it before the IndexError handler
        # would turn a missing argument into a traceback instead of usage.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for argv in (("new",), ("block", "S003")):
                with self.subTest(op=argv):
                    result = run_moltke(root, "--step", *argv)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn("usage", result.stderr)


class TestDestinationNeverClobbered(unittest.TestCase):
    """S089 (2026-08-08_adversarial.4-F02): the completion write went straight to
    `plan_done/<name>.md`. With the same id in both directories — an INV-6
    violation, which `--validate` reports rather than prevents — the write
    overwrote the finished step with the in-progress one, destroying the history
    AGENTS.md §11 forbids the agent from touching, from the command whose own
    documentation calls that directory immutable."""

    def duplicate(self, root):
        """The same id in plan_current/ and plan_done/, with bodies that differ
        so a clobber is visible rather than inferred."""
        return step_file(root / "adocs" / "plan_done", "S003", "active",
                         done="2026-08-01 the original completion, README and MANUAL checked")

    def test_done_refuses_a_duplicate_id_and_leaves_history_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            history = self.duplicate(root)
            before = history.read_bytes()
            add_testing_row(root, "S003")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S003", result.stderr)
            self.assertIn("INV-6", result.stderr)
            self.assertEqual(history.read_bytes(), before,
                             "plan_done/ is immutable history and may not be overwritten")
            self.assertIn("2026-08-01 the original completion",
                          history.read_text(encoding="utf-8"),
                          "the original done: stamp must survive")
            self.assertTrue((root / "adocs" / "plan_current" / "S003_active.md").is_file(),
                            "a refused completion leaves the source where it was")

    def test_done_refuses_before_the_suite_gate_runs(self):
        # S070's rule: nothing is written, and nothing expensive is run, until
        # every precondition holds. A gate that runs first would spend the
        # suite's wall clock to then refuse.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.duplicate(root)
            add_testing_row(root, "S003")
            marker = json.loads((root / ".moltke.json").read_text(encoding="utf-8"))
            marker["test_command"] = f"{sys.executable} -c \"open('ran','w').close()\""
            (root / ".moltke.json").write_text(json.dumps(marker), encoding="utf-8")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse((root / "ran").exists(),
                             "the duplicate is refused before the suite gate spends its time")

    def test_start_refuses_when_the_destination_name_is_taken(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            # The same id in plan_todo/ and plan_current/. locate_step searches
            # plan_todo first, so --step start reads the todo copy, decides the
            # step is not yet current, and renames it onto the file of the same
            # name already in plan_current/.
            occupied = step_file(root / "adocs" / "plan_current", "S002", "pending",
                                 touches="the copy already in plan_current")
            # The limits are raised so the active and stack gates pass and the
            # rename is what the test actually reaches; at the default 1 this
            # refuses on plan_active_max and proves nothing about clobbering.
            marker = json.loads((root / ".moltke.json").read_text(encoding="utf-8"))
            marker["plan_active_max"] = 3
            (root / ".moltke.json").write_text(json.dumps(marker), encoding="utf-8")
            before = occupied.read_bytes()
            result = run_moltke(root, "--step", "start", "S002")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-6", result.stderr)
            self.assertEqual(occupied.read_bytes(), before,
                             "an occupied destination may not be replaced")
            self.assertTrue((root / "adocs" / "plan_todo" / "S002_pending.md").is_file(),
                            "a refused start leaves the source where it was")

    def test_an_ordinary_completion_and_start_still_work(self):
        # Non-vacuity: the guard must not refuse the transitions it protects.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            add_testing_row(root, "S003")
            done = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertTrue((root / "adocs" / "plan_done" / "S003_active.md").is_file())
            start = run_moltke(root, "--step", "start", "S002")
            self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
            self.assertTrue((root / "adocs" / "plan_current" / "S002_pending.md").is_file())
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)


class TestStepOwnership(unittest.TestCase):
    """S121 (DEC-045): the plan is common and a step is claimed at start.
    --step start stamps author: from git config user.name, and INV-1 counts
    non-paused steps per author, so branch-per-member merges where each branch
    carries its owner's active step stay green while one person still cannot
    hold two."""

    def repo(self, tmp, name="alice"):
        root = workflow_repo(tmp)
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", name], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
        return root

    def test_start_stamps_the_author(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            (root / "adocs" / "plan_current" / "S003_active.md").rename(
                root / "adocs" / "plan_todo" / "S003_active.md")
            result = run_moltke(root, "--step", "start", "S003")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            fields = self.parse(root / "adocs" / "plan_current" / "S003_active.md")
            self.assertEqual(fields.get("author"), "alice")

    def parse(self, path):
        from surface import moltke
        return moltke.parse_step_file(path)

    def test_two_authors_may_each_hold_an_active_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active", author="alice")
            step_file(root / "adocs" / "plan_current", "S004", "second", author="bob")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            result = validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_one_author_still_cannot_hold_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active", author="alice")
            step_file(root / "adocs" / "plan_current", "S004", "second", author="alice")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            result = validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("alice", result.stdout)

    def test_start_is_refused_only_against_your_own_active_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp, name="bob")
            step_file(root / "adocs" / "plan_current", "S003", "active", author="alice")
            mine = run_moltke(root, "--step", "start", "S002")
            self.assertEqual(mine.returncode, 0,
                             "alice's active step must not block bob: "
                             + mine.stdout + mine.stderr)
            again = run_moltke(root, "--step", "new", "third_thing")
            self.assertEqual(again.returncode, 0)
            blocked = run_moltke(root, "--step", "start", "S004")
            self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
            self.assertIn("bob", blocked.stderr)

    def test_unowned_steps_share_one_bucket(self):
        # The solo fixture shape, unchanged: no git config, no author fields,
        # and two unowned active steps still violate.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S004", "second")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            result = validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


class TestStepIdCeiling(unittest.TestCase):
    """S097 (2026-08-09_adversarial-F01): `next_step_id` has no upper bound, and
    every id scan required exactly three digits. Past S999 the allocator produced
    an id nothing in the tool could read: the file lands in plan_todo/, the entry
    lands in plan.md, and `plan_steps`, `plan_order`, `derived_next`, `--roadmap`
    and all sixteen invariants are blind to it at once, with `--validate` green.

    S136 widens the recognised form to four digits, so the ceiling moves with it:
    S1000 is now an id every reader sees, and the refusal starts one past S9999,
    the widest form written. The ceiling is what keeps the two ends in step —
    beyond the widest recognised form the allocator would mint an unreadable id
    again, so it refuses and names the condition instead.
    """

    def at_the_ceiling(self, tmp):
        """A tree that passes every check, whose plan.md mentions S9999 in prose.

        The shipped templates/adocs/plan.md invites exactly this: "An id named in
        a sentence anywhere else in this file is prose: it does not change the
        order, and it is not checked."
        """
        root = workflow_repo(tmp)
        plan = root / "adocs" / "plan.md"
        plan.write_text("# Plan\n\nThe long tail of this work is tracked under S9999.\n\n"
                        "1. S001 base\n2. S002 pending\n3. S003 active\n", encoding="utf-8")
        self.assertEqual(validate(root).returncode, 0,
                         "precondition: the fixture must be green before the allocation")
        return root

    def test_new_refuses_past_the_ceiling_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.at_the_ceiling(tmp)
            before = (root / "adocs" / "plan.md").read_bytes()
            result = run_moltke(root, "--step", "new", "later_work")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S9999", result.stderr)
            self.assertIn("adocs/plan.md", result.stderr,
                          "the refusal must name where the ceiling came from")
            self.assertEqual((root / "adocs" / "plan.md").read_bytes(), before)
            self.assertEqual(list((root / "adocs" / "plan_todo").glob("*later_work*")), [])
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_block_refuses_past_the_ceiling_and_leaves_the_parent_unpaused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.at_the_ceiling(tmp)
            result = run_moltke(root, "--step", "block", "S003", "later_work")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S9999", result.stderr)
            parent = (root / "adocs" / "plan_current" / "S003_active.md").read_text(
                encoding="utf-8")
            self.assertNotIn("S10000", parent)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_no_id_wider_than_the_recognised_form_reaches_the_disk_or_the_plan(self):
        # The shape the defect produced, pinned directly: a file and a plan entry
        # that exist and that no scanner in the tool can read.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.at_the_ceiling(tmp)
            run_moltke(root, "--step", "new", "later_work")
            for directory in ("plan_todo", "plan_current", "plan_done"):
                self.assertEqual(
                    [p.name for p in (root / "adocs" / directory).iterdir()
                     if re.match(r"^S\d{5,}_", p.name)], [], directory)
            self.assertNotRegex((root / "adocs" / "plan.md").read_text(encoding="utf-8"),
                                r"\bS\d{5,}\b")

    def test_the_highest_id_below_the_ceiling_still_allocates(self):
        # Non-vacuity: S9999 itself is a legal id, so the refusal starts at the
        # step after it and not at the step that reaches it.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            plan = root / "adocs" / "plan.md"
            plan.write_text("# Plan\n\nA note about S9998.\n\n"
                            "1. S001 base\n2. S002 pending\n3. S003 active\n", encoding="utf-8")
            result = run_moltke(root, "--step", "new", "the_last_one")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "adocs" / "plan_todo" / "S9999_the_last_one.md").is_file())
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_ordinary_allocation_is_untouched(self):
        # The other non-vacuity anchor: a guard that refused everything would
        # pass every test above.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--step", "new", "ordinary")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "adocs" / "plan_todo" / "S004_ordinary.md").is_file())
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_the_step_after_s999_allocates_and_every_reader_sees_it(self):
        """S136: the old ceiling is now an ordinary allocation. Both halves are
        asserted together on purpose — an id the allocator hands out and no
        reader can see is the defect, not the fix."""
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            plan = root / "adocs" / "plan.md"
            plan.write_text("# Plan\n\nA note about S999.\n\n"
                            "1. S001 base\n2. S002 pending\n3. S003 active\n", encoding="utf-8")
            result = run_moltke(root, "--step", "new", "past_the_old_ceiling")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            path = root / "adocs" / "plan_todo" / "S1000_past_the_old_ceiling.md"
            self.assertTrue(path.is_file())
            self.assertIn("4. S1000", (root / "adocs" / "plan.md").read_text(encoding="utf-8"))
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)
            # Read back through the CLI, not through the file it just wrote.
            self.assertIn("S1000", run_moltke(root, "--roadmap").stdout)
            done = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            started = run_moltke(root, "--step", "start", "S1000")
            self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
            self.assertTrue(
                (root / "adocs" / "plan_current" / "S1000_past_the_old_ceiling.md").is_file())
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_an_id_wider_than_the_recognised_form_on_disk_refuses_allocation(self):
        """S136: the counter is computed from ids it can read, so a width it
        cannot read is an id it can hand out twice — which is how S1000 was
        minted twice before S097. Any id-shaped filename bumps the counter now,
        and a width past the ceiling turns into the loud refusal."""
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "plan_todo" / "S10000_from_the_future.md").write_text(
                "id:         S10000\ngoal:       arrived by hand\n", encoding="utf-8")
            self.assertEqual(validate(root).returncode, 0,
                             "precondition: nothing reads this file, so the tree is green")
            result = run_moltke(root, "--step", "new", "later_work")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S10000_from_the_future.md", result.stderr,
                          "the refusal must name the file the counter tripped over")
            self.assertEqual(list((root / "adocs" / "plan_todo").glob("*later_work*")), [])

    def test_an_allocated_id_is_never_one_already_on_disk(self):
        """The property behind both: `--step new` twice in a row, with the first
        id left where it landed, must not mint it again."""
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for name in ("first", "second", "third"):
                self.assertEqual(run_moltke(root, "--step", "new", name).returncode, 0, name)
            todo = sorted(p.name for p in (root / "adocs" / "plan_todo").iterdir())
            self.assertEqual(todo, ["S002_pending.md", "S004_first.md",
                                    "S005_second.md", "S006_third.md"])
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)


class TestWrittenFieldValuesRoundTrip(unittest.TestCase):
    """S099 (2026-08-09_adversarial-F03): S095 gave `parse_step_file` a rule for
    multi-line values and no writer honoured the other half of it. `write_step`,
    `append_to_plan` and `with_field` interpolate a value into one f-string, so a
    newline lands flush left — the one shape the parser is documented to drop.

    Two consequences, both on a success path. `--goal` with a newline puts a list
    entry into `plan.md` that no one typed, and `--validate` then reports it.
    `--stamp` with the README and MANUAL mention on its second line passes the
    gate that reads the string, writes a file that reads back without it, and
    blocks every Stop for the rest of the turn with a remedy that cannot be
    followed: the file is under `plan_done/`, which `--pre-write` refuses, and
    editing it from Bash turns the block into an INV-7 violation."""

    def parsed(self, path):
        from surface import moltke
        return moltke.parse_step_file(path)

    def test_a_goal_with_a_newline_never_reaches_plan_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            before = (root / "adocs" / "plan.md").read_bytes()
            result = run_moltke(root, "--step", "new", "fold_lines",
                                "--goal", "teach the parser to fold lines\n"
                                          "2. S999 injected by a newline")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual((root / "adocs" / "plan.md").read_bytes(), before)
            self.assertEqual(list((root / "adocs" / "plan_todo").glob("*fold_lines*")), [])
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_a_stamp_with_a_newline_completes_and_folds_back(self):
        # DEC-048 flips S099's stamp half: continuations are the file format's
        # own syntax, so a multi-line stamp is written indented and reads back
        # whitespace-normalized. --goal keeps the one-line refusal.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            stamp = "2026-08-11: suite green.\nDocs checked, no change needed."
            result = run_moltke(root, "--step", "done", "S003", "--stamp", stamp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            written = self.parsed(root / "adocs" / "plan_done" / "S003_active.md")
            self.assertEqual(written["done"], stamp.replace("\n", " "))
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_a_goal_written_by_the_cli_reads_back_whole(self):
        # The round trip the S095 tests skipped by hand-writing their fixtures,
        # which is why that step did not catch this.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            goal = "teach the parser to fold lines, and keep the plan entry on one line"
            result = run_moltke(root, "--step", "new", "round_trip", "--goal", goal)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            written = self.parsed(root / "adocs" / "plan_todo" / "S004_round_trip.md")
            self.assertEqual(written["goal"], goal)
            plan = (root / "adocs" / "plan.md").read_text(encoding="utf-8")
            self.assertIn(f"S004  {goal}", plan)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_a_stamp_written_by_the_cli_reads_back_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            add_testing_row(root, "S003")
            stamp = ("2026-08-09: suite green, 422 tests. README and MANUAL checked, "
                     "no change needed.")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", stamp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            written = self.parsed(root / "adocs" / "plan_done" / "S003_active.md")
            self.assertEqual(written["done"], stamp,
                             "the stamp the gate accepted and the stamp the file carries "
                             "must be the same string")

    def test_a_completed_step_never_fails_the_gate_that_let_it_through(self):
        # The wedge, stated as the property: nothing reachable through --step
        # leaves plan_done/ holding a stamp the Stop gate rejects.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            for args in (("add", "-A"), ("-c", "user.name=t", "-c", "user.email=t@t",
                                         "commit", "-qm", "base")):
                subprocess.run(["git", "-C", str(root), *args], check=True,
                               stdout=subprocess.DEVNULL)
            add_testing_row(root, "S003")
            run_moltke(root, "--step", "done", "S003", "--stamp",
                       "2026-08-09: green. README and MANUAL checked.")
            run_moltke(root, "--step", "status")
            problems = run_moltke(root, "--stop").stderr
            self.assertNotIn("without the README and MANUAL check recorded", problems)


class TestPlanPruning(unittest.TestCase):
    """S105 (DEC-042): plan.md grew one line per step forever — 68 bytes/step in
    an always-read file. --step done now prunes completed entries, keeping the
    last 5 done in plan order plus everything open, so plan.md is bounded by
    open work rather than by project age. plan_done/ keeps every id, so
    next_step_id and the S097 ceiling still see all of history."""

    def crowded(self, tmp):
        """Eight done steps listed and filed, one active, one pending."""
        root = workflow_repo(tmp)
        plan = ["# Plan", ""]
        for n in range(4, 12):
            step_file(root / "adocs" / "plan_done", f"S{n:03d}", f"old{n}",
                      done="2026-08-01 done, README and MANUAL checked")
            plan.append(f"{n - 3}. S{n:03d}  old{n}")
            add_testing_row(root, f"S{n:03d}")
        plan += ["9. S001  base", "10. S002  pending", "11. S003  active"]
        (root / "adocs" / "plan.md").write_text("\n".join(plan) + "\n", encoding="utf-8")
        add_testing_row(root, "S003")
        self.assertEqual(validate(root).returncode, 0, "precondition: fixture green")
        return root

    def test_done_prunes_to_the_last_five_done_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.crowded(tmp)
            result = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            plan = (root / "adocs" / "plan.md").read_text(encoding="utf-8")
            listed = re.findall(r"^\s*(?:\d+\.|[-*])\s+(S\d{3})\b", plan, re.M)
            done_listed = [s for s in listed if s not in ("S002",)]
            self.assertEqual(len(done_listed), 5,
                             f"five done entries kept, got {done_listed}")
            self.assertIn("S003", listed, "the just-completed step is the newest done")
            self.assertIn("S002", listed, "open work is never pruned")
            self.assertNotIn("S004", listed, "the oldest done entries are pruned")
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_derivations_survive_a_pruned_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.crowded(tmp)
            run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            run_moltke(root, "--step", "status")
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            self.assertIn("Last done: S003", status)
            self.assertIn("Next: S002", status)
            roadmap = run_moltke(root, "--roadmap")
            self.assertEqual(roadmap.returncode, 0, roadmap.stdout + roadmap.stderr)
            self.assertIn("10 done", roadmap.stdout,
                          "done count comes from plan_done/, not from the pruned list")

    def test_the_next_id_still_clears_every_pruned_id(self):
        # DEC-008: ids are never reused. The pruned entries live on as
        # plan_done/ filenames, which next_step_id also reads.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.crowded(tmp)
            run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            result = run_moltke(root, "--step", "new", "after_pruning")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "adocs" / "plan_todo" / "S012_after_pruning.md").is_file())

    def test_a_small_plan_is_not_pruned(self):
        # Non-vacuity: with five or fewer done entries nothing changes, so the
        # base fixture's shape survives an ordinary completion untouched.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            add_testing_row(root, "S003")
            run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            plan = (root / "adocs" / "plan.md").read_text(encoding="utf-8")
            for kept in ("S001", "S002", "S003"):
                self.assertIn(kept, plan)


class TestTestingWindow(unittest.TestCase):
    """S126 (DEC-048): testing.md grew forever by rule — the largest file in the
    repository, scanned by nothing since DEC-048, read by no one. --step done
    prunes rows whose steps left the plan window; git keeps every row."""

    def test_rows_for_pruned_steps_are_pruned_with_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            plan = ["# Plan", ""]
            testing = root / "adocs" / "testing.md"
            for n in range(4, 12):
                step_file(root / "adocs" / "plan_done", f"S{n:03d}", f"old{n}",
                          done="2026-08-01 done")
                plan.append(f"{n - 3}. S{n:03d}  old{n}")
                add_testing_row(root, f"S{n:03d}")
            plan += ["9. S001  base", "10. S002  pending", "11. S003  active"]
            (root / "adocs" / "plan.md").write_text("\n".join(plan) + "\n",
                                                    encoding="utf-8")
            add_testing_row(root, "S002")
            result = run_moltke(root, "--step", "done", "S003", "--stamp", "done, verified")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            rows = testing.read_text(encoding="utf-8")
            self.assertNotIn("S004", rows, "rows leave with their pruned plan entries")
            self.assertIn("S011", rows, "the kept window's rows stay")
            self.assertIn("S002", rows, "open work's rows are never pruned")
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)


class TestMultilineStepFields(unittest.TestCase):
    """S095: `parse_step_file` matched `^([a-z_]+):\\s*(.*)$` per line, and an
    indented continuation line matches nothing, so every field was silently
    truncated to its first line. Found live during S059: the Stop stamp gate
    reported the README and MANUAL check missing from a stamp that recorded it,
    two lines down. goal:, accepts:, touches: and excludes: already span lines
    across the plan directories, so every reader of those had been seeing the
    first line alone."""

    def parse(self, text):
        from surface import moltke
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "S004_x.md"
            path.write_text(text, encoding="utf-8")
            return moltke.parse_step_file(path)

    def test_a_continuation_line_is_part_of_the_field(self):
        fields = self.parse("id:         S004\n"
                            "goal:       first line\n"
                            "            second line\n"
                            "done:\n")
        self.assertEqual(fields["goal"], "first line second line")

    def stop_over_a_stamp(self, tmp, second_line):
        """--stop's stderr for a step arriving in plan_done/ with a two-line stamp."""
        root = workflow_repo(tmp)
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        for args in (("add", "-A"), ("-c", "user.name=t", "-c", "user.email=t@t",
                                     "commit", "-qm", "base")):
            subprocess.run(["git", "-C", str(root), *args], check=True,
                           stdout=subprocess.DEVNULL)
        (root / "adocs" / "plan_done" / "S004_late.md").write_text(
            "id:         S004\n"
            "goal:       late\n"
            "done:       2026-08-09: the work is finished and the suite is green,\n"
            f"            {second_line}\n",
            encoding="utf-8")
        (root / "adocs" / "plan.md").write_text(
            "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
        add_testing_row(root, "S004")
        return run_moltke(root, "--stop").stderr

    def test_a_stamp_whose_doc_check_is_on_the_second_line_satisfies_the_stop_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            problems = self.stop_over_a_stamp(tmp, "README and MANUAL checked, no change.")
            self.assertNotIn("without the README and MANUAL check recorded", problems)

    def test_a_two_line_stamp_reads_back_folded(self):
        # DEC-048: multi-line stamps fold back through parse_step_file; the
        # wording gates are gone, so only presence is judged.
        with tempfile.TemporaryDirectory() as tmp:
            problems = self.stop_over_a_stamp(tmp, "second line of the stamp.")
            self.assertNotIn("without a done: stamp", problems)

    def test_a_flush_left_line_that_looks_like_a_field_starts_a_new_one(self):
        fields = self.parse("id:         S004\n"
                            "goal:       first line\n"
                            "note: not a continuation\n")
        self.assertEqual(fields["goal"], "first line")
        self.assertEqual(fields["note"], "not a continuation")

    def test_a_blank_line_ends_a_field(self):
        fields = self.parse("id:         S004\n"
                            "goal:       first line\n"
                            "\n"
                            "  loose prose under the fields\n")
        self.assertEqual(fields["goal"], "first line")

    def test_setting_a_field_removes_the_lines_it_used_to_span(self):
        # Without this, making continuations meaningful turns every set_field on
        # a multi-line field into duplicated text — a new silent defect in place
        # of the one being removed.
        from surface import moltke
        text = ("id:         S004\n"
                "paused_by:  S005  # 2026-08-09\n"
                "            stale continuation\n"
                "done:\n")
        rewritten = moltke.with_field(text, "paused_by", "")
        self.assertNotIn("stale continuation", rewritten)
        self.assertIn("done:", rewritten)


class TestAClaimCanBeUndone(unittest.TestCase):
    """S154 (DEC-056, DEC-058): `--step` offered new, start, block, unpause,
    done and status, and nothing that undoes a claim. Twice the answer was to
    move a step out of `plan_current/` by hand, against §2's rule that the plan
    directories are moved only by `--step`. `unclaim` is `start` run backwards:
    the file returns to `plan_todo/` and the `author:` stamp `start` wrote comes
    off with it, because `author:` is the claim."""

    def repo(self, tmp):
        root = workflow_repo(tmp)
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Tester"],
                       check=True)
        return root

    def unclaim(self, root, step_id="S003"):
        return run_moltke(root, "--step", "unclaim", step_id)

    def test_a_claimed_step_returns_to_plan_todo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            self.assertEqual(run_moltke(root, "--step", "start", "S002").returncode, 0)
            result = self.unclaim(root, "S002")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "adocs" / "plan_todo" / "S002_pending.md").is_file())
            self.assertFalse((root / "adocs" / "plan_current" / "S002_pending.md").exists())
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_the_author_stamp_comes_off_with_the_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            run_moltke(root, "--step", "start", "S002")
            claimed = (root / "adocs" / "plan_current" / "S002_pending.md").read_text(
                encoding="utf-8")
            self.assertIn("Tester", claimed, "precondition: --step start stamped an author")
            self.unclaim(root, "S002")
            returned = (root / "adocs" / "plan_todo" / "S002_pending.md").read_text(
                encoding="utf-8")
            self.assertNotIn("Tester", returned)
            self.assertIn("author:", returned, "the field stays, emptied, like every cleared field")

    def test_it_clears_nothing_but_the_author(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            path = root / "adocs" / "plan_current" / "S003_active.md"
            path.write_text("id:         S003\n"
                            "goal:       active\n"
                            "accepts:    a testable thing\n"
                            "            spanning two lines\n"
                            "touches:    bin/moltke.py\n"
                            "decisions:  DEC-001\n"
                            "closes:     2026-08-01_adversarial-F01\n"
                            "blocks:\n"
                            "author:     Tester\n"
                            "done:\n", encoding="utf-8")
            self.assertEqual(self.unclaim(root).returncode, 0)
            returned = (root / "adocs" / "plan_todo" / "S003_active.md").read_text(
                encoding="utf-8")
            for kept in ("a testable thing", "spanning two lines", "bin/moltke.py",
                         "DEC-001", "2026-08-01_adversarial-F01"):
                self.assertIn(kept, returned)

    def test_a_step_that_was_never_claimed_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            result = self.unclaim(root, "S002")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("plan_todo", result.stderr)

    def test_a_completed_step_is_refused_as_immutable_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            result = self.unclaim(root, "S001")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("plan_done", result.stderr)
            self.assertTrue((root / "adocs" / "plan_done" / "S001_base.md").is_file())

    def test_a_step_that_does_not_exist_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            result = self.unclaim(root, "S099")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S099", result.stderr)

    def test_a_stamped_step_in_plan_current_is_refused(self):
        # A stamp is the evidence a step finished. Sending one back to plan_todo/
        # would make the plan claim unstarted work that records its own
        # completion, and --step done would then refuse it as a duplicate id the
        # moment it was completed properly.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            path = root / "adocs" / "plan_current" / "S003_active.md"
            path.write_text("id:         S003\ngoal:       active\n"
                            "done:       2026-08-01 the work is finished\n",
                            encoding="utf-8")
            result = self.unclaim(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("done:", result.stderr)
            self.assertTrue(path.is_file(), "the refusal moved nothing")

    def test_a_step_with_a_live_blocking_child_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            self.assertEqual(
                run_moltke(root, "--step", "block", "S003", "blocker").returncode, 0)
            result = self.unclaim(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S004", result.stderr, "the refusal names the child")
            self.assertTrue((root / "adocs" / "plan_current" / "S003_active.md").is_file())

    def test_an_unresolvable_pause_is_sent_to_unpause_rather_than_moved(self):
        # A phantom pauser is not a child in plan_current/, but carrying the
        # pause back to plan_todo/ would hide a violation --validate reports.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active",
                      paused_by="S099  # 2026-08-01")
            result = self.unclaim(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("--step unpause S003", result.stderr,
                          "the refusal must route to the command that clears the pause; "
                          "a bare \"unpause\" is in the unknown-operation message too")
            self.assertIn("S099", result.stderr, "and name the pauser")

    def test_unclaiming_frees_the_active_slot(self):
        # The whole point (DEC-056): plan_active_max is 1, and the by-hand move
        # existed because a claimed step could not step aside for another.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active", author="Tester")
            blocked = run_moltke(root, "--step", "start", "S002")
            self.assertEqual(blocked.returncode, 1, "precondition: the slot is taken")
            self.assertEqual(self.unclaim(root).returncode, 0)
            freed = run_moltke(root, "--step", "start", "S002")
            self.assertEqual(freed.returncode, 0, freed.stdout + freed.stderr)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_a_blocking_child_may_be_unclaimed_and_says_what_it_leaves_paused(self):
        # The other side of the block relation, permitted on purpose: refusing
        # here too would make a claimed stack impossible to put down, since the
        # parent is refused for its pause and the child for its parent. The
        # state it leaves is green and one command from repaired, so it is
        # reported instead.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            run_moltke(root, "--step", "block", "S003", "blocker")
            result = self.unclaim(root, "S004")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("S003 stays paused by S004", result.stdout)
            self.assertIn("--step start S004", result.stdout)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)
            resumed = run_moltke(root, "--step", "start", "S004")
            self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_usage_is_named_when_the_id_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(tmp)
            result = run_moltke(root, "--step", "unclaim")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("unclaim <id>", result.stderr)


class TestThisRepositoryPassesValidate(unittest.TestCase):
    """S153 (2026-08-19_adversarial-F13): the non-vacuity anchor for this file.
    `goal:`, `accepts:`, `touches:` and `excludes:` span lines all over `adocs/`,
    so a change to how fields are read has to leave the real tree green. It used
    to sit inside `TestMultilineStepFields`, which named the wrong thing on
    failure: an untriaged audit finding turned "multiline step fields" red."""

    def test_this_repository_still_validates(self):
        result = run_moltke(REPO, "--validate")
        self.assertEqual(
            result.returncode, 0,
            "this repository does not pass --validate.\n"
            "INV-10 lines here are the expected transient between writing an audit "
            "report and giving its findings a home: the report and the steps that "
            "close it land in one commit (skills/audit/SKILL.md step 4). "
            "Any other violation is a real break.\n"
            + result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
