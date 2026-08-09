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

    def test_inv8_still_sees_tampering_there(self):
        with tempfile.TemporaryDirectory() as tmp:
            _mono, root = self.vendored(tmp)
            decisions = root / "adocs" / "decisions.md"
            kept = [l for l in decisions.read_text(encoding="utf-8").splitlines()
                    if "base decision" not in l]
            decisions.write_text("\n".join(kept) + "\n", encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-8", result.stdout)

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
