id:         S092
goal:       git_prefix is computed once per root, not once per path
accepts:    One run_checks over this repository spawns a single
            git rev-parse --show-prefix, not 257.
            --validate and --stop on this repository drop from about 7s to under 1s.
            The S081 behaviour it exists for is unchanged: the monorepo fixture at
            tests/test_s003_invariants.py:371 still passes, and INV-7/INV-8 still
            print blob specs that resolve below the git top level.
            A test asserts an upper bound on _git_run calls for one run_checks over
            a fixture with several completed steps; it fails without the fix.
touches:    bin/moltke.py git_prefix, from_git_path, to_git_path, run_checks;
            tests/test_s003_invariants.py
excludes:   caching any other git query; changing what INV-7 or INV-8 check.
decisions:
closes:     2026-08-08_adversarial.4-F05
blocks:
paused_by:
done:      2026-08-09: git_prefix is computed once per root and cached, closing 2026-08-08_adversarial.4-F05. It shells out to git rev-parse --show-prefix and from_git_path and to_git_path call it once per path, so INV-7 and INV-8 walking every completed step and every history line spawned 257 processes for one run_checks over this repository — on every prompt, through the Stop and post-write hooks. Measured here against the stashed tree: --validate 9.54s to 0.72s, --stop 9.79s to 0.78s. The answer cannot change while a run is in flight, and the key is the root, so a process checking two roots still asks once for each. 1 test counting the subprocess spawns, red observed at 29 != 1; it asserts at least one lookup first, so a fixture without git history cannot pass by abstaining. S081's monorepo behaviour is unchanged and still green. Suite 397 OK, --validate green. README test count 396 to 397; MANUAL checked, no change — the caching is invisible at the surface it documents; specs gained a dated note carrying the measurements.
