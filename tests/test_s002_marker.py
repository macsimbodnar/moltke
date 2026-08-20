"""S002: marker gate (INV-11) and --validate marker checks.

Runs bin/moltke.py as a subprocess, the same surface hooks and humans use.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import marked_repo, workflow_repo, write_marker
from surface import declared_modes, moltke

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"

# Exempt from the gate by design, each for a stated reason:
#   --version   answers "which moltke is this", and is most useful exactly where
#               checkout and hooks disagree, marker or no marker (S127)
#   --scaffold  exists to create the marker the gate reads (DEC-017)
#   --decline   exists to write the marker that says no (DEC-017)
#   --watch     its exit codes are answers about a run; the gate's exit 0 would
#               read as a marker seen (DEC-049)
# The set is named rather than derived, so a mode added without a decision about
# it lands in the gated list and has to exit 0 (S150).
GATE_EXEMPT = ("--version", "--scaffold", "--decline", "--watch")

# Arguments for the gated modes that require them; a mode absent here takes none.
MODE_ARGS = {
    "--pre-write": ["some/path"],
    "--step": ["status"],
    "--audit": ["list"],
}


def gated_modes():
    """Every mode the parser declares that INV-11 must cover, as argv lists."""
    return [[mode, *MODE_ARGS.get(mode, [])]
            for mode in declared_modes() if mode not in GATE_EXEMPT]


def run_moltke(cwd, *args):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=cwd, capture_output=True, text=True,
    )


class TestInv11MarkerGate(unittest.TestCase):
    """INV-11: no marker or enabled false means exit 0, no friction.

    Non-vacuity: TestValidateMarker proves the same binary exits non-zero
    when the marker is present, enabled, and broken.
    """

    def test_every_mode_exits_0_without_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode in gated_modes():
                result = run_moltke(tmp, *mode)
                self.assertEqual(result.returncode, 0, (mode, result.stderr))

    def test_every_mode_exits_0_when_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"enabled": False})
            for mode in gated_modes():
                result = run_moltke(tmp, *mode)
                self.assertEqual(result.returncode, 0, (mode, result.stderr))

    def test_the_gated_list_is_the_parsers_own(self):
        """Non-vacuity for the two tests above: they asserted over a derived
        list, and a derivation quietly returning fewer modes would shrink their
        coverage while the names still read as every mode — F10 one level up.

        So the derivation is checked against a second read of the same parser:
        `declared_modes` walks the mutually exclusive group, this walks every
        action, and each option has to be a declared mode or one of the
        modifiers named here. Counting them instead would be an identity, since
        the gated list is the declared list minus the exempt one.
        """
        modifiers = {"-h", "--goal", "--stamp", "--pid", "--fail-re",
                     "--ceiling", "--interval"}
        options = {action.option_strings[0]
                   for action in moltke.build_parser()._actions
                   if action.option_strings}
        declared = declared_modes()
        self.assertEqual(options - modifiers, set(declared))
        for mode in GATE_EXEMPT:
            self.assertIn(mode, declared, "exempts a mode the parser does not declare")
        for mode in MODE_ARGS:
            self.assertIn(mode, declared, "arms a mode the parser does not declare")

    def test_disabled_beats_other_marker_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"enabled": False, "surface_guard": "bogus"})
            result = run_moltke(tmp, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_marker_found_from_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"surface_guard": "bogus"})
            sub = Path(tmp) / "src" / "deep"
            sub.mkdir(parents=True)
            result = run_moltke(sub, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


class TestValidateMarker(unittest.TestCase):
    """--validate exits 1 and names every marker violation."""

    def assert_violation(self, tmp, needle):
        result = run_moltke(tmp, "--validate")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("VIOLATION", result.stdout)
        self.assertIn(needle, result.stdout)

    def test_valid_marker_passes(self):
        # Re-targeted in S003: valid now means marker plus a minimal plan tree,
        # because INV-3 treats an enabled repo without plan.md as drift.
        with tempfile.TemporaryDirectory() as tmp:
            workflow_repo(tmp)
            result = run_moltke(tmp, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("all checks pass", result.stdout)

    def test_malformed_json_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_marker(tmp, "{this is not json")
            self.assert_violation(tmp, "unreadable")

    def test_non_object_marker_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_marker(tmp, [1, 2, 3])
            self.assert_violation(tmp, "JSON object")

    def test_bad_schema_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"schema": 2})
            self.assert_violation(tmp, "schema")

    def test_missing_enabled_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, remove=("enabled",))
            self.assert_violation(tmp, "enabled")

    def test_bad_limits_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"plan_active_max": 0, "plan_stack_max": "3"})
            result = run_moltke(tmp, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("plan_active_max", result.stdout)
            self.assertIn("plan_stack_max", result.stdout)

    def test_bad_surface_guard_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"surface_guard": "bogus"})
            self.assert_violation(tmp, "surface_guard")

    def test_all_violations_reported_not_just_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"schema": 9, "surface_guard": "nope"})
            result = run_moltke(tmp, "--validate")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("schema", result.stdout)
            self.assertIn("surface_guard", result.stdout)


if __name__ == "__main__":
    unittest.main()
