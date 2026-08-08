"""S003: INV-1..INV-7 against broken fixture repositories."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import step_file, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"


def run_validate(cwd):
    return subprocess.run(
        [sys.executable, str(MOLTKE), "--validate"],
        cwd=cwd, capture_output=True, text=True,
    )


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        capture_output=True, text=True, check=True,
    )


def git_baseline(root):
    for args in (("init", "-q"), ("add", "-A"), ("commit", "-qm", "base")):
        git(root, *args)


class TestInvariants(unittest.TestCase):
    def assert_violation(self, root, needle):
        result = run_validate(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(needle, result.stdout)

    def test_valid_tree_passes(self):
        # Non-vacuity anchor: every broken variant below starts from this tree.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv1_too_many_non_paused_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S004", "second")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            self.assert_violation(root, "INV-1")

    def test_inv1_paused_steps_do_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S004", "paused_parent",
                      paused_by="S003")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv2_stack_depth_exceeded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            current = root / "adocs" / "plan_current"
            for step_id in ("S004", "S005", "S006"):
                step_file(current, step_id, "paused", paused_by="S003")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001\n2. S002\n3. S003\n4. S004\n5. S005\n6. S006\n",
                encoding="utf-8")
            self.assert_violation(root, "INV-2")

    def test_inv3_step_missing_from_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_todo", "S009", "orphan")
            self.assert_violation(root, "INV-3")

    def test_inv3_a_step_named_only_in_prose_is_not_listed(self):
        # S048 (.2-F02): S045 narrowed plan_order to list entries and left INV-3
        # reading the whole file, so the two disagreed about what "listed" means.
        # A step could satisfy the invariant and still never become next.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\nS001 laid the base. Next we will do S002, then think about it.\n\n"
                "1. S001  base\n3. S003  active\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-3", result.stdout)
            self.assertIn("S002", result.stdout)

    def test_inv3_a_prose_id_is_neither_listed_nor_a_phantom(self):
        # One definition, both directions: prose is prose. A mention that has no
        # step file does not reorder anything and is not reported either.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\nEarlier we considered S404 and dropped it.\n\n"
                "1. S001  base\n2. S002  pending\n3. S003  active\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv3_the_message_no_longer_claims_a_phantom_is_next(self):
        # S045 made that sentence false: derived_next reads list entries only.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001\n2. S002\n3. S003\n4. S099  typo\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("S099", result.stdout)
            self.assertNotIn("is the derived next step", result.stdout)

    def test_inv3_plan_id_with_no_step_file(self):
        # S024 (F11): a mistyped id becomes the derived next step forever, and
        # status.md agrees with it, so nothing looks wrong.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001\n2. S002\n3. S003\n4. S099 typo\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-3", result.stdout)
            self.assertIn("S099", result.stdout)

    def test_inv3_ignores_a_phantom_id_that_is_only_guidance(self):
        # The scaffolded plan.md ships a commented example step; counting it
        # would make every fresh repository violate INV-3 on creation.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n<!-- 1. S099  example -->\n\n1. S001\n2. S002\n3. S003\n",
                encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv3_counts_a_completed_step_as_present(self):
        # Non-vacuity for the check above: plan_done/ holds S001, and a plan that
        # lists it must stay legal or every finished project would be a violation.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("S001", (root / "adocs" / "plan.md").read_text(encoding="utf-8"))
            self.assertTrue((root / "adocs" / "plan_done" / "S001_base.md").is_file())

    def test_inv4_done_step_still_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_todo", "S002", "pending", blocks="S001")
            self.assert_violation(root, "INV-4")

    def test_inv5_done_step_without_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_done", "S001", "base", done="")
            self.assert_violation(root, "INV-5")

    def test_inv5_done_step_without_testing_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "testing.md").write_text(
                "# Testing ledger\n\n| Step | Criterion | Test | Result |\n|---|---|---|---|\n",
                encoding="utf-8")
            self.assert_violation(root, "INV-5")

    def test_inv6_duplicate_step_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_todo", "S003", "dupe")
            self.assert_violation(root, "INV-6")

    def test_inv7_modified_done_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            done = root / "adocs" / "plan_done" / "S001_base.md"
            done.write_text(done.read_text(encoding="utf-8") + "tampered\n",
                            encoding="utf-8")
            self.assert_violation(root, "INV-7")

    def test_inv7_deleted_done_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            (root / "adocs" / "plan_done" / "S001_base.md").unlink()
            self.assert_violation(root, "INV-7")

    def test_inv7_survives_the_commit_that_hides_it(self):
        # S018 (F04): HEAD is not a baseline, it is a moving target, and the
        # workflow commits at every step completion. Committing the tampering
        # used to erase the violation.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            done = root / "adocs" / "plan_done" / "S001_base.md"
            done.write_text(done.read_text(encoding="utf-8") + "tampered\n",
                            encoding="utf-8")
            self.assert_violation(root, "INV-7")  # precondition: seen uncommitted
            git(root, "add", "-A")
            git(root, "commit", "-qm", "hide the tampering")
            self.assert_violation(root, "INV-7")

    def test_inv7_survives_a_committed_deletion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            (root / "adocs" / "plan_done" / "S001_base.md").unlink()
            (root / "adocs" / "testing.md").write_text(
                "# Testing ledger\n\n| Step | Criterion | Test | Result |\n|---|---|---|---|\n",
                encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "remove history")
            self.assert_violation(root, "INV-7")

    def test_inv7_a_repair_commit_clears_it(self):
        # DEC-026: history is permanent, so judging on "a bad commit exists" left
        # no way back to green. The invariant judges current content instead.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            done = root / "adocs" / "plan_done" / "S001_base.md"
            original = done.read_text(encoding="utf-8")
            done.write_text(original + "tampered\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "tamper")
            self.assert_violation(root, "INV-7")  # precondition: still caught
            done.write_text(original, encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "restore the original bytes")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv7_a_near_miss_repair_does_not_clear_it(self):
        # Non-vacuity for the row above: only the original bytes clear it.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            done = root / "adocs" / "plan_done" / "S001_base.md"
            done.write_text(done.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "tamper")
            done.write_text(done.read_text(encoding="utf-8").replace("tampered\n", "almost\n"),
                            encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "not quite a restore")
            self.assert_violation(root, "INV-7")

    def test_inv7_a_committed_deletion_clears_when_the_file_comes_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            done = root / "adocs" / "plan_done" / "S001_base.md"
            original = done.read_text(encoding="utf-8")
            done.unlink()
            git(root, "add", "-A")
            git(root, "commit", "-qm", "delete history")
            self.assert_violation(root, "INV-7")
            done.write_text(original, encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "put it back")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv7_abstains_without_history(self):
        # Non-vacuity: the same tree with history reports the violation.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            done = root / "adocs" / "plan_done" / "S001_base.md"
            done.write_text(done.read_text(encoding="utf-8") + "tampered\n",
                            encoding="utf-8")
            git(root, "init", "-q")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv7_added_done_step_is_allowed(self):
        # Append by move only: additions are the one legal change.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git(root, "init", "-q")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "base")
            (root / "adocs" / "plan_current" / "S003_active.md").unlink()
            step_file(root / "adocs" / "plan_done", "S003", "active",
                      done="2026-08-01 done")
            (root / "adocs" / "testing.md").write_text(
                (root / "adocs" / "testing.md").read_text(encoding="utf-8")
                + "| S003 | active works | manual | pass |\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()


class TestInv7NamesTheRenamedFile(unittest.TestCase):
    """S071 (2026-08-08_adversarial.2-F05): INV-7 sliced the porcelain line and
    never split on ` -> `, so a rename produced a violation naming both halves
    and a remedy that, pasted into a shell, redirects git checkout's stdout over
    the renamed file and truncates it. The one invariant whose subject is
    immutable history printed a command that destroys a file in it.
    porcelain_paths was added by S050 for exactly this and INV-7 was the twin
    nobody updated."""

    def renamed(self, tmp):
        root = workflow_repo(tmp)
        git_baseline(root)
        git(root, "mv", "adocs/plan_done/S001_base.md", "adocs/plan_done/S001_renamed.md")
        self.assertIn(" -> ", git(root, "status", "--porcelain", "--",
                                  "adocs/plan_done").stdout,
                      "precondition: git recorded a rename")
        return root

    def test_the_violation_names_one_file_and_not_an_arrow(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.renamed(tmp)
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            inv7 = [line for line in result.stdout.splitlines() if "INV-7" in line]
            self.assertTrue(inv7, result.stdout)
            for line in inv7:
                self.assertNotIn(" -> ", line, "the remedy is pasted into a shell")

    def test_the_remedy_does_not_redirect_over_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.renamed(tmp)
            for line in run_validate(root).stdout.splitlines():
                if "INV-7" not in line or "git checkout" not in line:
                    continue
                command = line.split("git checkout", 1)[1]
                self.assertNotIn(">", command,
                                 "a remedy containing > truncates whatever follows it")

    def test_a_rename_is_still_reported(self):
        # Non-vacuity: splitting the line must not make the rename invisible.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.renamed(tmp)
            result = run_validate(root)
            self.assertIn("INV-7", result.stdout)
            self.assertIn("S001_renamed.md", result.stdout)

    def test_dropping_r_from_the_status_codes_fails_a_test(self):
        # The finding measured that deleting R left the suite green, so the line
        # had no cover at all. This is that cover: a plain rename with the
        # destination byte-identical is caught by nothing else.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.renamed(tmp)
            statuses = [line[:2] for line in
                        git(root, "status", "--porcelain", "--", "adocs/plan_done")
                        .stdout.splitlines()]
            self.assertTrue(any(code.startswith("R") for code in statuses), statuses)
            self.assertEqual(run_validate(root).returncode, 1)
