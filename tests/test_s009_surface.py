"""S009: golden test over the moltke CLI surface (DEC-010, surface_guard "cli").

The golden fails on any added, renamed, or removed command, flag, or operation.
Refreshing it is deliberate: the documentation check below fails until the new
surface is described in the specs table and MANUAL, in the same commit.
"""

import importlib.util
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GOLDEN = Path(__file__).resolve().parent / "golden" / "cli_surface.txt"

_spec = importlib.util.spec_from_file_location("moltke", REPO / "bin" / "moltke.py")
moltke = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(moltke)

REFRESH = (f"Surface changed. Update the CLI table in project/specs.md and MANUAL.md in "
           f"this same commit, then refresh the golden with:\n"
           f"  python3 tests/test_s009_surface.py --refresh")


def current_surface():
    """One line per option: its flags, its argument shape, and its operations.

    Reads argparse's actions rather than --help text, so wording changes do not
    churn the golden but a rename or a new flag does.
    """
    lines = []
    for action in moltke.build_parser()._actions:
        if not action.option_strings:
            continue
        flags = "/".join(sorted(action.option_strings))
        if action.nargs == 0:
            shape = ""
        elif action.nargs == "?":
            shape = f"[{action.metavar or 'VALUE'}]"
        elif action.nargs in ("+", "*"):
            shape = f"{action.metavar or 'VALUE'}..."
        else:
            shape = action.metavar or "VALUE"
        ops = ""
        if flags == "--step":
            ops = "  ops: " + ",".join(sorted(moltke.STEP_OPS))
        elif flags == "--audit":
            ops = "  ops: " + ",".join(sorted(moltke.AUDIT_OPS))
        lines.append(f"{flags} {shape}".rstrip() + ops)
    return "\n".join(sorted(lines)) + "\n"


class TestGoldenSurface(unittest.TestCase):
    def test_surface_matches_the_golden(self):
        self.assertTrue(GOLDEN.is_file(), f"missing {GOLDEN}. {REFRESH}")
        self.assertEqual(current_surface(), GOLDEN.read_text(encoding="utf-8"), REFRESH)


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
        self.assertEqual(missing, [], f"{label} does not describe: {missing}. {REFRESH}")

    def test_specs_describes_every_mode(self):
        specs = REPO / "project" / "specs.md"
        self.assertIn("--goal", specs.read_text(encoding="utf-8"),
                      "precondition: the specs CLI table is present and detailed")
        self.assert_documented(specs, "project/specs.md")

    def test_manual_describes_every_mode_once_it_exists(self):
        manual = REPO / "MANUAL.md"
        if not manual.is_file():
            self.skipTest("MANUAL.md lands in S011; this check activates with it")
        self.assert_documented(manual, "MANUAL.md")


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
