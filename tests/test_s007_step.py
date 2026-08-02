"""S007: --step lifecycle operations.

Acceptance: every transition leaves INV-1..INV-7 satisfied, and completion is
refused with the specific missing condition named.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import step_file, workflow_repo

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
