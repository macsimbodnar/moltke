"""S013: the workflow directory is adocs/, never project/ (DEC-021).

History is exempt by design: plan_done/ is immutable, worklog.md and
decisions.md are append-only, and testing.md rows are never rewritten. Those
files keep saying project/ and read through DEC-021.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"
REPO = MOLTKE.parent.parent

# Pure documentation: any project/ here is a leftover, never history.
LIVE_DOCS = (
    "AGENTS.md",
    "templates/AGENTS.md",
    "README.md",
    "MANUAL.md",
    "templates/cursor_rules",
    "skills/init/SKILL.md",
    "skills/step/SKILL.md",
    "skills/audit/SKILL.md",
    "agents/adversarial_reviewer.md",
)


class TestScaffoldNamesAdocs(unittest.TestCase):
    def test_scaffold_creates_adocs_and_never_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(MOLTKE), "--scaffold"],
                                    cwd=tmp, capture_output=True, text=True, input="")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            # Precondition: the scaffold ran and produced a tree at all, so the
            # absence of project/ below is evidence and not an empty directory.
            self.assertTrue((Path(tmp) / "adocs" / "plan.md").is_file(),
                            "scaffold wrote no adocs/plan.md; the assertion below would be vacuous")
            self.assertFalse((Path(tmp) / "project").exists(),
                             "scaffold created project/; the directory is adocs/ (DEC-021)")


class TestNoStaleProjectPaths(unittest.TestCase):
    """Documentation must not instruct the old path.

    Naming `project/` as history is legal but must be deliberate: wrap it in
    `<!-- historical -->` ... `<!-- /historical -->`. Same idiom as
    strip_guidance in bin/moltke.py, where an HTML comment means "not data".
    Anything outside a marked block is a leftover.
    """

    def test_live_docs_name_adocs(self):
        stale, marked = [], 0
        for rel in LIVE_DOCS:
            path = REPO / rel
            self.assertTrue(path.is_file(), f"{rel} is missing; the scan below would be vacuous")
            historical = False
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "<!-- historical -->" in line:
                    historical = True
                elif "<!-- /historical -->" in line:
                    historical = False
                elif "project/" in line:
                    if historical:
                        marked += 1
                    else:
                        stale.append(f"{rel}:{number}: {line.strip()}")
            self.assertFalse(historical, f"{rel} opens a historical block and never closes it")
        # Non-vacuous by construction: if nothing anywhere says project/, the
        # scan proves nothing, so the marked mentions must actually be there.
        self.assertGreater(marked, 0, "no marked historical mention found; the scan is vacuous")
        self.assertEqual(stale, [], "these live files still name project/ outside a marked "
                                    "historical block (DEC-021):\n" + "\n".join(stale))


if __name__ == "__main__":
    unittest.main()
