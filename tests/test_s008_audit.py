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

    def test_refuses_to_overwrite_an_existing_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            run_moltke(root, "--audit", "new", "adversarial")
            report = root / "adocs" / "audit" / f"{TODAY}_adversarial.md"
            report.write_text("# real findings\n", encoding="utf-8")
            result = run_moltke(root, "--audit", "new", "adversarial")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(report.read_text(encoding="utf-8"), "# real findings\n")


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


class TestFindingIds(unittest.TestCase):
    def test_finding_id_must_match_its_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-07-01_security-F01", "accepted")],
                         name="2026-08-01_adversarial.md")
            result = run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("INV-10", result.stdout)


class TestReviewerWriteFence(unittest.TestCase):
    """The reviewer produces evidence, not patches (specs: subagent section)."""

    def pre_write(self, root, path):
        payload = json.dumps({"agent_type": "adversarial_reviewer",
                              "tool_input": {"file_path": path}})
        return run_moltke(root, "--pre-write", stdin=payload)

    def test_reviewer_cannot_write_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.pre_write(root, "src/main.py")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
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
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"agent_type": "general-purpose",
                                  "tool_input": {"file_path": "src/main.py"}})
            self.assertEqual(run_moltke(root, "--pre-write", stdin=payload).returncode, 0)


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
