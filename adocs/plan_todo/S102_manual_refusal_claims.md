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
done:
