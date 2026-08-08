"""S022 (DEC-024), S031 (DEC-032): secret-leak checks run inside the normal
suite, not as a separate ritual (AGENTS.md section 6).

The shapes live in bin/moltke.py and run as INV-15, so every repository moltke
is installed into inherits the check rather than only moltke's own suite. This
file imports them, so the detector has exactly one definition and the
non-vacuity guard below covers the version that ships.

Detect, never redact. Redaction at write time would contradict the verbatim
guarantee of section 9, and a false positive would silently destroy forensic
content, so the log would stop being evidence of what was actually said.

Prefixed key shapes and PEM headers only. No entropy or bare-hex heuristic: this
worklog is full of git shas and md5 digests, and those rules would fire on every
recap. The trade is deliberate — catch the shapes worth catching, stay quiet
otherwise.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import workflow_repo
from surface import moltke

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"

WORKLOG = Path(__file__).resolve().parent.parent / "adocs" / "worklog.md"

# The shipped shapes, not a copy: a second definition would drift, and the copy
# under test would stop being the code that runs in anyone's repository.
SHAPES = moltke.SECRET_SHAPES
scan = moltke.scan_secrets


# Shapes this must never fire on. The worklog records a commit sha in every recap
# and md5 digests wherever a file was verified byte-identical, so a bare-hex or
# entropy rule would make the suite red on every work turn.
BENIGN = [
    "e828210",
    "b492c06",
    "c52956752a8b022715f7dfdf49ca52d9",
    "fc2750fa1f4a4c2b9e6d8a7b5c3e1f0d2a4b6c8e",
    "550e8400-e29b-41d4-a716-446655440000",
    "sk-",
    "skipped the audit",
    "AKIA",
    "npm install",
    "-----BEGIN CERTIFICATE-----",
]


class TestDetector(unittest.TestCase):
    """Non-vacuous by construction: the detector is proven to work before it is
    pointed at the real file."""

    def test_every_shape_catches_its_known_bad_example(self):
        for label, pattern, example in SHAPES:
            with self.subTest(label):
                self.assertTrue(pattern.search(example),
                                f"{label} no longer matches its own example; the check below "
                                f"would pass by failing to look")

    def test_the_scan_reports_a_planted_secret(self):
        for label, _pattern, example in SHAPES:
            with self.subTest(label):
                planted = f"# Worklog\n\n## 2026-08-06 prompt\n\n> deploy with {example}\n"
                hits = scan(planted)
                self.assertTrue(hits, f"{label} planted in a worklog was not reported")
                self.assertEqual(hits[0][1], 5, "the reported line number is wrong")

    def test_benign_strings_never_fire(self):
        for value in BENIGN:
            with self.subTest(value=value):
                self.assertEqual(scan(f"commit {value} recorded"), [],
                                 f"{value!r} tripped the secret check; git shas, digests, and "
                                 f"ordinary prose must never make the suite red")


class TestWorklog(unittest.TestCase):
    def test_the_worklog_holds_no_secret_shapes(self):
        if not WORKLOG.is_file():
            self.skipTest(f"{WORKLOG} does not exist yet; this check activates with it")
        hits = scan(WORKLOG.read_text(encoding="utf-8", errors="replace"))
        report = "; ".join(f"{label} at line {number} (starts {snippet!r})"
                           for label, number, snippet in hits)
        self.assertEqual(
            hits, [],
            f"secret-shaped content in adocs/worklog.md: {report}. Prompts are recorded "
            f"verbatim, so this is a real leak until proven otherwise: rotate the credential "
            f"first, then edit the worklog — it is append-only by convention and not enforced, "
            f"so cleaning it is an ordinary commit. See MANUAL.md, known issues.")


class TestTheInvariantTravels(unittest.TestCase):
    """S031 (DEC-032): the shapes protected moltke's own worklog and nothing
    else. A repository that installs the plugin runs moltke's hooks, not
    moltke's suite, so it inherited verbatim prompt logging into a tracked file
    with no check at all — and moltke is the thing writing the secret to disk."""

    def run_moltke(self, root, *args, stdin=""):
        return subprocess.run([sys.executable, str(MOLTKE), *args], cwd=root,
                              capture_output=True, text=True, input=stdin)

    def planted(self, tmp, example):
        root = workflow_repo(tmp)
        worklog = root / "adocs" / "worklog.md"
        worklog.write_text(worklog.read_text(encoding="utf-8")
                           + f"\n## 2026-08-08 prompt\n\n> deploy with {example}\n",
                           encoding="utf-8")
        return root

    def test_validate_reports_every_planted_shape(self):
        for label, _pattern, example in SHAPES:
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                root = self.planted(tmp, example)
                result = self.run_moltke(root, "--validate")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("INV-15", result.stdout)
                self.assertIn(label, result.stdout)

    def test_stop_refuses_on_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.planted(tmp, SHAPES[0][2])
            result = self.run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("INV-15", result.stderr)

    def test_the_report_names_the_line_and_truncates_the_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            example = SHAPES[0][2]
            root = self.planted(tmp, example)
            planted_line = (root / "adocs" / "worklog.md").read_text(
                encoding="utf-8").splitlines().index(f"> deploy with {example}") + 1
            stdout = self.run_moltke(root, "--validate").stdout
            self.assertIn(f"line {planted_line}", stdout,
                          "the line number is what makes it findable")
            self.assertNotIn(example, stdout, "the whole value must never be printed")
            self.assertIn(example[:8], stdout)

    def test_a_clean_worklog_stays_silent(self):
        # Non-vacuity: the fixture repository must be green without the plant,
        # or every assertion above could be any other violation.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = self.run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_benign_content_in_a_real_worklog_does_not_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            worklog = root / "adocs" / "worklog.md"
            worklog.write_text(worklog.read_text(encoding="utf-8")
                               + "\n## 2026-08-08 recap S001\n\ncommit "
                               + ", ".join(BENIGN) + "\n", encoding="utf-8")
            result = self.run_moltke(root, "--validate")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_only_the_worklog_is_scanned(self):
        # The scope DEC-024 set: a key pasted into a decision entry or a step
        # file is out of scope, and widening it silently would be a different
        # trade than the one recorded.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            decisions = root / "adocs" / "decisions.md"
            decisions.write_text(decisions.read_text(encoding="utf-8")
                                 + f"\nkey {SHAPES[0][2]}\n", encoding="utf-8")
            result = self.run_moltke(root, "--validate")
            self.assertNotIn("INV-15", result.stdout)
