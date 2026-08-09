id:         S102
goal:       the two documented refusals match what the code does
accepts:    MANUAL's exit-code prose no longer names "--audit new on an existing
            report" as a refusal, because it takes a `.2` suffix and exits 0 —
            which the same file already describes correctly, and which S020 chose
            on purpose.
            --decline against an enabled repository is either routed through
            refuse, so it exits 1 on stderr like every other refusal, or the word
            "refuses" is dropped from MANUAL and specs. The exit-code table and
            the code agree afterwards, and the same choice is applied to
            --scaffold on a declined repository, which has the same shape.
            If the behaviour changes rather than the prose, the existing tests
            asserting exit 0 there are re-targeted rather than deleted, and the
            golden surface is refreshed only after specs and MANUAL carry it.
            A test asserts the chosen behaviour; it fails without the change.
touches:    MANUAL.md; adocs/specs.md; bin/moltke.py mode_decline and
            mode_scaffold only if the behaviour is what changes;
            tests/test_s006_scaffold.py
excludes:   making --audit new refuse a same-day re-run, which S020 rejected and
            which the finding itself says is almost certainly wrong
decisions:
closes:     2026-08-09_adversarial-F06
blocks:
paused_by:
done:      2026-08-09: the two refusals MANUAL named are now the two the code makes, closing 2026-08-09_adversarial-F06. --decline against an already-enabled repository goes through refuse and exits 1 on stderr, which is what MANUAL and the specs surface table have both claimed since it was written while the code printed to stdout and returned 0 — indistinguishable, by exit code and by stream, from the success it was declining to perform, which matters to anyone scripting the init flow outside Claude Code. The exit-code prose no longer lists --audit new on an existing report as a refusal: it takes a .2 suffix and exits 0, as S020 chose and as the same file already described correctly. --scaffold against a declined repository is deliberately not changed to match: routing it through refuse for symmetry was tried and reverted because INV-11 says every mode exits 0 in a declined repository, its test caught it, and a repository that declined feeling nothing outranks the tidiness of one exit code. No document calls that branch a refusal, so nothing disagrees with it. 5 tests, red observed on two; two existing tests were re-targeted to the new exit code rather than relaxed, keeping their unchanged-state assertions. Suite 440 OK, --validate green. README test count 435 to 440; MANUAL's exit-code prose corrected; specs gained a dated note and its --decline surface row now carries the exit code.
