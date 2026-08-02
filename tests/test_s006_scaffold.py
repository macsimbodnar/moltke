"""S006: --scaffold and --decline (setup modes, exempt from INV-11 by DEC-017)."""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"
REPO = MOLTKE.parent.parent
TEMPLATES = REPO / "templates"

SCAFFOLDED = (
    ".moltke.json",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules/moltke.mdc",
    "adocs/status.md",
    "adocs/specs.md",
    "adocs/plan.md",
    "adocs/decisions.md",
    "adocs/testing.md",
    "adocs/worklog.md",
    "adocs/plan_todo",
    "adocs/plan_current",
    "adocs/plan_done",
    "adocs/audit",
)


def run_moltke(cwd, *args):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=cwd, capture_output=True, text=True, input="",
    )


class TestScaffold(unittest.TestCase):
    def test_creates_the_full_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_moltke(tmp, "--scaffold")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for rel in SCAFFOLDED:
                self.assertTrue((Path(tmp) / rel).exists(), f"missing {rel}")
            marker = json.loads((Path(tmp) / ".moltke.json").read_text(encoding="utf-8"))
            self.assertTrue(marker["enabled"])
            self.assertEqual(marker["schema"], 1)
            self.assertEqual((Path(tmp) / "CLAUDE.md").read_text(encoding="utf-8").strip(),
                             "@AGENTS.md")

    def test_scaffolded_repo_validates_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_moltke(tmp, "--scaffold")
            result = run_moltke(tmp, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_running_twice_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_moltke(tmp, "--scaffold")
            before = {rel: (Path(tmp) / rel).read_bytes()
                      for rel in SCAFFOLDED if (Path(tmp) / rel).is_file()}
            # A real edit must survive the second run.
            status = Path(tmp) / "adocs" / "status.md"
            status.write_text("# Status\n\n- Next: nothing yet\n", encoding="utf-8")
            result = run_moltke(tmp, "--scaffold")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(status.read_text(encoding="utf-8"),
                             "# Status\n\n- Next: nothing yet\n")
            for rel, content in before.items():
                if rel != "adocs/status.md":
                    self.assertEqual((Path(tmp) / rel).read_bytes(), content, rel)

    def test_existing_agents_md_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / "AGENTS.md"
            agents.write_text("# House rules\n\nours, not moltke's\n", encoding="utf-8")
            result = run_moltke(tmp, "--scaffold")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(agents.read_text(encoding="utf-8"),
                             "# House rules\n\nours, not moltke's\n")
            self.assertIn("AGENTS.md", result.stdout)
            self.assertIn("kept", result.stdout.lower())

    def test_declined_repo_is_left_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".moltke.json").write_text('{"schema": 1, "enabled": false}\n',
                                                    encoding="utf-8")
            result = run_moltke(tmp, "--scaffold")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((Path(tmp) / "adocs").exists())
            self.assertFalse((Path(tmp) / "AGENTS.md").exists())

    def test_fresh_scaffold_is_immediately_clean(self):
        # Commented-out examples in the plan template are not the plan: a fresh
        # repo must not report a phantom next step, a stale status.md, or block
        # the first Stop.
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "-C", tmp, "init", "-q"], check=True)
            run_moltke(tmp, "--scaffold")
            session = run_moltke(tmp, "--session-start")
            context = json.loads(session.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("plan_current/ is empty", context)  # precondition: real output
            self.assertNotIn("stale", context.lower())
            self.assertNotRegex(context, r"Derived next step: S\d{3}")
            self.assertEqual(run_moltke(tmp, "--stop").returncode, 0,
                             "a freshly scaffolded repo must not block the first stop")

    def test_first_real_decision_does_not_collide_with_the_template_example(self):
        # The format example in decisions.md is guidance, not an entry.
        with tempfile.TemporaryDirectory() as tmp:
            run_moltke(tmp, "--scaffold")
            decisions = Path(tmp) / "adocs" / "decisions.md"
            decisions.write_text(decisions.read_text(encoding="utf-8")
                                 + "\n## DEC-001  2026-08-01  the first real decision\n"
                                   "Tags: setup\nContext: x\nDecision: y\n"
                                   "Rejected: z\nConsequences: none\n", encoding="utf-8")
            result = run_moltke(tmp, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_scaffolds_at_git_root_from_a_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "-C", tmp, "init", "-q"], check=True)
            sub = Path(tmp) / "src" / "deep"
            sub.mkdir(parents=True)
            run_moltke(sub, "--scaffold")
            self.assertTrue((Path(tmp) / ".moltke.json").is_file())
            self.assertFalse((sub / ".moltke.json").exists())


class TestDecline(unittest.TestCase):
    def test_decline_is_durable(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_moltke(tmp, "--decline")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            marker = json.loads((Path(tmp) / ".moltke.json").read_text(encoding="utf-8"))
            self.assertIs(marker["enabled"], False)
            # Durable: scaffolding afterwards does nothing, other modes stay silent.
            run_moltke(tmp, "--scaffold")
            self.assertFalse((Path(tmp) / "adocs").exists())
            self.assertEqual(run_moltke(tmp, "--validate").returncode, 0)
            self.assertEqual(run_moltke(tmp, "--stop").returncode, 0)

    def test_decline_refuses_to_disable_an_enabled_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_moltke(tmp, "--scaffold")
            before = (Path(tmp) / ".moltke.json").read_bytes()
            result = run_moltke(tmp, "--decline")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((Path(tmp) / ".moltke.json").read_bytes(), before)


class TestTemplatesAreGeneric(unittest.TestCase):
    """DEC-002: templates carry no project-specific content.

    Regression for the DEC-013 cross-reference found in the shipped ruleset.
    """

    def test_no_live_decision_ids_in_template_prose(self):
        prose_checked = 0
        for path in sorted(TEMPLATES.rglob("*")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            prose = re.sub(r"```.*?```", "", text, flags=re.S)
            if "decisions.md" in prose:
                prose_checked += 1  # precondition: prose survived stripping
            found = re.findall(r"\bDEC-\d{3}\b", prose)
            self.assertEqual(found, [], f"{path.name} references live decision ids: {found}")
        self.assertGreater(prose_checked, 0, "no template prose mentions decisions.md; "
                                             "the strip removed everything and the check is vacuous")

    def test_ruleset_template_matches_the_live_ruleset(self):
        self.assertEqual((TEMPLATES / "AGENTS.md").read_bytes(),
                         (REPO / "AGENTS.md").read_bytes(),
                         "templates/AGENTS.md drifted from AGENTS.md (DEC-012)")


class TestInitSkill(unittest.TestCase):
    def test_skill_declares_name_and_description(self):
        skill = REPO / "skills" / "init" / "SKILL.md"
        self.assertTrue(skill.is_file(), "skills/init/SKILL.md missing")
        text = skill.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "SKILL.md needs YAML frontmatter")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: init", frontmatter)
        self.assertRegex(frontmatter, r"description:\s*\S")


if __name__ == "__main__":
    unittest.main()
