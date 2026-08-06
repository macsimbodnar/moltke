"""S009: golden test over the moltke public surface (DEC-010, surface_guard "cli").

The golden fails on any added, renamed, or removed command, flag, or operation,
and since S023 on any added, renamed, or removed skill, hook event, or recognised
marker key. Refreshing it is deliberate: the documentation check below fails until
the new surface is described in the specs table and MANUAL, in the same commit.
"""

import re
import unittest
from pathlib import Path

from surface import (REPO, current_surface, declared_hook_events, declared_skills,
                     moltke)

GOLDEN = Path(__file__).resolve().parent / "golden" / "cli_surface.txt"

REFRESH = (f"Surface changed. Update the CLI table in adocs/specs.md and MANUAL.md in "
           f"this same commit, then refresh the golden with:\n"
           f"  python3 tests/test_s009_surface.py --refresh")


class TestGoldenSurface(unittest.TestCase):
    def test_surface_matches_the_golden(self):
        self.assertTrue(GOLDEN.is_file(), f"missing {GOLDEN}. {REFRESH}")
        self.assertEqual(current_surface(), GOLDEN.read_text(encoding="utf-8"), REFRESH)

    def test_the_golden_covers_more_than_argparse(self):
        # Precondition for the tampering the accepts calls for: if these three
        # lines were absent, every component check below would pass vacuously.
        golden = GOLDEN.read_text(encoding="utf-8")
        for prefix in ("hooks: ", "marker keys: ", "skills: "):
            self.assertIn(prefix, golden, f"the golden no longer declares {prefix!r}")


class TestSurfaceIsDocumented(unittest.TestCase):
    """Teeth: refreshing the golden alone does not make the suite green."""

    EXEMPT = {"--help", "-h", "--goal", "--stamp"}  # argparse builtin; the rest
    # are documented inside the --step row rather than as rows of their own.

    def assert_documented(self, path, label):
        text = path.read_text(encoding="utf-8")
        missing = []
        for action in moltke.build_parser()._actions:
            missing.extend(flag for flag in action.option_strings
                           if flag not in self.EXEMPT and flag not in text)
        # An operation counts as described only where its own mode is described,
        # so a bare "new" or "status" somewhere in the prose does not satisfy it.
        for mode, ops in (("--step", moltke.STEP_OPS), ("--audit", moltke.AUDIT_OPS)):
            scope = "\n".join(line for line in text.splitlines() if mode in line)
            missing.extend(f"{mode} {op}" for op in ops
                           if not re.search(rf"\b{re.escape(op)}\b", scope))
        # A skill counts as described where it is named as a component, either
        # `/moltke:<name>` or `<name>` in backticks — not merely as English prose,
        # since "step" and "audit" are words this documentation uses constantly.
        for skill in declared_skills():
            if not re.search(rf"(?:/moltke:{re.escape(skill)}|`{re.escape(skill)}`)", text):
                missing.append(f"skill {skill}")
        for event in declared_hook_events():
            if event not in text:
                missing.append(f"hook {event}")
        for key in moltke.MARKER_KEYS:
            if key not in text:
                missing.append(f"marker key {key}")
        self.assertEqual(missing, [], f"{label} does not describe: {missing}. {REFRESH}")

    def test_specs_describes_every_mode(self):
        specs = REPO / "adocs" / "specs.md"
        self.assertIn("--goal", specs.read_text(encoding="utf-8"),
                      "precondition: the specs CLI table is present and detailed")
        self.assert_documented(specs, "adocs/specs.md")

    def test_manual_describes_every_mode_once_it_exists(self):
        manual = REPO / "MANUAL.md"
        if not manual.is_file():
            self.skipTest("MANUAL.md lands in S011; this check activates with it")
        self.assert_documented(manual, "MANUAL.md")


class TestMarkerKeysAreLoadBearing(unittest.TestCase):
    """MARKER_KEYS is what the golden guards, so it must match what the code
    actually validates rather than being a decorative list."""

    GOOD = {"schema": 1, "enabled": True, "plan_active_max": 1,
            "plan_stack_max": 3, "surface_guard": "cli",
            "test_command": "true"}

    def test_the_good_marker_is_accepted(self):
        # Non-vacuity anchor for the per-key checks below.
        self.assertEqual(moltke.check_marker(dict(self.GOOD)), [])

    def test_every_declared_key_is_actually_validated(self):
        for key in moltke.MARKER_KEYS:
            with self.subTest(key):
                marker = dict(self.GOOD)
                marker[key] = ["not a valid value for any key"]
                violations = moltke.check_marker(marker)
                self.assertTrue(any(key in v for v in violations),
                                f"{key} is in MARKER_KEYS but check_marker ignores it, so the "
                                f"golden guards a key that means nothing")

    def test_an_unrecognised_key_is_ignored_not_rejected(self):
        marker = dict(self.GOOD)
        marker["some_future_key"] = "whatever"
        self.assertEqual(moltke.check_marker(marker), [])


class TestRulesetIdentity(unittest.TestCase):
    """DEC-012 identity is covered by test_s006_scaffold.py; this asserts the
    guard exists rather than duplicating the comparison."""

    def test_identity_guard_is_present(self):
        covering = (REPO / "tests" / "test_s006_scaffold.py").read_text(encoding="utf-8")
        self.assertIn("test_ruleset_template_matches_the_live_ruleset", covering)


if __name__ == "__main__":
    import sys
    if "--refresh" in sys.argv:
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(current_surface(), encoding="utf-8")
        print(f"refreshed {GOLDEN}")
    else:
        unittest.main()
