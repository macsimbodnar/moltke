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


class TestTemplateDriftReport(unittest.TestCase):
    """S029: a fresh clone of a repository that already uses moltke has every
    tracked file already — repository state travels in git, only the plugin
    install is per-machine. `--scaffold` there creates nothing, and said nothing
    about whether the ruleset it copied months ago still matches the installed
    plugin's. The kept-file lines carry that now: reported, never acted on."""

    RULESET = ("AGENTS.md", "CLAUDE.md", ".cursor/rules/moltke.mdc")

    def cloned(self, tmp):
        """A repository scaffolded by an older plugin: every file present, and
        AGENTS.md holding content this plugin's template no longer has."""
        root = Path(tmp)
        run_moltke(root, "--scaffold")
        agents = root / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8")
                          + "\n## Old rule from a previous release\n", encoding="utf-8")
        return root

    def test_a_kept_file_that_matches_the_template_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.cloned(tmp)
            result = run_moltke(root, "--scaffold")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in ("CLAUDE.md", ".cursor/rules/moltke.mdc"):
                line = next(l for l in result.stdout.splitlines() if name in l)
                self.assertIn("matches the installed template", line)

    def test_a_kept_file_that_drifted_is_reported_file_by_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.cloned(tmp)
            result = run_moltke(root, "--scaffold")
            line = next(l for l in result.stdout.splitlines() if "AGENTS.md" in l)
            self.assertIn("differs from the installed template", line)
            self.assertIn("AGENTS.md", result.stdout)

    def test_drift_is_reported_and_never_acted_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.cloned(tmp)
            before = (root / "AGENTS.md").read_text(encoding="utf-8")
            run_moltke(root, "--scaffold")
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), before,
                             "--scaffold overwrote a kept file")

    def test_the_workflow_state_files_are_not_compared(self):
        # adocs/ is the project's own content the moment it is used: comparing it
        # against the template would report drift on every real repository.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.cloned(tmp)
            specs = root / "adocs" / "specs.md"
            specs.write_text(specs.read_text(encoding="utf-8") + "\nreal content\n",
                             encoding="utf-8")
            result = run_moltke(root, "--scaffold")
            line = next(l for l in result.stdout.splitlines() if "adocs/specs.md" in l)
            self.assertNotIn("template", line)

    def test_an_untouched_scaffold_reports_no_drift_at_all(self):
        # Non-vacuity: if this reported drift, every line above would be noise.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_moltke(root, "--scaffold")
            result = run_moltke(root, "--scaffold")
            self.assertNotIn("differs from the installed template", result.stdout)
            self.assertIn("matches the installed template", result.stdout)


class TestInitSkill(unittest.TestCase):
    def test_skill_declares_name_and_description(self):
        skill = REPO / "skills" / "init" / "SKILL.md"
        self.assertTrue(skill.is_file(), "skills/init/SKILL.md missing")
        text = skill.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "SKILL.md needs YAML frontmatter")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: init", frontmatter)
        self.assertRegex(frontmatter, r"description:\s*\S")

    def test_the_already_enabled_branch_is_a_verification_path(self):
        # S029: "already set up, scaffolding again is pointless" was the whole
        # instruction for the commonest case there is — a colleague cloning a
        # repository that already uses moltke.
        text = (REPO / "skills" / "init" / "SKILL.md").read_text(encoding="utf-8")
        branch = text.split("`\"enabled\": true`", 1)[1].split("## 2.", 1)[0]
        for expected in ("--validate", "--session-start", "--scaffold", "drift"):
            self.assertIn(expected, branch,
                          f"the enabled-marker branch does not mention {expected!r}")
        self.assertRegex(branch, r"(?i)ask|yes|explicit",
                         "a template refresh must be offered, not applied")

    def test_the_planning_phase_uses_the_tool_rather_than_hand_copied_files(self):
        # S028: a scaffold leaves specs.md and plan.md as comments, and the step
        # after it was "seed plan.md and one step file per planned step, using
        # templates/step_template.md" — hand-copying into the one directory
        # --pre-write refuses. The skill drives the tool instead.
        text = (REPO / "skills" / "init" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("--step new", text,
                      "step files are created by the tool, not by copying a template")
        self.assertNotRegex(text, r"step_template\.md",
                            "the skill still points at hand-copying the step template")
        for expected in ("prime directive", "decisions.md", "--step status", "commit"):
            self.assertIn(expected, text, f"the planning phase does not mention {expected!r}")


class TestPlanningPhaseNudge(unittest.TestCase):
    """S028: the scaffold writes files whose content is a comment, and nothing
    said so. A repository can sit for weeks with an empty prime directive and an
    empty plan while every check reports green — which is honest, since both are
    the user's to write, and useless. `--session-start` says it is pending. It is
    a nudge in additionalContext and never an exit: DEC-006 and INV-12 make
    no-deadlock a property, and this is a file only a human can fill."""

    def scaffolded(self, tmp):
        root = Path(tmp)
        result = run_moltke(root, "--scaffold")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return root

    def context(self, root):
        result = run_moltke(root, "--session-start")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]

    def fill_specs(self, root):
        specs = root / "adocs" / "specs.md"
        specs.write_text(specs.read_text(encoding="utf-8").replace(
            "<!-- The single property this project must never violate. One sentence. -->",
            "Every request is answered from committed state alone."), encoding="utf-8")

    def fill_plan(self, root):
        run_moltke(root, "--step", "new", "first_thing", "--goal", "do the first thing")

    def test_a_fresh_scaffold_says_the_planning_phase_is_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.scaffolded(tmp)
            context = self.context(root)
            self.assertIn("planning", context.lower())
            self.assertIn("adocs/specs.md", context)
            self.assertIn("adocs/plan.md", context)

    def test_the_nudge_never_blocks(self):
        # It rides in additionalContext on an exit 0, and --stop does not gain a
        # new reason to refuse: an unfilled specs.md is not a violation.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.scaffolded(tmp)
            self.assertEqual(run_moltke(root, "--session-start").returncode, 0)
            self.assertEqual(run_moltke(root, "--validate").returncode, 0)
            stop = subprocess.run([sys.executable, str(MOLTKE), "--stop"], cwd=root,
                                  capture_output=True, text=True, input="{}")
            self.assertNotIn("planning", stop.stderr.lower())

    def test_only_the_prime_directive_missing_still_nudges_and_names_only_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.scaffolded(tmp)
            self.fill_plan(root)
            context = self.context(root)
            self.assertIn("adocs/specs.md", context)
            self.assertNotIn("adocs/plan.md", context)

    def test_only_the_plan_empty_still_nudges_and_names_only_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.scaffolded(tmp)
            self.fill_specs(root)
            context = self.context(root)
            self.assertIn("adocs/plan.md", context)
            self.assertNotIn("adocs/specs.md", context)

    def test_the_nudge_disappears_once_both_are_filled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.scaffolded(tmp)
            self.fill_specs(root)
            self.fill_plan(root)
            context = self.context(root)
            self.assertNotIn("planning", context.lower())

    def test_a_prime_directive_written_only_inside_guidance_does_not_count(self):
        # The template's own comment is guidance, and so is a fenced example: the
        # check reads the section through strip_guidance like everything else.
        with tempfile.TemporaryDirectory() as tmp:
            root = self.scaffolded(tmp)
            specs = root / "adocs" / "specs.md"
            specs.write_text(specs.read_text(encoding="utf-8").replace(
                "<!-- The single property this project must never violate. One sentence. -->",
                "```\nnever lose a write\n```"), encoding="utf-8")
            self.assertIn("adocs/specs.md", self.context(root))

    def test_an_unscaffolded_repository_says_nothing_about_planning(self):
        # Non-vacuity in the other direction: no marker means moltke is silent,
        # which INV-11 requires.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_moltke(root, "--session-start")
            self.assertEqual(result.returncode, 0)
            self.assertNotIn("planning", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
