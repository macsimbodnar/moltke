"""S033 (2026-08-07_adversarial-F02): a code fence must not be able to hide data.

`strip_guidance` exists so template guidance is never counted as data. Pairing
triple-backtick markers globally meant an odd marker shifted every later pairing
and deleted real content between two unrelated fences — turning a rule about
making guidance invisible into a way of making evidence invisible. The audit
report that reported this reproduced it on itself.
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import audit_report, workflow_repo
from surface import moltke

strip = moltke.strip_guidance
MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"


def run_validate(cwd):
    return subprocess.run([sys.executable, str(MOLTKE), "--validate"],
                          cwd=cwd, capture_output=True, text=True)


class TestBalancedFencesStillStrip(unittest.TestCase):
    """Non-vacuity anchor: the original job still gets done."""

    def test_a_closed_fence_is_removed(self):
        self.assertEqual(strip("before\n```\nhidden\n```\nafter\n"), "before\nafter\n")

    def test_two_closed_fences_are_removed_and_the_text_between_survives(self):
        text = "a\n```\nx\n```\nkeep me\n```\ny\n```\nb\n"
        self.assertEqual(strip(text), "a\nkeep me\nb\n")

    def test_html_comments_are_still_removed(self):
        self.assertEqual(strip("a <!-- gone --> b"), "a  b")


class TestUnbalancedFencesKeepData(unittest.TestCase):
    def test_a_trailing_unclosed_fence_does_not_swallow_the_rest(self):
        self.assertIn("keep me", strip("a\n```\nkeep me\nand me\n"))

    def test_a_stray_marker_no_longer_shifts_the_pairing_of_later_fences(self):
        # Before S033 the whole tail after an odd marker was mis-paired. Now the
        # unpaired marker is text and the fences after it pair with each other.
        text = "### KEEP\ntext\n```\nreally fenced\n```\n### ALSO KEEP\n```\nunclosed\ntail\n"
        kept = strip(text)
        self.assertIn("### KEEP", kept)
        self.assertIn("### ALSO KEEP", kept)
        self.assertIn("tail", kept)
        self.assertNotIn("really fenced", kept)

    def test_two_unclosed_fences_are_ambiguous_and_are_reported_not_guessed(self):
        # The shape from the finding: two evidence blocks, neither closed, with a
        # real finding between them. This is byte-identical to one closed fence,
        # and the templates deliberately put headings inside fences — the audit
        # report template's example finding is one — so no heuristic can tell
        # them apart. strip pairs them; INV-13 is what makes the file loud.
        text = ("### F01\n```\nevidence one\n"
                "### F02  the finding between them\n```\nevidence two\n### F03\n")
        self.assertNotIn("F02  the finding between them", strip(text),
                         "if this ever changes, the INV-13 tests below are the safety net")
        self.assertIn("### F03", strip(text))
        self.assertEqual(len(re.findall(r"^ {0,3}```", text, re.M)) % 2, 0,
                         "and the count is even, which is why parity alone cannot catch it")


class TestOnlyLineStartMarkersAreFences(unittest.TestCase):
    def test_a_quoted_marker_in_a_worklog_prompt_is_not_a_fence(self):
        # --log-prompt quotes every line with "> ", so a user pasting a fenced
        # snippet writes "> ```" — text, not a fence.
        text = "## prompt\n\n> here is code:\n> ```\n> x\n> ```\n\n## 2026-08-07 recap S001\n"
        self.assertIn("## 2026-08-07 recap S001", strip(text))
        self.assertIn("> x", strip(text))

    def test_an_inline_code_span_is_not_a_fence(self):
        self.assertEqual(strip("use ``` to open a block\nand more text\n"),
                         "use ``` to open a block\nand more text\n")

    def test_an_indented_fence_is_still_a_fence(self):
        # Up to three spaces is still a fence in markdown, and templates indent.
        self.assertEqual(strip("a\n   ```\nx\n   ```\nb\n"), "a\nb\n")


class TestAmbiguityIsReportedNotGuessed(unittest.TestCase):
    """Two unclosed fences are genuinely ambiguous: they look exactly like one
    closed fence, and the templates deliberately put headings inside fences, so
    no heuristic can tell them apart. INV-13 says so out loud instead."""

    def test_an_odd_marker_count_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            worklog = root / "adocs" / "worklog.md"
            worklog.write_text(worklog.read_text(encoding="utf-8") + "\n```\nunclosed\n",
                               encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-13", result.stdout)
            self.assertIn("worklog.md", result.stdout)

    def test_balanced_fences_are_not_reported(self):
        # Non-vacuity: the fixture repo and a closed fence must both stay clean.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            self.assertEqual(run_validate(root).returncode, 0)
            worklog = root / "adocs" / "worklog.md"
            worklog.write_text(worklog.read_text(encoding="utf-8") + "\n```\nclosed\n```\n",
                               encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_quoted_marker_in_a_prompt_does_not_trip_it(self):
        # The worklog quotes prompts, so pasted fences arrive as "> ```" and are
        # not markers at all. Counting them would make the check unusable.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            worklog = root / "adocs" / "worklog.md"
            worklog.write_text(worklog.read_text(encoding="utf-8")
                               + "\n## prompt\n\n> ```\n> x\n> ```\n> and one more:\n> ```\n",
                               encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_an_audit_report_with_an_odd_count_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "accepted")])
            report = root / "adocs" / "audit" / "2026-08-01_adversarial.md"
            report.write_text(report.read_text(encoding="utf-8") + "\n```\nevidence\n",
                              encoding="utf-8")
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-13", result.stdout)


if __name__ == "__main__":
    unittest.main()
