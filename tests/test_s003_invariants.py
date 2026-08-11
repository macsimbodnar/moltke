"""S003: INV-1..INV-7 against broken fixture repositories."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import step_file, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"
REPO = MOLTKE.parent.parent


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


class TestAMarkedRootBelowTheGitTopLevel(unittest.TestCase):
    """S081 (2026-08-08_adversarial.3-F02): every git call is `git -C <marked
    root>`, but porcelain, log and show all speak in paths relative to the
    repository top level, and nothing checked the two directories agree. A
    project vendored into a monorepo therefore had INV-7 calling a present file
    gone with a remedy that cannot run, INV-8 abstaining on real tampering, and
    the recap and stamp gates reading every path wrongly."""

    def vendored(self, tmp):
        """A git repository with a marked project at packages/foo."""
        mono = Path(tmp) / "mono"
        (mono / "packages" / "foo").mkdir(parents=True)
        git(mono, "init", "-q")
        root = workflow_repo(mono / "packages" / "foo")
        git(mono, "add", "-A")
        git(mono, "commit", "-qm", "vendored project")
        return mono, root

    def test_a_clean_vendored_project_validates_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            _mono, root = self.vendored(tmp)
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inv7_still_sees_a_removal_there(self):
        with tempfile.TemporaryDirectory() as tmp:
            _mono, root = self.vendored(tmp)
            (root / "adocs" / "plan_done" / "S001_base.md").unlink()
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-7", result.stdout)

    def test_the_remedy_it_prints_is_runnable_from_the_marked_root(self):
        # `git show <sha>:<path>` resolves from the top level whatever the cwd,
        # so that half keeps the prefix; the file it names and the destination
        # it redirects to are the marked root's, because that is where the
        # command is run. Both halves are asserted, since only their pairing is
        # correct.
        with tempfile.TemporaryDirectory() as tmp:
            _mono, root = self.vendored(tmp)
            done = root / "adocs" / "plan_done" / "S001_base.md"
            done.write_text(done.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            inv7 = [line for line in run_validate(root).stdout.splitlines() if "INV-7" in line]
            self.assertTrue(inv7)
            for line in inv7:
                subject = line.split("INV-7: ", 1)[1].split(" ", 1)[0]
                self.assertFalse(subject.startswith("packages/foo/"),
                                 f"the file it names must be the marked root's: {subject}")
                if "git show" not in line:
                    continue
                spec, destination = line.split("git show ", 1)[1].split(" > ", 1)
                self.assertIn("packages/foo/", spec,
                              "git show resolves from the top level, so the spec keeps it")
                self.assertFalse(destination.split(".")[0].startswith("packages/foo/"),
                                 f"the destination is written from the marked root: {destination}")

    def test_the_remedy_actually_restores_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            _mono, root = self.vendored(tmp)
            done = root / "adocs" / "plan_done" / "S001_base.md"
            original = done.read_text(encoding="utf-8")
            done.write_text(original + "tampered\n", encoding="utf-8")
            line = next(l for l in run_validate(root).stdout.splitlines()
                        if "INV-7" in l and "git show" in l)
            command = "git show " + line.split("git show ", 1)[1].rstrip(". ")
            command = command.split(". Never rewrite")[0]
            subprocess.run(command, shell=True, cwd=str(root), check=True,
                           stdout=subprocess.DEVNULL)
            self.assertEqual(done.read_text(encoding="utf-8"), original,
                             "following the printed remedy must restore the file")
            self.assertEqual(run_validate(root).returncode, 0)


class TestInv7RenameRemedyRestores(unittest.TestCase):
    """S084 (2026-08-08_adversarial.3-F05): S071 made the rename message safe to
    paste and left it a no-op. `git checkout -- <new path>` restores the new
    path from the index, which already holds the rename, so nothing changes; and
    following the second message as well writes the old name back beside the new
    one, which is an INV-6 duplicate id. A remedy INV-12 calls actionable has to
    end somewhere green."""

    def renamed(self, tmp):
        root = workflow_repo(tmp)
        git_baseline(root)
        git(root, "mv", "adocs/plan_done/S001_base.md", "adocs/plan_done/S001_renamed.md")
        return root

    def test_following_the_printed_remedy_clears_the_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.renamed(tmp)
            before = run_validate(root)
            self.assertEqual(before.returncode, 1, before.stdout)
            commands = [line.split(marker, 1)[1].rstrip(".")
                        for line in before.stdout.splitlines() if "INV-7" in line
                        for marker in ("restore it with ", "Undo it with ")
                        if marker in line]
            self.assertTrue(commands, before.stdout)
            for command in commands:
                subprocess.run(command, shell=True, cwd=str(root), check=True)
            after = run_validate(root)
            self.assertEqual(after.returncode, 0,
                             f"following the remedy left: {after.stdout}")

    def test_the_remedy_does_not_leave_a_duplicate_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.renamed(tmp)
            for line in run_validate(root).stdout.splitlines():
                for marker in ("restore it with ", "Undo it with "):
                    if "INV-7" in line and marker in line:
                        subprocess.run(line.split(marker, 1)[1].rstrip("."),
                                       shell=True, cwd=str(root), check=True)
            self.assertNotIn("INV-6", run_validate(root).stdout)
            self.assertTrue((root / "adocs" / "plan_done" / "S001_base.md").is_file())
            self.assertFalse((root / "adocs" / "plan_done" / "S001_renamed.md").exists())


class TestTheIdFieldAgreesWithTheFilename(unittest.TestCase):
    """S103 (2026-08-09_adversarial-F07): `write_step` is the only place `id`
    appears as a field key, and every reader takes the id from the filename
    instead, so nothing compared the two. `templates/step_template.md` ships
    `id:         S000`, and AGENTS.md documents hand-copying that template as the
    step format — which produces a file whose first line contradicts its name,
    with `--validate` green. An invariant stated in the ruleset's step layout and
    enforced nowhere."""

    def test_an_id_field_that_disagrees_with_the_filename_is_a_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            template = (Path(__file__).resolve().parent.parent
                        / "templates" / "step_template.md").read_text(encoding="utf-8")
            (root / "adocs" / "plan_todo" / "S050_hand_written.md").write_text(
                template, encoding="utf-8")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S050 hand written\n",
                encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S050", result.stdout)
            self.assertIn("S000", result.stdout,
                          "the violation must name both the filename's id and the field's")

    def test_a_step_written_by_the_cli_agrees_with_itself(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.assertEqual(run_moltke(root, "--step", "new", "ordinary").returncode, 0)
            self.assertEqual(run_validate(root).returncode, 0, run_validate(root).stdout)

    def test_a_step_file_with_no_id_field_is_not_reported(self):
        # Only a field that disagrees is a violation. A file without one is the
        # fixtures' own shape and is left alone rather than made a new failure.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            (root / "adocs" / "plan_todo" / "S002_pending.md").write_text(
                "goal:       pending\ndone:\n", encoding="utf-8")
            self.assertEqual(run_validate(root).returncode, 0, run_validate(root).stdout)

    def test_this_repository_passes(self):
        # Non-vacuity anchor: every step file across the three plan directories
        # carries the field today, so a rule that fired wrongly would be loud.
        result = run_moltke(REPO, "--validate")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestAPauseMustResolve(unittest.TestCase):
    """S098 (2026-08-09_adversarial-F02): S090 made a pause naming a step in no
    plan directory a violation, and left the neighbouring case open. A step that
    pauses itself, or two that pause each other, satisfies that rule — every
    pauser exists — while being just as unreachable: neither counts as active, so
    INV-1 and INV-2 report nothing, `--step done` sends you to the pauser and
    `--step unpause` sends you back to `--step done`. The two commands name each
    other."""

    def self_paused(self, root):
        return step_file(root / "adocs" / "plan_current", "S003", "active",
                         paused_by="S003  # 2026-08-09")

    def cycle(self, root):
        step_file(root / "adocs" / "plan_current", "S003", "active",
                  paused_by="S004  # 2026-08-09")
        step_file(root / "adocs" / "plan_current", "S004", "other",
                  paused_by="S003  # 2026-08-09")
        (root / "adocs" / "plan.md").write_text(
            "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")

    def test_a_step_paused_by_itself_is_a_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.self_paused(root)
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S003", result.stdout)
            self.assertIn("--step unpause", result.stdout,
                          "the violation must name the command that clears it")

    def test_two_steps_pausing_each_other_are_a_violation_naming_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.cycle(root)
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            cycle_lines = [l for l in result.stdout.splitlines()
                           if "S003" in l and "S004" in l]
            self.assertTrue(cycle_lines,
                            f"the cycle must be reported naming both members: {result.stdout}")

    def test_unpause_clears_what_validate_reports(self):
        # The dead end is the defect, so the fix is only a fix if the way out
        # exists: after unpause, validate is clean and the step completes.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.self_paused(root)
            cleared = run_moltke(root, "--step", "unpause", "S003")
            self.assertEqual(cleared.returncode, 0, cleared.stdout + cleared.stderr)
            self.assertEqual(run_validate(root).returncode, 0, run_validate(root).stdout)
            testing = root / "adocs" / "testing.md"
            testing.write_text(testing.read_text(encoding="utf-8")
                               + "| S003 | works | test_S003 | pass |\n", encoding="utf-8")
            done = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_unpause_clears_one_member_of_a_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.cycle(root)
            cleared = run_moltke(root, "--step", "unpause", "S003")
            self.assertEqual(cleared.returncode, 0, cleared.stdout + cleared.stderr)
            self.assertEqual(run_validate(root).returncode, 0, run_validate(root).stdout)

    def test_a_pause_naming_reachable_live_work_is_still_refused(self):
        # DEC-040's rule, which this step widens but must not repeal: a pause
        # that resolves to a step someone can actually finish is not clearable.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S004", "blocking_child",
                      blocks="S003")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            parent = step_file(root / "adocs" / "plan_current", "S003", "active",
                               paused_by="S004  # 2026-08-09")
            self.assertEqual(run_validate(root).returncode, 0, run_validate(root).stdout)
            result = run_moltke(root, "--step", "unpause", "S003")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S004", parent.read_text(encoding="utf-8"))

    def test_a_longer_chain_that_resolves_is_silent(self):
        # Non-vacuity for the cycle rule: following paused_by more than one hop
        # must not be mistaken for a cycle when it terminates.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active",
                      paused_by="S004  # 2026-08-09")
            step_file(root / "adocs" / "plan_current", "S004", "middle",
                      paused_by="S005  # 2026-08-09", blocks="S003")
            step_file(root / "adocs" / "plan_current", "S005", "leaf", blocks="S004")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n5. S005 e\n",
                encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_clearing_a_self_pause_says_it_paused_itself(self):
        # S115 (2026-08-11_adversarial-F04): the success message described the
        # pauser as having "no step file in any plan directory" — about a file
        # the command had just edited. Each kind now gets its own sentence, and
        # a self-pause is named as what it is rather than as a generic ring.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active",
                      paused_by="S003  # 2026-08-11")
            cleared = run_moltke(root, "--step", "unpause", "S003")
            self.assertEqual(cleared.returncode, 0, cleared.stdout + cleared.stderr)
            self.assertIn("paused itself", cleared.stdout)
            self.assertNotIn("no step file", cleared.stdout)

    def test_a_pause_naming_a_completed_step_is_reported_and_clearable(self):
        # S114 (2026-08-11_adversarial-F03): the pauser resolved days ago, the
        # parent shows Blocked: forever, and unpause + block prescribe a
        # --step done that refuses. The state is one --step done's own failure
        # path documents leaving behind.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active",
                      paused_by="S001  # 2026-08-01")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S001", result.stdout)
            self.assertIn("--step unpause", result.stdout)
            cleared = run_moltke(root, "--step", "unpause", "S003")
            self.assertEqual(cleared.returncode, 0, cleared.stdout + cleared.stderr)
            self.assertIn("resolved", cleared.stdout)
            self.assertEqual(run_validate(root).returncode, 0, run_validate(root).stdout)
            blocked = run_moltke(root, "--step", "block", "S003", "new_blocker")
            self.assertEqual(blocked.returncode, 0,
                             "the parent must be re-blockable after the clear: "
                             + blocked.stdout + blocked.stderr)

    def test_step_done_still_steps_over_a_stale_pause(self):
        # S070's path, unchanged: completing the parent needs no unpause first.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active",
                      paused_by="S001  # 2026-08-01")
            testing = root / "adocs" / "testing.md"
            testing.write_text(testing.read_text(encoding="utf-8")
                               + "| S003 | works | test_S003 | pass |\n", encoding="utf-8")
            done = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("stale", done.stdout)

    def test_the_phantom_pauser_rule_is_unchanged(self):
        # S090's case still reports, with its own message.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active",
                      paused_by="S999  # 2026-08-09")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S999", result.stdout)


class TestGitPrefixIsComputedOncePerRoot(unittest.TestCase):
    """S092 (2026-08-08_adversarial.4-F05): `git_prefix` shells out to
    `git rev-parse --show-prefix`, and `from_git_path`/`to_git_path` call it once
    per path. INV-7 and INV-8 walk every completed step and every history line, so
    one run_checks spawned a process per path — hundreds on this repository, on
    every prompt, for an answer that cannot change during a run."""

    def counted(self, root):
        """run_checks over `root`, returning how many git subprocesses it spawned."""
        from surface import moltke
        calls = []
        original = moltke._git_run

        def counting(*args, **kwargs):
            calls.append(args[0] if args else kwargs.get("args"))
            return original(*args, **kwargs)

        moltke._git_run = counting
        getattr(moltke, "_GIT_PREFIX_CACHE", {}).clear()
        try:
            config, _violations = moltke.load_marker(Path(root))
            moltke.run_checks(Path(root), config)
        finally:
            moltke._git_run = original
        return [c for c in calls if c and "--show-prefix" in c]

    def test_one_run_checks_asks_for_the_prefix_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for n in range(4, 12):
                step_file(root / "adocs" / "plan_done", f"S0{n:02d}", f"done_{n}",
                          done="2026-08-01 done, README and MANUAL checked")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n" + "".join(f"{i}. S0{i:02d} s\n" for i in range(1, 12)),
                encoding="utf-8")
            git_baseline(root)
            prefix_calls = self.counted(root)
            # Precondition: without git history INV-7 and INV-8 abstain and this
            # would measure nothing. git_baseline above is what makes it non-vacuous.
            self.assertTrue(prefix_calls, "no prefix lookup happened at all; the fixture "
                                          "has no git history and the check abstained")
            self.assertEqual(len(prefix_calls), 1,
                             f"the prefix cannot change during a run, and was asked for "
                             f"{len(prefix_calls)} times")


STAMP = "2026-08-09 suite green; README and MANUAL checked"


def run_moltke(cwd, *args):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=cwd, capture_output=True, text=True, input="",
    )


class TestPauserMustExist(unittest.TestCase):
    """S090 (2026-08-08_adversarial.4-F03): INV-1 counts a step as non-active
    whenever `paused_by` is non-empty, and nothing checked that the named pauser
    exists. A step waiting on work that is in no plan directory passed every
    check, could not be completed, and no `--step` operation reached the field —
    state derivable from tracked files, saying something untrue, with hand-editing
    the only way out."""

    def stranded(self, root):
        """The one step in plan_current/, waiting on an id that exists nowhere."""
        step_file(root / "adocs" / "plan_current", "S003", "active",
                  paused_by="S999  # 2026-08-08")
        return root / "adocs" / "plan_current" / "S003_active.md"

    def test_a_pauser_that_exists_nowhere_is_a_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.stranded(root)
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S003", result.stdout)
            self.assertIn("S999", result.stdout)
            self.assertIn("--step unpause", result.stdout,
                          "the violation must name the command that clears it")

    def test_the_named_command_clears_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.stranded(root)
            cleared = run_moltke(root, "--step", "unpause", "S003")
            self.assertEqual(cleared.returncode, 0, cleared.stdout + cleared.stderr)
            self.assertEqual(run_validate(root).returncode, 0, run_validate(root).stdout)
            testing = root / "adocs" / "testing.md"
            testing.write_text(testing.read_text(encoding="utf-8")
                               + "| S003 | works | test_S003 | pass |\n", encoding="utf-8")
            done = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_unpause_refuses_a_pause_that_is_real(self):
        # Non-vacuity: a command that cleared any pause would pass the two tests
        # above while destroying the accounting INV-1 exists to keep.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S004", "blocking_child",
                      blocks="S003")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            parent = step_file(root / "adocs" / "plan_current", "S003", "active",
                               paused_by="S004  # 2026-08-09")
            result = run_moltke(root, "--step", "unpause", "S003")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("S004", result.stderr)
            self.assertIn("S004", parent.read_text(encoding="utf-8"),
                          "a real pause may not be cleared")

    def test_a_legitimate_pause_is_still_silent(self):
        # The other non-vacuity anchor: the new check must not fire on the shape
        # the workflow creates on purpose.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S004", "paused_parent",
                      paused_by="S003")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001 a\n2. S002 b\n3. S003 c\n4. S004 d\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_pauser_already_in_plan_done_keeps_the_s070_behaviour(self):
        # S070's stale-pause path: --step done says so and goes on. This step
        # must not turn that working path into a refusal.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            step_file(root / "adocs" / "plan_current", "S003", "active",
                      paused_by="S001  # 2026-08-09")
            testing = root / "adocs" / "testing.md"
            testing.write_text(testing.read_text(encoding="utf-8")
                               + "| S003 | works | test_S003 | pass |\n", encoding="utf-8")
            done = run_moltke(root, "--step", "done", "S003", "--stamp", STAMP)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("stale", done.stdout)


if __name__ == "__main__":
    unittest.main()
