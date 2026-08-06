"""S010: plugin manifest and marketplace entry.

Verified statically here plus `claude plugin validate --strict`. Installing on a
second machine is S012 and belongs to the repository owner (DEC-014, DEC-019).
"""

import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from surface import declared_hook_events, declared_skills

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / ".claude-plugin" / "plugin.json"
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MANIFEST.is_file(), f"missing {MANIFEST}")
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_name_is_kebab_case_and_namespaces_the_skills(self):
        name = self.manifest["name"]
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertEqual(name, "moltke", "skills are documented as /moltke:<skill>")

    def test_version_is_explicit_and_semantic(self):
        # DEC-002: an explicit version means updates need a deliberate bump
        # instead of every commit being treated as a new release.
        self.assertRegex(self.manifest["version"], r"^\d+\.\d+\.\d+$")

    def test_describes_itself(self):
        self.assertGreater(len(self.manifest.get("description", "")), 20)

    def test_declared_component_paths_exist(self):
        for field in ("skills", "agents", "hooks", "commands", "mcpServers"):
            value = self.manifest.get(field)
            for entry in ([value] if isinstance(value, str) else value or []):
                self.assertTrue((REPO / entry).exists(), f"{field} points at missing {entry}")


class TestComponentsAreDiscoverable(unittest.TestCase):
    """Default layout: skills/, agents/, hooks/hooks.json at the plugin root."""

    def test_each_skill_directory_names_itself(self):
        # Discovered, not hardcoded: a hardcoded list made a fourth skill
        # invisible to the whole suite (S023, F10). The golden is what pins the
        # set; this pins name-matches-directory for whatever is there.
        skills = declared_skills()
        self.assertTrue(skills, "no skills discovered under skills/*/SKILL.md")
        for skill in skills:
            path = REPO / "skills" / skill / "SKILL.md"
            self.assertTrue(path.is_file(),
                            f"skill {skill!r} names itself but does not live in skills/{skill}/, "
                            f"so it cannot resolve as /moltke:{skill}")

    def test_skills_are_not_hidden_inside_the_manifest_directory(self):
        self.assertFalse((REPO / ".claude-plugin" / "skills").exists())

    def test_reviewer_agent_is_discoverable(self):
        self.assertTrue((REPO / "agents" / "adversarial_reviewer.md").is_file())

    def test_every_declared_hook_event_has_a_command(self):
        # assertTrue(commands) below was satisfied by any one surviving event, so
        # deleting Stop outright left the suite green (S023, F10).
        hooks = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        for event in declared_hook_events():
            matchers = hooks["hooks"][event]
            self.assertTrue([entry for matcher in matchers for entry in matcher["hooks"]],
                            f"hook event {event} is declared with no command")

    def test_hooks_call_the_checker_through_the_plugin_root(self):
        hooks = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        commands = [entry["command"]
                    for matchers in hooks["hooks"].values()
                    for matcher in matchers
                    for entry in matcher["hooks"]]
        self.assertTrue(commands, "no hook commands declared")
        for command in commands:
            self.assertIn("${CLAUDE_PLUGIN_ROOT}", command,
                          "plugins are copied into a cache; absolute paths break")
            self.assertIn("bin/moltke.py", command)
        self.assertTrue(os.access(REPO / "bin" / "moltke.py", os.X_OK),
                        "bin/moltke.py must be executable")


class TestMarketplace(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MARKETPLACE.is_file(), f"missing {MARKETPLACE}")
        self.marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))

    def test_lists_this_plugin_at_a_resolvable_source(self):
        self.assertRegex(self.marketplace["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertTrue(self.marketplace["owner"]["name"])
        entries = self.marketplace["plugins"]
        self.assertEqual(len(entries), 1, "this repository ships exactly one plugin")
        entry = entries[0]
        self.assertEqual(entry["name"], "moltke")
        source = entry["source"]
        self.assertIsInstance(source, str, "the plugin lives at the marketplace root")
        self.assertTrue((REPO / source / ".claude-plugin" / "plugin.json").is_file(),
                        f"source {source!r} does not resolve to the plugin")

    def test_entry_does_not_contradict_the_manifest(self):
        entry = self.marketplace["plugins"][0]
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if "version" in entry:
            self.assertEqual(entry["version"], manifest["version"],
                             "marketplace entry version overrides plugin.json; keep them equal")


class TestClaudeValidates(unittest.TestCase):
    def test_claude_plugin_validate_strict_passes(self):
        if shutil.which("claude") is None:
            self.skipTest("claude CLI not on PATH")
        result = subprocess.run(["claude", "plugin", "validate", str(REPO), "--strict"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
