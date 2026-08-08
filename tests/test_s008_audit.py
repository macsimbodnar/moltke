"""S008: audit reports, finding bookkeeping, and the reviewer's write fence."""

import datetime
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import audit_report, step_file, workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"
REPO = MOLTKE.parent.parent
TODAY = datetime.date.today().isoformat()


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


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TestAuditNew(unittest.TestCase):
    def test_creates_a_dated_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--audit", "new", "adversarial")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = root / "adocs" / "audit" / f"{TODAY}_adversarial.md"
            self.assertTrue(report.is_file(), result.stdout)
            self.assertIn(TODAY, report.read_text(encoding="utf-8"))

    def test_fresh_report_has_no_live_findings(self):
        # The format example in the template must not read as a real finding,
        # or every new report would violate INV-10 the moment it is created.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            validate = run_moltke(root, "--validate")
            self.assertEqual(validate.returncode, 0, validate.stdout)
            listing = run_moltke(root, "--audit", "list")
            self.assertIn("no findings", listing.stdout.lower())

    def test_a_same_day_rerun_suffixes_instead_of_overwriting(self):
        # S020 (F09): closure requires a re-run, so refusing a same-day re-run
        # left no compliant way to close a finding fixed the day it was found.
        # The no-overwrite property is what this test used to assert and still does.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            first = root / "adocs" / "audit" / f"{TODAY}_adversarial.md"
            first.write_text("# real findings\n", encoding="utf-8")
            result = run_moltke(root, "--audit", "new", "adversarial")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(first.read_text(encoding="utf-8"), "# real findings\n")
            second = root / "adocs" / "audit" / f"{TODAY}_adversarial.2.md"
            self.assertTrue(second.is_file(), result.stdout + result.stderr)
            self.assertIn(second.name, result.stdout)

    def test_reruns_keep_counting_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for expected in (f"{TODAY}_adversarial.md", f"{TODAY}_adversarial.2.md",
                             f"{TODAY}_adversarial.3.md"):
                result = run_moltke(root, "--audit", "new", "adversarial")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue((root / "adocs" / "audit" / expected).is_file(), expected)

    def test_a_rerun_report_states_its_own_finding_ids(self):
        # INV-10 keys findings to their report's stem, so the re-run's template
        # has to name the suffixed stem or the first finding written violates it.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            result = run_moltke(root, "--audit", "new", "adversarial")
            self.assertIn(f"{TODAY}_adversarial.2-F01", result.stdout)
            second = root / "adocs" / "audit" / f"{TODAY}_adversarial.2.md"
            self.assertIn(f"{TODAY}_adversarial.2-F", second.read_text(encoding="utf-8"))
            validate = run_moltke(root, "--validate")
            self.assertEqual(validate.returncode, 0, validate.stdout)

    def test_a_type_with_a_path_separator_is_refused(self):
        # S040 (F09): the type went straight into a filename and audit_new
        # mkdir'd the parents, so a report could land outside the glob every
        # check uses — filed, and counted by nothing.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--audit", "new", "../../outside/pwned")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("A-Za-z0-9", result.stderr)
            self.assertEqual(list((root / "adocs" / "audit").glob("**/*")), [],
                             "nothing may be created by a refused type")
            self.assertFalse((Path(tmp) / "outside").exists())

    def test_a_dotted_type_is_refused_because_the_suffix_namespace_is_reserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--audit", "new", "UPPER.2")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse((root / "adocs" / "audit" / f"{TODAY}_UPPER.2.md").exists(),
                             "a dotted type would collide with the same-day re-run namespace")

    def test_awkward_types_are_refused_before_they_reach_the_filesystem(self):
        for audit_type in ("with space", "sub/dir", "..", ".", "", "tab\there", "sec;rm"):
            with self.subTest(audit_type=audit_type), tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                result = run_moltke(root, "--audit", "new", audit_type)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                audit_dir = root / "adocs" / "audit"
                self.assertEqual(list(audit_dir.glob("**/*")) if audit_dir.is_dir() else [], [])

    def test_ordinary_types_still_work(self):
        # Non-vacuity: the rule must not refuse the types the skill documents.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for audit_type in ("adversarial", "security", "bugs", "perf-2", "dep_scan"):
                result = run_moltke(root, "--audit", "new", audit_type)
                self.assertEqual(result.returncode, 0, (audit_type, result.stderr))
                self.assertTrue((root / "adocs" / "audit" / f"{TODAY}_{audit_type}.md").is_file())

    def test_a_rerun_finding_id_does_not_satisfy_the_first_report(self):
        # The suffix makes the first report's stem a prefix of the re-run's, so
        # startswith would let a re-run id sit in the first report unnoticed.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [(f"{TODAY}_adversarial.2-F01", "accepted")],
                         name=f"{TODAY}_adversarial.md")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-10", result.stdout)


class TestAuditList(unittest.TestCase):
    def test_reports_status_and_whether_each_finding_is_referenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "open"),
                                ("2026-08-01_adversarial-F02", "accepted")])
            step_file(root / "adocs" / "plan_todo", "S004", "fix_it",
                      closes="2026-08-01_adversarial-F01")
            (root / "adocs" / "plan.md").write_text(
                "# Plan\n\n1. S001\n2. S002\n3. S003\n4. S004\n", encoding="utf-8")
            result = run_moltke(root, "--audit", "list")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("2026-08-01_adversarial-F01", result.stdout)
            self.assertIn("S004", result.stdout)          # names what closes it
            self.assertIn("accepted", result.stdout)

    def test_flags_an_unreferenced_open_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "open")])
            result = run_moltke(root, "--audit", "list")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("2026-08-01_adversarial-F01", result.stdout)


class TestGuidanceNeverDischargesAFinding(unittest.TestCase):
    """S019 (F05): finding_references was the one scanner that read decisions.md
    raw, so a finding id inside a fenced example discharged a real finding — and
    templates/adocs/decisions.md ships exactly such an example."""

    FINDING = "2026-08-01_adversarial-F01"

    def unreferenced(self, tmp):
        root = workflow_repo(tmp)
        audit_report(root, [(self.FINDING, "open")])
        return root

    def append_to_decisions(self, root, text):
        path = root / "adocs" / "decisions.md"
        path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")

    def test_a_fenced_example_does_not_discharge_a_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.unreferenced(tmp)
            # Baseline first, exactly as the audit reproduced it: unreferenced is
            # a violation, so a later exit 1 is not just the check being broken.
            self.assertEqual(run_moltke(root, "--validate").returncode, 1)
            self.append_to_decisions(root, f"\n```\nSee {self.FINDING} for the format.\n```\n")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-10", result.stdout)

    def test_an_html_comment_does_not_discharge_a_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.unreferenced(tmp)
            self.assertEqual(run_moltke(root, "--validate").returncode, 1)
            self.append_to_decisions(root, f"\n<!-- example: {self.FINDING} -->\n")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-10", result.stdout)

    def test_a_real_entry_still_discharges_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.unreferenced(tmp)
            self.append_to_decisions(
                root,
                f"\n## DEC-002  2026-08-02  accept the finding\nTags: audit\n"
                f"Context: {self.FINDING} is by design\nDecision: accept it\n"
                f"Rejected: fixing it\nConsequences: none\n")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_audit_list_agrees_with_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.unreferenced(tmp)
            self.append_to_decisions(root, f"\n```\n{self.FINDING}\n```\n")
            result = run_moltke(root, "--audit", "list")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertNotIn("referenced in decisions.md", result.stdout)


class TestFindingIds(unittest.TestCase):
    def test_finding_id_must_match_its_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-07-01_security-F01", "accepted")],
                         name="2026-08-01_adversarial.md")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("INV-10", result.stdout)


# Observed live on 2026-08-06 (S016) by instrumenting the installed 0.2.0 hook
# and spawning each agent through the plugin. The scoped form is what Claude Code
# actually sends; the bare form is what the fence used to compare against.
SCOPED_REVIEWER = "moltke:adversarial_reviewer"
BARE_REVIEWER = "adversarial_reviewer"


class TestReviewerWriteFence(unittest.TestCase):
    """The reviewer produces evidence, not patches (specs: subagent section)."""

    def pre_write(self, root, path, agent_type=SCOPED_REVIEWER):
        payload = json.dumps({"agent_type": agent_type,
                              "tool_input": {"file_path": path}})
        return run_moltke(root, "--pre-write", stdin=payload)

    def test_reviewer_cannot_write_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for agent_type in (SCOPED_REVIEWER, BARE_REVIEWER):
                result = self.pre_write(root, "src/main.py", agent_type)
                self.assertEqual(result.returncode, 2,
                                 (agent_type, result.stdout + result.stderr))
                self.assertIn("adocs/audit/", result.stderr)

    def test_reviewer_cannot_write_plan_or_specs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for path in ("adocs/specs.md", "adocs/plan.md",
                         "adocs/plan_todo/S002_pending.md"):
                self.assertEqual(self.pre_write(root, path).returncode, 2, path)

    def test_reviewer_may_write_its_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, f"adocs/audit/{TODAY}_adversarial.md")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_other_agents_are_unaffected(self):
        # Non-vacuity: the same path is fine for anyone who is not the reviewer.
        # general-purpose is the observed agent_type of a built-in subagent.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for agent_type in ("general-purpose", "Explore", "other:adversarial-reviewer"):
                payload = json.dumps({"agent_type": agent_type,
                                      "tool_input": {"file_path": "src/main.py"}})
                self.assertEqual(
                    run_moltke(root, "--pre-write", stdin=payload).returncode, 0, agent_type)

    def test_main_thread_is_unaffected(self):
        # Observed: the main thread sends no agent_type and no agent_id at all.
        # A missing field must not read as the reviewer, and must not fence the
        # session that does the actual work.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"tool_input": {"file_path": "src/main.py"}})
            result = run_moltke(root, "--pre-write", stdin=payload)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestAuditReconciliation(unittest.TestCase):
    """S017 (DEC-022): mutation during an audit is legitimate — the reviewer
    needs to reproduce defects — so the run is reconciled afterwards instead of
    prevented. `Bash` is unconstrained by design, which is exactly why the
    reconciliation has to exist."""

    def committed_repo(self, tmp):
        root = workflow_repo(tmp)
        write(root, "src/main.py", "print('source')\n")
        write(root, "tests/test_existing.py", "# an existing test\n")
        git_baseline(root)
        return root

    def check(self, root):
        return run_moltke(root, "--audit", "check")

    def test_only_the_reports_own_changes_are_expected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            report = root / "adocs" / "audit" / f"{TODAY}_adversarial.md"
            report.write_text(report.read_text(encoding="utf-8") + "\n### finding\n",
                              encoding="utf-8")
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(f"{TODAY}_adversarial.md", result.stdout)

    def test_a_new_test_file_is_expected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "tests/test_regression.py", "# red first\n")
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("tests/test_regression.py", result.stdout)

    def test_a_modified_existing_test_is_unexpected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "tests/test_existing.py", "# weakened\n")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("tests/test_existing.py", result.stdout)

    def test_a_source_change_is_unexpected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "src/main.py", "print('patched')\n")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("src/main.py", result.stdout)

    def test_a_dirty_starting_tree_is_not_blamed_on_the_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            write(root, "src/main.py", "print('dirty before the audit')\n")
            run_moltke(root, "--audit", "new", "adversarial")
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("src/main.py", result.stdout)

    def test_a_second_change_to_an_already_dirty_file_is_caught(self):
        # Porcelain status stays " M" across both edits, so status alone cannot
        # see this; the baseline records a content hash for that reason.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            write(root, "src/main.py", "print('dirty before the audit')\n")
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "src/main.py", "print('changed again during the audit')\n")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("src/main.py", result.stdout)

    def test_reverting_someone_elses_change_is_unexpected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            write(root, "src/main.py", "print('dirty before the audit')\n")
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "src/main.py", "print('source')\n")  # back to HEAD
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("src/main.py", result.stdout)

    def test_a_committed_source_patch_is_unexpected(self):
        # S032 (F01): a clean tracked file that the run patches AND commits was
        # in neither snapshot, so the check printed "no change since --audit new"
        # for a run that had rewritten source. DEC-022 traded the write fence
        # away for this check, and git commit defeated it.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "src/main.py", "print('patched by the reviewer')\n")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "reviewer patches source")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("src/main.py", result.stdout)

    def test_a_committed_weakened_test_is_unexpected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "tests/test_existing.py", "# weakened\n")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "reviewer weakens a test")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("tests/test_existing.py", result.stdout)

    def test_committing_the_report_and_a_new_test_stays_expected(self):
        # Non-vacuity: the fix must not call every commit contamination.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "tests/test_regression.py", "# red first\n")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "report plus a new regression test")
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("tests/test_regression.py", result.stdout)

    def test_a_commit_made_before_the_run_is_not_blamed_on_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            write(root, "src/main.py", "print('someone else, earlier')\n")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "unrelated work before the audit")
            run_moltke(root, "--audit", "new", "adversarial")
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("src/main.py", result.stdout)

    def log_prompt(self, root, text="a prompt during the audit"):
        result = run_moltke(root, "--log-prompt", stdin=json.dumps({"prompt": text}))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_worklog_append_during_the_run_is_expected(self):
        # S036 (F05): UserPromptSubmit appends on every prompt, so every audit
        # that spans a prompt had a worklog change in its footprint — blamed on a
        # reviewer that is fenced out of that file and never touched it. A gate
        # that is wrong every time is one people learn to wave through.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            self.log_prompt(root)
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_committed_worklog_append_is_also_expected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            self.log_prompt(root)
            git(root, "add", "-A")
            git(root, "commit", "-qm", "the turn's prompts and the report")
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_worklog_rewrite_during_the_run_is_still_unexpected(self):
        # Non-vacuity, and the point of scoping this to appends: an append is
        # what the hook does, a rewrite is what covering your tracks looks like.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "adocs/worklog.md", "# Worklog\n\n(history removed)\n")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("worklog.md", result.stdout)

    def test_a_worklog_append_after_a_rewrite_is_still_unexpected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            write(root, "adocs/worklog.md", "# Worklog\n\n(history removed)\n")
            self.log_prompt(root)
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("worklog.md", result.stdout)

    def test_a_hook_append_is_expected_and_says_so_rather_than_going_unmentioned(self):
        # S056 (.2-F09): S036 traded a false positive for a blind spot in the
        # same file. The exemption stays — a wrong gate is one people wave
        # through — but the append is named, so it is never silently expected.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            self.log_prompt(root)
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("adocs/worklog.md", result.stdout)
            self.assertIn("prompt", result.stdout)

    def test_an_append_the_prompt_hook_would_not_have_written_is_unexpected(self):
        # The shape the finding measured: a fabricated recap heading appended
        # from Bash, which silences the Stop recap gate for whatever the reviewer
        # did, and which the exemption called expected.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            worklog = root / "adocs" / "worklog.md"
            worklog.write_text(worklog.read_text(encoding="utf-8")
                               + "\n## 2026-08-07 recap S001\n\nnothing to see here\n",
                               encoding="utf-8")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("adocs/worklog.md", result.stdout)
            self.assertIn("recap", result.stdout)

    def test_a_hook_append_next_to_a_fabricated_one_is_still_unexpected(self):
        # The evasion the corroboration has to survive: bury the recap between
        # real prompt entries so the tail is mostly hook-shaped.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            self.log_prompt(root, "first")
            worklog = root / "adocs" / "worklog.md"
            worklog.write_text(worklog.read_text(encoding="utf-8")
                               + "\n## 2026-08-07 recap S001\n\nnothing to see here\n",
                               encoding="utf-8")
            self.log_prompt(root, "second")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("adocs/worklog.md", result.stdout)

    def test_a_multi_line_prompt_is_still_a_hook_append(self):
        # Non-vacuity for the corroboration: prompts are arbitrary text, quoted
        # line by line, and one of them containing "recap" or a blank line must
        # not read as fabrication.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            self.log_prompt(root, "## 2026-08-07 recap S001\n\nwrite the recap for me\n```\nx\n```")
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_check_without_a_baseline_refuses_and_says_what_to_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.committed_repo(tmp)
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("--audit new", result.stderr)


class TestAuditReconciliationInAWorktree(unittest.TestCase):
    """S035 (F04): a linked worktree's .git is a file, so `--audit new` recorded
    no baseline and told the user there was no git worktree, inside a worktree
    where git works."""

    def linked_worktree(self, tmp):
        root = workflow_repo(tmp)
        write(root, "src/main.py", "print('source')\n")
        git_baseline(root)
        worktree = Path(tmp) / "linked"
        subprocess.run(["git", "-C", str(root), "worktree", "add", "-q", "-b", "wt",
                        str(worktree)], capture_output=True, text=True, check=True)
        assert (worktree / ".git").is_file(), "precondition: .git is a file here"
        return worktree

    def test_a_baseline_is_recorded_and_check_reconciles(self):
        with tempfile.TemporaryDirectory() as tmp:
            worktree = self.linked_worktree(tmp)
            opened = run_moltke(worktree, "--audit", "new", "adversarial")
            self.assertEqual(opened.returncode, 0, opened.stdout + opened.stderr)
            self.assertNotIn("no git", opened.stderr)
            clean = run_moltke(worktree, "--audit", "check")
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
            write(worktree, "src/main.py", "print('patched')\n")
            dirty = run_moltke(worktree, "--audit", "check")
            self.assertEqual(dirty.returncode, 1, dirty.stdout + dirty.stderr)
            self.assertIn("src/main.py", dirty.stdout)

    def test_without_git_the_warning_is_accurate_and_check_still_refuses(self):
        # Non-vacuity: the fix must not make every directory look like a repo.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            opened = run_moltke(root, "--audit", "new", "adversarial")
            self.assertEqual(opened.returncode, 0, opened.stdout + opened.stderr)
            self.assertIn("--audit check", opened.stderr)
            self.assertEqual(run_moltke(root, "--audit", "check").returncode, 1)


class TestReviewerMayWriteNewTests(unittest.TestCase):
    """DEC-022 widens the fence: a new regression test is evidence, editing an
    existing one is a patch."""

    def pre_write(self, root, path):
        payload = json.dumps({"agent_type": SCOPED_REVIEWER,
                              "tool_input": {"file_path": path}})
        return run_moltke(root, "--pre-write", stdin=payload)

    def test_new_test_file_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, "tests/test_regression.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_existing_test_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            write(root, "tests/test_existing.py", "# an existing test\n")
            result = self.pre_write(root, "tests/test_existing.py")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("tests/", result.stderr)

    def test_a_relative_escape_through_tests_is_blocked(self):
        # S041 (F10): rel.parts is not normalised, so a first component of
        # "tests" was enough — the absolute form of the same path was already
        # blocked, which is what made this a hole rather than a design.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for path in ("tests/../bin/moltke.py", "tests/../bin/newfile.py",
                         "adocs/audit/../../bin/moltke.py"):
                result = self.pre_write(root, path)
                self.assertEqual(result.returncode, 2, (path, result.stdout + result.stderr))

    def test_a_path_that_leaves_the_repository_stays_unpoliced(self):
        # Deliberate boundary, unchanged: moltke governs the repository it is
        # marked in. `tests/../../outside.py` resolves outside the root, so it is
        # allowed here for the same reason an absolute path elsewhere always was.
        # The fence is not the guarantee anyway (DEC-022) — Bash is unfenced.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, "tests/../../outside.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_absolute_form_of_the_same_path_is_blocked_too(self):
        # Non-vacuity anchor: absolute paths were already resolved, so this is
        # what the relative branch is being brought into line with.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, str(root / "tests" / ".." / "bin" / "newfile.py"))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_a_genuine_new_test_is_still_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for path in ("tests/test_regression.py", "tests/unit/test_deep.py",
                         "./tests/test_dotted.py"):
                result = self.pre_write(root, path)
                self.assertEqual(result.returncode, 0, (path, result.stdout + result.stderr))

    def test_everything_else_is_still_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            for path in ("src/main.py", "bin/moltke.py", "adocs/specs.md",
                         "tests_helper.py", "docs/tests/new.py"):
                self.assertEqual(self.pre_write(root, path).returncode, 2, path)


class TestDefinitions(unittest.TestCase):
    def test_reviewer_agent_is_read_only_plus_write(self):
        agent = REPO / "agents" / "adversarial_reviewer.md"
        self.assertTrue(agent.is_file(), "agents/adversarial_reviewer.md missing")
        frontmatter = agent.read_text(encoding="utf-8").split("---", 2)[1]
        self.assertIn("name: adversarial_reviewer", frontmatter)
        self.assertRegex(frontmatter, r"description:\s*\S")
        tools = [t.strip() for t in
                 frontmatter.split("tools:", 1)[1].splitlines()[0].split(",")]
        self.assertIn("Read", tools)
        self.assertIn("Write", tools)   # to write its report
        self.assertNotIn("Edit", tools)  # never to change source

    def test_audit_skill_declares_name_and_description(self):
        skill = REPO / "skills" / "audit" / "SKILL.md"
        self.assertTrue(skill.is_file(), "skills/audit/SKILL.md missing")
        frontmatter = skill.read_text(encoding="utf-8").split("---", 2)[1]
        self.assertIn("name: audit", frontmatter)
        self.assertRegex(frontmatter, r"description:\s*\S")


if __name__ == "__main__":
    unittest.main()
