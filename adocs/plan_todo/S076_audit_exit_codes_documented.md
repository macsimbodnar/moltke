id:         S076
goal:       --audit's exit codes match the documented table, and a write failure says write
accepts:    --audit's exit codes match README's table and MANUAL's, or the tables are corrected to match the code: today the backstop returns 2 from a mode the tables assign 0 and 1 only; a write failure is reported as could not read the repository, which is false for that path; red observed with both, and the exit-code test extended to cover --audit
touches:    bin/moltke.py the main backstop and mode_audit; README.md; MANUAL.md; tests/test_s025_exit_codes.py
excludes:   changing the exit codes of --validate, --step, or the hooks
decisions:  
closes:     2026-08-08_adversarial.2-F10
blocks:
paused_by:
done:
