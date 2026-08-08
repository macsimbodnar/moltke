id:         S074
goal:       tests/test_s033_fences.py runs every class when invoked directly
accepts:    python3 tests/test_s033_fences.py runs every class in the file; unittest.main() sits above the S063 and S064 classes today, so nine tests never run when it is invoked directly, while discovery runs them; red observed by counting tests in both invocations
touches:    tests/test_s033_fences.py
excludes:   changing what the tests assert
decisions:  
closes:     2026-08-08_adversarial.2-F08
blocks:
paused_by:
done:
