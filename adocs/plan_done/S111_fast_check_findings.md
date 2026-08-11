id:         S111
goal:       fix the five findings of the batch's own fast check
accepts:    acceptance criteria, testable
touches:    areas of the codebase
excludes:   explicitly out of scope
decisions:
closes:
blocks:
paused_by:
done:      2026-08-11: the five findings of the batch's own tier-1 fast check, fixed. The real one: the .git/info/exclude check was a substring test, so a line like .moltke.local.md.bak read as already-excluded and the real exclusion was never appended — now line-wise, red observed. The other four were comments still naming INV-8 beside INV-7 after S105 retired it; they now name INV-7 alone. First live run of the S108 tier-1 model: one small subagent over the two code commits, findings routed as trivial-fix-now with a red-first test for the one behavioural edge. 1 test. Suite 445 OK, --validate green. README test count 444 to 445; MANUAL checked, no change.
