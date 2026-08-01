"""S002: marker gate (INV-11) and --validate marker checks.

Runs bin/moltke.py as a subprocess, the same surface hooks and humans use.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import marked_repo, write_marker

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"

ALL_MODES = (
    ["--session-start"],
    ["--log-prompt"],
    ["--pre-write", "some/path"],
    ["--post-write"],
    ["--stop"],
    ["--validate"],
    ["--scaffold"],
)


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
            for mode in ALL_MODES:
                result = run_moltke(tmp, *mode)
                self.assertEqual(result.returncode, 0, (mode, result.stderr))

    def test_every_mode_exits_0_when_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"enabled": False})
            for mode in ALL_MODES:
                result = run_moltke(tmp, *mode)
                self.assertEqual(result.returncode, 0, (mode, result.stderr))

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
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp)
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
