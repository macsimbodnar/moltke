"""S022 (DEC-024): secret-leak checks run inside the normal suite, not as a
separate ritual (AGENTS.md section 6).

Detect, never redact. Redaction at write time would contradict the verbatim
guarantee of section 9, and a false positive would silently destroy forensic
content, so the log would stop being evidence of what was actually said.

Prefixed key shapes and PEM headers only. No entropy or bare-hex heuristic: this
worklog is full of git shas and md5 digests, and those rules would fire on every
recap. The trade is deliberate — catch the shapes worth catching, stay quiet
otherwise.
"""

import re
import unittest
from pathlib import Path

WORKLOG = Path(__file__).resolve().parent.parent / "adocs" / "worklog.md"

# (label, pattern, a known-bad example the pattern must catch). The examples are
# synthetic and exist to keep the detector honest: a pattern that stopped
# matching would otherwise leave this whole file passing on an empty scan.
SHAPES = [
    ("AWS access key id",
     re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
     "AKIA" + "IOSFODNN7EXAMPLE"),
    ("GitHub token",
     re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
     "ghp_" + "0123456789abcdefghijklmnopqrstuvwxyzAB"),
    ("GitHub fine-grained PAT",
     re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b"),
     "github_pat_" + "11ABCDEFG0abcdefghijklmn"),
    ("Anthropic API key",
     re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
     "sk-ant-" + "api03-Aa0Bb1Cc2Dd3Ee4Ff5Gg6"),
    ("OpenAI API key",
     re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}\b"),
     "sk-" + "Aa0Bb1Cc2Dd3Ee4Ff5Gg6Hh7Ii8Jj9Kk0Ll1"),
    ("Slack token",
     re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
     "xoxb-" + "1234567890-ABCdefGHIjkl"),
    ("Google API key",
     re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
     "AIza" + "SyA0123456789abcdefghijklmnopqrstuv"),
    ("Stripe live key",
     re.compile(r"\b[srp]k_live_[A-Za-z0-9]{16,}\b"),
     "sk_live_" + "0123456789abcdefghij"),
    ("npm token",
     re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"),
     "npm_" + "0123456789abcdefghijklmnopqrstuvwxyz"),
    ("PEM private key header",
     re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
     "-----BEGIN RSA PRIVATE KEY-----"),
    ("JSON web token",
     re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
     "eyJhbGciOiJIUzI1NiJ9." + "eyJzdWIiOiIxMjM0NTY3ODkwIn0." + "dBjftJeZ4CVPmB92K27u"),
]

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


def scan(text):
    """[(label, line number, first 8 characters of the match)] for every hit."""
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        for label, pattern, _example in SHAPES:
            match = pattern.search(line)
            if match:
                hits.append((label, number, match.group(0)[:8]))
    return hits


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
