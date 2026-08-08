id:         S074
goal:       tests/test_s033_fences.py runs every class when invoked directly
accepts:    python3 tests/test_s033_fences.py runs every class in the file; unittest.main() sits above the S063 and S064 classes today, so nine tests never run when it is invoked directly, while discovery runs them; red observed by counting tests in both invocations
touches:    tests/test_s033_fences.py
excludes:   changing what the tests assert
decisions:  
closes:     2026-08-08_adversarial.2-F08
blocks:
paused_by:
done:      2026-08-08: unittest.main() is the last thing in every test file, so running one directly collects every class in it. test_s033_fences.py had the guard above two classes and ran 26 of its 35 tests directly against 35 under discovery, which hid nine tests from the red-first workflow AGENTS.md section 6 prescribes: for S063 and S064 the file reported OK while running none of their cases. Two further files, test_s022_secrets.py and test_s025_exit_codes.py, had no guard at all and ran nothing when invoked directly. A new surface test flags both shapes. Test-only step, no behaviour change. Red observed on three files, and every file now measured to agree with discovery. Suite 340 OK, --validate green. README test count 339 to 340; MANUAL and specs needed no change.
