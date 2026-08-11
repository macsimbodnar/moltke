"""S033 (2026-08-07_adversarial-F02): a code fence must not be able to hide data.

`strip_guidance` exists so template guidance is never counted as data. Pairing
triple-backtick markers globally meant an odd marker shifted every later pairing
and deleted real content between two unrelated fences — turning a rule about
making guidance invisible into a way of making evidence invisible. The audit
report that reported this reproduced it on itself.
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import audit_report, workflow_repo
from surface import REPO, moltke

strip = moltke.strip_guidance
MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"


def run_moltke(cwd, *args, stdin=""):
    return subprocess.run([sys.executable, str(MOLTKE), *args],
                          cwd=cwd, input=stdin, capture_output=True, text=True)


def run_validate(cwd):
    return run_moltke(cwd, "--validate")


# The J2 case of 2026-08-07_adversarial-F02, verbatim: two evidence blocks, the
# second finding between them. `CLOSED` is the control; removing the two closing
# markers is the whole of the tampering.
CLOSED_REPORT = ("# Audit\n\n"
                 "### 2026-08-01_adversarial-F01  high  one\n\nStatus: accepted\n\n"
                 "```\nevidence one\n```\n\n"
                 "### 2026-08-01_adversarial-F02  high  two\n\nStatus: open\n\n"
                 "```\nevidence two\n```\n")
UNCLOSED_REPORT = CLOSED_REPORT.replace("evidence one\n```", "evidence one") \
                               .replace("evidence two\n```", "evidence two")


def report_repo(tmp, body):
    root = workflow_repo(tmp)
    report = audit_report(root, [("2026-08-01_adversarial-F01", "accepted")])
    report.write_text(body, encoding="utf-8")
    return root, report


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
    def test_an_inline_code_span_is_not_a_fence(self):
        self.assertEqual(strip("use ``` to open a block\nand more text\n"),
                         "use ``` to open a block\nand more text\n")

    def test_an_indented_fence_is_still_a_fence(self):
        # Up to three spaces is still a fence in markdown, and templates indent.
        self.assertEqual(strip("a\n   ```\nx\n   ```\nb\n"), "a\nb\n")


class TestAReportCannotHideItsOwnFindings(unittest.TestCase):
    """Retargeted by S124 (DEC-047): INV-14 is retired, and a fence-swallowed
    finding surfaces through --audit list as `hidden` instead of blocking."""
    """S049 (2026-08-07_adversarial-F02, .2-F04): parity catches one unclosed
    fence, not two. Two unclosed fences are two markers, pair as one closed
    fence, and the finding between them vanishes with INV-13 silent. INV-14
    compares the finding headings in the raw text against the ones that survive
    stripping, scoped to the report's own stem — which is what keeps the
    template's fenced `YYYY-MM-DD_type-F01` example guidance rather than a
    hidden finding."""

    def test_the_control_is_the_same_report_with_both_fences_closed(self):
        # Non-vacuity: without this, an exit 1 below could be the checker being
        # broken rather than the finding being hidden. Closed, F02 is visible,
        # open, and unreferenced, so INV-10 has something to say.
        with tempfile.TemporaryDirectory() as tmp:
            root, _report = report_repo(tmp, CLOSED_REPORT)
            result = run_validate(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("INV-10", result.stdout)
            self.assertIn("2026-08-01_adversarial-F02", result.stdout)
            self.assertNotIn("INV-14", result.stdout)

    def test_audit_list_names_the_hidden_finding_instead_of_omitting_it(self):
        # The half of the finding that --validate does not cover: the report the
        # operator reads listed F01 alone and exited 0.
        with tempfile.TemporaryDirectory() as tmp:
            root, _report = report_repo(tmp, UNCLOSED_REPORT)
            result = run_moltke(root, "--audit", "list")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("2026-08-01_adversarial-F02", result.stdout)
            self.assertIn("hidden", result.stdout)

    def test_a_report_whose_findings_are_all_visible_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _report = report_repo(
                tmp, "# Audit\n\n### 2026-08-01_adversarial-F01  high  one\n\n"
                     "Status: accepted\n\n```\nevidence one\n```\n")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_freshly_created_report_is_clean(self):
        # The case the rule deliberately cannot see, and the reason the template
        # stopped substituting the real stem into its fenced example: guidance
        # written under this report's own name is byte-identical to a swallowed
        # finding. A scaffolded report must stay clean.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            created = run_moltke(root, "--audit", "new", "adversarial")
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            report = next((root / "adocs" / "audit").glob("*.md"))
            self.assertRegex(report.read_text(encoding="utf-8"), r"(?m)^###\s+\S*-F\d{2}\b",
                             "precondition: the report really does fence an example finding")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_shipped_template_does_not_write_a_finding_under_the_real_stem(self):
        # Why the test above passes, stated as its own property: the substitution
        # in audit_new must not reach inside the fenced example.
        template = (REPO / "templates" / "audit_report_template.md").read_text(encoding="utf-8")
        stem = "2026-08-01_adversarial"
        substituted = template.replace("YYYY-MM-DD_type", stem).replace("YYYY-MM-DD", "2026-08-01")
        self.assertEqual(moltke.own_finding_headings(substituted, stem), [])

    def test_a_quoted_heading_from_another_report_is_not_a_hidden_finding(self):
        # Reports quote each other constantly — the verdict sections of the
        # 2026-08-07 runs are nothing but that. Only this report's own stem
        # counts, so a quoted foreign heading inside a closed fence stays quiet.
        with tempfile.TemporaryDirectory() as tmp:
            root, _report = report_repo(
                tmp, "# Audit\n\n### 2026-08-01_adversarial-F01  high  one\n\n"
                     "Status: accepted\n\n```\n### 2026-07-01_security-F03  high  quoted\n```\n")
            result = run_validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_same_day_rerun_report_is_scoped_to_its_own_stem(self):
        # `<stem>.2` is a prefix relative of `<stem>`, which is the trap S020
        # named for INV-10; the same trap applies to matching headings here.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            audit_report(root, [("2026-08-01_adversarial-F01", "accepted")])
            rerun = audit_report(root, [("2026-08-01_adversarial.2-F01", "accepted")],
                                 name="2026-08-01_adversarial.2.md")
            rerun.write_text("# Audit\n\n### 2026-08-01_adversarial.2-F01  high  one\n\n"
                             "Status: accepted\n\n```\nevidence\n"
                             "### 2026-08-01_adversarial.2-F02  high  two\n\nStatus: open\n\n"
                             "```\nmore evidence\n", encoding="utf-8")
            result = run_moltke(root, "--audit", "list")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("hidden", result.stdout)
            self.assertIn("2026-08-01_adversarial.2-F02", result.stdout)

    def test_this_repository_is_clean(self):
        # moltke's own reports are the largest real corpus of fenced evidence
        # there is, and they were written before this check existed.
        for report in sorted((REPO / "adocs" / "audit").glob("*.md")):
            self.assertEqual(moltke.hidden_findings(report), [], report.name)




class TestOneDecodePolicy(unittest.TestCase):
    """S064 (2026-08-08_adversarial-F05): thirteen readers decoded strictly and
    six replaced, and INV-14's two halves disagreed about the same file. One
    non-UTF-8 byte — a pasted terminal capture, a Bash heredoc, a file another
    tool wrote — turned every mode into a traceback, which from a Stop hook
    means exit 1, no message, and every gate off."""

    LATIN1 = b"note: caf\xe9 latin-1\n"

    def test_one_bad_byte_in_a_step_file_does_not_break_any_mode(self):
        # S063 already made the strip_guidance readers tolerant; these are the
        # ones it did not touch — parse_step_file, the testing ledger, status.md.
        for target in ("adocs/plan_current/S003_active.md", "adocs/testing.md",
                       "adocs/status.md"):
            for mode, allowed in (("--validate", (0, 1)), ("--post-write", (0, 2)),
                                  ("--stop", (0, 2)), ("--session-start", (0,)),
                                  ("--step", (0, 1))):
                with self.subTest(target=target, mode=mode), \
                        tempfile.TemporaryDirectory() as tmp:
                    root = workflow_repo(tmp)
                    path = root / target
                    path.write_bytes(path.read_bytes() + self.LATIN1)
                    argv = [mode, "status"] if mode == "--step" else [mode]
                    result = run_moltke(root, *argv, stdin="{}")
                    output = result.stdout + result.stderr
                    self.assertNotIn("UnicodeDecodeError", output)
                    self.assertNotIn("Traceback", output)
                    self.assertIn(result.returncode, allowed, output)

    def test_one_bad_byte_in_an_audit_report_does_not_break_any_mode(self):
        # The S049 twin: hidden_findings replaced and report_findings did not,
        # so the two halves of one invariant disagreed about the same bytes.
        for mode in ("--validate", "--stop", "--post-write"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = workflow_repo(tmp)
                report = audit_report(root, [("2026-08-01_adversarial-F01", "accepted")])
                report.write_bytes(report.read_bytes() + b"evidence: caf\xe9\n")
                result = run_moltke(root, mode, stdin="{}")
                self.assertNotIn("UnicodeDecodeError", result.stdout + result.stderr)

    def test_audit_list_survives_it_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            report = audit_report(root, [("2026-08-01_adversarial-F01", "accepted")])
            report.write_bytes(report.read_bytes() + b"evidence: caf\xe9\n")
            result = run_moltke(root, "--audit", "list")
            self.assertNotIn("UnicodeDecodeError", result.stdout + result.stderr)
            self.assertIn("2026-08-01_adversarial-F01", result.stdout)

    def test_there_is_one_decode_policy_in_the_source(self):
        # Stated as a property of the code, since the defect was two policies
        # rather than either one of them.
        source = (REPO / "bin" / "moltke.py").read_text(encoding="utf-8")
        strict = [line.strip() for line in source.splitlines()
                  if ".read_text(" in line and "errors=" not in line]
        self.assertEqual(strict, [], "read repository files through read_file")


if __name__ == "__main__":
    unittest.main()
