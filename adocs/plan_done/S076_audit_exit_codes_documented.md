id:         S076
goal:       --audit's exit codes match the documented table, and a write failure says write
accepts:    --audit's exit codes match README's table and MANUAL's, or the tables are corrected to match the code: today the backstop returns 2 from a mode the tables assign 0 and 1 only; a write failure is reported as could not read the repository, which is false for that path; red observed with both, and the exit-code test extended to cover --audit
touches:    bin/moltke.py the main backstop and mode_audit; README.md; MANUAL.md; tests/test_s025_exit_codes.py
excludes:   changing the exit codes of --validate, --step, or the hooks
decisions:  
closes:     2026-08-08_adversarial.2-F10
blocks:
paused_by:
done:      2026-08-08: --audit refuses with exit 1 on stderr like --step does, instead of returning the main backstop exit 2 that README assigns to the three hook modes only, and its message says whether the failure was a read or a write. A failed --audit new was reported as could not read the repository, with --validate named as the remedy, which had nothing to do with it; the exit table had stopped being traceable to the code that produces it, which section 7 requires of every doc claim. 3 tests, red observed on both the write and the read path. Suite 345 OK, --validate green. README test count 342 to 345; the exit tables in README and MANUAL are correct again without editing, since the code now matches them; specs gained a dated note.
